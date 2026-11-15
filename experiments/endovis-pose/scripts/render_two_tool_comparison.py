"""Render baseline and controlled-gap tracks side by side from existing CSVs."""
import argparse
import csv
import json
from collections import deque
from pathlib import Path

import cv2
import numpy as np


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("video", "tracks_dir", "output"):
        p.add_argument(name, type=Path)
    args = p.parse_args()
    tracks = []
    for name in ("baseline", "controlled_gap"):
        with (args.tracks_dir/f"{name}_tracks.csv").open() as f:
            tracks.append({(int(r["frame"]), int(r["id"])): r for r in csv.DictReader(f)})
    overlays = []
    for name in ("baseline", "controlled_gap"):
        f = args.tracks_dir/f"{name}_overlays.json"
        overlays.append(json.loads(f.read_text()) if f.is_file() else {})
    masks = {}
    mask_file = args.tracks_dir / "masks.csv"
    if mask_file.is_file():
        with mask_file.open() as f:
            masks = {int(r["frame"]):r for r in csv.DictReader(f)}
    frame_ids = sorted({f for f, _ in tracks[0]})
    if not frame_ids or frame_ids != sorted({f for f, _ in tracks[1]}):
        raise ValueError("Tracking files must cover the same frames")
    cap = cv2.VideoCapture(str(args.video))
    width, height = map(int, (cap.get(3), cap.get(4)))
    if not cap.isOpened() or (width, height) != (720, 576):
        raise OSError("Expected a readable 720x576 Dataset1 video")
    writer = cv2.VideoWriter(str(args.output), cv2.VideoWriter_fourcc(*"mp4v"),
                             12.5, (2*width+16, height+116))
    if not writer.isOpened():
        raise OSError("Cannot open intermediate video writer")
    colors = {1: (255,196,85), 2: (119,232,57)}
    trails = [{k:deque(maxlen=18) for k in colors} for _ in tracks]

    def text(img, msg, x, y, scale=.62, color=(240,240,240)):
        cv2.putText(img, msg, (x,y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, 1 if scale < .7 else 2, cv2.LINE_AA)

    try:
        for frame in range(1, frame_ids[-1]+1):
            ok, img = cap.read()
            if not ok:
                raise OSError(f"Cannot decode frame {frame}")
            if frame not in frame_ids:
                continue
            canvas = np.full((height+116,width*2+16,3),29,dtype=np.uint8)
            for j,(title,table) in enumerate(zip(("Original tracking","Masked input: rerun model" if masks else "Controlled detection gap"),tracks)):
                x0 = j*(width+16)
                shot = img.copy()
                if j == 1 and frame in masks:
                    r = masks[frame]
                    xa,ya,xb,yb = (int(r[k]) for k in ("x1","y1","x2","y2"))
                    shot[ya:yb,xa:xb] = 114
                    cv2.rectangle(shot,(xa,ya),(xb-1,yb-1),(50,212,255),2)
                    text(shot,r["location"]+" mask",xb+7,max(20,ya-5),.57,(50,212,255))
                elif j == 1 and not masks and 105 <= frame <= 109:
                    # Display-only mask centered on the original run's ID 1 tip.
                    ref = tracks[0][frame, 1]
                    cx, cy = (round(float(ref[c])) for c in ("x_px", "y_px"))
                    xa, xb = max(0,cx-12), min(width,cx+12)
                    ya, yb = max(0,cy-12), min(height,cy+12)
                    shot[ya:yb, xa:xb] = 114
                    cv2.rectangle(shot,(xa,ya),(xb-1,yb-1),(50,212,255),1)
                    text(shot,"Simulated gap",xb+7,max(20,ya-5),.53,(50,212,255))
                text(canvas,title,x0+16,30,.82)
                for k,color in colors.items():
                    row = table.get((frame,k),{})
                    trail = trails[j][k]
                    status = row.get("status","missing")
                    overlay = overlays[j].get(str(frame), {}).get(str(k))
                    if overlay:
                        x1,y1,x2,y2 = map(round, overlay["box"])
                        cv2.rectangle(shot,(x1,y1),(x2,y2),color,2,cv2.LINE_AA)
                        for point in overlay["points"]:
                            if point is None:
                                continue
                            px,py,score = point
                            pixel = (round(px),round(py))
                            cv2.circle(shot,pixel,5,(20,20,20),-1,cv2.LINE_AA)
                            cv2.circle(shot,pixel,4,color,-1 if score>=.5 else 1,cv2.LINE_AA)
                    if row.get("x_px"):
                        xy = tuple(round(float(row[c])) for c in ("x_px","y_px"))
                        trail.append(xy)
                        for a,b in zip(trail,list(trail)[1:]):
                            cv2.line(shot,a,b,color,2,cv2.LINE_AA)
                        cv2.circle(shot,xy,7,(15,15,15),-1,cv2.LINE_AA)
                        cv2.circle(shot,xy,5,color,1 if overlay else -1,cv2.LINE_AA)
                        text(shot,str(k),xy[0]+10,xy[1]-7,.7,color)
                    else:
                        trail.clear()
                    speed = row.get("speed_px_s")
                    state = f"{float(speed):.1f} px/s" if speed else f"{status} | speed unavailable"
                    text(canvas,f"ID {k}: {state}",x0+16,height+63+(k-1)*23,.60,color)
                canvas[44:44+height,x0:x0+width] = shot
            caption = f"Frame {frame:03d}  |  0.5x playback  |  speed from source at 25 FPS"
            if masks:
                if frame in masks:
                    name = masks[frame]["location"]
                    caption += f"   |   {name} masked" + (" for 1 s at source FPS" if name=="Tip" else "")
                elif frame in (90,130,170):
                    caption += "   |   Mask removed"
            elif 105 <= frame <= 109:
                caption += "   |   Right: ID 1 removed; gray mask is visual only"
            elif frame == 110:
                caption += "   |   ID 1 rejoined; speed blank"
            elif frame == 111:
                caption += "   |   ID 1 speed resumes"
            text(canvas,caption,16,height+108,.52)
            if any(overlays):
                text(canvas,"Box + 5 keypoints | Hollow tip marker = clasper midpoint",width+25,height+108,.52)
            writer.write(canvas)
    finally:
        cap.release()
        writer.release()


if __name__ == "__main__":
    main()
