from __future__ import annotations

import hashlib
from datetime import UTC, datetime

from bs4 import BeautifulSoup
import httpx

from app.pipeline.models import CityMetric, CityProfile


def _bounded_score(seed: str, low: float, high: float) -> float:
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    value = int(digest[:8], 16) / 0xFFFFFFFF
    return round(low + (high - low) * value, 2)


def collect_demo_metrics(cities: list[CityProfile]) -> list[CityMetric]:
    metrics: list[CityMetric] = []
    scraped_at = datetime.now(UTC)

    for city in cities:
        population_weight = min(city.population_millions / 12, 1)
        cost = _bounded_score(f"{city.city}:cost", 35, 115)
        rent = _bounded_score(f"{city.city}:rent", 20, 120)
        groceries = _bounded_score(f"{city.city}:groceries", 30, 115)
        restaurant = _bounded_score(f"{city.city}:restaurant", 25, 120)
        purchasing = _bounded_score(f"{city.country}:purchasing", 45, 150)
        quality = _bounded_score(f"{city.city}:quality", 85, 195)
        safety = _bounded_score(f"{city.city}:safety", 35, 92)
        healthcare = _bounded_score(f"{city.country}:health", 40, 96)
        climate = _bounded_score(f"{city.city}:climate", 45, 98)
        internet = _bounded_score(f"{city.country}:internet", 35, 260)
        startup = round(
            (population_weight * 35)
            + (_bounded_score(f"{city.city}:startup", 20, 95) * 0.45)
            + (internet / 260 * 20),
            2,
        )
        remote = round(
            ((150 - cost) / 150 * 30)
            + (quality / 220 * 30)
            + (safety / 100 * 15)
            + (internet / 260 * 25),
            2,
        )

        metrics.append(
            CityMetric(
                city=city.city,
                country=city.country,
                region=city.region,
                cost_of_living_index=cost,
                rent_index=rent,
                groceries_index=groceries,
                restaurant_price_index=restaurant,
                purchasing_power_index=purchasing,
                quality_of_life_index=quality,
                safety_index=safety,
                healthcare_index=healthcare,
                climate_index=climate,
                internet_speed_mbps=internet,
                startup_score=min(startup, 100),
                remote_work_score=min(remote, 100),
                scraped_at=scraped_at,
            )
        )

    return metrics


async def scrape_city_metric_page(url: str) -> dict[str, str]:
    """Small generic HTML scraper for metric pages with label/value tables."""
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(url)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select("tr")
    metrics: dict[str, str] = {}
    for row in rows:
        cells = [cell.get_text(" ", strip=True) for cell in row.select("td, th")]
        if len(cells) >= 2:
            metrics[cells[0].strip(": ")] = cells[1]
    return metrics
