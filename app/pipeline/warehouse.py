from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

from app.pipeline.models import CityMetric, CityRecommendation


METRIC_COLUMNS = tuple(CityMetric.model_fields.keys())
RECOMMENDATION_COLUMNS = tuple(CityRecommendation.model_fields.keys())


class CityWarehouse:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS city_metrics (
                    city TEXT NOT NULL,
                    country TEXT NOT NULL,
                    region TEXT NOT NULL,
                    cost_of_living_index REAL NOT NULL,
                    rent_index REAL NOT NULL,
                    groceries_index REAL NOT NULL,
                    restaurant_price_index REAL NOT NULL,
                    purchasing_power_index REAL NOT NULL,
                    quality_of_life_index REAL NOT NULL,
                    safety_index REAL NOT NULL,
                    healthcare_index REAL NOT NULL,
                    climate_index REAL NOT NULL,
                    internet_speed_mbps REAL NOT NULL,
                    startup_score REAL NOT NULL,
                    remote_work_score REAL NOT NULL,
                    scraped_at TEXT NOT NULL,
                    source TEXT NOT NULL,
                    PRIMARY KEY (city, country, scraped_at)
                );

                CREATE TABLE IF NOT EXISTS city_recommendations (
                    city TEXT NOT NULL,
                    country TEXT NOT NULL,
                    affordability_score REAL NOT NULL,
                    livability_score REAL NOT NULL,
                    opportunity_score REAL NOT NULL,
                    overall_score REAL NOT NULL,
                    PRIMARY KEY (city, country)
                );
                """
            )

    def replace_metrics(self, metrics: list[CityMetric]) -> None:
        self.initialize()
        values = [metric.model_dump(mode="json") for metric in metrics]
        placeholders = ", ".join([f":{column}" for column in METRIC_COLUMNS])
        with self.connect() as connection:
            connection.execute("DELETE FROM city_metrics")
            connection.executemany(
                f"INSERT INTO city_metrics ({', '.join(METRIC_COLUMNS)}) VALUES ({placeholders})",
                values,
            )

    def replace_recommendations(self, recommendations: list[CityRecommendation]) -> None:
        self.initialize()
        values = [recommendation.model_dump(mode="json") for recommendation in recommendations]
        placeholders = ", ".join([f":{column}" for column in RECOMMENDATION_COLUMNS])
        with self.connect() as connection:
            connection.execute("DELETE FROM city_recommendations")
            connection.executemany(
                "INSERT INTO city_recommendations "
                f"({', '.join(RECOMMENDATION_COLUMNS)}) VALUES ({placeholders})",
                values,
            )

    def list_metrics(self, limit: int = 50) -> list[dict]:
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM city_metrics
                ORDER BY remote_work_score DESC, startup_score DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def list_recommendations(self, limit: int = 25) -> list[dict]:
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM city_recommendations
                ORDER BY overall_score DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def export_tables(self, export_dir: Path) -> dict[str, Path]:
        export_dir.mkdir(parents=True, exist_ok=True)
        outputs = {
            "city_metrics": export_dir / "city_metrics.csv",
            "city_recommendations": export_dir / "city_recommendations.csv",
        }
        with self.connect() as connection:
            for table, path in outputs.items():
                rows = connection.execute(f"SELECT * FROM {table}").fetchall()
                if not rows:
                    path.write_text("", encoding="utf-8")
                    continue
                with path.open("w", newline="", encoding="utf-8") as file:
                    writer = csv.DictWriter(file, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(dict(row) for row in rows)
        return outputs
