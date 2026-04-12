import os
from copy import deepcopy

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from moveit_configs_utils import MoveItConfigsBuilder
import xacro
import yaml


def _parse_bool_argument(value):
    normalized_value = value.strip().lower()
    if normalized_value in {"true", "1", "yes", "on"}:
        return True
    if normalized_value in {"false", "0", "no", "off"}:
        return False
    raise RuntimeError(
        f"Unsupported boolean value '{value}'. Expected one of true/false, 1/0, yes/no, on/off."
    )


def _load_yaml_file(file_path):
    with open(file_path, encoding="utf-8") as file_handle:
        return yaml.safe_load(file_handle)


def _pop_controller_definition(controller_manager_config, *candidate_names):
    for controller_name in candidate_names:
        if controller_name in controller_manager_config:
            return deepcopy(controller_manager_config.pop(controller_name))
    raise RuntimeError(
        f"None of the controller names {candidate_names} exist in the loaded MoveIt controller config."
    )


def _rewrite_controller_config(
    controller_config,
    *,
    cell_mode,
    controller_action_ns,
    group_1_controller_name,
    group_2_controller_name,
    rail_controller_name,
):
    controller_manager_config = controller_config["moveit_simple_controller_manager"]

    group_1_controller = _pop_controller_definition(
        controller_manager_config, "group_1_controller", "group_1_follow_joint_trajectory"
    )
    group_2_controller = _pop_controller_definition(
        controller_manager_config, "group_2_controller", "group_2_follow_joint_trajectory"
    )

    for controller in (group_1_controller, group_2_controller):
        controller["action_ns"] = controller_action_ns

    controller_manager_config["controller_names"] = [
        group_1_controller_name,
        group_2_controller_name,
    ]
    controller_manager_config[group_1_controller_name] = group_1_controller
    controller_manager_config[group_2_controller_name] = group_2_controller

    if cell_mode == "rail":
        rail_controller = _pop_controller_definition(
            controller_manager_config, "rail_controller", "rail_follow_joint_trajectory"
        )
        rail_controller["action_ns"] = controller_action_ns
        controller_manager_config["controller_names"].append(
            rail_controller_name)
        controller_manager_config[rail_controller_name] = rail_controller


def _launch_setup(context, *args, **kwargs):
    package_share = get_package_share_directory(
        "motoman_gp12_dual_moveit2_config")

    cell_mode = LaunchConfiguration("cell_mode").perform(context)
    attach_target = LaunchConfiguration("attach_target").perform(context)
    config_file = LaunchConfiguration("config_file").perform(context)
    group_1_controller_name = LaunchConfiguration(
        "group_1_controller_name").perform(context)
    group_2_controller_name = LaunchConfiguration(
        "group_2_controller_name").perform(context)
    rail_controller_name = LaunchConfiguration(
        "rail_controller_name").perform(context)
    controller_action_ns = LaunchConfiguration(
        "controller_action_ns").perform(context)
    moveit_manage_controllers = _parse_bool_argument(
        LaunchConfiguration("moveit_manage_controllers").perform(context)
    )

    if cell_mode not in {"rail", "fixed"}:
        raise RuntimeError(
            f"Unsupported cell_mode '{cell_mode}'. Expected 'rail' or 'fixed'.")

    robot_description_file_path = os.path.join(
        package_share, "config", "motoman_gp12_dual.urdf.xacro"
    )
    robot_description_semantic_file_path = os.path.join(
        package_share, "config", f"motoman_gp12_dual_{cell_mode}.srdf"
    )
    trajectory_execution_file_path = os.path.join(
        package_share, "config", f"moveit_controllers_{cell_mode}.yaml"
    )
    kinematics_file_path = os.path.join(
        package_share, "config", f"kinematics_{cell_mode}.yaml"
    )
    joint_limits_file_path = os.path.join(
        package_share, "config", f"joint_limits_{cell_mode}.yaml"
    )
    rviz_config_file_path = os.path.join(
        package_share, "config", "moveit.rviz")

    xacro_mappings = {
        "cell_mode": cell_mode,
        "attach_target": attach_target,
        "config_file": config_file,
    }

    robot_description_contents = xacro.process_file(
        robot_description_file_path, mappings=xacro_mappings
    ).toxml()

    warehouse_ros_config = {
        "warehouse_plugin": "warehouse_ros_sqlite::DatabaseConnection",
        "warehouse_host": LaunchConfiguration("warehouse_host"),
    }
    controller_config = _load_yaml_file(trajectory_execution_file_path)
    _rewrite_controller_config(
        controller_config,
        cell_mode=cell_mode,
        controller_action_ns=controller_action_ns,
        group_1_controller_name=group_1_controller_name,
        group_2_controller_name=group_2_controller_name,
        rail_controller_name=rail_controller_name,
    )

    moveit_config = (
        MoveItConfigsBuilder(
            "motoman_gp12_dual",
            package_name="motoman_gp12_dual_moveit2_config",
        )
        .robot_description(file_path=robot_description_file_path, mappings=xacro_mappings)
        .robot_description_semantic(file_path=robot_description_semantic_file_path)
        .robot_description_kinematics(file_path=kinematics_file_path)
        .joint_limits(file_path=joint_limits_file_path)
        .trajectory_execution(file_path=trajectory_execution_file_path)
        .to_moveit_configs()
    )

    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            moveit_config.to_dict(),
            controller_config,
            {"moveit_manage_controllers": moveit_manage_controllers},
            warehouse_ros_config,
        ],
        arguments=["--ros-args", "--log-level", "info"],
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config_file_path],
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.planning_pipelines,
            moveit_config.joint_limits,
            warehouse_ros_config,
        ],
    )

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="both",
        parameters=[{"robot_description": robot_description_contents}],
    )

    joint_state_publisher_node = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        name="joint_state_publisher",
        output="screen",
    )

    return [
        move_group_node,
        rviz_node,
        robot_state_publisher_node,
        joint_state_publisher_node,
    ]


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "warehouse_host",
                default_value="",
                description="Database connection path",
            ),
            DeclareLaunchArgument(
                "cell_mode",
                default_value="rail",
                description="Cell topology: rail or fixed",
            ),
            DeclareLaunchArgument(
                "attach_target",
                default_value="true",
                description="Attach the target mesh to group_2",
            ),
            DeclareLaunchArgument(
                "config_file",
                default_value=os.path.join(
                    get_package_share_directory(
                        "motoman_gp12_dual_cell_support"),
                    "config",
                    "gp12_dual_cell.yaml",
                ),
                description="Absolute path to the dual-cell YAML config file",
            ),
            DeclareLaunchArgument(
                "group_1_controller_name",
                default_value="group_1_controller",
                description="MoveIt controller name for the first GP12 trajectory action server",
            ),
            DeclareLaunchArgument(
                "group_2_controller_name",
                default_value="group_2_controller",
                description="MoveIt controller name for the second GP12 trajectory action server",
            ),
            DeclareLaunchArgument(
                "rail_controller_name",
                default_value="rail_controller",
                description="MoveIt controller name for the rail trajectory action server in rail mode",
            ),
            DeclareLaunchArgument(
                "controller_action_ns",
                default_value="follow_joint_trajectory",
                description="Action namespace appended to each configured controller name",
            ),
            DeclareLaunchArgument(
                "moveit_manage_controllers",
                default_value="false",
                description="Whether MoveIt should try to manage controller lifecycle directly",
            ),
            OpaqueFunction(function=_launch_setup),
        ]
    )
