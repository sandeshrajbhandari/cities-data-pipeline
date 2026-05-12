from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class CityProfile(BaseModel):
    city: str
    country: str
    region: str
    population_millions: float = Field(ge=0)
    timezone: str


class CityMetric(BaseModel):
    city: str
    country: str
    region: str
    cost_of_living_index: float = Field(ge=0, le=150)
    rent_index: float = Field(ge=0, le=150)
    groceries_index: float = Field(ge=0, le=150)
    restaurant_price_index: float = Field(ge=0, le=150)
    purchasing_power_index: float = Field(ge=0, le=180)
    quality_of_life_index: float = Field(ge=0, le=220)
    safety_index: float = Field(ge=0, le=100)
    healthcare_index: float = Field(ge=0, le=100)
    climate_index: float = Field(ge=0, le=100)
    internet_speed_mbps: float = Field(ge=0)
    startup_score: float = Field(ge=0, le=100)
    remote_work_score: float = Field(ge=0, le=100)
    scraped_at: datetime
    source: Literal["demo_collector", "html_scraper", "teleport_api"] = "demo_collector"


class CityRecommendation(BaseModel):
    city: str
    country: str
    affordability_score: float
    livability_score: float
    opportunity_score: float
    overall_score: float
