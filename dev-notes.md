# Dev Notes

## What We Built So Far

This repo now contains a working MVP for the Startup City Data Pipeline project.

- FastAPI app with health, pipeline trigger, city metrics, recommendations, region analytics, and dashboard routes.
- Deterministic demo collector that generates cost-of-living, quality-of-life, startup, and remote-work metrics for a 220-city catalog.
- Transformation layer that calculates affordability, livability, opportunity, and overall recommendation scores.
- Local SQLite warehouse at `data/cities.sqlite3`.
- CSV exports for dashboarding at `exports/city_metrics.csv` and `exports/city_recommendations.csv`.
- Screenshot-friendly dashboard at `/dashboard`.
- Live Teleport source mode for public urban-area quality-of-life scores.
- Power BI model notes in `docs/powerbi_model.md`.
- Snowflake starter schema in `sql/snowflake_schema.sql`.
- Docker, docker-compose, Makefile, tests, linting, and GitHub Actions CI.

## Current Architecture

```mermaid
flowchart LR
    catalog["City Catalog<br/>220 default cities"]
    collector["Collectors<br/>demo + Teleport live API"]
    transform["Transform Layer<br/>scoring models"]
    warehouse["SQLite Warehouse<br/>city_metrics<br/>city_recommendations"]
    exports["CSV Exports<br/>Power BI-ready files"]
    api["FastAPI API<br/>/cities<br/>/recommendations<br/>/analytics/regions"]
    dashboard["Dashboard<br/>/dashboard"]

    catalog --> collector
    collector --> transform
    transform --> warehouse
    warehouse --> exports
    warehouse --> api
    api --> dashboard
```

## Pipeline Flow

```mermaid
sequenceDiagram
    participant User
    participant API as FastAPI
    participant Runner as Pipeline Runner
    participant Collector
    participant Transform
    participant DB as SQLite Warehouse
    participant Export as CSV Export

    User->>API: POST /pipeline/run?limit=220
    API->>Runner: run_pipeline()
    Runner->>Collector: collect_demo_metrics() or collect_teleport_metrics()
    Collector-->>Runner: raw city metrics
    Runner->>Transform: build_recommendations(metrics)
    Transform-->>Runner: scored recommendations
    Runner->>DB: replace_metrics()
    Runner->>DB: replace_recommendations()
    Runner->>Export: export_tables()
    Runner-->>API: load counts, export paths, top city
    API-->>User: JSON response
```

## API Surface

```mermaid
flowchart TB
    client["Browser / Power BI / API Consumer"]
    health["GET /health"]
    run["POST /pipeline/run"]
    cities["GET /cities"]
    recs["GET /recommendations"]
    regions["GET /analytics/regions"]
    dash["GET /dashboard"]
    db["SQLite Warehouse"]

    client --> health
    client --> run
    client --> cities
    client --> recs
    client --> regions
    client --> dash
    run --> db
    cities --> db
    recs --> db
    regions --> db
    dash --> cities
    dash --> recs
    dash --> regions
```

## Local Commands

```bash
make install
make test
make run
make api
```

Or manually:

```bash
python -m app.cli --limit 220
uvicorn app.main:app --reload
```

Useful local URLs:

- `http://127.0.0.1:8000/dashboard`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/recommendations?limit=10`
- `http://127.0.0.1:8000/analytics/regions`

## Next Steps: Azure, Power BI, and Cloud

### 1. Expand Real Data Sources

- Teleport is now integrated as the first real public data source.
- Keep expanding source adapters under `app/pipeline/`.
- Use public APIs, downloadable datasets, or compliant scraping targets.
- Store source metadata, scrape timestamp, and raw payload references.
- Add retry/backoff and source-specific validation.

Current live source:

- Teleport urban areas list: `https://api.teleport.org/api/urban_areas/`
- Teleport urban-area scores: `https://api.teleport.org/api/urban_areas/slug:{slug}/scores/`
- Local run command: `python -m app.cli --source teleport --limit 50`

Target shape:

```mermaid
flowchart LR
    sources["External Sources<br/>cost, safety, internet, startup signals"]
    adapters["Source Adapters<br/>HTTP/API/scraper modules"]
    raw["Raw Landing<br/>Blob Storage or Data Lake"]
    transform["Validation + Transform"]
    warehouse["Analytics Warehouse"]

    sources --> adapters
    adapters --> raw
    raw --> transform
    transform --> warehouse
```

### 2. Move Storage to Azure

Recommended Azure MVP:

- Azure Blob Storage or ADLS Gen2 for raw files and CSV exports.
- Azure SQL Database for relational serving tables, or Azure Synapse/Fabric Warehouse for analytics.
- Azure Key Vault for API keys and connection strings.
- Azure Container Apps or Azure App Service for the FastAPI API.
- Azure Container Registry for Docker image storage.

Cloud target:

```mermaid
flowchart TB
    scheduler["Azure Logic Apps<br/>or Timer Trigger"]
    container["Azure Container Apps<br/>pipeline job + FastAPI"]
    registry["Azure Container Registry"]
    keyvault["Azure Key Vault"]
    lake["ADLS Gen2 / Blob Storage<br/>raw + exports"]
    sql["Azure SQL / Synapse / Fabric Warehouse"]
    powerbi["Power BI Semantic Model"]
    report["Power BI Report"]

    registry --> container
    keyvault --> container
    scheduler --> container
    container --> lake
    container --> sql
    lake --> powerbi
    sql --> powerbi
    powerbi --> report
```

### 3. Connect Power BI

Practical options:

- Fastest: import `exports/city_metrics.csv` and `exports/city_recommendations.csv`.
- Better: publish CSVs to Azure Blob Storage and connect Power BI to Blob Storage.
- Production: load tables into Azure SQL, Synapse, or Fabric Warehouse and connect Power BI directly.

Power BI model:

- `city_metrics` joins to `city_recommendations` on `city` and `country`.
- Use `city_metrics` for operational metrics.
- Use `city_recommendations` for ranking and scoring visuals.
- Create measures for average score, city count, average cost index, and average remote score.

### 4. Add Orchestration

Good cloud scheduling paths:

- Azure Container Apps Jobs for scheduled pipeline execution.
- Azure Functions Timer Trigger for lightweight scheduled ingestion.
- GitHub Actions scheduled workflow for a simple portfolio deployment.
- Azure Data Factory if the project needs more enterprise-style orchestration.

### 5. Add CI/CD Deployment

Suggested deployment flow:

```mermaid
flowchart LR
    push["Git Push"]
    ci["GitHub Actions<br/>test + lint"]
    build["Build Docker Image"]
    acr["Push to ACR"]
    deploy["Deploy to Azure Container Apps"]
    verify["Smoke Test<br/>/health + /dashboard"]

    push --> ci
    ci --> build
    build --> acr
    acr --> deploy
    deploy --> verify
```

### 6. Productionize the Data Model

- Add `dim_city`, `dim_country`, `fact_city_metric_snapshot`, and `fact_city_recommendation` tables.
- Keep historical snapshots instead of replacing all rows.
- Add data quality checks for missing values, impossible ranges, and duplicate city snapshots.
- Add dbt models if using Synapse, Fabric Warehouse, Snowflake, or BigQuery.

### 7. Portfolio Polish

- Add screenshots to the README.
- Add an architecture section with one Mermaid diagram.
- Deploy `/dashboard` publicly.
- Add a short "Data Caveat" note explaining that demo metrics are synthetic until real source adapters are connected.
- Record a 30-second demo showing pipeline run, API docs, dashboard, and Power BI import.
