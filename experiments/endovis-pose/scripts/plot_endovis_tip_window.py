"""Plot continuous predictions, sparse labels and adjacent-frame speed."""
import argparse
import csv
from pathlib import Path

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from ultralytics import YOLO


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("weights", "video", "labels_csv", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    start, end = 480, 550
    frames = np.arange(start, end+1)
    xy = np.full((len(frames), 2), np.nan)
    truth = np.full_like(xy, np.nan)
    with args.labels_csv.open() as f:
        for row in csv.DictReader(f):
            frame = int(row["frame"].split("_")[2])
            if start <= frame <= end:
                truth[frame-start] = float(row["true_x"]), float(row["true_y"])
    model = YOLO(str(args.weights))
    if list(model.model.yaml.get("kpt_shape", [])) != [5, 3]:
        raise ValueError("Expected the five-point checkpoint")
    cap = cv2.VideoCapture(str(args.video))
    try:
        fps = cap.get(cv2.CAP_PROP_FPS)
        if not cap.isOpened() or not np.isfinite(fps) or fps <= 0:
            raise OSError("Cannot read video and FPS")
        # Decode sequentially; annotation number 1 is the first decoded frame.
        for n in range(1, end+1):
            ok, img = cap.read()
            if not ok:
                raise OSError(f"Cannot decode source frame {n}")
            if n < start:
                continue
            result = model.predict(img, imgsz=640, conf=.25, device="cpu", verbose=False)[0]
            if result.keypoints is None:
                continue
            valid = []
            for score, pts in zip(result.boxes.conf.tolist(), result.keypoints.data.numpy()):
                jaws = pts[:2]
                if np.isfinite(jaws).all() and (jaws[:, 2] >= .5).all():
                    valid.append((score, jaws[:, :2].mean(axis=0)))
            if valid:
                xy[n-start] = max(valid, key=lambda c:c[0])[1]
    finally:
        cap.release()
    speed = np.r_[np.nan, np.linalg.norm(np.diff(xy, axis=0), axis=1)*fps]
    args.output.mkdir(parents=True, exist_ok=True)
    np.savetxt(args.output/"frame_window.csv", np.column_stack((frames, (frames-1)/fps, xy, truth, speed)),
               delimiter=",", header="source_frame,time_s,pred_x_px,pred_y_px,truth_x_px,truth_y_px,speed_px_s",
               comments="", fmt=["%d","%.3f",*(["%.3f"]*5)])
    fig, axes = plt.subplots(3, 1, figsize=(10, 7.2), sharex=True, layout="constrained")
    fig.suptitle("Dataset4: predicted tip motion around frames 505–520", fontweight="bold", fontsize=16)
    for i, ax in enumerate(axes):
        ax.axvspan(505, 520, color="#ffedbe", alpha=.8, label="Frames 505–520" if i==0 else None)
        ax.grid(axis="y", alpha=.22)
        ax.spines[["top","right"]].set_visible(False)
        if i < 2:
            ax.plot(frames, xy[:,i], color="#205db1", lw=1.6, label="Predicted midpoint")
            ax.scatter(frames, truth[:,i], s=17, color="#00836a", zorder=4, label="Annotated midpoint")
            ax.set_ylabel(("x","y")[i]+" (px)")
        else:
            ax.plot(frames,speed,color="#aa3b37",lw=1.55)
            ax.set(ylabel="Speed (px/s)",xlabel=f"Original frame number · {fps:g} FPS")
    axes[0].legend(loc="upper left", ncol=3, frameon=False, fontsize=9)
    if np.isfinite(speed).any():
        j = np.nanargmax(speed)
        axes[2].scatter(frames[j],speed[j],color="#aa3b37",s=23)
        axes[2].annotate(f"{speed[j]:.0f} px/s at frame {frames[j]}", xy=(frames[j],speed[j]), xytext=(8,-16) if frames[j]<530 else (-125,-16),
                         textcoords="offset points", fontsize=9)
        print("Peak:", frames[j], speed[j])
    fig.savefig(args.output/"tip_motion.png",dpi=150)
    print("Valid predictions:", np.isfinite(xy[:,0]).sum(), "| annotated frames:", np.isfinite(truth[:,0]).sum())
    for a,b in [(480,504),(505,520),(521,550)]:
        mask=(frames>=a)&(frames<=b)
        print(a,b,"peak speed",float(np.nanmax(speed[mask])))
    overlap=np.isfinite(truth[:,0])
    print("Midpoint errors on annotated frames:", np.round(np.linalg.norm(xy[overlap]-truth[overlap],axis=1),2))
if __name__ == "__main__":
    main()
