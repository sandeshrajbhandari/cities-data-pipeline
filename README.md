# Startup City Data Pipeline

FastAPI-based data pipeline for collecting, scoring, storing, and exporting cost-of-living and quality-of-life metrics for startup and remote-work cities.

This repo is an MVP version of the resume project: it ships with a deterministic demo collector, a local SQLite warehouse, recommendation scoring, CSV exports for Power BI, and API endpoints to trigger and inspect the pipeline. The collector is intentionally swappable so real sources such as Numbeo-style pages, public datasets, or vendor APIs can replace the demo metrics later.

## What It Does

- Builds a global city catalog with a default 220-city run.
- Generates cost, rent, grocery, restaurant, purchasing power, safety, healthcare, climate, internet, startup, and remote-work metrics.
- Transforms raw metrics into affordability, livability, opportunity, and overall recommendation scores.
- Loads the current run into a local warehouse at `data/cities.sqlite3`.
- Exports `exports/city_metrics.csv` and `exports/city_recommendations.csv` for Power BI.
- Exposes FastAPI endpoints for pipeline execution and dashboard consumption.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
python -m app.cli
```

Start the API:

```bash
uvicorn app.main:app --reload
```

Or run it in Docker:

```bash
docker compose up --build
```

Open:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/dashboard`
- `POST http://127.0.0.1:8000/pipeline/run?limit=220`
- `GET http://127.0.0.1:8000/recommendations`
- `GET http://127.0.0.1:8000/recommendations?region=Europe&min_overall_score=60`
- `GET http://127.0.0.1:8000/cities`
- `GET http://127.0.0.1:8000/analytics/regions`

For portfolio screenshots, run the API and capture `/dashboard`. A sample browser capture is stored at `screenshots/dashboard-localhost.png`.

Or use the Makefile:

```bash
make install
make test
make run
make api
```

## Project Structure

```text
app/
  main.py                 FastAPI app and endpoints
  cli.py                  Batch runner
  pipeline/
    catalog.py            City catalog seed
    collector.py          Demo collector plus generic HTML table scraper
    transform.py          Scoring logic
    warehouse.py          SQLite load/export layer
    runner.py             End-to-end pipeline orchestration
tests/
  test_pipeline.py        Pipeline smoke tests
```

## Power BI

After running the CLI or `/pipeline/run`, import these files into Power BI:

- `exports/city_metrics.csv`
- `exports/city_recommendations.csv`

Useful visuals:

- Top cities by `overall_score`
- Affordability vs opportunity scatter plot
- Region-level average `remote_work_score`
- Cost-of-living vs quality-of-life matrix

See `docs/powerbi_model.md` for join keys and starter DAX measures.

## Snowflake

The starter Snowflake warehouse schema lives in `sql/snowflake_schema.sql`. It mirrors the local SQLite tables and includes a `region_summary` view for analytics workloads.

## Next Upgrades

- Replace `collect_demo_metrics` with real source adapters.
- Add dbt models for dimensional marts.
- Add a Snowflake loader implementation beside `CityWarehouse`.
- Schedule the CLI with Cloud Run Jobs, Cloud Scheduler, or GitHub Actions.
