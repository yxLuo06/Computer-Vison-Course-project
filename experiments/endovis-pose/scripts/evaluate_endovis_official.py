"""Evaluate frozen EndoVis pose weights on the official set's annotated frames."""
import argparse
import csv
import json
from itertools import product
import math
import re
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

JAWS = ("LeftClasperPoint", "RightClasperPoint")


def matches(cost, threshold=None):
    if not cost.size:
        return []
    if cost.shape[0] > 2:
        raise ValueError("This evaluation expects at most two labeled instruments")
    choices = [[-1] + [j for j, v in enumerate(row) if threshold is None or v <= threshold]
               for row in cost]
    best = (0, 0)
    pairs = []
    for cols in product(*choices):
        matched = [(i,j) for i,j in enumerate(cols) if j >= 0]
        if len({j for _,j in matched}) != len(matched):
            continue
        key = (-len(matched), sum(cost[i,j] for i,j in matched))
        if key < best:
            best, pairs = key, matched
    return pairs


def summarize(rows):
    errors = [x for r in rows for x in r["paired_errors"]]
    gt = sum(r["truth_count"] for r in rows)
    pred = sum(r["candidate_count"] for r in rows)
    tp10 = sum(r["tp_10"] for r in rows)
    tp20 = sum(r["tp_20"] for r in rows)
    return dict(frames=len(rows), truth=gt, candidates=pred, assigned_for_rmse=len(errors),
                rmse_px=math.sqrt(sum(x*x for x in errors)/len(errors)) if errors else None,
                hit_10px=tp10/gt, precision_20px=tp20/pred if pred else None,
                recall_20px=tp20/gt, tp_20px=tp20, fp_20px=pred-tp20, fn_20px=gt-tp20)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("weights","data","output"):
        p.add_argument(name,type=Path)
    a=p.parse_args()
    model=YOLO(str(a.weights))
    if list(model.model.yaml.get("kpt_shape", []))!=[5,3]:
        raise ValueError("Expected five-keypoint checkpoint")
    rows, skipped = [], []
    for seq in range(1,7):
        labels={}
        for rec in json.loads((a.data/f'labels/test{seq}_labels.json').read_text()):
            if not rec["annotations"]:
                continue
            frame=int(re.search(r"\d+",Path(rec["filename"]).stem)[0])
            groups=defaultdict(lambda: defaultdict(list))
            for x in rec["annotations"]:
                if x.get("id"):
                    groups[x["id"]][x["class"]].append((x["x"],x["y"]))
            if (not groups or any(x["class"] in JAWS and not x.get("id") for x in rec["annotations"])
                or any(len(g[k])!=1 or not all(math.isfinite(v) and 0<=v<n for v,n in zip(g[k][0],(720,576)))
                       for g in groups.values() for k in JAWS)):
                skipped.append({"sequence":seq,"frame":frame,"reason":"incomplete, conflicting or invalid clasper pairs"})
                continue
            labels[frame]=[np.mean([g[k][0] for k in JAWS],axis=0) for g in groups.values()]
        cap=cv2.VideoCapture(str(a.data/f'raw/Tracking/Dataset{seq}/Video.avi'))
        if not cap.isOpened():
            raise OSError(f"Cannot open sequence {seq}")
        try:
            for f in range(1,max(labels)+1):
                ok,img=cap.read()
                if not ok: raise OSError(f"Cannot decode sequence {seq} frame {f}")
                if f not in labels: continue
                gt=np.asarray(labels[f])
                r=model.predict(img,imgsz=640,conf=.25,device="cpu",verbose=False)[0]
                candidates=[]
                if r.keypoints is not None:
                    for pts in r.keypoints.data.cpu().numpy():
                        jaws=pts[:2]
                        if np.isfinite(jaws).all() and (jaws[:,2]>=.5).all():
                            candidates.append(jaws[:,:2].mean(axis=0))
                pred=np.asarray(candidates).reshape(-1,2)
                cost=np.linalg.norm(gt[:,None,:]-pred[None,:,:],axis=2)
                rows.append(dict(sequence=seq,frame=f,truth_count=len(gt),candidate_count=len(pred),
                                 tp_10=len(matches(cost,10)),tp_20=len(matches(cost,20)),
                                 paired_errors=[float(cost[i,j]) for i,j in matches(cost)]))
        finally:
            cap.release()
        print(seq, summarize([r for r in rows if r["sequence"]==seq]),flush=True)
    result=dict(protocol={"imgsz":640,"box_conf":.25,"clasper_conf":.5,
                         "rmse":"minimum-distance one-to-one pairs without cutoff; unmatched truths excluded",
                         "threshold_matching":"maximum one-to-one match count inside radius, then minimum distance",
                         "excluded_frames":"whole annotated frame excluded when any tagged tool lacks a unique valid clasper pair"},
                annotated_frames_total=len(rows)+len(skipped),skipped=skipped,
                overall=summarize(rows),
                related_1_to_4=summarize([r for r in rows if r["sequence"]<=4]),
                additional_5_to_6=summarize([r for r in rows if r["sequence"]>=5]),
                per_sequence={seq:summarize([r for r in rows if r["sequence"]==seq]) for seq in range(1,7)})
    a.output.mkdir(parents=True,exist_ok=True)
    (a.output/"summary.json").write_text(json.dumps(result,indent=2)+"\n")
    with (a.output/"per_frame.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(json.dumps({k:result[k] for k in ('overall','related_1_to_4','additional_5_to_6')},indent=2))

if __name__=="__main__":
    main()
