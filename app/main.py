from __future__ import annotations

from fastapi import Depends, FastAPI, Query

from app.pipeline.config import Settings, get_settings
from app.pipeline.runner import run_pipeline
from app.pipeline.warehouse import CityWarehouse


def get_warehouse(settings: Settings = Depends(get_settings)) -> CityWarehouse:
    return CityWarehouse(settings.database_path)


app = FastAPI(
    title="Startup City Data Pipeline",
    description="Ingests, scores, stores, and exports city cost-of-living and quality metrics.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/pipeline/run")
def trigger_pipeline(
    limit: int = Query(default=220, ge=1, le=1000),
    settings: Settings = Depends(get_settings),
    warehouse: CityWarehouse = Depends(get_warehouse),
) -> dict:
    metrics, recommendations, exports = run_pipeline(
        warehouse=warehouse,
        city_limit=limit,
        export_dir=settings.export_dir,
    )
    return {
        "loaded_metrics": len(metrics),
        "loaded_recommendations": len(recommendations),
        "exports": {name: str(path) for name, path in exports.items()},
        "top_city": recommendations[0].model_dump() if recommendations else None,
    }


@app.get("/cities")
def list_cities(
    limit: int = Query(default=50, ge=1, le=1000),
    region: str | None = None,
    country: str | None = None,
    min_remote_work_score: float | None = Query(default=None, ge=0, le=100),
    warehouse: CityWarehouse = Depends(get_warehouse),
) -> list[dict]:
    warehouse.initialize()
    return warehouse.list_metrics(
        limit=limit,
        region=region,
        country=country,
        min_remote_work_score=min_remote_work_score,
    )


@app.get("/recommendations")
def list_recommendations(
    limit: int = Query(default=25, ge=1, le=1000),
    region: str | None = None,
    country: str | None = None,
    min_overall_score: float | None = Query(default=None, ge=0, le=100),
    warehouse: CityWarehouse = Depends(get_warehouse),
) -> list[dict]:
    warehouse.initialize()
    return warehouse.list_recommendations(
        limit=limit,
        region=region,
        country=country,
        min_overall_score=min_overall_score,
    )


@app.get("/analytics/regions")
def region_summary(warehouse: CityWarehouse = Depends(get_warehouse)) -> list[dict]:
    warehouse.initialize()
    return warehouse.region_summary()
