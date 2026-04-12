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

The dual-cell description is split across two packages:

- [`src/motoman_gp12_support/urdf/gp12_dual_rail.xacro`](/home/peterc/devDir/ws_ros/motoros2_moveit2_config_packages/src/motoman_gp12_support/urdf/gp12_dual_rail.xacro) builds the shared `world` frame, the rail, `rail_joint`, a rail-mounted `group_1` GP12, and a fixed `group_2` GP12.
- [`src/motoman_gp12_support/urdf/gp12_dual_rail_tool.xacro`](/home/peterc/devDir/ws_ros/motoros2_moveit2_config_packages/src/motoman_gp12_support/urdf/gp12_dual_rail_tool.xacro) extends that scene by attaching the Itokawa target mesh through an explicit `group_2/target_mount` frame.
- [`src/cosmica_resources/launch/view_gp12_dual_rail_target.launch.xml`](/home/peterc/devDir/ws_ros/motoros2_moveit2_config_packages/src/cosmica_resources/launch/view_gp12_dual_rail_target.launch.xml) launches `robot_state_publisher`, `joint_state_publisher_gui`, and RViz for the combined scene.

The current transform chain for the target is simple:

- `world -> group_2/base_link -> ... -> group_2/flange -> group_2/tool0 -> group_2/target_mount -> group_2/target`
- the target mount offset is controlled in the `tool0 -> target_mount` joint
- the mesh scale is hard-coded to `0.001`

## Current State Review

The repository is already useful for two things:

- single-robot MoveIt 2 visualization and planning for GP12 and HC10
- RViz-only visualization of a dual GP12 scene with a rail and attached target

The main gaps between the current state and a production-ready dual-robot stack are:

- there is no dedicated dual GP12 MoveIt 2 config package yet
- the rail joint exists in the URDF, but it is not modeled in any SRDF, controller config, or kinematics setup
- the target mount is now explicit, but it is still embedded directly in the dual-scene xacro instead of being a reusable mount macro or cell-level description
- GP12-specific scene launches currently live in `cosmica_resources`, which is otherwise a generic target-assets package
- the local helper script `display_dual_gp12_target_rail.sh` currently launches the single-robot GP12 MoveIt demo instead of the dual target scene

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

## Suggested Next Technical Milestone

Before building ROS 2 interfaces that feed MoveIt 2, the cleanest next step is:

1. Freeze the scene description for the dual cell.
2. Introduce a dedicated dual MoveIt package.
3. Decide the canonical joint list for visualization:
   `rail_joint`, `group_1/joint_1..6`, `group_2/joint_1..6`.
4. Build an interface node that converts your upstream data into `sensor_msgs/msg/JointState`.

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
