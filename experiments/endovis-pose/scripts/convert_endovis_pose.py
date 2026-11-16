"""Prepare a provisional five-keypoint dataset; no source annotations are changed."""
import json,collections,shutil
from pathlib import Path
import cv2,yaml
ROOT=Path.cwd().resolve()
BASE=ROOT/'datasets/endovis2015'
OUT=BASE/'yolo_pose'
KEYS=['LeftClasperPoint','RightClasperPoint','HeadPoint','ShaftPoint','EndPoint']

def main():
    report={'keypoints':KEYS,'box_policy':'Keypoint envelope padded by max(10 pixels, 10% of span) per side, clipped to image. Proxy boxes, not full-instrument ground truth.','visibility_policy':'Annotated points: 1 (location labeled; true occlusion status unknown); missing: 0. No claim of observed visibility.','split_policy':'Dataset1-3 train, Dataset4 validation; official test data is evaluated separately.','excluded':[],'counts':{},'manifest':[]}
    for seq in range(1,5):
        split='val' if seq==4 else 'train'
        for sub in ['images','labels']:(OUT/sub/split).mkdir(parents=True,exist_ok=True)
        rows=json.loads((ROOT/f'EndoVisPoseAnnotation/train_labels/train{seq}_labels.json').read_text())
        n=instances=0
        for row in rows:
            if not row['annotations']:continue # Unannotated frames are NOT negative samples.
            groups=collections.defaultdict(dict);duplicates=[]
            for a in row['annotations']:
                if a['class'] not in KEYS:continue
                if a['class'] in groups[a['id']]:duplicates.append([a['id'],a['class']])
                groups[a['id']][a['class']]=(float(a['x']),float(a['y']))
            name=Path(row['filename']).name
            if duplicates:
                report['excluded'].append({'sequence':seq,'image':name,'duplicate_keys':duplicates});continue
            source=BASE/f'frames/Dataset{seq}'/name
            img=cv2.imread(str(source))
            if img is None:raise RuntimeError(f'Missing image: {source}')
            h,w=img.shape[:2]; lines=[];objects=[]
            for tool,points in sorted(groups.items()):
                assert all(0<=x<w and 0<=y<h for x,y in points.values())
                xs,ys=zip(*points.values()); dx=max(10,.1*(max(xs)-min(xs)));dy=max(10,.1*(max(ys)-min(ys)))
                x1=max(0,min(xs)-dx);x2=min(w,max(xs)+dx);y1=max(0,min(ys)-dy);y2=min(h,max(ys)+dy)
                values=[0,(x1+x2)/2/w,(y1+y2)/2/h,(x2-x1)/w,(y2-y1)/h]
                for key in KEYS:
                    values.extend([points[key][0]/w,points[key][1]/h,1] if key in points else [0,0,0])
                assert len(values)==20 and all(0<=v<=1 for v in values)
                lines.append(' '.join(f'{v:.8f}' for v in values))
                objects.append({'source_tool_id':tool,'missing':[k for k in KEYS if k not in points]})
            stem=f'dataset{seq}_{Path(name).stem}'
            shutil.copy2(source,OUT/'images'/split/f'{stem}.png')
            (OUT/'labels'/split/f'{stem}.txt').write_text('\n'.join(lines)+'\n')
            report['manifest'].append({'image':f'images/{split}/{stem}.png','sequence':seq,'original_frame':int(name.split('_')[1]),'fps':25,'objects':objects})
            n+=1;instances+=len(lines)
            if n==1:
                canvas=img.copy()
                for line in lines:
                    a=list(map(float,line.split()));cx,cy,bw,bh=a[1:5]
                    cv2.rectangle(canvas,(round((cx-bw/2)*w),round((cy-bh/2)*h)),(round((cx+bw/2)*w),round((cy+bh/2)*h)),(0,255,0),2)
                    for i in range(5):
                        x,y,v=a[5+3*i:8+3*i]
                        if v:cv2.circle(canvas,(round(x*w),round(y*h)),4,(0,255,255),-1)
                cv2.imwrite(str(OUT/f'preview_dataset{seq}.jpg'),canvas)
        report['counts'][f'Dataset{seq}']={'split':split,'images':n,'instances':instances}
    config={'path':str(OUT),'train':'images/train','val':'images/val','kpt_shape':[5,3],'names':{0:'instrument'},'kpt_names':{0:KEYS}}
    (OUT/'data.yaml').write_text(yaml.safe_dump(config,sort_keys=False))
    (OUT/'conversion_report.json').write_text(json.dumps(report,indent=2))
    (OUT/'README.md').write_text('Provisional EndoVis pose dataset\n\nSee conversion_report.json for provenance, exclusions, keypoint order, visibility policy and proxy-box limitations. TrackedPoint is intentionally omitted. Missing annotation does not imply absence. Disable horizontal flips (fliplr=0.0, flipud=0.0) until jaw semantics under reflection are verified. Validation is Dataset4 only; this is not the official test set. Original video frame 0 is provisionally mapped to annotation img_000001; first previews were visually checked, not every frame. Labels contain one instrument class; original tool IDs remain in the manifest for provenance and are not predicted track IDs.\n')
    print(json.dumps({'counts':report['counts'],'excluded':report['excluded']},indent=2))
if __name__=='__main__':main()
