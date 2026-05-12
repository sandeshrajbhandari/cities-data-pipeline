from __future__ import annotations

import argparse

from app.pipeline.config import get_settings
from app.pipeline.runner import run_pipeline
from app.pipeline.warehouse import CityWarehouse


def main() -> None:
    settings = get_settings()
    parser = argparse.ArgumentParser(description="Run the startup city data pipeline.")
    parser.add_argument("--limit", type=int, default=settings.default_city_limit)
    parser.add_argument("--no-export", action="store_true")
    args = parser.parse_args()

    warehouse = CityWarehouse(settings.database_path)
    metrics, recommendations, exports = run_pipeline(
        warehouse=warehouse,
        city_limit=args.limit,
        export_dir=None if args.no_export else settings.export_dir,
    )

    print(f"Loaded {len(metrics)} metric rows")
    print(f"Built {len(recommendations)} recommendation rows")
    if recommendations:
        top = recommendations[0]
        print(f"Top city: {top.city}, {top.country} ({top.overall_score})")
    for name, path in exports.items():
        print(f"Exported {name}: {path}")


if __name__ == "__main__":
    main()
