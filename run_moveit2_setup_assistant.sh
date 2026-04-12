# Source ros2
source /opt/ros/jazzy/setup.bash

# Source this environemnt setup (assuming it has been built)
source install/setup.bash

# Run
ros2 launch moveit_setup_assistant setup_assistant.launch.py
