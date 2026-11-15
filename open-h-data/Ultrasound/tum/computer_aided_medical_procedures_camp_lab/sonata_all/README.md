# SonATA - README

---

## 📋 At a Glance

*SonATA is a comprehensive robotic sonography dataset that integrates synchronized ultrasound imaging, external visual data, contact force measurements, robot motion data, and textual instructions, collected from abdomen, thyroid, and arm phantoms to support research on language-conditioned autonomous scanning, perception, and learning-based ultrasound systems.*

*SonATA, comprising three subset datasets — SonATA-Abdomen, SonATA-Thyroid, and SonATA-Arm — contains ober 2,000 demonstrations of a robot arm performing diverse ultrasound scanning tasks on three phantoms. It includes three primary task categories (placement, scanning, and navigation), along with **599 unique task instructions** across all subsets, providing a robust dataset for training autonomous robotic ultrasound systems.*

---

## 📊 Dataset Statistics

| Subset | Episodes | Frames | Tasks | Duration | Train | Val | Test |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **SonATA-Arm** | 605 | 265,451 | 195 | 147.5 min (2.46 h) | 423 | 60 | 122 |
| **SonATA-Abdomen** | 1,532 | 325,594 | 284 | 180.9 min (3.01 h) | 1,070 | 154 | 308 |
| **SonATA-Thyroid** | 260 | 42,559 | 120 | 23.6 min (0.39 h) | 182 | 24 | 54 |
| **SonATA-All** | **2,397** | **633,604** | **599** | **352.0 min (5.87 h)** | **1,677** | **238** | **482** |

- **FPS**: 30  
- **Train / Val / Test split**: 70% / 10% / 20% (per-subset stratified shuffle)

---

## 📖 File Structure
The file structure of this directory is shown below:
```text
./
├── SonATA_*/
│   └── ...
├── overview/
│   ├── SonATA_*/
│   ├── SonATA_*.csv
│   └── lerobot_config.yaml
└── README.md
```

The `SonATA_*` directories contain all demonstrated data, with each directory corresponding to a specific SonATA subset. The `overview/` directory provides the initial configurations for each demonstration in the form of images, together with the corresponding textual instructions and trajectory lengths. The features of the converted LeRobot dataset are defined in `lerobot_config.yaml`.

---

## ✅ Quality Control

### Timestamp Integrity

The exhaustive release audit checked **2,397 episode Parquet files mapped to this release path**, containing **633,604 frame rows (5.866704 nominal hours at 30 FPS)**.

**Audit status:** **NO TIMESTAMP FINDING**

Every discovered episode table had a canonical `timestamp` field whose values were readable, numeric, and finite. For sequences with at least two rows, no configured audit rule was triggered for constant or effectively collapsed ranges, duplicated or very-low-uniqueness values, decreasing transitions, epoch-like/non-relative representation or float32 absolute-time precision loss, or mean positive spacing outside the declared-frame-rate thresholds.

The mean-spacing rule flags values below 0.1× or above 5× the expected `1 / FPS` interval; it is not a frame-level jitter bound. Nominal hours are computed from row count and declared FPS, not timestamp span. This result applies only to the timestamp representation in the episode Parquets included in the audit. It does not establish video integrity, physical video–kinematic synchronization, or annotation correctness.


### Video–Kinematic Delay

Manual review recorded **3 episode measurements across 1 dataset** in the **TUM CAMP: SonATA** family, using one camera stream per episode. Positive delay means the visible event followed the kinematic event. Observed delay includes physical response and recording latency; this sample does not establish alignment for every episode.

| Dataset | Episodes measured | Median delay (ms) | Range (ms) | Review scope |
| :--- | ---: | ---: | ---: | :--- |
| [sonata_all](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment/blob/main/Ultrasound/tum/computer_aided_medical_procedures_camp_lab/sonata_all/README.md) | 3 | +66.7 | +33.3 to +66.7 | Measured sample |

<details>
<summary>Audited episodes and measurements</summary>

Episode indices and paths refer to the released dataset. Frame indices are zero-based. Delay is `(visual frame − kinematic frame) / measured video FPS × 1000`, rounded to 0.1 ms.

| Dataset | Episode | Episode table | Reviewed video | Signal | Kinematic frame | Visual frame | FPS | Delay (ms) |
| :--- | ---: | :--- | :--- | :--- | ---: | ---: | ---: | ---: |
| sonata_all | 753 | [Ultrasound/tum/computer_aided_medical_procedures_camp_lab/sonata_all/data/chunk-000/episode_000753.parquet](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment/blob/9ee1dd90cc2d9e816e3787b10644d3241d8613d1/Ultrasound/tum/computer_aided_medical_procedures_camp_lab/sonata_all/data/chunk-000/episode_000753.parquet) | [Ultrasound/tum/computer_aided_medical_procedures_camp_lab/sonata_all/videos/chunk-000/observation.images.tpv_camera/episode_000753.mp4](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment/blob/9ee1dd90cc2d9e816e3787b10644d3241d8613d1/Ultrasound/tum/computer_aided_medical_procedures_camp_lab/sonata_all/videos/chunk-000/observation.images.tpv_camera/episode_000753.mp4) | `action[0]` | 5 | 6 | 29.999997 | +33.3 |
| sonata_all | 850 | [Ultrasound/tum/computer_aided_medical_procedures_camp_lab/sonata_all/data/chunk-000/episode_000850.parquet](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment/blob/9ee1dd90cc2d9e816e3787b10644d3241d8613d1/Ultrasound/tum/computer_aided_medical_procedures_camp_lab/sonata_all/data/chunk-000/episode_000850.parquet) | [Ultrasound/tum/computer_aided_medical_procedures_camp_lab/sonata_all/videos/chunk-000/observation.images.tpv_camera/episode_000850.mp4](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment/blob/9ee1dd90cc2d9e816e3787b10644d3241d8613d1/Ultrasound/tum/computer_aided_medical_procedures_camp_lab/sonata_all/videos/chunk-000/observation.images.tpv_camera/episode_000850.mp4) | `action[0]` | 10 | 12 | 30.000001 | +66.7 |
| sonata_all | 1204 | [Ultrasound/tum/computer_aided_medical_procedures_camp_lab/sonata_all/data/chunk-001/episode_001204.parquet](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment/blob/9ee1dd90cc2d9e816e3787b10644d3241d8613d1/Ultrasound/tum/computer_aided_medical_procedures_camp_lab/sonata_all/data/chunk-001/episode_001204.parquet) | [Ultrasound/tum/computer_aided_medical_procedures_camp_lab/sonata_all/videos/chunk-001/observation.images.tpv_camera/episode_001204.mp4](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment/blob/9ee1dd90cc2d9e816e3787b10644d3241d8613d1/Ultrasound/tum/computer_aided_medical_procedures_camp_lab/sonata_all/videos/chunk-001/observation.images.tpv_camera/episode_001204.mp4) | `action[0]` | 10 | 12 | 30.000000 | +66.7 |

</details>


---

## 👥 Attribution & Contact

*Please provide attribution for the dataset creators and a point of contact.*

| | |
| :--- | :--- |
| **Dataset Lead** | `Dianye Huang` |
| **Institution** | `Technical University of Munich (TUM), Germany` |
| **Contact Email** | `dianye.huang@tum.de` |
| **Citation (BibTeX)** | <pre><code>@misc{robosono_2025,<br>  author = {Dianye Huang, Pei Liu, Zhongliang Jiang, Nassir Navab},<br>  title = {SonATA: A Robotic Sonography Dataset for Abdomen, Thyroid and Arm Examination},<br>  year = {2025},<br>  publisher = {Open-H-Embodiment},<br>  note = {}<br>}</code></pre> |
<!-- | **Citation (BibTeX)** | note = {https://hrpp.research.virginia.edu/teams/irb-sbs/researcher-guide-irb-sbs/identifiers}<br>}| -->

