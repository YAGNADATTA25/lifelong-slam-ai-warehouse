import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # Package directories
    pkg_simulation = get_package_share_directory('overhead_slam_simulation')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_turtlebot3_gazebo = get_package_share_directory('turtlebot3_gazebo')

    # Paths to files
    world_path = os.path.join(pkg_simulation, 'worlds', 'slam_world.world')

    # Environment variables
    set_tb3_model = SetEnvironmentVariable(name='TURTLEBOT3_MODEL', value='waffle_pi')

    tb3_models_path = os.path.join(pkg_turtlebot3_gazebo, 'models')
    autorace_models_path = os.path.join(tb3_models_path, 'turtlebot3_autorace_2020')
    user_gazebo_models = os.path.expanduser('~/.gazebo/models')
    existing_model_path = os.environ.get('GAZEBO_MODEL_PATH', '')

    set_gazebo_model_path = SetEnvironmentVariable(
        name='GAZEBO_MODEL_PATH',
        value=f"{user_gazebo_models}:{tb3_models_path}:{autorace_models_path}:{existing_model_path}"
    )

    disable_online_model_db = SetEnvironmentVariable(
        name='GAZEBO_MODEL_DATABASE_URI',
        value=''
    )

    # 1. Gazebo Server & Client
    start_gazebo_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'world': world_path, 'verbose': 'true'}.items()
    )

    # 2. Static TF Publisher - Map to World (Identity link to resolve detached camera TF warnings)
    tf_map_world = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_map_world',
        arguments=[
            '--x', '0.0', '--y', '0.0', '--z', '0.0',
            '--roll', '0.0', '--pitch', '0.0', '--yaw', '0.0',
            '--frame-id', 'map', '--child-frame-id', 'world'
        ]
    )

    # 3. Static TF Publisher - Room 1 Camera (Centered at X=-6.0, Y=3.5)
    tf_room1 = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_room1_camera',
        arguments=[
            '--x', '-6.0', '--y', '3.5', '--z', '3.0',
            '--roll', '0.0', '--pitch', '1.5708', '--yaw', '1.5708',
            '--frame-id', 'world', '--child-frame-id', 'room1_camera_link'
        ]
    )

    # 4. Static TF Publisher - Room 2 Camera (Centered at X=2.0, Y=3.5)
    tf_room2 = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_room2_camera',
        arguments=[
            '--x', '2.0', '--y', '3.5', '--z', '3.0',
            '--roll', '0.0', '--pitch', '1.5708', '--yaw', '1.5708',
            '--frame-id', 'world', '--child-frame-id', 'room2_camera_link'
        ]
    )

    # 5. Robot State Publisher (Publishes base_link, base_footprint, base_scan, etc.)
    robot_state_publisher = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_turtlebot3_gazebo, 'launch', 'robot_state_publisher.launch.py')
        ),
        launch_arguments={'use_sim_time': 'true'}.items()
    )

    # 6. Spawn TurtleBot3 at the exact warehouse center (0.0, 0.0, 0.01)
    spawn_turtlebot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_turtlebot3_gazebo, 'launch', 'spawn_turtlebot3.launch.py')
        ),
        launch_arguments={
            'x_pose': '0.0',
            'y_pose': '0.0',
            'z_pose': '0.01'
        }.items()
    )

    return LaunchDescription([
        set_tb3_model,
        set_gazebo_model_path,
        disable_online_model_db,
        start_gazebo_cmd,
        tf_map_world,
        tf_room1,
        tf_room2,
        robot_state_publisher,
        spawn_turtlebot
    ])