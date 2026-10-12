import pandas as pd
from fastapi.testclient import TestClient
from backend.main import app
from quality.pipeline import run
from quality.ai import investigate

def test_pipeline(tmp_path):
    x=pd.DataFrame({"sepal_length":[5.1,-1],"sepal_width":[3.5,3.0],
      "petal_length":[1.4,1.3],"petal_width":[0.2,0.2],"species":["setosa","setosa"]})
    p=tmp_path/"source.csv";x.to_csv(p,index=False)
    report=run(str(p),str(tmp_path/"lake"),str(tmp_path/"reports"))
    assert report["raw"]==2 and report["rejected"]==1
    assert report["alerts"][0]["rule"]=="REJECTION_RATE"

def test_endpoints(monkeypatch,tmp_path):
    monkeypatch.setenv("REPORT_PATH",str(tmp_path/"missing.json"))
    monkeypatch.setenv("GOLD_PATH",str(tmp_path/"missing.parquet"))
    c=TestClient(app)
    assert c.get("/health").status_code==200
    assert c.get("/api/quality").json()["classes"]==[]
    assert c.post("/api/ai/investigate").status_code==404

def test_mock_ai(monkeypatch):
    monkeypatch.setenv("LLM_MODE","mock")
    a=investigate({"raw":10,"valid":9,"rejected":1,"rejection_rate":.1,"alerts":[]})
    assert a["human_approval_required"]
