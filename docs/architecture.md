# Architecture and deployment scope

Implemented: attributed open UCI Iris data, Pandas Bronze/Silver/Gold Parquet pipeline, schema/range/duplicate checks, rejected row records, JSON metrics and threshold alerts, read-only FastAPI, Streamlit dashboard, mock/Ollama incident analyst, Docker Compose, pytest and GitHub Actions CI.

Cloud blueprint (not deployed): Azure Data Factory / Event Hubs ingestion -> Azure Data Lake Gen2 Bronze -> Databricks Spark + Delta Lake Silver/Gold -> Azure Database for PostgreSQL monitoring metrics -> Azure Container Apps backend/frontend -> Azure Monitor, Key Vault, managed identities and Entra ID. Terraform currently declares resource group and ADLS Gen2 storage only.

Not implemented: production streaming, scheduling, historical SLAs, drift monitoring, automatic incident remediation, real alert delivery, authentication or actual Azure deployment. Read-only AI output must undergo human review. Cloud resources incur costs if provisioned.
