# SurgPose stereo instrument-tip localization

This experiment adapts the [EndoVis YOLO26n-Pose checkpoint](../endovis-pose/weights/best.pt) to SurgPose. It fine-tunes on sequence `000000` for 10 epochs, then initializes a second 10-epoch run from the best pilot checkpoint using sequences `000001`–`000010`. The final [SurgPose checkpoint](weights/best.pt) is the one used to render the held-out sequence `000011`.

## Labels and splits

The model retains the five-output layout of the EndoVis checkpoint. Each instrument box is paired with its SurgPose landmarks. The two supervised slots are the clasper tips, IDs 4 and 5 for PSM1 and IDs 11 and 12 for PSM3. Missing or out-of-frame tips and the head, shaft and endpoint slots use `0 0 0`. The training script masks unknown points in the confidence loss and retains the existing coordinate mask. The SurgPose experiment evaluates individual jaw tips. The [EndoVis experiment](../endovis-pose/README.md) uses their midpoint for instrument tracking and velocity.

Left and right views of the same time step share a split. Frame zero and the gaps around the validation segment are excluded. The pilot uses frames 620–819 inclusive for validation. The second run uses approximately 62%–82% of each sequence for within-sequence validation, with 14,400 training images and 4,000 validation images. See the [conversion counts](results/000001-000010-conversion.json).

| Run | Epoch | Box mAP50–95 | Pose mAP50–95 | Record |
| --- | ---: | ---: | ---: | --- |
| Pilot `000000` | 10 | 92.69% | 99.23% | [Training CSV](results/000000-training.csv) |
| Fine-tune `000001`–`000010` | 10 | 91.27% | 99.22% | [Training CSV](results/000001-000010-training.csv) |

The CSV values above come from each run's final epoch on within-sequence validation frames. Sequence `000011` was used for qualitative evaluation. The stereo overlay shows the left camera on the left and the right camera on the right, with green circles for available ground truth and orange crosses for estimates. The detector and displayed tip scores both use a cutoff of 0.25. The stereo video contains 1,001 synchronized frames at 30 fps.

## Reproduce locally

The recorded training environment used Python 3.13.13, Ultralytics 8.4.215 and PyTorch 2.11.0 with CUDA 12.8. Install the [dependencies](requirements.txt), use a PyTorch build suitable for your device, and put FFmpeg on PATH. Obtain the original SurgPose archives separately. The scripts read the original per-camera videos and annotations directly from the archives.

From the repository root, in PowerShell:

```powershell
$exp = "experiments/surgpose-tip"
$archives = "E:/cv_workshop"
$work = "$exp/local"
python "$exp/scripts/render_stereo.py" --archive "$archives/000011.zip" --weights "$exp/weights/best.pt" --output "$work/000011-stereo.mp4"
```

To rerun training, use a fresh local work directory so each run has its expected name:

```powershell
python "$exp/scripts/train_surgpose_000000.py" prepare --archive "$archives/000000.zip" --root "$work/pilot"
python "$exp/scripts/train_surgpose_000000.py" train --weights "experiments/endovis-pose/weights/best.pt" --root "$work/pilot" --device 0
python "$exp/scripts/train_surgpose_range.py" --archives "$archives" --pilot-root "$work/pilot" --root "$work/range" --device 0
```

The second command writes the pilot checkpoint at `local/pilot/runs/surgpose_000000_tip/weights/best.pt`. The third command writes the second-stage checkpoint at `local/range/runs/surgpose_000001_000010_tip/weights/best.pt`. The archived run resumed from epoch 2 with optimizer state. The commands above start both training stages from scratch and can yield different results.
