<!--
Open-H Embodiment Dataset README Template (v1.0)
Please fill out this template and include it in the ./metadata directory of your LeRobot dataset.
This file helps others understand the context and details of your contribution.
-->

# Needle Transfer (Simulation)- README

---

## 📋 At a Glance

*Teleoperated demonstrations of the da Vinci robot in orbitsurgical library in Isaac Sim performing needle transfer*

<!--
**Example:** *Teleoperated demonstrations of a da Vinci robot performing needle passing on a silicone phantom.*
-->

---

## 📖 Dataset Description

<!--
*Briefly describe the purpose and content of this dataset. What key skills or scenarios does it demonstrate?*

**Example:** *This dataset contains 2,500 trajectories of expert surgeons using the dVRK to perform surgical suturing tasks. It includes successful trials, failures, and recovery attempts to provide a robust dataset for training imitation learning policies.*
-->
The dataset comprises around 500 dVRK trajectories of the needle transfer task including successful trials and some failure cases. It provides synchronized cartesian, joint and video data for training and evaluating robot learning policies. The asset used is from orbitsurgical library. 


| | |
| :--- | :--- |
| **Total Trajectories** | `500` |
| **Total Hours** | `2.5` |
| **Data Type** | `[ ] Clinical` `[ ] Ex-Vivo` `[ ] Table-Top Phantom` `[X] Digital Simulation` `[ ] Physical Simulation` `[ ] Other (If checked, update "Other")` |
| **License** | CC BY 4.0 |
| **Version** | `[e.g., 1.0]` |

---

## 🎯 Tasks & Domain

### Domain

*Select the primary domain for this dataset.*

- [x] **Surgical Robotics**
- [ ] **Ultrasound Robotics**
- [ ] **Other Healthcare Robotics** (Please specify: `[Your Domain]`)

### Demonstrated Skills

*List the primary skills or procedures demonstrated in this dataset.*
- Needle Pickup
- Needle Passing

<!--
***Example:***
- Needle-passing
- Suture-tying
- ...
-->
---

## 🔬 Collection Procedure

### Collection Method

*How was the data collected?*

- [x] **Human Teleoperation**
- [ ] **Programmatic/State-Machine**
- [ ] **AI Policy / Autonomous**
- [ ] **Other** (Please specify: `[Your Method]`)

### Operator Details

| | Description |
| :--- | :--- |
| **Operator Count** | `1` |
| **Operator Skill Level** | `[ ] Expert (e.g., Surgeon, Sonographer)` <br> `[x] Intermediate (e.g., Trained Researcher)` <br> `[ ] Novice (e.g., ML Researcher with minimal experience)` <br> `[ ] N/A` |
| **Collection Period** | From `[2025-10-01]` to `[2026-01-15]` |

### Recovery Demonstrations

*Does this dataset include examples of recovering from failure?*

- [ ] **Yes**
- [X] **No**

**If yes, please briefly describe the recovery process:**

<!--
*Example: For 250 demonstrations, demonstrations are initialized from a failed needle grasp position, the operator re-orients the robotic grippers and attempts to grasp the needle again from a different angle.*
-->
---

## 💡 Diversity Dimensions

*Check all dimensions that were intentionally varied during data collection.*

- [ ] **Camera Position / Angle**
- [ ] **Lighting Conditions**
- [ ] **Target Object** (e.g., different phantom models, suture types)
- [x] **Spatial Layout** (e.g., placing the target suture needle in various locations)
- [ ] **Robot Embodiment** (if multiple robots were used)
- [x] **Task Execution** (e.g., different techniques for the same task)
- [ ] **Background / Scene**
- [ ] **Other** (Please specify: `[Your Dimension]`)

*If you checked any of the above please briefly elaborate below.*
Each demonstration has a slightly different needle pickup location and pass location, also with the different pick up and pass style. 
<!--

**Example:** We adjusted the room camera perspective every 100 demonstrations. The camera angle was varied by panning up and down by +/- 10 degrees, as well as manually adjusting the height of the camera mount by +/- 2 cm. Additionally, we varied the needle used by swapping out various curvatures, including 1/4, 3/8, 1/2, and 5/8.
-->
---

## 🛠️ Equipment & Setup

### Robotic Platform(s)

*List the primary robot(s) used.*

- **Robot 1:** `dVRK (da Vinci Research Kit)`

### Sensors & Cameras

*List the sensors and cameras used. Specify model names where possible. 

| Type | Model/Details |
| :--- | :--- |
| **Primary Camera** | `Camera in Isaac Sim, 640x480 @ 20fps with both left and right video feed` |
| **Joint/Position Encoders** | |

---

## 🎯 Action & State Space Representation

*Describe how actions and robot states are represented in your dataset. This is crucial for understanding data compatibility and enabling effective policy learning.*

### Action Space Representation

**Primary Action Representation:**
- [x] **Absolute Cartesian** (position/orientation relative to camera frame (ECM))
- [ ] **Relative Cartesian** (delta position/orientation from current pose)
- [ ] **Joint Space** (direct joint angle commands)
- [ ] **Other** (Please specify: `[Your Representation]`)

**Orientation Representation:**
- [ ] **Quaternions** (x, y, z, w)
- [x] **Euler Angles** (roll, pitch, yaw)
- [ ] **Axis-Angle** (rotation vector)
- [ ] **Rotation Matrix** (3x3 matrix)
- [ ] **Other** (Please specify: `[Your Representation]`)

**Reference Frame:**
- [x] **Robot Base Frame**
- [ ] **Tool/End-Effector Frame**
- [ ] **World/Global Frame**
- [ ] **Camera Frame**
- [ ] **Other** (Please specify: `[Your Frame]`)

**Action Dimensions:**
*List the action space dimensions and their meanings.*
```
action: [PSM{i}_jaw, PSM{i}_ee_x, PSM{i}_ee_y, PSM{i}_ee_z, PSM{i}_ee_roll, PSM{i}_ee_pitch, PSM{i}_ee_yaw]
- PSM{i} represents the arm (Could be PSM1 or PSM2)
- PSM{i}_jaw: Jaw angle in radians
- PSM{i}_ee_x, PSM{i}_ee_y, PSM{i}_ee_z: Absolute position in camera frame (ECM frame)
- PSM{i}_ee_roll, PSM{i}_ee_pitch, PSM{i}_ee_yaw: Absolute Orientation as Euler Angles
```
<!--
**Example:**
```
action: [x, y, z, qx, qy, qz, qw, gripper]
- x, y, z: Absolute position in robot base frame (meters)
- qx, qy, qz, qw: Absolute orientation as quaternion
- gripper: Gripper opening angle (radians)
```
-->
### State Space Representation

**State Information Included:**
- [x] **Joint Positions** (all articulated joints)
- [ ] **Joint Velocities**
- [x] **End-Effector Pose** (Cartesian position/orientation)
- [ ] **Force/Torque Readings**
- [x] **Gripper State** (position, force, etc.)
- [ ] **Other** (Please specify: `[Your State Info]`)

**State Dimensions:**
*List the state space dimensions and their meanings.*

```
observation.state: [PSM{i}_joint_1, PSM{i}_joint_2, PSM{i}_joint_3, PSM{i}_joint_4, PSM{i}_joint_5, PSM{i}_joint_6, PSM{i}_jaw, PSM{i}_ee_x, PSM{i}_ee_y, PSM{i}_ee_z, PSM{i}_ee_roll, PSM{i}_ee_pitch, PSM{i}_ee_yaw]
- PSM{i} represents the arm (Could be PSM1 or PSM2)
- PSM{i}_joint_1 to PSM{i}_joint_6: Absolute joint positions for the 7-DOF arm (radians)
- PSM{i}_jaw: Jaw angle of the gripper (radians)
- PSM{i}_ee_x, PSM{i}_ee_y, PSM{i}_ee_z: End-effector absolute position in robot frame (meters)
- PSM{i}_ee_roll, PSM{i}_ee_pitch, PSM{i}_ee_yaw: End-effector absolute orientation as Euler angles (radians)

```

---

## ⏱️ Data Synchronization Approach

*Describe how you achieved proper data synchronization across different sensors, cameras, and robotic systems during data collection. This is crucial for ensuring temporal alignment of all modalities in your dataset.*

Our capture loop captures robot state, timestamp, and both camera frames in one tuple per frame and enqueues it. The ring buffer guarantees FIFO delivery so that logger thread dequeues the same tuple, writes the paired images, and records the synchronized data in exactly one row. 
Data is recorded around 20 Hz, with the camera feed acting as the bottleneck. resulting in approximately 460 frames per 25-second episode. 

<!--
**Example:** *We collect joint kinematics from our Franka Research 3 and RGB-D frames from Intel RealSense D435 cameras, all running in ROS 2 Galactic on the same workstation clocked with ROS Time. Both drivers stamp their outgoing messages’ header.stamp fields with the shared system clock, and we record /joint_states, /camera/*/image_raw, and /camera/*/camera_info in a single rosbag2 session. During export to LeRobot, each data point’s ROS header.stamp is written verbatim into the timestamp attribute. Offline checks show inter-sensor skew stays below ±2 ms across a 2-minute capture.*
-->
---

## ✅ Quality Control

### Timestamp Integrity

The exhaustive release audit checked **500 episode Parquet files mapped to this release path**, containing **229,232 frame rows (3.351345 nominal hours at 19 FPS)**.

**Audit status:** **NO TIMESTAMP FINDING**

Every discovered episode table had a canonical `timestamp` field whose values were readable, numeric, and finite. For sequences with at least two rows, no configured audit rule was triggered for constant or effectively collapsed ranges, duplicated or very-low-uniqueness values, decreasing transitions, epoch-like/non-relative representation or float32 absolute-time precision loss, or mean positive spacing outside the declared-frame-rate thresholds.

The mean-spacing rule flags values below 0.1× or above 5× the expected `1 / FPS` interval; it is not a frame-level jitter bound. Nominal hours are computed from row count and declared FPS, not timestamp span. This result applies only to the timestamp representation in the episode Parquets included in the audit. It does not establish video integrity, physical video–kinematic synchronization, or annotation correctness.


### Video–Kinematic Delay

Manual video–kinematic synchronization testing was **not performed** for the **Stanford CHARM: simulation** family because video and kinematics are **perfectly synchronized by design** in simulation.


---

## 👥 Attribution & Contact

*Please provide attribution for the dataset creators and a point of contact.*

| | |
| :--- | :--- |
| **Dataset Creators** | `Alaa Eldin Abdelaal`, `Chetan Reddy Narayanaswamy`, `Jiaqi Shao`, `Howard Ji`, `Allison Okamura` |
| **Institution** | `Stanford University` |
| **Contact Email** | `abdelaal@stanford.edu OR alaaaldinmagdy@gmail.com`, `chetanrn@stanford.edu`, `jiaqis7@stanford.edu`, `howardji@stanford.edu`, `aokamura@stanford.edu` |
| **Point of Contact** | `abdelaal@stanford.edu OR alaaaldinmagdy@gmail.com` |
