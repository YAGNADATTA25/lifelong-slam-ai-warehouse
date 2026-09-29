import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_simulation = get_package_share_directory('overhead_slam_simulation')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')
    pkg_turtlebot3_nav2 = get_package_share_directory('turtlebot3_navigation2')

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    map_yaml = LaunchConfiguration('map', default='')

    # Custom Nav2 params configured specifically for simulation time & SLAM mapping
    param_dir = os.path.join(pkg_simulation, 'config', 'nav2_params.yaml')
    if not os.path.exists(param_dir):
        tb3_model = os.environ.get('TURTLEBOT3_MODEL', 'waffle_pi')
        param_dir = os.path.join(pkg_turtlebot3_nav2, 'param', 'humble', f'{tb3_model}.yaml')

    rviz_config_dir = os.path.join(
        pkg_turtlebot3_nav2,
        'rviz',
        'tb3_navigation2.rviz'
    )

    # Bring up SLAM + Nav2 stack
    nav2_bringup_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'slam': 'True',
            'map': map_yaml,
            'use_sim_time': use_sim_time,
            'params_file': param_dir
        }.items()
    )

    # Launch RViz for visualization
    rviz_cmd = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_dir],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'
        ),
        DeclareLaunchArgument(
            'map',
            default_value='',
            description='Path to map yaml file (optional for SLAM mode)'
        ),
        nav2_bringup_cmd,
        rviz_cmd
    ])
