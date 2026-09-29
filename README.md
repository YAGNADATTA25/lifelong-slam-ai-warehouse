### `lifelong-slam-ai-warehouse` `README.md`

```markdown
# Infrastructure-Assisted Lifelong SLAM: Overhead RGB-D Submap Fusion for AMRs

![Status](https://img.shields.io/badge/Status-Active_R%26D_Phase_2-brightgreen.svg)
![ROS 2 Humble](https://img.shields.io/badge/ROS_2-Humble-blue.svg)
![Python 3.10](https://img.shields.io/badge/Language-Python_3.10-yellow.svg)
![C++17](https://img.shields.io/badge/Language-C%2B%2B17-green.svg)
![Gazebo Simulator](https://img.shields.io/badge/Simulator-Gazebo_Classic-orange.svg)
![License](https://img.shields.io/badge/License-Apache_2.0-red.svg)

An active Master's R&D project developing an infrastructure-assisted SLAM and environment monitoring framework for Autonomous Mobile Robots (AMRs) operating in dynamic warehouse environments. The system leverages off-board overhead RGB-D sensor networks to generate local 2D occupancy submaps from 3D point clouds, streaming continuous spatial updates over ROS 2 topics to resolve local mobile robot sensor occlusions, reduce map entropy, and prevent long-term pose drift.

```

---

## 🏗 System Architecture & ROS 2 Data Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          GAZEBO WORLD FRAME                             │
│   ┌──────────────────────────────┐    ┌──────────────────────────────┐  │
│   │ Room 1 Overhead Cam (RGB-D)  │    │ Room 2 Overhead Cam (RGB-D)  │  │
│   └──────────────┬───────────────┘    └──────────────┬───────────────┘  │
└──────────────────┼───────────────────────────────────┼──────────────────┘
                   │ PointCloud2                       │ PointCloud2
┌──────────────────▼───────────────────────────────────▼──────────────────┐
│                           ROS 2 PROCESSING                              │
│   ┌──────────────────────────────┐    ┌──────────────────────────────┐  │
│   │    room1_submap_node (Py/C++)│    │   room2_submap_node (Py/C++) │  │
│   └──────────────┬───────────────┘    └──────────────┬───────────────┘  │
│                  └─────────────────┬─────────────────┘                  │
│                                    │ nav_msgs/msg/OccupancyGrid         │
│                        Global Submap Data Stream                        │
│                                    │                                    │
│   ┌────────────────────────────────▼─────────────────────────────┐      │
│   │  TurtleBot3 Nav2 Integration / Global Costmap Aggregator     │      │
│   │  Autonomous Exploration Loop (auto_map.py / Nav2 Commander)  │      │
│   └────────────────────────────────┬─────────────────────────────┘      │
└────────────────────────────────────┼────────────────────────────────────┘
                                     │ /tf & /map
┌────────────────────────────────────▼────────────────────────────────────┐
│                         RViz2 State Visualization                       │
└─────────────────────────────────────────────────────────────────────────┘

```

---

## 🔑 Key Engineering & R&D Highlights

* **Off-Board Infrastructure Perception:** Integrates ceiling-mounted overhead RGB-D sensors (`libgazebo_ros_camera`) to monitor spatial occupancy across multi-room warehouse environments independent of mobile robot line-of-sight occlusions.


* **Autonomous SLAM Mapping Loop:** Features an automated exploration script (`auto_map.py`) utilizing `nav2_simple_commander` (`BasicNavigator`) to route the AMR through room waypoints while building baseline Cartographer SLAM occupancy grids.


* **Point-Cloud to Occupancy Grid Conversion:** Filters and projects 3D point clouds (`sensor_msgs/msg/PointCloud2`) onto 2D local occupancy planes (`nav_msgs/msg/OccupancyGrid`) to update costmap layers.


* **Multi-Room Frame Synchronization:** Formulates static TF2 coordinate frame trees (`world` -> `room1_camera_link`, `world` -> `room2_camera_link`) ensuring spatial consistency across multi-room submaps.



---

## 📁 Package Architecture & Workspace Structure

```
overhead_slam_simulation/
├── package.xml               # Dependencies (rclcpp, rclpy, sensor_msgs, nav_msgs, tf2_ros)
├── setup.py                  # Python package entry points and install configurations
├── launch/
│   ├── dsm_world.launch.py   # Spawns Gazebo multi-room environment, overhead cameras & TB3
│   ├── slam_cartographer.launch.py # Launches Cartographer SLAM node
│   └── tb3_explore.launch.py # Autonomous exploration launcher
├── scripts/
│   └── auto_map.py           # Nav2 Waypoint Commander for automated mapping
├── worlds/
│   └── dsm_world.world       # Gazebo SDF environment with structural obstacles & cameras
└── urdf/                     # Robot & overhead camera sensor descriptions

```

---

## 📊 R&D Milestone Roadmap

```
Phase 1: Environment & Static TF Setup ────────────────────────────► [COMPLETED]
Phase 2: Cartographer SLAM & Auto-Mapping Loop (auto_map.py) ─────► [IN PROGRESS]
Phase 3: PointCloud2-to-OccupancyGrid Submap Projection Nodes ────► [IN PROGRESS]
Phase 4: Costmap Aggregation & Lifelong Drift Benchmarking ────────► [PLANNED]

```

---

## 💻 Tech Stack & Dependencies

* **ROS 2 Middleware:** Humble Hawksbill
* **Programming Languages:** Python 3.10, C++17
* **Core ROS 2 Interfaces:** `sensor_msgs/msg/PointCloud2`, `nav_msgs/msg/OccupancyGrid`, `geometry_msgs/msg/PoseStamped`
* **Libraries & Tools:** Nav2 Simple Commander, Cartographer SLAM, TF2, Gazebo Classic 11

---

## 🚀 Quick Start Guide

### Prerequisites

Ensure ROS 2 Humble and Gazebo Classic are sourced on Ubuntu 22.04 LTS.

```bash
# 1. Clone into your ROS 2 workspace src directory
cd ~/overhead_slam_ws/src
git clone [https://github.com/YAGNADATTA25/lifelong-slam-ai-warehouse.git](https://github.com/YAGNADATTA25/lifelong-slam-ai-warehouse.git)

# 2. Build workspace
cd ~/overhead_slam_ws
colcon build --symlink-install --packages-select overhead_slam_simulation
source install/setup.bash

# 3. Launch World & Autonomous SLAM Exploration
ros2 launch overhead_slam_simulation dsm_world.launch.py
ros2 run overhead_slam_simulation auto_map.py

```
