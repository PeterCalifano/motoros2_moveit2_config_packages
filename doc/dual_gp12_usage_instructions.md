# Dual GP12 Usage Instructions

## Purpose

This guide documents how to use the current dual GP12 configuration in this workspace for visualization of:

- two GP12 robots
- a shared rail for `group_1`
- an Itokawa target mesh mounted on `group_2`

## Files That Define The Scene

- [`src/motoman_gp12_dual_cell_support/urdf/gp12_dual_cell.xacro`](/home/peterc/devDir/ws_ros/motoros2_moveit2_config_packages/src/motoman_gp12_dual_cell_support/urdf/gp12_dual_cell.xacro): top-level dual GP12 cell with `rail|fixed` topology selection and optional target attachment.
- [`src/motoman_gp12_dual_cell_support/urdf/gp12_dual_rail_tool.xacro`](/home/peterc/devDir/ws_ros/motoros2_moveit2_config_packages/src/motoman_gp12_dual_cell_support/urdf/gp12_dual_rail_tool.xacro): compatibility wrapper for rail mode with target attached.
- [`src/motoman_gp12_dual_cell_support/launch/view_gp12_dual_cell.launch.xml`](/home/peterc/devDir/ws_ros/motoros2_moveit2_config_packages/src/motoman_gp12_dual_cell_support/launch/view_gp12_dual_cell.launch.xml): RViz launch for the dual scene with configurable topology and target attachment.
- [`src/motoman_gp12_support/urdf/gp12_macro.xacro`](/home/peterc/devDir/ws_ros/motoros2_moveit2_config_packages/src/motoman_gp12_support/urdf/gp12_macro.xacro): shared GP12 link, joint, and `tool0` definition.

## Current Frame Layout

- `world` is the shared fixed frame.
- `rail` is fixed in `world`.
- `rail_joint` moves `group_1/base_link` along the rail.
- `group_2/base_link` is fixed directly in `world`.
- `group_2/target_mount` is fixed to `group_2/tool0`.
- `group_2/target` is fixed to `group_2/target_mount`.

## Prerequisites

- ROS 2 installed and sourceable, currently matching your workspace setup such as Jazzy.
- Workspace dependencies installed.
- Workspace built at least once.

Example setup:

```bash
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build
source install/setup.bash
```

If you use Humble instead of Jazzy, replace the ROS setup path accordingly.

## Launch The Dual GP12 + Rail + Target Scene

After building and sourcing the workspace:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch motoman_gp12_dual_cell_support view_gp12_dual_cell.launch.xml cell_mode:=rail attach_target:=true
```

This launch starts:

- `robot_state_publisher`
- `joint_state_publisher_gui`
- `rviz2`

In RViz, the fixed frame should be `world`.

## What You Should See

- robot 1 as `group_1`, mounted on the prismatic `rail_joint`
- robot 2 as `group_2`, fixed in the world frame
- the rail geometry as a simple box
- the Itokawa target mesh attached through `group_2/target_mount`

The `joint_state_publisher_gui` window lets you manually move:

- `rail_joint`
- `group_1/joint_1` through `group_1/joint_6`
- `group_2/joint_1` through `group_2/joint_6`

## Validate The Xacro Directly

When you change the dual-scene xacro, it is helpful to validate expansion before launching:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
xacro src/motoman_gp12_dual_cell_support/urdf/gp12_dual_cell.xacro cell_mode:=rail attach_target:=true > /tmp/gp12_dual_rail_tool.urdf
```

The current dual xacros expand successfully in this workspace.

## Editing The Scene

Use these locations depending on what you want to change:

- rail dimensions and world placement:
  [`src/motoman_gp12_dual_cell_support/config/gp12_dual_cell.yaml`](/home/peterc/devDir/ws_ros/motoros2_moveit2_config_packages/src/motoman_gp12_dual_cell_support/config/gp12_dual_cell.yaml)
- target mesh, scale, and mount transform:
  [`src/cosmica_resources/urdf/itokawa_target.xacro`](/home/peterc/devDir/ws_ros/motoros2_moveit2_config_packages/src/cosmica_resources/urdf/itokawa_target.xacro)
  and
  [`src/motoman_gp12_dual_cell_support/config/gp12_dual_cell.yaml`](/home/peterc/devDir/ws_ros/motoros2_moveit2_config_packages/src/motoman_gp12_dual_cell_support/config/gp12_dual_cell.yaml)
- robot tool frame definition:
  [`src/motoman_gp12_support/urdf/gp12_macro.xacro`](/home/peterc/devDir/ws_ros/motoros2_moveit2_config_packages/src/motoman_gp12_support/urdf/gp12_macro.xacro)

Important current values in the target scene:

- `target.mesh_scale_xyz` is `0.001 0.001 0.001`
- `target.parent_to_mount_xyz` and `target.parent_to_mount_rpy` define `group_2/tool0 -> group_2/target_mount`

## Current Limitations

- The dual MoveIt package exists at
  [`src/motoman_gp12_dual_moveit2_config`](/home/peterc/devDir/ws_ros/motoros2_moveit2_config_packages/src/motoman_gp12_dual_moveit2_config),
  but the real controller endpoints and joint-state sources still need to match your MotoROS2 deployment.
- The existing GP12 MoveIt package remains single-robot only:
  [`src/motoman_gp12_moveit2_config`](/home/peterc/devDir/ws_ros/motoros2_moveit2_config_packages/src/motoman_gp12_moveit2_config)
- `display_dual_gp12_target_rail.sh` still points at a compatibility viewer launch and should be renamed or simplified.
- The dual package defaults to one external `FollowJointTrajectory` action server per GP12, plus an optional separate rail action server in rail mode.

## Recommended Usage Pattern Right Now

Use the current setup in two modes:

1. Use `ros2 launch motoman_gp12_dual_cell_support view_gp12_dual_cell.launch.xml cell_mode:=rail attach_target:=true` when you want to inspect geometry, frames, and scene layout.
2. Use `ros2 launch motoman_gp12_dual_moveit2_config demo.launch.py cell_mode:=rail` when you want the dual-stack MoveIt 2 flow.
3. Use `ros2 launch motoman_gp12_moveit2_config demo.launch.py` only when you want the existing single-robot MoveIt 2 flow.

Do not expect the dual MoveIt package to execute trajectories correctly until its controller names, action namespace, and joint-state source match the deployed MotoROS2 system.

## Best Next Step

The clean next development step is to feed the dual package with joint data for:

- `rail_joint`
- `group_1/joint_1..6`
- `group_2/joint_1..6`

That will let you drive visualization and planning from live or simulated interface data without depending on the joint-state GUI.
