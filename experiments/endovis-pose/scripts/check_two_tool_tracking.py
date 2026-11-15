"""Replay Dataset1 with/without a named track's detections removed for five frames."""
import argparse
import csv
import itertools
import json
import math
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

START, END = 60, 220
GAP_START, GAP_END = 105, 109
MAX_MISSED = 8
MODEL_CONF, POINT_CONF = .25, .5


def assignment(cost, gate, margin=0):
    """Maximum number of gated matches, then minimum total cost."""
    n, m = cost.shape
    options = []
    for cols in itertools.product(range(-1, m), repeat=n):
        selected = [c for c in cols if c >= 0]
        if len(set(selected)) != len(selected):
            continue
        pairs = {(i, c) for i, c in enumerate(cols) if c >= 0}
        values = [cost[i,c] for i,c in pairs]
        if all(v <= gate for v in values):
            options.append((-len(pairs), sum(values), pairs))
    options.sort(key=lambda x: x[:2])
    count, best, pairs = options[0]
    certain = pairs.copy()
    for k, value, alt in options[1:]:
        if k != count or value > best + margin:
            break
        certain.intersection_update(alt)
    return sorted(certain), bool(pairs - certain)


def track(detections, fps):
    tracks, rows, mapping = {}, [], {}
    next_id = 1
    for frame, candidates in detections.items():
        # Retain an identity through short gaps; this demo expects at most two tools.
        tracks = {k:v for k,v in tracks.items() if frame-v[0] <= MAX_MISSED+1}
        ids = list(tracks)
        cost = np.empty((len(ids),len(candidates)))
        for i,k in enumerate(ids):
            for j, (_,tip,head) in enumerate(candidates):
                _, previous_tip, previous_head = tracks[k]
                cost[i,j] = .4*math.dist(tip,previous_tip)+.6*math.dist(head,previous_head)
        matches, ambiguous = assignment(cost, gate=45, margin=8)
        claimed = set()
        current = {}
        for i,j in matches:
            current[ids[i]] = j
            claimed.add(j)
        if not ambiguous:
            for j in sorted(set(range(len(candidates)))-claimed, key=lambda j:-candidates[j][0]):
                if len(set(ids) | set(current)) >= 2:
                    break
                current[next_id] = j
                next_id += 1
        mapping[frame] = {}
        for k in sorted(set(ids) | set(current)):
            if k not in current:
                rows.append(dict(frame=frame,id=k,status="ambiguous" if ambiguous else "missing",
                                 x_px=None,y_px=None,vx_px_s=None,vy_px_s=None,speed_px_s=None))
                continue
            j=current[k]
            _,tip,head=candidates[j]
            last=tracks.get(k)
            vx=vy=speed=None
            state="new"
            if last is not None:
                if last[0] == frame-1:
                    state="linked"
                    vx,vy=(tip-last[1])*fps
                    speed=math.hypot(vx,vy)
                else:
                    state="rejoined"
            tracks[k]=(frame,tip,head)
            mapping[frame][k]=j
            rows.append(dict(frame=frame,id=k,status=state,x_px=float(tip[0]),y_px=float(tip[1]),
                             vx_px_s=vx,vy_px_s=vy,speed_px_s=speed))
    return rows,mapping


def labels(path):
    out={}
    for row in json.loads(path.read_text()):
        frame=int(Path(row["filename"]).name.split("_")[1])
        if not START <= frame <= END or not row["annotations"]:
            continue
        groups={}
        for a in row["annotations"]:
            groups.setdefault(a["id"],{}).setdefault(a["class"],[]).append((a["x"],a["y"]))
        if len(groups)==2 and all(len(g.get(k,[]))==1 for g in groups.values()
                                 for k in ("LeftClasperPoint","RightClasperPoint")):
            out[frame]={t:np.mean([g[k][0] for k in ("LeftClasperPoint","RightClasperPoint")],axis=0)
                        for t,g in groups.items()}
    return out


def evaluate(rows, truth):
    last, audit, switches = {}, [], 0
    for frame, tools in truth.items():
        observed=[r for r in rows if r["frame"]==frame and r["x_px"] is not None]
        cost=np.empty((len(tools),len(observed)))
        for i,tip in enumerate(tools.values()):
            for j,r in enumerate(observed):
                cost[i,j]=math.dist(tip,(r["x_px"],r["y_px"]))
        matches,_=assignment(cost,gate=20,margin=1e-6)
        chosen=dict(matches)
        for i,tool in enumerate(tools):
            j=chosen.get(i)
            k=observed[j]["id"] if j is not None else None
            changed=k is not None and tool in last and last[tool]!=k
            switches+=changed
            if k is not None:
                last[tool]=k
            audit.append(dict(frame=frame,tool=tool,track_id=k,id_switch=changed,
                              error_px=float(cost[i,j]) if j is not None else None))
    return audit,dict(annotated_instances=len(audit),matched=sum(r["track_id"] is not None for r in audit),
                      observed_id_switches=switches,velocity_samples=sum(r["speed_px_s"] is not None for r in rows))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("weights","video","labels","output"):
        p.add_argument(name,type=Path)
    args=p.parse_args()
    model=YOLO(str(args.weights))
    if list(model.model.yaml.get("kpt_shape",[]))!=[5,3]:
        raise ValueError("Expected left/right clasper and head at indices 0/1/2")
    cap=cv2.VideoCapture(str(args.video))
    fps=cap.get(cv2.CAP_PROP_FPS)
    if not cap.isOpened() or not math.isfinite(fps) or fps<=0:
        raise OSError("Cannot read video or FPS")
    detections={}
    try:
        for frame in range(1,END+1):
            ok,img=cap.read()
            if not ok:
                raise OSError(f"Cannot decode frame {frame}")
            if frame<START:
                continue
            result=model.predict(img,imgsz=640,conf=MODEL_CONF,device="cpu",verbose=False)[0]
            candidates=[]
            if result.keypoints is not None:
                for score,kpts in zip(result.boxes.conf.tolist(),result.keypoints.data.cpu().numpy()):
                    pts=kpts[:3]
                    if np.isfinite(pts).all() and (pts[:,2]>=POINT_CONF).all():
                        candidates.append((score,pts[:2,:2].mean(axis=0),pts[2,:2]))
            detections[frame]=candidates
    finally:
        cap.release()
    baseline, mapping=track(detections,fps)
    target_id=1
    for f in range(GAP_START-1,GAP_END+2):
        if target_id not in mapping[f] or len(mapping[f])!=2:
            raise RuntimeError(f"Controlled gap requires two baseline tracks at frame {f}")
    hidden={f:[d for j,d in enumerate(ds) if not (GAP_START<=f<=GAP_END and j==mapping[f][target_id])]
            for f,ds in detections.items()}
    trial,_=track(hidden,fps)
    target={r["frame"]:r for r in trial if r["id"]==target_id}
    blocked=all(target[f]["status"]=="missing" and target[f]["speed_px_s"] is None
                for f in range(GAP_START,GAP_END+1))
    rejoin=target[GAP_END+1]
    expected=detections[GAP_END+1][mapping[GAP_END+1][target_id]][1]
    restored=(rejoin["status"]=="rejoined" and rejoin["speed_px_s"] is None
              and math.dist((rejoin["x_px"],rejoin["y_px"]),expected)<1e-6)
    resumed=target[GAP_END+2]["speed_px_s"] is not None
    truth=labels(args.labels)
    args.output.mkdir(parents=True,exist_ok=False)
    summary={"video":"EndoVis Dataset1 (seen during pose training)","fps":fps,
             "frames":[START,END],"annotation_frames":len(truth),"evaluation_gate_px":20,
             "rejoin_checks":{"suppressed_frames":[GAP_START,GAP_END],"track_id":target_id,
                               "missing_speed_blank":blocked,"same_candidate_and_id_at_rejoin":restored,
                               "rejoin_frame":GAP_END+1,"rejoin_speed_blank":rejoin["speed_px_s"] is None,
                               "speed_resumes_next_frame":resumed}}
    for name,rows in (("baseline",baseline),("controlled_gap",trial)):
        audit,summary[name]=evaluate(rows,truth)
        for suffix,items in (("tracks",rows),("identity_audit",audit)):
            with (args.output/f"{name}_{suffix}.csv").open("w",newline="") as f:
                w=csv.DictWriter(f,fieldnames=list(items[0]))
                w.writeheader()
                w.writerows(items)
    (args.output/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
    if not (blocked and restored and resumed):
        raise SystemExit("Controlled gap did not pass all checks")


if __name__=="__main__":
    main()
