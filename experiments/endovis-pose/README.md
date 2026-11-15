# EndoVis surgical instrument tip localization and tracking

We fine-tuned YOLO26n-Pose on EndoVis 2015 to predict instrument boxes and five landmarks (left clasper, right clasper, head, shaft, and endpoint). The tip is the midpoint of the two claspers. A separate tracker associates instrument detections one-to-one, using tip and head positions. Image-plane velocity is the coordinate difference divided by elapsed time, in pixels per second. The tracker does not report velocity for a new detection, an unresolved match, or the first frame after a gap.

### Training and data split

Dataset1–3 supplied 699 training images; Dataset4 supplied 238 validation images for checkpoint selection. We excluded three frames with conflicting labels and generated proxy boxes from the extent of the landmarks with padding. We fine-tuned pretrained YOLO26n-Pose for 30 epochs with input size 640 and batch size 4 on Apple MPS. Dataset4 here refers to the sequence held out from the training archive, not the official test sequence with the same name.

### Results

| Split or condition | Evaluated frames | Tip RMSE (px) | Precision at 20 px | Recall at 20 px |
|---|---:|---:|---:|---:|
| [Dataset4 validation](results/dataset4.json) | 238 | 11.54 | 94.24% | 96.22% |
| [Dataset4 with a 24 px square over the annotated tip](results/dataset4-occluded.json) | 238 | 16.72 | 80.99% | 82.35% |
| [Official EndoVis test: all six sequences](results/endovis-official.json) | 895 | 13.68 | 98.47% | 61.76% |
| Official EndoVis test: related sequences 1–4 | 306 | 7.08 | 99.23% | 99.74% |
| Official EndoVis test: additional sequences 5–6 | 589 | 16.63 | 97.98% | 49.32% |
| [JIGSAWS: subset with complete two-tool labels](results/jigsaws-ground-truth.json) | 276 | 41.23 | 62.07% | 3.26% |

At inference we used box confidence ≥0.25 and both clasper scores ≥0.50 for midpoint evaluation. A 20 px match is one-to-one; unmatched candidates count as false positives and unmatched labeled tips count as false negatives. Dataset4 RMSE uses the highest-scoring eligible prediction per frame. Official EndoVis and JIGSAWS RMSE use minimum-distance one-to-one pairs without a distance cutoff, excluding unmatched labels. JIGSAWS RMSE uses only 29 pairs; the low recall is the more informative result. The [training log](results/training-metrics.csv) reports separate box and pose metrics.

On Dataset4 we also inspected [position and speed around a high-error interval](figures/dataset4-motion.png). Visually, these errors coincide with reflections or low contrast in some frames; causality was not tested. On a training sequence, a [controlled two-tool detection gap](figures/two-tool-rejoin.png) showed ID recovery after five suppressed detections. A separate [image-space occlusion experiment](results/spatial-video-occlusion.json) reran the model with masks at the head, tip, and shaft. The one-second tip mask caused a persistent position offset while ID remained unchanged. The apparent speed spikes are not independently verified motion. Natural occlusion recovery in held-out video and velocity accuracy remain open.

### Reproduce the experiments

The recorded runtime was Python 3.14.6. Install the dependencies in [requirements.txt](requirements.txt) in a local environment. MATLAB with Computer Vision Toolbox was used only to export JIGSAWS ground truth.

Data and checkpoints are obtained separately. Use the [OpenCAS EndoVis archive](https://archive.iar.kit.edu/opencas/index.html%3Fq%3Dnode%252F30.html), [Du et al.'s labels](https://github.com/surgical-vision/EndoVisPoseAnnotation), [Ultralytics Pose weights](https://docs.ultralytics.com/models/yolo26/), and the [JIGSAWS annotation release](https://shadowfax11.github.io/mfc_tracking/). This experiment directory contains code, numeric results and plots, without bundling the external videos, annotation exports, or learned weights.

From the experiment directory, set the script path before changing into a separate training workspace:

```bash
EXP="$(pwd)"
WORK=/path/to/your/endovis-workspace
cd "$WORK"
python "$EXP/scripts/inspect_endovis.py"
python "$EXP/scripts/convert_endovis_pose.py"
python "$EXP/scripts/train_pose_full.py"
```

Before running, put `yolo26n-pose.pt` and the label repository `EndoVisPoseAnnotation/` at the workspace root. Extract the training archive to yield `datasets/endovis2015/raw/Tracking_Robotic_Training/Training/Dataset1/Video.avi` (likewise for sequences 2–4). The conversion script writes `datasets/endovis2015/yolo_pose/data.yaml`. The training script prints the output directory; use its `weights/best.pt` or the existing course checkpoint for evaluation. Retraining can yield different metrics.

```bash
WEIGHTS=/path/to/best.pt
python "$EXP/scripts/evaluate_endovis_precision.py" "$WEIGHTS" \
  "$WORK/datasets/endovis2015/yolo_pose" ./dataset4-eval
python "$EXP/scripts/evaluate_endovis_occlusion.py" "$WEIGHTS" \
  "$WORK/datasets/endovis2015/yolo_pose" ./dataset4-occluded --occlusion-size 24
python "$EXP/scripts/evaluate_endovis_official.py" "$WEIGHTS" \
  /path/to/official-test ./official-eval
```

The official test directory must contain `raw/Tracking/Dataset1–6/Video.avi` and `labels/test1_labels.json` through `test6_labels.json`. JIGSAWS inference takes the original `annotations_val` directory. Its scoring script compares exported clasper midpoints on frames with two complete jaw labels. See the [export script](scripts/export_jigsaws_midpoints.m), [inference script](scripts/test_jigsaws_external.py), and [scoring script](scripts/score_jigsaws_midpoints.py). Run any script with `--help` to see its CLI arguments when supported.

The point annotations originate from [Du et al. (2018)](https://doi.org/10.1109/TMI.2017.2787672). The JIGSAWS jaw annotations originate from [Ghanekar et al.](https://arxiv.org/abs/2501.18361).
