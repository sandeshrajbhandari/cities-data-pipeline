# Power BI Model

Import these CSV files after running the pipeline:

- `exports/city_metrics.csv`
- `exports/city_recommendations.csv`

Join keys:

- `city_metrics.city` to `city_recommendations.city`
- `city_metrics.country` to `city_recommendations.country`

Recommended visuals:

- Bar chart: top 20 cities by `overall_score`
- Scatter: `cost_of_living_index` vs `quality_of_life_index`, sized by `startup_score`
- Map: city/country colored by `remote_work_score`
- Matrix: region averages for affordability, livability, opportunity, and overall score

Useful DAX measures:

```DAX
Average Overall Score = AVERAGE(city_recommendations[overall_score])
Average Remote Work Score = AVERAGE(city_metrics[remote_work_score])
Average Cost Index = AVERAGE(city_metrics[cost_of_living_index])
City Count = DISTINCTCOUNT(city_metrics[city])
```
