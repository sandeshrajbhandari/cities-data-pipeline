from __future__ import annotations

from pathlib import Path

from app.pipeline.catalog import get_city_catalog
from app.pipeline.collector import collect_demo_metrics, collect_teleport_metrics
from app.pipeline.models import CityMetric, CityRecommendation
from app.pipeline.transform import build_recommendations
from app.pipeline.warehouse import CityWarehouse


def run_pipeline(
    warehouse: CityWarehouse,
    city_limit: int,
    export_dir: Path | None = None,
    source: str = "demo",
    teleport_api_base_url: str = "https://api.teleport.org/api",
) -> tuple[list[CityMetric], list[CityRecommendation], dict[str, Path]]:
    if source == "teleport":
        metrics = collect_teleport_metrics(city_limit, base_url=teleport_api_base_url)
    elif source == "demo":
        cities = get_city_catalog(city_limit)
        metrics = collect_demo_metrics(cities)
    else:
        raise ValueError(f"Unsupported data source: {source}")

    recommendations = build_recommendations(metrics)
    warehouse.replace_metrics(metrics)
    warehouse.replace_recommendations(recommendations)
    exports = warehouse.export_tables(export_dir) if export_dir else {}
    return metrics, recommendations, exports
