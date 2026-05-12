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


def test_warehouse_filters_and_region_summary(tmp_path):
    warehouse = CityWarehouse(tmp_path / "cities.sqlite3")
    run_pipeline(
        warehouse=warehouse,
        city_limit=40,
        export_dir=tmp_path / "exports",
    )

    oceania_cities = warehouse.list_metrics(region="Oceania", limit=50)
    australian_recommendations = warehouse.list_recommendations(country="Australia", limit=50)
    strong_recommendations = warehouse.list_recommendations(min_overall_score=60, limit=50)
    summary = warehouse.region_summary()

    assert oceania_cities
    assert all(city["region"] == "Oceania" for city in oceania_cities)
    assert australian_recommendations
    assert all(row["country"] == "Australia" for row in australian_recommendations)
    assert all(row["overall_score"] >= 60 for row in strong_recommendations)
    assert {row["region"] for row in summary}
