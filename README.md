# Enterprise Data Quality and Observability

A practical **local, full-stack data quality platform**: attributed public Iris data, Bronze/Silver/Gold Parquet ETL, schema/range/duplicate checks, rejected-record quarantine, quality alerts and run reports, FastAPI monitoring backend, Streamlit frontend, Docker, CI, optional local open-weight Ollama incident analysis, and Azure storage Terraform.

> **Status:** Source committed. No cloud resources were created. CI runs, end-to-end Docker startup, and real Ollama inference have not yet been independently verified.

## Architecture

```text
UCI Iris CSV (150 rows, CC BY 4.0)
         |
    Pandas ingestion
         |
  Bronze raw Parquet -> Silver valid + rejected Parquet -> Gold aggregated Parquet
                                      |
                                rule-based alerts
                                      |
                              JSON metrics report
                                      |
                    FastAPI /api/quality and /api/ai/investigate
                                      |
                           Streamlit monitoring dashboard

GitHub Actions: tests + image build | Azure: ADLS Gen2 Terraform example
```

## Public dataset

The included [Iris dataset](data/public/iris.csv) has **150 records** from the [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/53/iris) (CC BY 4.0, DOI 10.24432/C56C76), normalized from scikit-learn's public mirror. Details and attribution: [data provenance](data/public/README.md). This dataset is intentionally small; it is suitable for reproducing the pipeline, not demonstrating enterprise throughput.

## Windows PowerShell quick start

```powershell
git clone https://github.com/Khadija162/Enterprise-Data-Quality-and-Observability.git
cd Enterprise-Data-Quality-and-Observability
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m quality.pipeline
.\.venv\Scripts\python.exe -m pytest -q
```

This creates Bronze/Silver/Gold files under `data/` and a report at `artifacts/latest.json`.

Launch the application in separate terminals:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
.\.venv\Scripts\python.exe -m streamlit run frontend/app.py
```

Or, after running the pipeline, launch Docker Desktop:

```powershell
docker compose up --build
```

- Backend docs: http://localhost:8000/docs
- Dashboard: http://localhost:8501

The API reads Gold data and reports via read-only Docker volume mounts. It cannot change pipeline data.

## Open-weight AI incident investigation

The default `LLM_MODE=mock` produces deterministic read-only investigation tips. To use an actual locally hosted model, install [Ollama](https://ollama.com/) and run the **host-side backend** in the same PowerShell session:

```powershell
ollama pull qwen2.5:3b
$env:LLM_MODE="ollama"
$env:OLLAMA_MODEL="qwen2.5:3b"
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

Docker Compose defaults to mock mode. The AI does not fix data automatically or execute generated code.

## Cloud architecture

Recommended Azure path: ingestion using Data Factory or Event Hubs -> Azure Data Lake Storage Gen2 -> Databricks Delta Lake Bronze/Silver/Gold -> monitoring PostgreSQL -> API and dashboard on Azure Container Apps -> Azure Monitor and Key Vault. Terraform currently describes **only a resource group and ADLS Gen2 storage**. Nothing has been provisioned and applying the example may incur costs.

## Scope and limitations

This is a single-run local prototype; not yet an enterprise deployment. It lacks scheduling, historical SLA checks, trend/drift monitoring, authentication, tenant isolation and operational alert delivery. Never expose the unauthenticated API on the public internet. See [architecture notes](docs/architecture.md).

Files: `quality/` ETL and AI; `backend/` FastAPI; `frontend/` Streamlit; `tests/` pytest; `infra/terraform/` Azure starter; `.github/workflows/` CI.
