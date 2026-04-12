import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from moveit_configs_utils import MoveItConfigsBuilder
import xacro


def _launch_setup(context, *args, **kwargs):
    package_share = get_package_share_directory("motoman_gp12_dual_moveit2_config")
    cell_support_share = get_package_share_directory("motoman_gp12_dual_cell_support")

    cell_mode = LaunchConfiguration("cell_mode").perform(context)
    attach_target = LaunchConfiguration("attach_target").perform(context)
    config_file = LaunchConfiguration("config_file").perform(context)

    if cell_mode not in {"rail", "fixed"}:
        raise RuntimeError(f"Unsupported cell_mode '{cell_mode}'. Expected 'rail' or 'fixed'.")

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
    rviz_config_file_path = os.path.join(package_share, "config", "moveit.rviz")

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
        parameters=[moveit_config.to_dict(), warehouse_ros_config],
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
                    get_package_share_directory("motoman_gp12_dual_cell_support"),
                    "config",
                    "gp12_dual_cell.yaml",
                ),
                description="Absolute path to the dual-cell YAML config file",
            ),
            OpaqueFunction(function=_launch_setup),
        ]
    )
