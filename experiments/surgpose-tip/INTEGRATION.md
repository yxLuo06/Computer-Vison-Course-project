# SurgPose 实验如何并入课程仓库

SurgPose 放在 `experiments/surgpose-tip/`，与现有的 `experiments/endovis-pose/` 并列。仓库首页通过相对链接进入新实验。新实验沿用了现有的 `scripts/`、`results/` 和 `weights/` 布局，并直接使用 EndoVis 实验的 checkpoint 作为第一阶段的训练起点。

| 位置 | 内容 |
| --- | --- |
| [实验 README](README.md) | 数据划分、点位映射、实验结果和复现命令 |
| [scripts/](scripts/) | `000000` 转换和微调、`000001`–`000010` 续训、`000011` 双目叠图 |
| [results/](results/) | 两阶段训练曲线的 CSV 和转换张数统计 |
| [weights/best.pt](weights/best.pt) | 第二阶段的最终最佳 checkpoint，也是第 11 组演示所用权重 |
| `local/` | 生成的训练数据、训练过程产物和本地演示视频，由实验目录的 `.gitignore` 忽略 |

原始 SurgPose ZIP、原视频、标注和解码帧保留在本地。当前的双目演示也留在本地，因为其中含数据集原画面。其他测试中的临时导出文件和中间权重留在工作区。复现者把数据目录传给脚本即可生成效果视频。

模型沿用 EndoVis 的五个输出槽位。SurgPose 实验训练与展示每把工具的两枚夹爪尖端。课程主线使用两个尖端的中点做跟踪和速度估计，两处结果分别记录在各自的实验页。第 11 组是一整条留出序列的视觉检查，训练 CSV 的 mAP 来自训练序列中的留出时段。

合并时，将 `experiments/surgpose-tip/` 放入仓库，再把下列条目加到根 `README.md` 的 EndoVis 结果下方。审核 diff 后可将根 README 和新实验目录一起提交。

```markdown
- [SurgPose stereo tip localization](experiments/surgpose-tip/README.md) adapts the EndoVis checkpoint to SurgPose and includes a reproducible stereo overlay for held-out sequence 000011.
```
