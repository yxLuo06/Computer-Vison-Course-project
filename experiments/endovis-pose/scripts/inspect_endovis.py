"""Extract annotated training frames; frame names use a provisional 1-based index."""
import json,re
from pathlib import Path
import cv2
ROOT=Path.cwd().resolve()
BASE=ROOT/'datasets/endovis2015'
OUT=BASE/'inspection'
OUT.mkdir(exist_ok=True)
report=[]
for seq in range(1,5):
    labels=json.loads((ROOT/f'EndoVisPoseAnnotation/train_labels/train{seq}_labels.json').read_text())
    selected={int(re.search(r'img_(\d+)',x['filename']).group(1)):x for x in labels if x['annotations']}
    video=BASE/f'raw/Tracking_Robotic_Training/Training/Dataset{seq}/Video.avi'
    cap=cv2.VideoCapture(str(video))
    if not cap.isOpened(): raise RuntimeError(f'Cannot open {video}')
    info={'sequence':seq,'fps':cap.get(cv2.CAP_PROP_FPS),'reported_frames':int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),'label_records':len(labels),'annotated_frames':len(selected),'width':int(cap.get(3)),'height':int(cap.get(4))}
    target=BASE/f'frames/Dataset{seq}'
    target.mkdir(parents=True,exist_ok=True)
    count=saved=0
    while True:
        ok,frame=cap.read()
        if not ok:break
        count+=1
        if count not in selected:continue
        path=target/f'img_{count:06d}_raw.png'
        if not cv2.imwrite(str(path),frame):raise RuntimeError(str(path))
        saved+=1
        if saved==1:
            canvas=frame.copy()
            for a in selected[count]['annotations']:
                xy=(round(a['x']),round(a['y']))
                color=(0,255,255) if a['id']=='tool1' else (255,255,0)
                cv2.circle(canvas,xy,4,color,-1)
                cv2.putText(canvas,a['class'].replace('Point',''),(xy[0]+5,xy[1]-5),cv2.FONT_HERSHEY_SIMPLEX,.36,color,1)
            cv2.imwrite(str(OUT/f'dataset{seq}_preview.jpg'),canvas)
    cap.release()
    info.update(decoded_frames=count,extracted_frames=saved)
    assert saved==len(selected),info
    report.append(info)
    print(json.dumps(info),flush=True)
(OUT/'report.json').write_text(json.dumps({'frame_mapping':'Video frame 0 -> img_000001_raw.png; verify visually before training','sequences':report},indent=2))
