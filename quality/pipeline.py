"""Idempotent local Bronze/Silver/Gold quality pipeline with rejected row lineage."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

COLUMNS=["sepal_length","sepal_width","petal_length","petal_width","species"]
SPECIES={"setosa","versicolor","virginica"}

def run(source="data/public/iris.csv",output="data",report_dir="artifacts"):
    frame=pd.read_csv(source)
    missing=set(COLUMNS)-set(frame.columns)
    if missing: raise ValueError(f"Missing fields: {sorted(missing)}")
    root=Path(output)
    for layer in ("bronze","silver","gold"): (root/layer).mkdir(parents=True,exist_ok=True)
    frame.to_parquet(root/"bronze"/"events.parquet",index=False)
    numeric=frame[COLUMNS[:4]].apply(pd.to_numeric,errors="coerce")
    valid=numeric.notna().all(axis=1)&numeric.gt(0).all(axis=1)&frame["species"].isin(SPECIES)
    valid &= ~frame.duplicated(keep="first")
    clean=frame.loc[valid].copy()
    rejected=frame.loc[~valid].copy()
    clean.to_parquet(root/"silver"/"valid.parquet",index=False)
    rejected.to_parquet(root/"silver"/"rejected.parquet",index=False)
    group=clean.groupby("species",as_index=False).agg(records=("species","size"),mean_sepal_length=("sepal_length","mean"))
    group.to_parquet(root/"gold"/"quality_by_class.parquet",index=False)
    report={"run_at":datetime.now(timezone.utc).isoformat(),"source":"Iris (UCI, CC BY 4.0)",
        "raw":int(len(frame)),"valid":int(len(clean)),"rejected":int(len(rejected)),
        "rejection_rate":round(len(rejected)/max(len(frame),1),4),"class_count":int(len(group)),
        "alerts":[]}
    if len(frame)==0: report["alerts"].append({"rule":"EMPTY_SOURCE","severity":"warning"})
    if report["rejection_rate"]>.05: report["alerts"].append({"rule":"REJECTION_RATE","severity":"critical"})
    destination=Path(report_dir)/"latest.json";destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(report,indent=2),encoding="utf-8")
    return report

if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--csv",default="data/public/iris.csv")
    args=a.parse_args();print(json.dumps(run(args.csv),indent=2))
