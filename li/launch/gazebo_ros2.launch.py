from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    lab2_pkg = FindPackageShare('li')
    ros_gz_sim_pkg = FindPackageShare('ros_gz_sim')

    world_file = PathJoinSubstitution([lab2_pkg, 'worlds', 'test.sdf'])
    rviz_config = PathJoinSubstitution([lab2_pkg, 'config', 'robot.rviz'])
    gz_sim_launch = PathJoinSubstitution([ros_gz_sim_pkg, 'launch', 'gz_sim.launch.py'])

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gz_sim_launch),
            launch_arguments={'gz_args': [world_file]}.items(),
        ),

        # 2. Bridge between Gazebo and ROS2
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '/lidar@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
                '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            ],
            output='screen'
        ),

        # 3. Launch RViz2 for visualization
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            output='screen'
        ),
    ])