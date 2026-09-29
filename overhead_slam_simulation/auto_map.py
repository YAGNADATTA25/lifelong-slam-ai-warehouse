#!/usr/bin/env python3

import math
import rclpy
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

def euler_to_quaternion(yaw):
    """Convert a yaw angle (radians) to a Quaternion (qx, qy, qz, qw)."""
    qz = math.sin(yaw / 2.0)
    qw = math.cos(yaw / 2.0)
    return 0.0, 0.0, qz, qw

def create_pose(navigator, x, y, yaw=0.0):
    """Helper function to format a PoseStamped waypoint using simulation time."""
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = float(x)
    pose.pose.position.y = float(y)
    pose.pose.position.z = 0.0
    qx, qy, qz, qw = euler_to_quaternion(yaw)
    pose.pose.orientation.x = qx
    pose.pose.orientation.y = qy
    pose.pose.orientation.z = qz
    pose.pose.orientation.w = qw
    return pose

def main():
    rclpy.init()

    navigator = BasicNavigator()

    print("⏳ Waiting for Nav2 action server (/navigate_to_pose) to be ready...")
    server_ready = False
    while rclpy.ok() and not server_ready:
        server_ready = navigator.nav_to_pose_client.wait_for_server(timeout_sec=2.0)
        if not server_ready:
            print("⏳ Nav2 action server not ready yet, waiting...")

    print("✅ Nav2 active! Initializing autonomous mapping patrol...")

    PI = math.pi

    # --- Mode Selection ---
    # Set TEST_MODE = True for a 3-waypoint verification test
    # Set TEST_MODE = False for full 18-waypoint global warehouse mapping
    TEST_MODE = True

    if TEST_MODE:
        print("\n🧪 Running 3-Waypoint Verification Mode [(1,0) -> (2,0) -> (2,2)]...")
        waypoints = [
            create_pose(navigator, 1.0, 0.0, 0.0),   # Waypoint 1: 1m East
            create_pose(navigator, 2.0, 0.0, 0.0),   # Waypoint 2: 2m East
            create_pose(navigator, 2.0, 2.0, PI / 2) # Waypoint 3: 2m East, 2m North
        ]
    else:
        print("\n🌐 Running Full 18-Waypoint Warehouse Mapping Mode...")
        waypoints = [
            # --- Phase 1: Main Floor South & East Sweep ---
            create_pose(navigator, 3.0, -4.0, 0.0),       # Step 1
            create_pose(navigator, 8.0, -5.0, 0.0),       # Step 2
            create_pose(navigator, 9.0, -2.0, PI / 2),    # Step 3
            create_pose(navigator, 9.0, 2.0, PI),         # Step 4
            create_pose(navigator, 5.0, -1.0, PI),        # Step 5

            # --- Phase 2: Room 2 Patrol ---
            create_pose(navigator, 2.0, -0.5, PI / 2),    # Step 6: Outside Room 2
            create_pose(navigator, 2.0, 2.5, PI / 2),     # Step 7: Enter Room 2
            create_pose(navigator, 0.5, 4.0, 3 * PI / 4), # Step 8: Left corner
            create_pose(navigator, 3.5, 4.0, PI / 4),     # Step 9: Right corner
            create_pose(navigator, 2.0, -0.5, -PI / 2),   # Step 10: Exit Room 2

            # --- Phase 3: Room 1 Patrol ---
            create_pose(navigator, -3.0, -1.0, PI),       # Step 11: Transition west
            create_pose(navigator, -6.0, -0.5, PI / 2),   # Step 12: Outside Room 1
            create_pose(navigator, -6.0, 2.5, PI / 2),    # Step 13: Enter Room 1
            create_pose(navigator, -7.5, 4.0, 3 * PI / 4),# Step 14: Left corner
            create_pose(navigator, -4.5, 4.0, PI / 4),    # Step 15: Right corner
            create_pose(navigator, -6.0, -0.5, -PI / 2),  # Step 16: Exit Room 1

            # --- Phase 4: South-West Sweep & Return ---
            create_pose(navigator, -8.0, -4.0, -PI / 2),  # Step 17
            create_pose(navigator, 0.0, 0.0, 0.0)         # Step 18: Return to (0,0)
        ]

    completed = 0
    for idx, target in enumerate(waypoints, start=1):
        print(f"📍 Navigating to Waypoint {idx}/{len(waypoints)} -> X={target.pose.position.x:.1f}, Y={target.pose.position.y:.1f}")
        navigator.goToPose(target)

        # Spin ROS node loop to handle callbacks and status updates properly
        while not navigator.isTaskComplete():
            rclpy.spin_once(navigator, timeout_sec=0.1)

        result = navigator.getResult()
        if result == TaskResult.SUCCEEDED:
            completed += 1
            print(f"  └─ Waypoint {idx} reached successfully!")
        elif result == TaskResult.CANCELED:
            print(f"  └─ Waypoint {idx} canceled.")
            break
        elif result == TaskResult.FAILED:
            print(f"  └─ Waypoint {idx} failed. Stopping navigation.")
            break

    print(f"\n Patrol finished! Reached {completed}/{len(waypoints)} waypoints.")
    navigator.lifecycleShutdown()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
