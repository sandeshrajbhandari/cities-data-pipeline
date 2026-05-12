from app.pipeline.collector import collect_demo_metrics
from app.pipeline.catalog import get_city_catalog
from app.pipeline.transform import build_recommendations
from app.pipeline.warehouse import CityWarehouse
from app.pipeline.runner import run_pipeline


def test_build_recommendations_sorts_by_overall_score():
    cities = get_city_catalog(10)
    metrics = collect_demo_metrics(cities)
    recommendations = build_recommendations(metrics)

    assert len(recommendations) == 10
    assert recommendations[0].overall_score >= recommendations[-1].overall_score


def test_run_pipeline_loads_and_exports(tmp_path):
    warehouse = CityWarehouse(tmp_path / "cities.sqlite3")
    metrics, recommendations, exports = run_pipeline(
        warehouse=warehouse,
        city_limit=12,
        export_dir=tmp_path / "exports",
    )

    assert len(metrics) == 12
    assert len(recommendations) == 12
    assert len(warehouse.list_metrics(limit=20)) == 12
    assert exports["city_metrics"].exists()
    assert exports["city_recommendations"].exists()
