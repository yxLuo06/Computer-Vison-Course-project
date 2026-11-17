import argparse
from contextlib import ExitStack
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

import cv2
import torch
import yaml
from ultralytics import YOLO

from train_surgpose_000000 import HEIGHT, TOOL_POINTS, WIDTH

sides = ("left", "right")
panel_width, panel_height, header = 700, 494, 50
gt_color = (95, 255, 75)
pred_color = (40, 188, 255)


def marker(image, point, estimate):
    x, y = point
    center = (int(x * panel_width / WIDTH), int(y * panel_height / HEIGHT))
    if estimate:
        for color, thickness in (((0, 0, 0), 4), (pred_color, 2)):
            cv2.drawMarker(image, center, color, cv2.MARKER_TILTED_CROSS, 13, thickness, cv2.LINE_AA)
    else:
        for color, thickness in (((0, 0, 0), 4), (gt_color, 2)):
            cv2.circle(image, center, 9, color, thickness, cv2.LINE_AA)


def valid(point):
    return point is not None and 0 <= point[0] < WIDTH and 0 <= point[1] < HEIGHT


def panel(frame, truth, estimates, side, index):
    image = cv2.resize(frame, (panel_width, panel_height), interpolation=cv2.INTER_AREA)
    for point in truth:
        marker(image, point, False)
    for point in estimates:
        marker(image, point, True)
    result = cv2.copyMakeBorder(image, header, 0, 0, 0, cv2.BORDER_CONSTANT, value=(23, 23, 23))
    cv2.putText(result, f"{side.title()} camera", (17, 32), cv2.FONT_HERSHEY_SIMPLEX, .75, (250, 250, 250), 2, cv2.LINE_AA)
    cv2.putText(result, f"Frame {index:04d}", (220, 32), cv2.FONT_HERSHEY_SIMPLEX, .57, (225, 225, 225), 1, cv2.LINE_AA)
    cv2.circle(result, (392, 25), 8, gt_color, 2, cv2.LINE_AA)
    cv2.putText(result, "Ground truth", (408, 32), cv2.FONT_HERSHEY_SIMPLEX, .57, (245, 245, 245), 1, cv2.LINE_AA)
    cv2.drawMarker(result, (555, 25), pred_color, cv2.MARKER_TILTED_CROSS, 13, 2, cv2.LINE_AA)
    cv2.putText(result, "Estimate", (571, 32), cv2.FONT_HERSHEY_SIMPLEX, .57, (245, 245, 245), 1, cv2.LINE_AA)
    return result


def main():
    parser = argparse.ArgumentParser(description="Render SurgPose 000011 stereo clasper tip overlays.")
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    encoder = shutil.which("ffmpeg")
    if encoder is None:
        parser.error("ffmpeg is required on PATH")

    model = YOLO(args.weights)
    cuda = torch.cuda.is_available()
    cv2.setNumThreads(2)
    with ExitStack() as stack:
        source = stack.enter_context(zipfile.ZipFile(args.archive))
        temporary = stack.enter_context(tempfile.TemporaryDirectory(dir=output.parent))
        staging = Path(temporary) / "stereo.mp4"
        annotations = [yaml.safe_load(source.read(f"000011/keypoints_{side}.yaml")) for side in sides]
        count = len(annotations[0])
        captures = []
        for side, points in zip(sides, annotations):
            member = f"000011/regular/{side}_video.mp4"
            cap = cv2.VideoCapture(str(source.extract(member, temporary)))
            stack.callback(cap.release)
            assert cap.isOpened() and int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) == count
            assert set(points) == set(range(count))
            assert (cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) == (WIDTH, HEIGHT)
            assert cap.get(cv2.CAP_PROP_FPS) == 30
            captures.append(cap)
        ffmpeg = [
            encoder, "-v", "error", "-y", "-f", "rawvideo",
            "-pix_fmt", "bgr24", "-s", f"{2 * panel_width}x{panel_height + header}",
            "-r", "30", "-i", "pipe:0", "-an", "-c:v", "libx264", "-threads", "6",
            "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", str(staging),
        ]
        proc = stack.enter_context(subprocess.Popen(ffmpeg, stdin=subprocess.PIPE))
        totals = [[0, 0], [0, 0]]
        for start in range(0, count, 8):
            frames = []
            for index in range(start, min(start + 8, count)):
                for cap in captures:
                    ok, frame = cap.read()
                    if not ok:
                        raise RuntimeError(f"Failed to read frame {index}")
                    frames.append(frame)
            results = model.predict(frames, imgsz=640, conf=.25, device=0 if cuda else "cpu", quantize=16 if cuda else 32, verbose=False)
            for offset in range(0, len(results), 2):
                index = start + offset // 2
                panels = []
                for camera, side in enumerate(sides):
                    points = annotations[camera][index]
                    truth = [points.get(tip) for tool in TOOL_POINTS for tip in tool if valid(points.get(tip))]
                    result = results[offset + camera]
                    keypoints = result.keypoints.data.cpu().numpy()[:, :2, :]
                    estimates = [(x, y) for x, y, score in keypoints.reshape(-1, 3) if score >= .25 and valid((x, y))]
                    totals[camera][0] += len(truth)
                    totals[camera][1] += len(estimates)
                    panels.append(panel(frames[offset + camera], truth, estimates, side, index))
                proc.stdin.write(cv2.hconcat(panels).tobytes())
            if start % 80 == 0:
                print(f"Rendered through frame {index} of {count - 1}", flush=True)
        proc.stdin.close()
        if proc.wait():
            raise RuntimeError("FFmpeg failed")
        staging.replace(output)
    print(f"Rendered {count} synchronized frames. Marker totals (GT, estimate): {totals}", flush=True)


if __name__ == "__main__":
    main()
