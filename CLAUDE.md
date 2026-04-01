# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ROS2 workspace containing MoveIt2 configuration packages for Yaskawa Motoman robots (GP12 and HC10DTP variants). Designed for use with MotoROS2 driver on Ubuntu with ROS2 Humble/Jazzy.

## Build & Run Commands

```bash
# Install dependencies
rosdep install --from-paths src --ignore-src

# Build all packages
colcon build

# Build a single package
colcon build --packages-select motoman_gp12_moveit2_config

# Source environment (after build)
source /opt/ros/jazzy/setup.bash   # or humble
source install/local_setup.bash

# Generate URDF from xacro (run from package urdf/ directory)
xacro gp12.xacro > gp12.urdf

# Launch MoveIt2 demo
ros2 launch motoman_gp12_moveit2_config demo.launch.py
ros2 launch motoman_hc10dtp_b00_moveit2_config demo.launch.py

# Launch with warehouse database
ros2 launch motoman_gp12_moveit2_config demo.launch.py warehouse_host:=filename.sqlite

# View robot model only (no MoveIt)
ros2 launch motoman_gp12_support view_gp12.launch.xml
```

## Architecture

### Package Dependency Graph

```
motoman_gp12_moveit2_config ──┐
                              ├── motoman_gp12_support ──┐
                              │                          ├── motoman_resources (shared colors, materials, rviz configs)
motoman_hc10dtp_b00_moveit2_config                       │
                              ├── motoman_hc10_support ──┘
                              └── moveit2 / warehouse_ros_sqlite
```

- **`*_moveit2_config`** packages: MoveIt2 launch files (`demo.launch.py`), SRDF, kinematics, joint limits, controller configs
- **`*_support`** packages: URDF/xacro models, visual/collision meshes, simple viewer launch files
- **`motoman_resources`**: Shared xacro includes (`common_colors.xacro`, `common_materials.xacro`) and RViz configs

### Launch Flow (demo.launch.py)

Uses `MoveItConfigsBuilder` from `moveit_configs_utils` to:
1. Process xacro URDF at launch time
2. Load all MoveIt configs (SRDF, kinematics, joint limits, controllers)
3. Start `robot_state_publisher`, `move_group`, and `rviz2` nodes
4. Optionally connect to `warehouse_ros_sqlite` database

### Joint Naming Convention

All joints and links use the MotoROS2 group prefix: `group_1/joint_1` through `group_1/joint_6`, `group_1/base_link`, `group_1/link_N`, `group_1/tool0`. This naming must match between URDF and the MotoROS2 controller configuration.

## Adding a New Robot

1. Create or obtain a `*_support` package with URDF/xacro and meshes under `src/`
2. Generate URDF: `xacro robot.xacro > robot.urdf`
3. Run MoveIt Setup Assistant: `ros2 launch moveit_setup_assistant setup_assistant.launch.py`
4. Apply post-generation fixes documented in README.md Step 6 (warehouse_ros_sqlite integration, controller namespace fixes, robot_state_publisher addition)
5. Build and test: `colcon build && source install/local_setup.bash`
