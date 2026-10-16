from datetime import timedelta

import requests
from django.core.cache import cache

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
BATCH_SIZE = 50
CACHE_SECONDS = 30 * 60
FORECAST_DAYS = 7


def round_location(lat, lon):
    """Round to about 1 km so nearby points share one forecast."""
    return round(lat, 2), round(lon, 2)


def get_forecasts(locations):
    """Hourly forecasts for many (lat, lon) locations, using the cache when we can."""
    unique = list(dict.fromkeys(locations))
    forecasts = {}
    missing = []

    for location in unique:
        cached = cache.get(_cache_key(location))
        if cached:
            forecasts[location] = cached
        else:
            missing.append(location)

    for start in range(0, len(missing), BATCH_SIZE):
        batch = missing[start:start + BATCH_SIZE]
        for location, forecast in zip(batch, _fetch_batch(batch)):
            forecasts[location] = forecast
            cache.set(_cache_key(location), forecast, CACHE_SECONDS)

    return forecasts


def weather_at(forecast, when):
    """Wind, rain and snow at the forecast hour closest to `when` (a UTC datetime)."""
    nearest_hour = (when + timedelta(minutes=30)).replace(minute=0, second=0, microsecond=0)
    key = nearest_hour.strftime("%Y-%m-%dT%H:%M")

    try:
        i = forecast["times"].index(key)
    except ValueError:
        return None  # ETA is outside the forecast range

    return {
        "wind_mph": round(forecast["wind"][i], 1),
        "rain_in": round(forecast["rain"][i], 2),
        "snow_in": round(forecast["snow"][i], 2),
    }


def _cache_key(location):
    lat, lon = location
    return f"weather:{lat}:{lon}"


def _fetch_batch(batch):
    """One Open-Meteo call for up to 50 locations."""
    params = {
        "latitude": ",".join(str(lat) for lat, _ in batch),
        "longitude": ",".join(str(lon) for _, lon in batch),
        "hourly": "wind_speed_10m,rain,showers,snowfall",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "timezone": "GMT",
        "forecast_days": FORECAST_DAYS,
    }
    response = requests.get(FORECAST_URL, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()
    if isinstance(data, dict):  # one location comes back as a dict, many as a list
        data = [data]
    return [_simplify(item["hourly"]) for item in data]


def _simplify(hourly):
    """Keep just the hourly numbers we need. Missing values count as 0."""
    rain = [(r or 0) + (s or 0) for r, s in zip(hourly["rain"], hourly["showers"])]
    return {
        "times": hourly["time"],
        "wind": [w or 0 for w in hourly["wind_speed_10m"]],
        "rain": rain,
        "snow": [s or 0 for s in hourly["snowfall"]],
    }