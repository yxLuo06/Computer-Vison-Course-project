import argparse
import json
import tempfile
import zipfile
from collections import Counter
from pathlib import Path
import cv2
import yaml
from train_surgpose_000000 import label_frame, train

parser = argparse.ArgumentParser(description="Convert SurgPose 000001–000010 and fine-tune the 000000 checkpoint.")
parser.add_argument("--archives", type=Path, required=True)
parser.add_argument("--pilot-root", type=Path, required=True)
parser.add_argument("--root", type=Path, required=True)
parser.add_argument("--device", default="0")
parser.add_argument("--prepare-only", action="store_true")
args = parser.parse_args()
root = args.root.resolve()

for split in ('train', 'val'):
    for kind in ('images', 'labels'):
        (root / kind / split).mkdir(parents=True, exist_ok=True)

report = {}
for seq in (f'{i:06}' for i in range(1, 11)):
    counts = Counter()
    sides = ('left', 'right')
    with tempfile.TemporaryDirectory(dir=root) as stage:
        with zipfile.ZipFile(args.archives / f'{seq}.zip') as source:
            points = [yaml.safe_load(source.read(f'{seq}/keypoints_{side}.yaml')) for side in sides]
            boxes = [json.loads(source.read(f'{seq}/bbox_{side}.json')) for side in sides]
            videos = [source.extract(f'{seq}/regular/{side}_video.mp4', stage) for side in sides]
        caps = [cv2.VideoCapture(video) for video in videos]
        try:
            assert all(cap.isOpened() for cap in caps), seq
            n = int(caps[0].get(cv2.CAP_PROP_FRAME_COUNT))
            assert int(caps[1].get(cv2.CAP_PROP_FRAME_COUNT)) == n, seq
            for i in range(n):
                frames = [cap.read() for cap in caps]
                assert all(ok and image.shape[:2] == (986, 1400) for ok, image in frames), (seq, i)
                t = i / n
                if not i or .58 <= t < .62 or .82 <= t < .86:
                    continue
                split = 'val' if .62 <= t < .82 else 'train'
                try:
                    labels = [label_frame(p[i], b[str(i)]) for p, b in zip(points, boxes)]
                except (KeyError, ValueError, TypeError) as error:
                    counts['excluded_pairs'] += 1
                    if counts['excluded_pairs'] <= 3:
                        print(seq, i, error, flush=True)
                    continue
                for side, (_, image), label in zip(sides, frames, labels):
                    name = f'{seq}_{side}_{i:06}'
                    assert cv2.imwrite(str(root / 'images' / split / f'{name}.jpg'), image)
                    (root / 'labels' / split / f'{name}.txt').write_text(label, encoding='ascii')
                    counts[split] += 1
        finally:
            for cap in caps:
                cap.release()
    assert counts['train'] and counts['val'], seq
    report[seq] = dict(counts)
    print(seq, report[seq], flush=True)
config = yaml.safe_load((args.pilot_root / 'data.yaml').read_text())
config['path'] = root.as_posix()
(root / 'data.yaml').write_text(yaml.safe_dump(config), encoding='utf-8')
(root / 'conversion.json').write_text(json.dumps(report, indent=2))
if not args.prepare_only:
    weights = args.pilot_root.resolve() / "runs/surgpose_000000_tip/weights/best.pt"
    train(weights, root, args.device, 10, run_name="surgpose_000001_000010_tip")
