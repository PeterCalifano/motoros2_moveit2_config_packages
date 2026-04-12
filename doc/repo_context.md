# Repo Context

## Overview

This repository is a ROS 2 workspace for Yaskawa Motoman robots using MotoROS2 and MoveIt 2.

At the moment, the workspace contains:

- `motoman_gp12_support`: GP12 robot description, meshes, and basic viewer launches.
- `motoman_gp12_moveit2_config`: a MoveIt 2 package for a single GP12 using the `group_1/` joint naming convention.
- `motoman_hc10_support` and `motoman_hc10dtp_b00_moveit2_config`: the same pattern for the HC10 variant.
- `motoman_resources`: shared RViz configs and common xacro materials.
- `cosmica_resources`: target meshes and the dual GP12 plus rail plus target viewer launch.

## How The Current GP12 Dual Setup Works

The dual-cell description is now split across the cell package and the target-assets package:

- [`src/motoman_gp12_dual_cell_support/urdf/gp12_dual_cell.xacro`](/home/peterc/devDir/ws_ros/motoros2_moveit2_config_packages/src/motoman_gp12_dual_cell_support/urdf/gp12_dual_cell.xacro) composes the shared `world` frame, rail or fixed-base topology, dual GP12 robots, and optional target attachment.
- [`src/motoman_gp12_dual_cell_support/launch/view_gp12_dual_cell.launch.xml`](/home/peterc/devDir/ws_ros/motoros2_moveit2_config_packages/src/motoman_gp12_dual_cell_support/launch/view_gp12_dual_cell.launch.xml) launches `robot_state_publisher`, `joint_state_publisher_gui`, and RViz for the combined cell scene.
- [`src/cosmica_resources/urdf/itokawa_target.xacro`](/home/peterc/devDir/ws_ros/motoros2_moveit2_config_packages/src/cosmica_resources/urdf/itokawa_target.xacro) owns the reusable Itokawa target link geometry and simplified collision proxy.

The current transform chain for the target is simple:

- `world -> group_2/base_link -> ... -> group_2/flange -> group_2/tool0 -> group_2/target_mount -> group_2/target`
- the target mount offset is controlled in the `tool0 -> target_mount` joint
- the mesh scale and target collision proxy are parameterized through the cell YAML and target macro

## Current State Review

The repository is already useful for two things:

- single-robot MoveIt 2 visualization and planning for GP12 and HC10
- dual GP12 visualization and dual-stack MoveIt configuration for rail and fixed-base modes

The main gaps between the current state and a production-ready dual-robot stack are:

- live joint-state integration is still not defined for the dual stack
- the production action-server endpoints for the two GP12s and the rail still need to be matched to the deployed MotoROS2 topology
- automated self-collision matrix generation still needs to be rerun in an environment with the MoveIt Setup Assistant
- the local helper script `display_dual_gp12_target_rail.sh` still launches a compatibility viewer launch and should be renamed or folded into a `scripts/` layout

## Recommended Production Structure

If you want to grow this into a production workspace, I would separate responsibilities more clearly:

- Keep vendor-style robot support in `motoman_*_support`.
- Keep MoveIt 2 configuration in `*_moveit2_config`.
- Create a dedicated cell package for facility-specific scenes, for example `cosmica_dual_gp12_cell_support` or `motoman_gp12_cell_description`.
- Move the rail, target mount, and scene parameters into reusable xacro macros under that cell package.
- Put operator scripts in a tracked `scripts/` or `tools/` directory and name them for their real behavior.
- Store mount transforms, target scale, and rail geometry in YAML or xacro args instead of hard-coded literals.
- Add a dual MoveIt package, likely named `motoman_gp12_dual_moveit2_config`, with planning groups for `group_1`, `group_2`, and combined motions including the rail when needed.
- Add lightweight validation checks, at minimum xacro expansion checks and one launch smoke test.

## Current Dual Cell Configuration Source

The dual-cell scene is now parameterized from:

- [`src/motoman_gp12_dual_cell_support/config/gp12_dual_cell.yaml`](/home/peterc/devDir/ws_ros/motoros2_moveit2_config_packages/src/motoman_gp12_dual_cell_support/config/gp12_dual_cell.yaml)

That YAML owns the current cell dimensions and placement parameters for:

- rail geometry and rail joint limits
- world-to-rail transform
- `group_1` fixed-base transform for fixed mode
- `group_2` fixed-base transform
- target mount transform
- target mesh scale and material parameters

The top-level cell xacro that consumes this file is:

- [`src/motoman_gp12_dual_cell_support/urdf/gp12_dual_cell.xacro`](/home/peterc/devDir/ws_ros/motoros2_moveit2_config_packages/src/motoman_gp12_dual_cell_support/urdf/gp12_dual_cell.xacro)

The dual-cell launch entrypoint is:

- [`src/motoman_gp12_dual_cell_support/launch/view_gp12_dual_cell.launch.xml`](/home/peterc/devDir/ws_ros/motoros2_moveit2_config_packages/src/motoman_gp12_dual_cell_support/launch/view_gp12_dual_cell.launch.xml)

It accepts:

- `cell_mode:=rail|fixed`
- `attach_target:=true|false`

## Canonical Target Transform Chain

In rail mode, the mounted target chain is:

- `world -> group_2/base_link -> ... -> group_2/flange -> group_2/tool0 -> group_2/target_mount -> group_2/target`

In fixed mode, the target chain is the same from `group_2/base_link` downward.

`group_1` changes by mode:

- rail mode: `world -> rail -> group_1/base_link`
- fixed mode: `world -> group_1/base_link`

## Suggested Next Technical Milestone

Before building ROS 2 interfaces that feed MoveIt 2, the cleanest next step is:

1. Freeze the controller endpoint naming for the deployed MotoROS2 graph.
2. Decide the canonical joint list for live visualization:
   `rail_joint`, `group_1/joint_1..6`, `group_2/joint_1..6`.
3. Build an interface node that converts your upstream data into `sensor_msgs/msg/JointState`.
4. Validate the dual MoveIt launch against the real action-server endpoints.

That path will let RViz and MoveIt share the same robot description instead of maintaining separate visualization logic.

## Aligning The Target STL To The Flange

For alignment, I would avoid leaving the target directly attached to `tool0` with a guessed zero transform.

A better approach is:

- add an explicit intermediate frame such as `group_2/target_mount`
- measure or define the transform from `group_2/tool0` to the physical mount interface
- attach the STL to `target_mount`, not directly to `tool0`
- expose the mount `xyz` and `rpy` as xacro properties or arguments

Practical workflow:

1. In CAD or MeshLab, identify the target mesh reference point you want to coincide with the robot mounting frame.
2. Measure the translation from that reference point to the flange center.
3. Measure the rotation needed so the target axes match the flange or tool axes.
4. Put those values in the fixed joint from `tool0` to `target_mount`.
5. Re-open RViz, enable TF axes, and tune the final few millimeters/degrees visually.

The GP12 macro now exposes a dedicated `flange` frame before `tool0`, which is a better base for future tooling and calibration work.
