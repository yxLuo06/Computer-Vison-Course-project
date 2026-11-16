"""Score only images with both tools' complete three-vertex jaw labels."""
import argparse
from collections import defaultdict, Counter
import csv
from itertools import product
import json
import math
from pathlib import Path


def match(distances, threshold=math.inf):
    best=(0,0); selected=[]
    for choices in product(*[[-1]+[j for j,d in enumerate(row) if d<=threshold] for row in distances]):
        pairs=[(i,j) for i,j in enumerate(choices) if j!=-1]
        if len({j for _,j in pairs})!=len(pairs):continue
        key=(-len(pairs),sum(distances[i][j] for i,j in pairs))
        if key<best:best,selected=key,pairs
    return selected


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ("annotations","predictions","output"):p.add_argument(key,type=Path)
    a=p.parse_args()
    labels=defaultdict(dict)
    with a.annotations.open() as f:
        for r in csv.DictReader(f):
            k=r["sequence"],r["image"]
            assert r["tool"] not in labels[k]
            labels[k][r["tool"]]=r
    preds=json.loads(a.predictions.read_text())
    assert len({(r["sequence"],r["image"]) for r in preds})==len(preds)==len(labels)==450
    output=[]; errors=[]; excluded=Counter()
    for r in preds:
        key=r["sequence"],r["image"]
        entries=labels[key]
        assert set(entries)=={"Left","Right"}
        if any(x["status"]!="valid" for x in entries.values()):
            reason="+".join(sorted({x["status"] for x in entries.values()}-{"valid"}))
            excluded[reason]+=1
            output.append(dict(sequence=key[0],image=key[1],status=reason,
                               truth="",predictions="",tp10="",tp20="",paired_errors_px=""))
            continue
        gt=[tuple((float(x[f"tip1_{d}"])+float(x[f"tip2_{d}"]))/2 for d in "xy") for x in entries.values()]
        ps=[]
        for obj in r["predictions"]:
            k=obj["keypoints"][:2]
            if obj["box_confidence"]>=.25 and min(x["confidence"] for x in k)>=.5:
                ps.append(tuple(sum(x[d] for x in k)/2 for d in "xy"))
        distances=[[math.dist(g,p) for p in ps] for g in gt]
        e=[distances[i][j] for i,j in match(distances)]
        errors.extend(e)
        output.append(dict(sequence=key[0],image=key[1],status="evaluated",truth=len(gt),
                           predictions=len(ps),tp10=len(match(distances,10)),tp20=len(match(distances,20)),
                           paired_errors_px=json.dumps(e)))
    kept=[r for r in output if r["status"]=="evaluated"]
    gt,n,tp10,tp20=(sum(r[k] for r in kept) for k in ("truth","predictions","tp10","tp20"))
    summary=dict(total_images=len(preds),evaluated_images=len(kept),excluded_images=dict(excluded),
                 truth=gt,eligible_predictions=n,tp_20px=tp20,fp_20px=n-tp20,fn_20px=gt-tp20,
                 precision_20px=tp20/n if n else None,recall_20px=tp20/gt,pck_10px=tp10/gt,
                 rmse_px=math.sqrt(sum(x*x for x in errors)/len(errors)) if errors else None,
                 instances_used_for_rmse=len(errors),frames_without_prediction=sum(not r["predictions"] for r in kept))
    a.output.mkdir(parents=True,exist_ok=True)
    (a.output/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    with (a.output/"per_image.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(output[0]));w.writeheader();w.writerows(output)
    print(json.dumps(summary,indent=2))

if __name__=="__main__":
    main()
