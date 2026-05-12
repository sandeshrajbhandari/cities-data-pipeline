from urllib.parse import urlparse

import httpx

from app.pipeline.collector import collect_teleport_metrics
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


def test_collect_teleport_metrics_maps_live_scores(monkeypatch):
    responses = {
        "/api/urban_areas/": {
            "_links": {
                "ua:item": [
                    {
                        "name": "Melbourne",
                        "href": "https://api.teleport.org/api/urban_areas/slug:melbourne/",
                    }
                ]
            }
        },
        "/api/urban_areas/slug:melbourne/": {
            "_links": {"ua:countries": [{"name": "Australia"}]}
        },
        "/api/urban_areas/slug:melbourne/scores/": {
            "teleport_city_score": 72.5,
            "categories": [
                {"name": "Housing", "score_out_of_10": 5.2},
                {"name": "Cost of Living", "score_out_of_10": 6.1},
                {"name": "Startups", "score_out_of_10": 7.0},
                {"name": "Venture Capital", "score_out_of_10": 6.5},
                {"name": "Business Freedom", "score_out_of_10": 8.0},
                {"name": "Safety", "score_out_of_10": 7.8},
                {"name": "Healthcare", "score_out_of_10": 8.2},
                {"name": "Environmental Quality", "score_out_of_10": 7.1},
                {"name": "Economy", "score_out_of_10": 6.4},
                {"name": "Internet Access", "score_out_of_10": 8.8},
            ],
        },
    }

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def get(self, url):
            path = urlparse(url).path
            return httpx.Response(200, json=responses[path], request=httpx.Request("GET", url))

    monkeypatch.setattr("app.pipeline.collector.httpx.Client", FakeClient)

    metrics = collect_teleport_metrics(limit=1)

    assert len(metrics) == 1
    assert metrics[0].city == "Melbourne"
    assert metrics[0].country == "Australia"
    assert metrics[0].region == "Oceania"
    assert metrics[0].source == "teleport_api"
    assert metrics[0].startup_score == 71.67
