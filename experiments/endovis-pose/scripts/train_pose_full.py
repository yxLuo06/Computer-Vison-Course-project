"""Train the full prepared dataset and evaluate held-out Dataset4."""
from pathlib import Path
from ultralytics import YOLO
import torch
ROOT=Path.cwd().resolve()

def main():
    model=YOLO(str(ROOT/'yolo26n-pose.pt'))
    model.train(data=str(ROOT/'datasets/endovis2015/yolo_pose/data.yaml'),epochs=30,
                imgsz=640,batch=4,device=('mps' if torch.backends.mps.is_available() else 'cpu'),workers=0,seed=0,deterministic=True,
                project=str(ROOT/'runs/pose'),name='endovis_full_mps',exist_ok=False,
                fliplr=0.0,flipud=0.0,mosaic=0.0,mixup=0.0,copy_paste=0.0,
                cache=False,plots=True,patience=10)
    folder=Path(model.trainer.save_dir)
    best=YOLO(str(folder/'weights/best.pt'))
    sources=sorted((ROOT/'datasets/endovis2015/yolo_pose/images/val').glob('*.png'))
    chosen=[sources[round(i*(len(sources)-1)/7)] for i in range(8)]
    best.predict(source=[str(p) for p in chosen],imgsz=640,conf=0.25,device=('mps' if torch.backends.mps.is_available() else 'cpu'),save=True,
                 project=str(ROOT/'runs/pose'),name='endovis_full_prediction',exist_ok=False)
    print('FULL_COMPLETE',folder,flush=True)
if __name__=='__main__':main()
