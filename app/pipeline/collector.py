from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import Any

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


def _score_map(categories: list[dict[str, Any]]) -> dict[str, float]:
    return {
        category["name"]: float(category.get("score_out_of_10") or 0)
        for category in categories
        if category.get("name")
    }


def _score(scores: dict[str, float], name: str, default: float = 5) -> float:
    return scores.get(name, default)


def _category_to_positive_index(score_out_of_10: float, high: float = 100) -> float:
    return round(max(0, min(high, score_out_of_10 * (high / 10))), 2)


def _category_to_cost_index(score_out_of_10: float) -> float:
    return round(max(0, min(130, 130 - (score_out_of_10 * 10))), 2)


def _city_slug_from_href(href: str) -> str:
    marker = "/slug:"
    if marker in href:
        return href.split(marker, 1)[1].strip("/").split("/", 1)[0]
    return href.rstrip("/").rsplit("/", 1)[-1]


def _fallback_region(country: str) -> str:
    regions = {
        "Australia": "Oceania",
        "New Zealand": "Oceania",
        "United States": "North America",
        "Canada": "North America",
        "Mexico": "North America",
        "Brazil": "South America",
        "Argentina": "South America",
        "Chile": "South America",
        "Colombia": "South America",
        "Peru": "South America",
        "United Kingdom": "Europe",
        "Germany": "Europe",
        "France": "Europe",
        "Spain": "Europe",
        "Portugal": "Europe",
        "Netherlands": "Europe",
        "Ireland": "Europe",
        "Japan": "Asia",
        "South Korea": "Asia",
        "Singapore": "Asia",
        "Thailand": "Asia",
        "India": "Asia",
        "United Arab Emirates": "Asia",
        "South Africa": "Africa",
        "Kenya": "Africa",
        "Egypt": "Africa",
    }
    return regions.get(country, "Unknown")


def _extract_country(urban_area_payload: dict[str, Any]) -> str:
    countries = urban_area_payload.get("_links", {}).get("ua:countries", [])
    if countries:
        return countries[0].get("name") or "Unknown"
    return "Unknown"


def collect_teleport_metrics(
    limit: int,
    base_url: str = "https://api.teleport.org/api",
    timeout_seconds: float = 20,
) -> list[CityMetric]:
    """Collect live city quality metrics from Teleport's public urban areas API."""
    base_url = base_url.rstrip("/")
    scraped_at = datetime.now(UTC)
    metrics: list[CityMetric] = []

    try:
        with httpx.Client(timeout=timeout_seconds, follow_redirects=True) as client:
            urban_areas = client.get(f"{base_url}/urban_areas/").raise_for_status().json()
            items = urban_areas.get("_links", {}).get("ua:item", [])[:limit]

            for item in items:
                name = item["name"]
                href = item["href"]
                slug = _city_slug_from_href(href)
                details = client.get(f"{base_url}/urban_areas/slug:{slug}/").raise_for_status().json()
                score_payload = (
                    client.get(f"{base_url}/urban_areas/slug:{slug}/scores/")
                    .raise_for_status()
                    .json()
                )
                scores = _score_map(score_payload.get("categories", []))
                country = _extract_country(details)
                quality_score = float(score_payload.get("teleport_city_score") or 50)
                internet_score = _score(scores, "Internet Access")
                startup_score = round(
                    (
                        _score(scores, "Startups")
                        + _score(scores, "Venture Capital")
                        + _score(scores, "Business Freedom")
                    )
                    / 3
                    * 10,
                    2,
                )
                cost_index = _category_to_cost_index(_score(scores, "Cost of Living"))
                rent_index = _category_to_cost_index(_score(scores, "Housing"))
                safety_index = _category_to_positive_index(_score(scores, "Safety"))
                healthcare_index = _category_to_positive_index(_score(scores, "Healthcare"))
                climate_index = _category_to_positive_index(_score(scores, "Environmental Quality"))
                remote_work_score = round(
                    ((130 - cost_index) / 130 * 30)
                    + (quality_score / 100 * 25)
                    + (internet_score / 10 * 25)
                    + (safety_index / 100 * 20),
                    2,
                )

                metrics.append(
                    CityMetric(
                        city=name,
                        country=country,
                        region=_fallback_region(country),
                        cost_of_living_index=cost_index,
                        rent_index=rent_index,
                        groceries_index=cost_index,
                        restaurant_price_index=cost_index,
                        purchasing_power_index=_category_to_positive_index(
                            _score(scores, "Economy"), 180
                        ),
                        quality_of_life_index=round(quality_score * 2.2, 2),
                        safety_index=safety_index,
                        healthcare_index=healthcare_index,
                        climate_index=climate_index,
                        internet_speed_mbps=round(internet_score * 25, 2),
                        startup_score=min(startup_score, 100),
                        remote_work_score=min(remote_work_score, 100),
                        scraped_at=scraped_at,
                        source="teleport_api",
                    )
                )
    except httpx.HTTPError as exc:
        raise RuntimeError(f"Teleport API request failed: {exc}") from exc

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
