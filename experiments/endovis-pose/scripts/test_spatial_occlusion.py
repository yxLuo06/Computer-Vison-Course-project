"""Apply masks to Dataset1 input pixels and rerun the same tracker."""
import argparse
import csv
import json
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

from check_two_tool_tracking import assignment, evaluate, labels, track

# Inclusive source frame ranges at 25 FPS. Widths match across conditions.
WINDOWS = [(80, 89, "Head", 2), (105, 129, "Tip", None), (160, 169, "Shaft", 3)]
SIZE = 64


def apply_mask(image, rect):
    x1, y1, x2, y2 = rect
    image[y1:y2, x1:x2] = 114


def detect(model, image):
    r = model.predict(image, imgsz=640, conf=.25, device="cpu", verbose=False)[0]
    if r.keypoints is None:
        return [], []
    candidates, landmarks = [], []
    for score, pts, box in zip(r.boxes.conf.tolist(), r.keypoints.data.cpu().numpy(), r.boxes.xyxy.cpu().tolist()):
        if np.isfinite(pts[:3]).all() and (pts[:3, 2] >= .5).all():
            candidates.append((score, pts[:2,:2].mean(axis=0), pts[2,:2]))
            landmarks.append((pts, box))
    return candidates, landmarks


def write_csv(path, rows):
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("weights", "video", "labels", "output"):
        p.add_argument(name, type=Path)
    args = p.parse_args()
    model = YOLO(str(args.weights))
    cap = cv2.VideoCapture(str(args.video))
    if not cap.isOpened() or cap.get(cv2.CAP_PROP_FPS) != 25:
        raise ValueError("Expected a readable 25 FPS Dataset1 video")
    imgs, base, landmarks = {}, {}, {}
    try:
        for f in range(1, 221):
            ok, im = cap.read()
            if not ok:
                raise OSError(f"Cannot decode frame {f}")
            if f >= 60:
                imgs[f] = im
                base[f], landmarks[f] = detect(model, im)
    finally:
        cap.release()
    clean, mapping = track(base, 25)
    masks, altered = [], dict(base)
    altered_landmarks = dict(landmarks)
    for lo, hi, name, k in WINDOWS:
        for f in range(lo, hi+1):
            j = mapping[f][1]
            pts = landmarks[f][j][0]
            center = base[f][j][1] if k is None else pts[k,:2]
            if k is not None and (not np.isfinite(pts[k]).all() or pts[k,2] < .5):
                raise ValueError(f"Missing clean {name} estimate at frame {f}")
            x, y = map(round, center)
            h, w = imgs[f].shape[:2]
            rect = (max(0,x-SIZE//2), max(0,y-SIZE//2), min(w,x+SIZE//2), min(h,y+SIZE//2))
            masked = imgs[f].copy()
            apply_mask(masked, rect)
            altered[f], altered_landmarks[f] = detect(model, masked)
            masks.append(dict(frame=f,location=name,x1=rect[0],y1=rect[1],x2=rect[2],y2=rect[3]))
    trial, mapped = track(altered, 25)
    actual = {(r["frame"], r["id"]):r for r in trial}
    original = {(r["frame"], r["id"]):r for r in clean}
    truth = labels(args.labels)
    base_audit, base_stats = evaluate(clean, truth)
    altered_audit, altered_stats = evaluate(trial, truth)

    def outcome(f):
        # Compare contemporaneous tips to clean track 1, not ground truth.
        ids = list(mapped[f])
        cost = np.array([[np.linalg.norm(base[f][mapping[f][k]][1]-altered[f][mapped[f][j]][1])
                          for j in ids] for k in (1,2)])
        match, _ = assignment(cost, 20, 1e-6)
        return next(((ids[j],float(cost[i,j])) for i,j in match if i==0), (None,None))

    windows = []
    for lo,hi,name,_ in WINDOWS:
        matches = [outcome(f) for f in range(lo,hi+1)]
        near = [d for k,d in matches if k is not None]
        after = [{"frame":f,"id_near_clean_id1":outcome(f)[0],
                  "id1_status":actual.get((f,1),{}).get("status"),
                  "id1_speed_present":actual.get((f,1),{}).get("speed_px_s") is not None}
                 for f in range(hi+1,hi+4)]
        windows.append(dict(location=name,frames=[lo,hi],duration_s=(hi-lo+1)/25,
                            frames_near_clean_tip=len(near),frames_same_id_near_clean_tip=sum(k==1 for k,d in matches),
                            id1_no_output=sum(actual.get((f,1),{}).get("x_px") is None for f in range(lo,hi+1)),
                            immediately_after=after))
    args.output.mkdir(parents=True, exist_ok=False)
    for name, rows in (("baseline_tracks",clean),("controlled_gap_tracks",trial),("masks",masks),
                       ("baseline_identity_audit",base_audit),("occluded_identity_audit",altered_audit)):
        write_csv(args.output/f"{name}.csv", rows)
    for name, matches, predictions in (("baseline", mapping, landmarks),
                                       ("controlled_gap", mapped, altered_landmarks)):
        overlays = {}
        for frame, ids in matches.items():
            overlays[frame] = {}
            for track_id, index in ids.items():
                pts, box = predictions[frame][index]
                overlays[frame][track_id] = {
                    "box": box,
                    "points": [q.tolist() if np.isfinite(q).all() else None for q in pts],
                }
        (args.output/f"{name}_overlays.json").write_text(json.dumps(overlays, allow_nan=False)+"\n")
    summary = dict(fps=25, mask_side_px=SIZE, windows=windows, clean=base_stats, occluded=altered_stats)
    (args.output/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))

if __name__ == "__main__":
    main()
