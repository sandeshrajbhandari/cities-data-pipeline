from __future__ import annotations

from itertools import cycle

from app.pipeline.models import CityProfile


BASE_CITIES: tuple[tuple[str, str, str, str, float], ...] = (
    ("Hobart", "Australia", "Oceania", "Australia/Hobart", 0.25),
    ("Melbourne", "Australia", "Oceania", "Australia/Melbourne", 5.2),
    ("Sydney", "Australia", "Oceania", "Australia/Sydney", 5.3),
    ("Brisbane", "Australia", "Oceania", "Australia/Brisbane", 2.7),
    ("Adelaide", "Australia", "Oceania", "Australia/Adelaide", 1.4),
    ("Perth", "Australia", "Oceania", "Australia/Perth", 2.2),
    ("Auckland", "New Zealand", "Oceania", "Pacific/Auckland", 1.7),
    ("Wellington", "New Zealand", "Oceania", "Pacific/Auckland", 0.4),
    ("Singapore", "Singapore", "Asia", "Asia/Singapore", 5.9),
    ("Tokyo", "Japan", "Asia", "Asia/Tokyo", 37.2),
    ("Osaka", "Japan", "Asia", "Asia/Tokyo", 19.0),
    ("Seoul", "South Korea", "Asia", "Asia/Seoul", 9.4),
    ("Taipei", "Taiwan", "Asia", "Asia/Taipei", 2.5),
    ("Hong Kong", "Hong Kong", "Asia", "Asia/Hong_Kong", 7.5),
    ("Bangkok", "Thailand", "Asia", "Asia/Bangkok", 10.7),
    ("Chiang Mai", "Thailand", "Asia", "Asia/Bangkok", 1.2),
    ("Kuala Lumpur", "Malaysia", "Asia", "Asia/Kuala_Lumpur", 8.8),
    ("Ho Chi Minh City", "Vietnam", "Asia", "Asia/Ho_Chi_Minh", 9.3),
    ("Hanoi", "Vietnam", "Asia", "Asia/Ho_Chi_Minh", 8.4),
    ("Manila", "Philippines", "Asia", "Asia/Manila", 14.7),
    ("Jakarta", "Indonesia", "Asia", "Asia/Jakarta", 11.4),
    ("Bali", "Indonesia", "Asia", "Asia/Makassar", 4.4),
    ("Bengaluru", "India", "Asia", "Asia/Kolkata", 13.6),
    ("Mumbai", "India", "Asia", "Asia/Kolkata", 21.7),
    ("Delhi", "India", "Asia", "Asia/Kolkata", 32.9),
    ("Kathmandu", "Nepal", "Asia", "Asia/Kathmandu", 1.6),
    ("Dubai", "United Arab Emirates", "Asia", "Asia/Dubai", 3.6),
    ("Tel Aviv", "Israel", "Asia", "Asia/Jerusalem", 4.3),
    ("London", "United Kingdom", "Europe", "Europe/London", 9.7),
    ("Manchester", "United Kingdom", "Europe", "Europe/London", 2.8),
    ("Dublin", "Ireland", "Europe", "Europe/Dublin", 1.3),
    ("Amsterdam", "Netherlands", "Europe", "Europe/Amsterdam", 1.2),
    ("Berlin", "Germany", "Europe", "Europe/Berlin", 3.6),
    ("Munich", "Germany", "Europe", "Europe/Berlin", 1.6),
    ("Paris", "France", "Europe", "Europe/Paris", 11.2),
    ("Barcelona", "Spain", "Europe", "Europe/Madrid", 5.7),
    ("Madrid", "Spain", "Europe", "Europe/Madrid", 6.8),
    ("Lisbon", "Portugal", "Europe", "Europe/Lisbon", 3.0),
    ("Porto", "Portugal", "Europe", "Europe/Lisbon", 1.7),
    ("Prague", "Czechia", "Europe", "Europe/Prague", 1.3),
    ("Warsaw", "Poland", "Europe", "Europe/Warsaw", 1.9),
    ("Krakow", "Poland", "Europe", "Europe/Warsaw", 0.8),
    ("Vienna", "Austria", "Europe", "Europe/Vienna", 2.0),
    ("Zurich", "Switzerland", "Europe", "Europe/Zurich", 1.4),
    ("Stockholm", "Sweden", "Europe", "Europe/Stockholm", 1.7),
    ("Copenhagen", "Denmark", "Europe", "Europe/Copenhagen", 1.4),
    ("Helsinki", "Finland", "Europe", "Europe/Helsinki", 1.3),
    ("Oslo", "Norway", "Europe", "Europe/Oslo", 1.1),
    ("Tallinn", "Estonia", "Europe", "Europe/Tallinn", 0.5),
    ("Riga", "Latvia", "Europe", "Europe/Riga", 0.6),
    ("Vilnius", "Lithuania", "Europe", "Europe/Vilnius", 0.6),
    ("Athens", "Greece", "Europe", "Europe/Athens", 3.2),
    ("Istanbul", "Turkey", "Europe", "Europe/Istanbul", 15.9),
    ("New York", "United States", "North America", "America/New_York", 18.8),
    ("San Francisco", "United States", "North America", "America/Los_Angeles", 3.3),
    ("Seattle", "United States", "North America", "America/Los_Angeles", 4.0),
    ("Austin", "United States", "North America", "America/Chicago", 2.3),
    ("Boston", "United States", "North America", "America/New_York", 4.9),
    ("Chicago", "United States", "North America", "America/Chicago", 8.9),
    ("Miami", "United States", "North America", "America/New_York", 6.1),
    ("Denver", "United States", "North America", "America/Denver", 3.0),
    ("Los Angeles", "United States", "North America", "America/Los_Angeles", 12.5),
    ("Portland", "United States", "North America", "America/Los_Angeles", 2.5),
    ("Toronto", "Canada", "North America", "America/Toronto", 6.8),
    ("Vancouver", "Canada", "North America", "America/Vancouver", 2.7),
    ("Montreal", "Canada", "North America", "America/Toronto", 4.3),
    ("Mexico City", "Mexico", "North America", "America/Mexico_City", 22.3),
    ("Guadalajara", "Mexico", "North America", "America/Mexico_City", 5.5),
    ("Medellin", "Colombia", "South America", "America/Bogota", 4.1),
    ("Bogota", "Colombia", "South America", "America/Bogota", 11.5),
    ("Lima", "Peru", "South America", "America/Lima", 11.2),
    ("Santiago", "Chile", "South America", "America/Santiago", 6.9),
    ("Buenos Aires", "Argentina", "South America", "America/Argentina/Buenos_Aires", 15.5),
    ("Montevideo", "Uruguay", "South America", "America/Montevideo", 1.8),
    ("Sao Paulo", "Brazil", "South America", "America/Sao_Paulo", 22.6),
    ("Rio de Janeiro", "Brazil", "South America", "America/Sao_Paulo", 13.7),
    ("Florianopolis", "Brazil", "South America", "America/Sao_Paulo", 1.3),
    ("Cape Town", "South Africa", "Africa", "Africa/Johannesburg", 4.9),
    ("Johannesburg", "South Africa", "Africa", "Africa/Johannesburg", 6.2),
    ("Nairobi", "Kenya", "Africa", "Africa/Nairobi", 5.3),
    ("Lagos", "Nigeria", "Africa", "Africa/Lagos", 15.9),
    ("Cairo", "Egypt", "Africa", "Africa/Cairo", 22.2),
    ("Marrakesh", "Morocco", "Africa", "Africa/Casablanca", 1.0),
)


def get_city_catalog(limit: int = 220) -> list[CityProfile]:
    cities: list[CityProfile] = []
    for index, (city, country, region, timezone, population) in enumerate(cycle(BASE_CITIES), start=1):
        if len(cities) >= limit:
            break
        suffix = "" if index <= len(BASE_CITIES) else f" Metro {index - len(BASE_CITIES)}"
        cities.append(
            CityProfile(
                city=f"{city}{suffix}",
                country=country,
                region=region,
                timezone=timezone,
                population_millions=population,
            )
        )
    return cities
