<!--
Open-H Embodiment Dataset README Template (v1.0)
Please fill out this template and include it in the ./metadata directory of your LeRobot dataset.
This file helps others understand the context and details of your contribution.
-->

# surgical_actions_v2_with_tip2d - README

---

## 📋 At a Glance

*Clip-level labeled surgical endoscopic video segments with tool segmentation, monocular depth, and per-frame 2D tool-tip pose annotations for surgical action understanding.*

---

## 📖 Dataset Overview

This dataset provides clip-level annotated surgical endoscopic videos designed for learning and benchmarking visual surgical action understanding and tool-centric perception.  
Each clip contains synchronized RGB frames, monocular depth predictions, tool segmentation masks, and per-frame 2D tool-tip pose states. The dataset focuses on recognizing and localizing short-duration surgical actions such as grasping, pulling, exploration, and camera zoom.

| | |
| :--- | :--- |
| **Total Trajectories** | *TBD (filled after packaging)* |
| **Total Hours** | *TBD (filled after packaging)* |
| **Data Type** | ☑ Clinical ☐ Ex-Vivo ☐ Table-Top Phantom ☐ Digital Simulation ☐ Physical Simulation ☐ Other |
| **License** | CC BY 4.0 |
| **Version** | 2.0 |

---

## 🎯 Tasks & Domain

### Domain

- [x] **Surgical Robotics**
- [ ] **Ultrasound Robotics**
- [ ] **Other Healthcare Robotics**

### Demonstrated Skills

The dataset contains clip-level labels for the following surgical actions:

- CONTACT
- EXPLORATION
- GRASPING
- MOVE
- PULLING
- STATIC
- ZOOM_IN

Natural-language descriptions of each task are provided in `meta/tasks.jsonl`.

---

## 🔬 Data Collection Details

### Collection Method

- [x] **Human Teleoperation / Clinical Operation**
- [ ] Programmatic/State-Machine
- [ ] AI Policy / Autonomous
- [ ] Other

### Operator Details

| | Description |
| :--- | :--- |
| **Operator Count** | Multiple clinical operators (exact count not recorded) |
| **Operator Skill Level** | [x] Expert (surgeon) |
| **Collection Period** | *TBD* |

### Recovery Demonstrations

- [ ] **Yes**
- [x] **No**

This dataset does not explicitly include recovery-from-failure demonstrations.

---

## 💡 Diversity Dimensions

- [x] **Background / Scene**
- [x] **Task Execution**
- [x] **Target Object** (different tissues / anatomical structures)

The dataset spans diverse surgical scenes and anatomical contexts, with different execution styles for the same semantic action (e.g., pulling, grasping, and exploration).

---

## 🛠️ Equipment & Setup

### Robotic Platform(s)

This dataset consists of clinical endoscopic video only and does not include robot control signals.

- **Robot 1:** Clinical surgical robotic system (endoscopic video stream only)

### Sensors & Cameras

| Type | Model/Details |
| :--- | :--- |
| **Primary Camera** | Clinical endoscopic camera, RGB, clip-level video |
| **Medical Imager** | Monocular depth generated offline using VideoDepthAnything / DepthAnything v2 |
| **Other** | Tool segmentation masks generated offline using SAM3 |

---

## 🎯 Action & State Space Representation

This dataset is designed primarily for visual action understanding and tool-centric perception.  
It does **not** include low-level robot control commands.

### Action Space Representation

**Primary Action Representation:**

- [x] **Other** – Discrete semantic action label per clip

**Description**

action.label

css
Copy code

A categorical label indicating the surgical action being performed in the clip
(e.g., CONTACT, GRASPING, PULLING, MOVE, etc.).  
The label is repeated for all frames in the corresponding clip.

### State Space Representation

**State Information Included:**

- [x] **Other** – 2D tool tip pose in the image

**State Dimensions**

`observation.state.tip_2d: K x 3`

where `K` is the number of tools in the frame:

- x_px: horizontal image coordinate of the tool tip (pixels)
- y_px: vertical image coordinate of the tool tip (pixels)
- theta_deg: in-plane tool orientation (degrees)

Tool identity is provided by `observation.meta.tool_name`. The correspondence rule is `observation.state.tip_2d[i] ↔ observation.meta.tool_name[i]`.

If a tool is not visible in a frame, its values are set to `NaN`.

**Additional visual state representations:**

- RGB frames: `observation.images.color`
- Monocular depth: `observation.images.depth`
- Tool segmentation masks: `observation.images.tool_segmentation`

### 📋 Recommended Additional Representations

Not applicable.  
This dataset intentionally does not include joint states or Cartesian robot poses.

---

## ⏱️ Data Synchronization Approach

Within each clip, RGB frames, depth maps, tool segmentation masks, and 2D tool-tip pose annotations are aligned by frame index.  
All modalities are truncated to the minimum available length to guarantee temporal alignment.

Each frame contains a timestamp field (`timestamp_s`) in seconds. No multi-sensor hardware synchronization is required since all modalities are derived from the same RGB video stream during post-processing.

---

## ✅ Quality Control

### Timestamp Integrity

An exhaustive automated audit checked all **62 episode Parquet files** in this dataset, containing **6,690 frames (0.06194 nominal hours at 30 FPS)**.

**Audit status:** **ERROR — canonical schema compatibility**

| Finding | Severity | Affected episodes | Frames in affected episodes | Nominal hours |
| :--- | :--- | ---: | ---: | ---: |
| Canonical LeRobot `timestamp` column is absent; time is stored as `timestamp_s` | ERROR | 62 | 6,690 | 0.06194 |
| **Distinct affected total** | **ERROR** | **62** | **6,690** | **0.06194** |

This is a field-name compatibility finding, not missing or corrupted timing information. The existing `timestamp_s` column was also checked exhaustively: it contains finite numeric double-precision values that are relative, unique, strictly increasing, with cadence consistent with 1/30 s at the declared 30 FPS. Consumers that require the canonical LeRobot `timestamp` field must explicitly map or rename `timestamp_s`.

This audit evaluates timestamp schema, representation, and cadence. It does not directly measure physical video–kinematic synchronization; the frame-index alignment procedure described above is a separate property.



### Video–Kinematic Delay

No video–kinematic delay measurements were recorded for the **UTennessee: clinical da Vinci Xi** family. The scope of this manual check is shown below.

| Dataset | Episodes measured | Median delay (ms) | Range (ms) | Review scope |
| :--- | ---: | ---: | ---: | :--- |
| [surgical_video_datasets](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment/blob/main/Surgical/utenn/surgical_video_datasets/README.md) | 0 | N/A | N/A | Excluded: no usable kinematics |
| [surgical_video_datasets_round2_with_part_seg](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment/blob/main/Surgical/utenn/surgical_video_datasets_round2_with_part_seg/README.md) | 0 | N/A | N/A | Excluded: no usable kinematics |
| [surgical_video_datasets_with_tip_pose](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment/blob/main/Surgical/utenn/surgical_video_datasets_with_tip_pose/README.md) | 0 | N/A | N/A | Excluded: no usable kinematics |


---

## 👥 Attribution & Contact

| | |
| :--- | :--- |
| **Dataset Lead** | Nan Xiao, Tom Olesch, Farong Wang, Fei Liu, DeLong Jonathan C. |
| **Institution** | University of Tennessee, Knoxville (AURAS Lab); UT Medical Center |
| **Contact Email** | nxiao4@vols.utk.edu |
| **Citation (BibTeX)** | <pre><code>@misc{surgical_actions_v2_with_tip2d_2025,<br>  author = {Nan Xiao, Tom Olesch, Farong Wang, Fei Liu, DeLong Jonathan C.},<br>  title = {surgical\_actions\_v2\_with\_tip2d: Clip-level Surgical Action Dataset with 2D Tool Tip Pose},<br>  year = {2025},<br>  publisher = {Open-H-Embodiment}<br>}</code></pre> |




