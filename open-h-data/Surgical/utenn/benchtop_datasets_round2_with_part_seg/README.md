<!--
Open-H Embodiment Dataset README Template (v1.0)
Please fill out this template and include it in the ./metadata directory of your LeRobot dataset.
This file helps others understand the context and details of your contribution.
-->

# Benchtop Surgical Tool Manipulation Dataset (Open-H) - README

---

## 📋 At a Glance

Bench-top surgical-tool video episodes with aligned **RGB**, **per-frame depth** (NPZ + visualization video), **part segmentation label maps**, **2D tool poses**, and optional **dynamic 3D Gaussian** scene/tool representations.

---

## 📖 Dataset Overview

This dataset packages labeled benchtop clips into a **LeRobot dataset v2.1-style** directory layout that is **submit-ready for Open-H**. Each episode corresponds to a single recorded clip under an action label (task). For every timestep, we provide consistent indexing and references to raw depth/segmentation assets, plus per-tool 2D pose states.

| | |
| :--- | :--- |
| **Total Trajectories** | `2` |
| **Total Hours** | `Around 25 seconds` |
| **Data Type** | `[ ] Clinical` `[ ] Ex-Vivo` `[x] Table-Top Phantom` `[ ] Digital Simulation` `[ ] Physical Simulation` `[ ] Other (If checked, update "Other")` |
| **License** | CC BY 4.0 |
| **Version** | `1.0` |

---

## 🧭 Dataset Structure & Navigation

This dataset follows the LeRobot v2.1-style layout (manual writer) with **videos**, **per-episode parquet tables**, and **raw assets**.

```
<dataset_root>/
  data/
    chunk-000/
      episode_000000.parquet
      episode_000001.parquet
      ...
  videos/
    chunk-000/
      observation.images.rgb/        episode_000000.mp4 ...
      observation.images.depth_vis/  episode_000000.mp4 ...
      observation.images.part_id/    episode_000000.mp4 ...
  meta/
    info.json
    tasks.jsonl
    episodes.jsonl
    episodes_stats.jsonl
  metadata/
    README.md   <-- this file
  raw/
    depth/episode_000000/frame_000000.npz ...
    seg/episode_000000/00000.png ...
    toolposes/episode_000000/tool_poses.json
    toolposes/episode_000000/tool_name_to_slot.json
    seg_schema/episode_000000/label_schema.json
    seg_schema/episode_000000/label_id_maps.json
    gaussians/episode_000000/dynamic_gaussians_frames.jsonl.gz   (optional)
    gaussians/episode_000000/dynamic_gaussians_meta.json         (optional)
    gaussians/episode_000000/photometric_cam_T_wc.json           (optional)
```

### Where to look first
- **meta/info.json**: overall dataset metadata (fps, splits, modalities, counts)
- **meta/tasks.jsonl**: list of action labels / tasks
- **meta/episodes.jsonl**: episode index → clip id, paths, tool list, gaussians presence
- **data/chunk-000/episode_XXXXXX.parquet**: per-timestep table (timestamps, tool poses, raw pointers)
- **videos/**: fast visualization for RGB / depth_vis / part_id
- **raw/**: submission-grade assets (relative depth NPZ, label-map PNGs, toolposes JSON, optional gaussians)

---

## 🎯 Tasks & Domain

### Domain
- [x] **Surgical Robotics**
- [ ] **Ultrasound Robotics**
- [ ] **Other Healthcare Robotics** (Please specify: `N/A`)

### Demonstrated Skills
Action labels are stored in:
- `meta/tasks.jsonl` (task definitions)
- `action.label` column in each parquet

Examples (replace with your actual labels):
- Tool manipulation (grasp / pick-and-place)
- Retraction / interaction
- Cutting / dissection-like motions

---

## 🔬 Data Collection Details

### Collection Method
- [x] **Human Teleoperation** *(typical for benchtop surgical tool demos; update if different)*
- [ ] **Programmatic/State-Machine**
- [ ] **AI Policy / Autonomous**
- [ ] **Other** (Please specify: `TBD`)

### Operator Details

| | Description |
| :--- | :--- |
| **Operator Count** | `N/A` |
| **Operator Skill Level** | `[ ] Expert (e.g., Surgeon, Sonographer)` <br> `[x] Intermediate (e.g., Trained Researcher)` <br> `[ ] Novice (e.g., ML Researcher with minimal experience)` <br> `[ ] N/A` |
| **Collection Period** | `N/A` |

### Recovery Demonstrations
- [ ] **Yes**
- [x] **No**

If yes, describe: `TBD`

---

## 💡 Diversity Dimensions

- [ ] **Camera Position / Angle**
- [ ] **Lighting Conditions**
- [ ] **Target Object**
- [ ] **Spatial Layout**
- [ ] **Robot Embodiment**
- [ ] **Task Execution**
- [ ] **Background / Scene**
- [ ] **Other** (Please specify: `TBD`)

Elaboration: `TBD`

---

## 🛠️ Equipment & Setup


### Sensors & Cameras

| Type | Model/Details |
| :--- | :--- |
| **Primary Camera** | `Monocular RGB video (resolution in meta/episodes_stats.jsonl)` |
| **Depth** | `Per-frame depth stored as NPZ (raw/depth) + depth_vis mp4 (videos/...)` |
| **Segmentation** | `Part/label-map PNGs (raw/seg) + part_id mp4 (videos/...)` |
| **Other** | `Dynamic 3D Gaussians (optional) in raw/gaussians/` |

---

## 🎯 Action & State Space Representation

This dataset is primarily **vision + tool-state** oriented. Robot kinematics may not be included.

### Action Space Representation

**Primary Action Representation:**
- [ ] **Absolute Cartesian**
- [ ] **Relative Cartesian**
- [ ] **Joint Space**
- [x] **Other**: *Action is a categorical label per episode (`action.label`)*

**Action Dimensions:**
```
action.label: string
- Categorical action label (same for all timesteps in an episode)
```

### State Space Representation

**State Information Included:**
- [ ] **Joint Positions**
- [ ] **Joint Velocities**
- [ ] **End-Effector Pose**
- [ ] **Force/Torque Readings**
- [ ] **Gripper State**
- [x] **Other**: *2D tool pose state (per tool)*

**State Dimensions:**
```
observation.state.tool_pose_2d: [num_tools, 3]
- tx_px: tool center / tip x position in pixels (see toolposes JSON definition)
- ty_px: tool center / tip y position in pixels
- theta_rad: in-plane rotation (radians)
```

Additional related fields in parquet:
- `observation.meta.tool_name`: list of tool names (ordering reference)
- `observation.meta.tool_visible`: per-tool boolean mask
- `observation.meta.depth_npz_relpath`: pointer to raw depth NPZ per timestep
- `observation.meta.seg_png_relpath`: pointer to raw part label-map PNG per timestep

### Dynamic 3D Gaussians (Optional)

If present, per-episode files live under:
- `raw/gaussians/episode_XXXXXX/dynamic_gaussians_frames.jsonl.gz`
- `raw/gaussians/episode_XXXXXX/dynamic_gaussians_meta.json`
- `raw/gaussians/episode_XXXXXX/photometric_cam_T_wc.json`

These encode per-frame 3D Gaussian parameters (positions/covariances/colors/opacities, etc. as reconstructed by MoSca https://github.com/JiahuiLei/MoSca) as benchtop scene representations and camera transforms (intrinsics and extrinsics) for 3D reconstruction or tracking research.

---

## ⏱️ Data Synchronization Approach

All modalities are aligned **by frame index** during export.

- The RGB video provides the reference frame count.
- Depth NPZ frames, segmentation PNG frames, and tool pose frames are truncated to:
  ```
  n_steps = min(rgb_frames, depth_npz_count, seg_png_count, toolposes_num_frames)
  ```
- Timestamps are generated as:
  ```
  timestamp_s = step_index / fps_timestamps
  ```
  where `fps_timestamps` is recorded in `meta/info.json`.

This approach ensures consistent timestep alignment across all exported modalities.

---

## ✅ Quality Control

### Timestamp Integrity

An exhaustive automated audit checked all **2 episode Parquet files** in this dataset, containing **223 frames (0.00619 nominal hours at 10 FPS)**.

**Audit status:** **ERROR — canonical schema compatibility**

| Finding | Severity | Affected episodes | Frames in affected episodes | Nominal hours |
| :--- | :--- | ---: | ---: | ---: |
| Canonical LeRobot `timestamp` column is absent; time is stored as `timestamp_s` | ERROR | 2 | 223 | 0.00619 |
| **Distinct affected total** | **ERROR** | **2** | **223** | **0.00619** |

This is a field-name compatibility finding, not missing or corrupted timing information. The existing `timestamp_s` column was also checked exhaustively: it contains finite numeric double-precision values that are relative, unique, strictly increasing, with cadence consistent with 0.1 s at the declared 10 FPS. Consumers that require the canonical LeRobot `timestamp` field must explicitly map or rename `timestamp_s`.

This audit evaluates timestamp schema, representation, and cadence. It does not directly measure physical video–kinematic synchronization; the frame-index alignment procedure described above is a separate property.



### Video–Kinematic Delay

No video–kinematic delay measurements were recorded for the **UTennessee: benchtop dVRK** family. The scope of this manual check is shown below.

| Dataset | Episodes measured | Median delay (ms) | Range (ms) | Review scope |
| :--- | ---: | ---: | ---: | :--- |
| [benchtop_datasets_round2_with_part_seg](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment/blob/main/Surgical/utenn/benchtop_datasets_round2_with_part_seg/README.md) | 0 | N/A | N/A | Excluded: no usable kinematics |


---

## 👥 Attribution & Contact

| | |
| :--- | :--- |
| **Dataset Lead** | Nan Xiao, Tom Olesch, Farong Wang, Fei Liu, DeLong Jonathan C. |
| **Institution** | University of Tennessee, Knoxville (AURAS Lab) |
| **Contact Email** | nxiao4@vols.utk.edu |
| **Citation (BibTeX)** | <pre><code>@misc{benchtop_openh_2026,<br>  author = {Xiao, Nan and collaborators},<br>  title = {Benchtop Surgical Tool Manipulation Dataset (Open-H)},<br>  year = {2026},<br>  publisher = {Open-H-Embodiment},<br>  note = {Dataset packaging in LeRobot v2.1-style layout}<br>}</code></pre> |
