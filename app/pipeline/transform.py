from __future__ import annotations

from app.pipeline.models import CityMetric, CityRecommendation


def _clamp(value: float, low: float = 0, high: float = 100) -> float:
    return round(max(low, min(high, value)), 2)


def build_recommendations(metrics: list[CityMetric]) -> list[CityRecommendation]:
    recommendations: list[CityRecommendation] = []
    for metric in metrics:
        affordability = _clamp(
            ((130 - metric.cost_of_living_index) / 130 * 45)
            + ((130 - metric.rent_index) / 130 * 35)
            + (metric.purchasing_power_index / 180 * 20)
        )
        livability = _clamp(
            (metric.quality_of_life_index / 220 * 35)
            + (metric.safety_index / 100 * 25)
            + (metric.healthcare_index / 100 * 20)
            + (metric.climate_index / 100 * 20)
        )
        opportunity = _clamp(
            (metric.startup_score * 0.55)
            + (metric.remote_work_score * 0.25)
            + (metric.internet_speed_mbps / 260 * 20)
        )
        overall = _clamp((affordability * 0.35) + (livability * 0.35) + (opportunity * 0.30))
        recommendations.append(
            CityRecommendation(
                city=metric.city,
                country=metric.country,
                affordability_score=affordability,
                livability_score=livability,
                opportunity_score=opportunity,
                overall_score=overall,
            )
        )
    return sorted(recommendations, key=lambda item: item.overall_score, reverse=True)
