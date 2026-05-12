from __future__ import annotations

from pathlib import Path

from app.pipeline.catalog import get_city_catalog
from app.pipeline.collector import collect_demo_metrics
from app.pipeline.models import CityMetric, CityRecommendation
from app.pipeline.transform import build_recommendations
from app.pipeline.warehouse import CityWarehouse


def run_pipeline(
    warehouse: CityWarehouse,
    city_limit: int,
    export_dir: Path | None = None,
) -> tuple[list[CityMetric], list[CityRecommendation], dict[str, Path]]:
    cities = get_city_catalog(city_limit)
    metrics = collect_demo_metrics(cities)
    recommendations = build_recommendations(metrics)
    warehouse.replace_metrics(metrics)
    warehouse.replace_recommendations(recommendations)
    exports = warehouse.export_tables(export_dir) if export_dir else {}
    return metrics, recommendations, exports
