<!--
Open-H Embodiment Dataset README Template (v1.0)
Please fill out this template and include it in the ./metadata directory of your LeRobot dataset.
This file helps others understand the context and details of your contribution.
-->

# Needle Transfer - README

---

## 📋 At a Glance

*Teleoperated demonstrations of the da Vinci Si robot performing needle transfer with a suturing needle.*

<!--
**Example:** *Teleoperated demonstrations of a da Vinci robot performing needle passing on a silicone phantom.*
-->

---

## 📖 Dataset Description

<!--
*Briefly describe the purpose and content of this dataset. What key skills or scenarios does it demonstrate?*

**Example:** *This dataset contains 2,500 trajectories of expert surgeons using the dVRK to perform surgical suturing tasks. It includes successful trials, failures, and recovery attempts to provide a robust dataset for training imitation learning policies.*
-->
The dataset comprises 700 dVRK trajectories of needle transfer performed on a table top phantom, including successful trials, failures, and recovery attempts. It provides synchronized cartesian, joint and video data for training and evaluating robot learning policies. NOTE: The initial few episodes are a little zoomed out but the positioning of the camera is much closer after 100 episodes. 


| | |
| :--- | :--- |
| **Total Trajectories** | `700` |
| **Total Hours** | `2.9` |
| **Data Type** | `[ ] Clinical` `[ ] Ex-Vivo` `[x] Table-Top Phantom` `[ ] Digital Simulation` `[ ] Physical Simulation` `[ ] Other (If checked, update "Other")` |
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
- Needle Collection

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
| **Collection Period** | From `[2025-10-01]` to `[2025-01-15]` |

### Recovery Demonstrations

*Does this dataset include examples of recovering from failure?*

- [x] **Yes**
- [ ] **No**

**If yes, please briefly describe the recovery process:**
The dataset includes 25 recovery demonstrations and 75 failure demonstrations. In the failure cases, the robotic arm fails to achieve a grasp or drops while passing. In the recovery cases, the arm grasps the object with an incorrect orientation for passing, after which the operator re-orients the grasp before completing the pass. 

<!--
*Example: For 250 demonstrations, demonstrations are initialized from a failed needle grasp position, the operator re-orients the robotic grippers and attempts to grasp the needle again from a different angle.*
-->
---

## 💡 Diversity Dimensions

*Check all dimensions that were intentionally varied during data collection.*

- [x] **Camera Position / Angle**
- [x] **Lighting Conditions**
- [x] **Target Object** (e.g., different phantom models, suture types)
- [x] **Spatial Layout** (e.g., placing the target suture needle in various locations)
- [ ] **Robot Embodiment** (if multiple robots were used)
- [ ] **Task Execution** (e.g., different techniques for the same task)
- [ ] **Background / Scene**
- [ ] **Other** (Please specify: `[Your Dimension]`)

*If you checked any of the above please briefly elaborate below.*
The camera configuration was adjusted every 50–100 demonstrations by varying the setup height by ±2 cm. In addition, the needle type and phantom base were changed periodically. Lighting conditions were varied between 60% and 100%. Each demonstration also features a slightly different needle pickup location.
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
| **Primary Camera** | `Endoscopic Camera, 1920x1080 @ 30fps with both left and right video feed` |
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
- [ ] **Robot Base Frame**
- [ ] **Tool/End-Effector Frame**
- [ ] **World/Global Frame**
- [x] **Camera Frame**
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

**Example:**
```
observation.state: [PSM{i}_joint_1, PSM{i}_joint_2, PSM{i}_joint_3, PSM{i}_joint_4, PSM{i}_joint_5, PSM{i}_joint_6, PSM{i}_jaw, PSM{i}_ee_x, PSM{i}_ee_y, PSM{i}_ee_z, PSM{i}_ee_roll, PSM{i}_ee_pitch, PSM{i}_ee_yaw]
- PSM{i} represents the arm (Could be PSM1 or PSM2)
- PSM{i}_joint_1 to PSM{i}_joint_6: Absolute joint positions for the 7-DOF arm (radians)
- PSM{i}_jaw: Jaw angle of the gripper (radians)
- PSM{i}_ee_x, PSM{i}_ee_y, PSM{i}_ee_z: End-effector absolute position in camera (ECM) frame (meters)
- PSM{i}_ee_roll, PSM{i}_ee_pitch, PSM{i}_ee_yaw: End-effector absolute orientation as Euler angles (radians)

```

---

## ⏱️ Data Synchronization Approach

*Describe how you achieved proper data synchronization across different sensors, cameras, and robotic systems during data collection. This is crucial for ensuring temporal alignment of all modalities in your dataset.*

We use the ApproximateTimeSynchronizer [[Link]](https://wiki.ros.org/message_filters/ApproximateTime) from the ROS message_filters package to synchronize all data streams. The queue_size parameter controls the number of incoming messages buffered for each topic, while the slop parameter specifies the maximum allowable time difference between messages for them to be considered synchronized. This approach aligns messages based on their timestamps within a defined tolerance rather than requiring exact matches. 

Data is recorded at 30 Hz, with the camera feed acting as the bottleneck. During data collection, we monitor the inter-frame time difference and ensure it remains close to 33 ms, resulting in approximately 450 frames per 15-second episode. In rare cases, message delays lead to significantly fewer frames (fewer than 435); such episodes are discarded and re-recorded.

<!--
**Example:** *We collect joint kinematics from our Franka Research 3 and RGB-D frames from Intel RealSense D435 cameras, all running in ROS 2 Galactic on the same workstation clocked with ROS Time. Both drivers stamp their outgoing messages’ header.stamp fields with the shared system clock, and we record /joint_states, /camera/*/image_raw, and /camera/*/camera_info in a single rosbag2 session. During export to LeRobot, each data point’s ROS header.stamp is written verbatim into the timestamp attribute. Offline checks show inter-sensor skew stays below ±2 ms across a 2-minute capture.*
-->
---

## ✅ Quality Control

### Timestamp Integrity

The exhaustive release audit checked **700 episode Parquet files mapped to this release path**, containing **313,882 frame rows (2.906315 nominal hours at 30 FPS)**.

**Audit status:** **NO TIMESTAMP FINDING**

Every discovered episode table had a canonical `timestamp` field whose values were readable, numeric, and finite. For sequences with at least two rows, no configured audit rule was triggered for constant or effectively collapsed ranges, duplicated or very-low-uniqueness values, decreasing transitions, epoch-like/non-relative representation or float32 absolute-time precision loss, or mean positive spacing outside the declared-frame-rate thresholds.

The mean-spacing rule flags values below 0.1× or above 5× the expected `1 / FPS` interval; it is not a frame-level jitter bound. Nominal hours are computed from row count and declared FPS, not timestamp span. This result applies only to the timestamp representation in the episode Parquets included in the audit. It does not establish video integrity, physical video–kinematic synchronization, or annotation correctness.


### Video–Kinematic Delay

Manual review recorded **3 episode measurements across 3 datasets** in the **Stanford CHARM: real dVRK** family, using one camera stream per episode. Positive delay means the visible event followed the kinematic event. Observed delay includes physical response and recording latency; this sample does not establish alignment for every episode.

| Dataset | Episodes measured | Median delay (ms) | Range (ms) | Review scope |
| :--- | ---: | ---: | ---: | :--- |
| [needle_transfer](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment/blob/main/Surgical/stanford/collaborative_haptics_and_robotics_in_medicine_lab/real_robot_dvrk/needle_transfer/README.md) | 1 | +66.7 | N/A | Single measurement |
| [peg_transfer](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment/blob/main/Surgical/stanford/collaborative_haptics_and_robotics_in_medicine_lab/real_robot_dvrk/peg_transfer/README.md) | 1 | +200.0 | N/A | Single measurement |
| [tissue_retraction](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment/blob/main/Surgical/stanford/collaborative_haptics_and_robotics_in_medicine_lab/real_robot_dvrk/tissue_retraction/README.md) | 1 | +66.7 | N/A | Single measurement |

<details>
<summary>Audited episodes and measurements</summary>

Episode indices and paths refer to the released dataset. Frame indices are zero-based. Delay is `(visual frame − kinematic frame) / measured video FPS × 1000`, rounded to 0.1 ms.

| Dataset | Episode | Episode table | Reviewed video | Signal | Kinematic frame | Visual frame | FPS | Delay (ms) |
| :--- | ---: | :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| needle_transfer | 223 | [Surgical/stanford/collaborative_haptics_and_robotics_in_medicine_lab/real_robot_dvrk/needle_transfer/data/chunk-000/episode_000223.parquet](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment/blob/9ee1dd90cc2d9e816e3787b10644d3241d8613d1/Surgical/stanford/collaborative_haptics_and_robotics_in_medicine_lab/real_robot_dvrk/needle_transfer/data/chunk-000/episode_000223.parquet) | [Surgical/stanford/collaborative_haptics_and_robotics_in_medicine_lab/real_robot_dvrk/needle_transfer/videos/chunk-000/observation.images.camera_left/episode_000223.mp4](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment/blob/9ee1dd90cc2d9e816e3787b10644d3241d8613d1/Surgical/stanford/collaborative_haptics_and_robotics_in_medicine_lab/real_robot_dvrk/needle_transfer/videos/chunk-000/observation.images.camera_left/episode_000223.mp4) | `observation.state[19]` | 139 | 141 | 30.000000 | +66.7 |
| peg_transfer | 225 | [Surgical/stanford/collaborative_haptics_and_robotics_in_medicine_lab/real_robot_dvrk/peg_transfer/data/chunk-000/episode_000225.parquet](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment/blob/9ee1dd90cc2d9e816e3787b10644d3241d8613d1/Surgical/stanford/collaborative_haptics_and_robotics_in_medicine_lab/real_robot_dvrk/peg_transfer/data/chunk-000/episode_000225.parquet) | [Surgical/stanford/collaborative_haptics_and_robotics_in_medicine_lab/real_robot_dvrk/peg_transfer/videos/chunk-000/observation.images.camera_left/episode_000225.mp4](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment/blob/9ee1dd90cc2d9e816e3787b10644d3241d8613d1/Surgical/stanford/collaborative_haptics_and_robotics_in_medicine_lab/real_robot_dvrk/peg_transfer/videos/chunk-000/observation.images.camera_left/episode_000225.mp4) | `observation.state[6]` | 280 | 286 | 30.000000 | +200.0 |
| tissue_retraction | 273 | [Surgical/stanford/collaborative_haptics_and_robotics_in_medicine_lab/real_robot_dvrk/tissue_retraction/data/chunk-000/episode_000273.parquet](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment/blob/9ee1dd90cc2d9e816e3787b10644d3241d8613d1/Surgical/stanford/collaborative_haptics_and_robotics_in_medicine_lab/real_robot_dvrk/tissue_retraction/data/chunk-000/episode_000273.parquet) | [Surgical/stanford/collaborative_haptics_and_robotics_in_medicine_lab/real_robot_dvrk/tissue_retraction/videos/chunk-000/observation.images.camera_left/episode_000273.mp4](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment/blob/9ee1dd90cc2d9e816e3787b10644d3241d8613d1/Surgical/stanford/collaborative_haptics_and_robotics_in_medicine_lab/real_robot_dvrk/tissue_retraction/videos/chunk-000/observation.images.camera_left/episode_000273.mp4) | `observation.state[6]` | 191 | 193 | 30.000000 | +66.7 |

</details>


---

## 👥 Attribution & Contact

*Please provide attribution for the dataset creators and a point of contact.*

| | |
| :--- | :--- |
| **Dataset Creators** | `Alaa Eldin Abdelaal`, `Chetan Reddy Narayanaswamy`, `Jiaqi Shao`, `Howard Ji`, `Allison Okamura` |
| **Institution** | `Stanford University` |
| **Contact Email** | `abdelaal@stanford.edu OR alaaaldinmagdy@gmail.com`, `chetanrn@stanford.edu`, `jiaqis7@stanford.edu`, `howardji@stanford.edu`, `aokamura@stanford.edu` |
| **Point of Contact** | `abdelaal@stanford.edu OR alaaaldinmagdy@gmail.com` |
