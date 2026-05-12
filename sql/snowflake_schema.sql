CREATE SCHEMA IF NOT EXISTS startup_city;

CREATE OR REPLACE TABLE startup_city.city_metrics (
    city STRING NOT NULL,
    country STRING NOT NULL,
    region STRING NOT NULL,
    cost_of_living_index NUMBER(8, 2) NOT NULL,
    rent_index NUMBER(8, 2) NOT NULL,
    groceries_index NUMBER(8, 2) NOT NULL,
    restaurant_price_index NUMBER(8, 2) NOT NULL,
    purchasing_power_index NUMBER(8, 2) NOT NULL,
    quality_of_life_index NUMBER(8, 2) NOT NULL,
    safety_index NUMBER(8, 2) NOT NULL,
    healthcare_index NUMBER(8, 2) NOT NULL,
    climate_index NUMBER(8, 2) NOT NULL,
    internet_speed_mbps NUMBER(8, 2) NOT NULL,
    startup_score NUMBER(8, 2) NOT NULL,
    remote_work_score NUMBER(8, 2) NOT NULL,
    scraped_at TIMESTAMP_TZ NOT NULL,
    source STRING NOT NULL
);

CREATE OR REPLACE TABLE startup_city.city_recommendations (
    city STRING NOT NULL,
    country STRING NOT NULL,
    affordability_score NUMBER(8, 2) NOT NULL,
    livability_score NUMBER(8, 2) NOT NULL,
    opportunity_score NUMBER(8, 2) NOT NULL,
    overall_score NUMBER(8, 2) NOT NULL
);

CREATE OR REPLACE VIEW startup_city.region_summary AS
SELECT
    metrics.region,
    COUNT(*) AS city_count,
    ROUND(AVG(metrics.cost_of_living_index), 2) AS avg_cost_of_living_index,
    ROUND(AVG(metrics.quality_of_life_index), 2) AS avg_quality_of_life_index,
    ROUND(AVG(metrics.internet_speed_mbps), 2) AS avg_internet_speed_mbps,
    ROUND(AVG(metrics.remote_work_score), 2) AS avg_remote_work_score,
    ROUND(AVG(recommendations.overall_score), 2) AS avg_overall_score
FROM startup_city.city_metrics metrics
JOIN startup_city.city_recommendations recommendations
    ON recommendations.city = metrics.city
    AND recommendations.country = metrics.country
GROUP BY metrics.region;
