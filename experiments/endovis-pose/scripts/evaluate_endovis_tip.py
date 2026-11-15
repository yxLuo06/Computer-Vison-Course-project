"""Evaluate the clasper midpoint on the annotated, single-instrument Dataset4."""
import argparse
import csv
import json
import math
from pathlib import Path

import cv2
from ultralytics import YOLO


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("weights", type=Path)
    parser.add_argument("dataset", type=Path, help="Root containing images/val and labels/val")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    paths = sorted((args.dataset / "images/val").glob("*.png"))
    if not paths:
        parser.error("No validation PNGs found")
    model = YOLO(str(args.weights))
    if list(model.model.yaml.get("kpt_shape", [])) != [5, 3]:
        parser.error("Expected the five-point checkpoint with clasper indices 0 and 1")
    rows = []
    for path in paths:
        label = args.dataset / "labels/val" / f"{path.stem}.txt"
        fields = list(map(float, label.read_text().split()))
        if len(fields) != 20 or fields[0] != 0 or min(fields[7], fields[10]) <= 0:
            raise ValueError(f"Expected one instrument with both claspers annotated: {label}")
        img = cv2.imread(str(path))
        if img is None:
            raise OSError(f"Cannot read {path}")
        h, w = img.shape[:2]
        truth = ((fields[5]+fields[8])*w/2, (fields[6]+fields[9])*h/2)
        result = model.predict(img, imgsz=640, conf=.25, device="cpu", verbose=False)[0]
        candidates = []
        if result.keypoints is not None:
            for score, coords in zip(result.boxes.conf.tolist(), result.keypoints.data.tolist()):
                left, right = coords[:2]
                if min(left[2], right[2]) >= .5 and all(map(math.isfinite, left+right)):
                    tip = ((left[0]+right[0])/2, (left[1]+right[1])/2)
                    candidates.append((score, tip))
        row = dict(frame=path.name, true_x=truth[0], true_y=truth[1], detections=len(result.boxes),
                   valid_candidates=len(candidates), pred_x=None, pred_y=None, error_px=None)
        if candidates:
            _, tip = max(candidates, key=lambda item: item[0])
            row.update(pred_x=tip[0], pred_y=tip[1], error_px=math.dist(tip, truth))
        rows.append(row)
    errors = sorted(row["error_px"] for row in rows if row["error_px"] is not None)
    n = len(rows)
    summary = {
        "weights": str(args.weights), "validation_images": n, "box_confidence_min": .25,
        "keypoint_score_min": .5, "prediction_rule": "highest box score among candidates with both clasper scores passing",
        "valid_midpoints": len(errors), "missing_midpoints": n-len(errors),
        "frames_with_multiple_valid_candidates": sum(row["valid_candidates"] > 1 for row in rows),
        "rmse_px_on_valid_predictions": math.sqrt(sum(e*e for e in errors)/len(errors)) if errors else None,
        "mean_error_px_on_valid_predictions": sum(errors)/len(errors) if errors else None,
        **{f"pck_{t}px_all_frames": sum(e <= t for e in errors)/n for t in (10, 20)},
    }
    args.output.mkdir(parents=True, exist_ok=False)
    with (args.output / "per_frame.csv").open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
