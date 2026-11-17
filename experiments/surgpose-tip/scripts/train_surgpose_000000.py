"""Prepare SurgPose 000000 and fine-tune a five-slot EndoVis checkpoint."""
import argparse
import json
import subprocess
import zipfile
from pathlib import Path

import yaml

WIDTH, HEIGHT = 1400, 986
TOOL_POINTS = ((4, 5), (11, 12))


def label_frame(points, boxes):
    boxes = list(boxes.values())
    if len(boxes) != 2:
        raise ValueError(f"Expected two boxes, got {boxes}")
    # Match by all seven SurgPose landmarks, allowing small mask/bbox offsets.
    def distance(box, ids):
        x, y, w, h = box
        return sum(
            max(x - px, 0, px - x - w) ** 2 + max(y - py, 0, py - y - h) ** 2
            for px, py in (points[i] for i in ids if i in points and points[i] is not None)
        )

    ids_a, ids_b = range(1, 8), range(8, 15)
    direct = distance(boxes[0], ids_a) + distance(boxes[1], ids_b)
    reverse = distance(boxes[1], ids_a) + distance(boxes[0], ids_b)
    if direct == reverse:
        raise ValueError(f"Ambiguous tool-to-box match: {boxes}")
    if reverse < direct:
        boxes.reverse()

    rows = []
    for (x, y, w, h), tips in zip(boxes, TOOL_POINTS):
        x1, y1 = max(0, x), max(0, y)
        x2, y2 = min(WIDTH, x + w), min(HEIGHT, y + h)
        if x2 <= x1 or y2 <= y1:
            raise ValueError(f"Invalid box: {(x, y, w, h)}")
        values = [
            0, (x1 + x2) / (2 * WIDTH), (y1 + y2) / (2 * HEIGHT),
            (x2 - x1) / WIDTH, (y2 - y1) / HEIGHT,
        ]
        for tip in tips:
            point = points.get(tip)
            if point is not None and 0 <= point[0] < WIDTH and 0 <= point[1] < HEIGHT:
                values.extend((point[0] / WIDTH, point[1] / HEIGHT, 1))
            else:
                values.extend((0, 0, 0))
        # Head, Shaft and EndPoint have no verified equivalent for this pilot.
        values.extend([0, 0, 0] * 3)
        if not all(0 <= value <= 1 for value in values):
            raise ValueError(f"Out-of-range YOLO label: {values}")
        rows.append(" ".join(f"{value:.8f}" for value in values))
    return "\n".join(rows) + "\n"


def prepare(archive, root):
    for split in ("train", "val"):
        for kind in ("images", "labels"):
            (root / kind / split).mkdir(parents=True, exist_ok=True)
    counts = {"train": 0, "val": 0}
    with zipfile.ZipFile(archive) as source:
        for side in ("left", "right"):
            points = yaml.safe_load(source.read(f"000000/keypoints_{side}.yaml"))
            boxes = json.loads(source.read(f"000000/bbox_{side}.json"))
            video = source.extract(f"000000/regular/{side}_video.mp4", root)
            staging = root / side
            staging.mkdir(exist_ok=True)
            subprocess.run([
                "ffmpeg", "-v", "error", "-y", "-i", str(video),
                "-q:v", "2", "-start_number", "0", str(staging / "%06d.jpg"),
            ], check=True)
            frames = sorted(staging.glob("*.jpg"))
            if len(frames) != 1001 or set(points) != set(range(1001)) or set(boxes) != {str(i) for i in points}:
                raise ValueError(f"{side}: expected 1001 aligned frames and label records")
            for frame in frames:
                index = int(frame.stem)
                # Keep a temporal gap on both sides of the held-out middle block.
                if 580 <= index < 620 or 820 <= index < 860 or index == 0:
                    continue
                split = "val" if 620 <= index < 820 else "train"
                name = f"{side}_{index:06d}"
                try:
                    labels = label_frame(points[index], boxes[str(index)])
                except ValueError as error:
                    raise ValueError(f"{side} frame {index}: {error}") from error
                frame.replace(root / "images" / split / f"{name}.jpg")
                (root / "labels" / split / f"{name}.txt").write_text(labels, encoding="ascii")
                counts[split] += 1
    config = {
        "path": root.as_posix(), "train": "images/train", "val": "images/val",
        "names": {0: "instrument"}, "kpt_shape": [5, 3],
        "kpt_names": {0: ["LeftClasperPoint", "RightClasperPoint", "HeadPoint", "ShaftPoint", "EndPoint"]},
    }
    (root / "data.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")
    print(counts, flush=True)


def train(weights, root, device, epochs, run_name="surgpose_000000_tip", resume=False):
    import torch
    from ultralytics import YOLO
    from ultralytics.utils.loss import PoseLoss26

    if device != "cpu" and not torch.cuda.is_available():
        raise RuntimeError("CUDA PyTorch is required for the selected device.")
    model = YOLO(str(weights))
    if resume and (model.ckpt.get("epoch", -1) < 0 or model.ckpt.get("optimizer") is None):
        raise ValueError("Checkpoint lacks resumable optimizer or epoch state.")
    if list(model.model.yaml["kpt_shape"]) != [5, 3]:
        raise ValueError("Expected the five-slot EndoVis checkpoint.")

    class TipConfidence(torch.nn.Module):
        def __init__(self, original):
            super().__init__()
            self.original = original
            self.calls = 0

        def forward(self, logits, targets):
            if logits.shape[-1] != 5 or targets.shape != logits.shape:
                raise ValueError("Unexpected pose-confidence tensor shape.")
            if targets[..., 2:].any():
                raise ValueError("This loss override expects tip-only labels.")
            self.calls += 1
            # Missing SurgPose landmarks are unknown, including occasional missing tips.
            known = targets[..., :2].bool()
            return self.original(logits[..., :2][known], targets[..., :2][known]) if known.any() else logits.sum() * 0

    original_init = PoseLoss26.__init__
    losses = []

    def init_tip_loss(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.bce_pose = TipConfidence(self.bce_pose)
        losses.append(self.bce_pose)

    def verify_loss_used(_trainer):
        if not any(loss.calls for loss in losses):
            raise RuntimeError("Training did not use the modified pose loss.")

    PoseLoss26.__init__ = init_tip_loss
    model.add_callback("on_train_epoch_end", verify_loss_used)
    try:
        if resume:
            model.train(resume=True)
        else:
            model.train(
                data=str(root / "data.yaml"), epochs=epochs, imgsz=640, batch=4,
                device=device, workers=0, optimizer="AdamW", lr0=0.0003,
                amp=False, fliplr=0, flipud=0, mosaic=0, mixup=0, copy_paste=0,
                cache=False, project=str(root / "runs"), name=run_name,
            )
    finally:
        PoseLoss26.__init__ = original_init
    print(Path(model.trainer.save_dir) / "weights" / "best.pt", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "train"))
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--weights", type=Path)
    parser.add_argument("--device", default="0")
    parser.add_argument("--epochs", type=int, default=10)
    args = parser.parse_args()
    if args.mode == "prepare":
        if args.archive is None:
            parser.error("prepare requires --archive")
        prepare(args.archive, args.root.resolve())
    else:
        if args.weights is None:
            parser.error("train requires --weights")
        train(args.weights.resolve(), args.root.resolve(), args.device, args.epochs)

