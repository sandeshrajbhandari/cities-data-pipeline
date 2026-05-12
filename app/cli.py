from __future__ import annotations

import argparse
import sys

from app.pipeline.config import get_settings
from app.pipeline.runner import run_pipeline
from app.pipeline.warehouse import CityWarehouse


def main() -> None:
    settings = get_settings()
    parser = argparse.ArgumentParser(description="Run the startup city data pipeline.")
    parser.add_argument("--limit", type=int, default=settings.default_city_limit)
    parser.add_argument(
        "--source",
        choices=["demo", "teleport"],
        default=settings.default_data_source,
        help="Data source to use. Use 'teleport' for live public urban-area scores.",
    )
    parser.add_argument("--no-export", action="store_true")
    args = parser.parse_args()

    warehouse = CityWarehouse(settings.database_path)
    try:
        metrics, recommendations, exports = run_pipeline(
            warehouse=warehouse,
            city_limit=args.limit,
            export_dir=None if args.no_export else settings.export_dir,
            source=args.source,
            teleport_api_base_url=settings.teleport_api_base_url,
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc

    print(f"Loaded {len(metrics)} metric rows from {args.source}")
    print(f"Built {len(recommendations)} recommendation rows")
    if recommendations:
        top = recommendations[0]
        print(f"Top city: {top.city}, {top.country} ({top.overall_score})")
    for name, path in exports.items():
        print(f"Exported {name}: {path}")


if __name__ == "__main__":
    main()
