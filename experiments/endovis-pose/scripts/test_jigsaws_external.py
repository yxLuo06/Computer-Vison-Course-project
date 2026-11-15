"""Run the frozen EndoVis model on the author's JIGSAWS validation images."""
import argparse
import csv
import json
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

NAMES = ("LeftClasperPoint", "RightClasperPoint", "HeadPoint", "ShaftPoint", "EndPoint")
COLORS = [(40,220,255),(255,205,50),(120,255,85),(235,120,255),(255,130,75)]


def text(img, msg, xy, color=(245,245,245), scale=.48):
    cv2.putText(img,msg,xy,cv2.FONT_HERSHEY_SIMPLEX,scale,(22,22,22),3,cv2.LINE_AA)
    cv2.putText(img,msg,xy,cv2.FONT_HERSHEY_SIMPLEX,scale,color,1,cv2.LINE_AA)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ("weights","validation_dir","output"):
        parser.add_argument(name,type=Path)
    a=parser.parse_args()
    images=sorted(a.validation_dir.glob("video_*/images/*.jpg"))
    if not images:
        parser.error("Expected annotations_val containing video_*/images/*.jpg")
    model=YOLO(str(a.weights))
    if list(model.model.yaml.get("kpt_shape",[])) != [5,3]:
        raise ValueError("Expected the EndoVis five-point checkpoint")
    a.output.mkdir(parents=True,exist_ok=False)
    rows=[]
    examples={}
    all_preds=[]
    for path in images:
        seq=path.parents[1].name
        dst=a.output/"overlays"/seq
        dst.mkdir(parents=True,exist_ok=True)
        frame=cv2.imread(str(path))
        if frame is None: raise OSError(path)
        result=model.predict(frame,imgsz=640,conf=.25,device="cpu",verbose=False)[0]
        draw=cv2.copyMakeBorder(frame,34,57,0,0,cv2.BORDER_CONSTANT,value=(26,26,26))
        objects=[]
        if result.keypoints is not None:
            boxes=result.boxes.xyxy.cpu().tolist()
            scores=result.boxes.conf.cpu().tolist()
            points=result.keypoints.data.cpu().tolist()
            if not len(boxes)==len(scores)==len(points):
                raise ValueError(f"Inconsistent predictions for {path}")
            for box,score,kpts in zip(boxes,scores,points):
                x1,y1,x2,y2=map(round,box)
                cv2.rectangle(draw,(x1,y1+34),(x2,y2+34),(210,175,66),2,cv2.LINE_AA)
                text(draw,f"instrument {score:.2f}",(max(3,x1),max(45,y1+30)),(245,222,120))
                entries=[]
                for i,(name,pt,color) in enumerate(zip(NAMES,kpts,COLORS),1):
                    x,y,k=pt
                    entries.append(dict(name=name,x=x,y=y,confidence=k))
                    pixel=(round(x),round(y)+34)
                    cv2.circle(draw,pixel,5,color,-1 if k>=.50 else 1,cv2.LINE_AA)
                    text(draw,str(i),(min(frame.shape[1]-14,pixel[0]+6),max(45,pixel[1]-4)),color,.4)
                objects.append(dict(box_xyxy=box,box_confidence=score,keypoints=entries))
        text(draw,f"{seq} / {path.stem}  |  {len(objects)} detections",(12,22))
        h=frame.shape[0]+34
        text(draw,"1 Left tip  2 Right tip  3 Head  4 Shaft  5 End",(12,h+20))
        text(draw,"Box label: detector score | Hollow point: score < 0.50",(12,h+42),scale=.44)
        if not cv2.imwrite(str(dst/path.name),draw):raise OSError(dst/path.name)
        if path.stem in ("frame000","frame037","frame074"):
            examples[(seq,path.stem)]=cv2.resize(draw,(384,342))
        rows.append(dict(sequence=seq,image=path.name,boxes=len(objects),
                         eligible_midpoints=sum(min(k["confidence"] for k in o["keypoints"][:2])>=.50
                                                for o in objects)))
        all_preds.append(dict(sequence=seq,image=path.name,predictions=objects))
    with (a.output/"per_image.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (a.output/"predictions.json").write_text(json.dumps(all_preds,allow_nan=False))
    if len(examples)==18:
        seqs=sorted({s for s,_ in examples})
        panels=[np.hstack([examples[(seq,n)] for n in ("frame000","frame037","frame074")]) for seq in seqs]
        for i in (0,1):
            if not cv2.imwrite(str(a.output/f"preview-{i+1}.jpg"),np.vstack(panels[i*3:i*3+3])):
                raise OSError("Cannot write preview")
    def stats(rr):
        return dict(images=len(rr), no_box=sum(r["boxes"]==0 for r in rr),
                    at_least_two_boxes=sum(r["boxes"]>=2 for r in rr),
                    no_eligible_midpoint=sum(r["eligible_midpoints"]==0 for r in rr))
    summary=dict(overall=stats(rows),imgsz=640,box_threshold=.25,midpoint_point_threshold=.5,
                 per_sequence={s:stats([r for r in rows if r["sequence"]==s])
                               for s in sorted({r["sequence"] for r in rows})})
    (a.output/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))

if __name__=="__main__":
    main()
