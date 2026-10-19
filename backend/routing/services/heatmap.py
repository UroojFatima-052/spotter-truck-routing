from datetime import timedelta, timezone

from .checkpoints import distance_miles
from .risk import classify
from .weather import get_forecasts, round_location, weather_at

HOURS_AHEAD = 48
GRID_CELLS_ACROSS = 20
MIN_STEP_DEGREES = 0.25
PADDING_DEGREES = 0.5
CORRIDOR_MILES = 60
MAX_CELLS = 200


def build_heatmap(route_points, departure, weight_lb):
    """Risk for a grid of squares around the trip, for every hour 0 to 48."""
    cells, step = _corridor_cells(route_points)
    forecasts = get_forecasts(cells)

    start = departure.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)
    hours = [start + timedelta(hours=h) for h in range(HOURS_AHEAD + 1)]

    risk, wind, rain, snow = [], [], [], []
    for hour in hours:
        hour_risk, hour_wind, hour_rain, hour_snow = [], [], [], []
        for cell in cells:
            weather = weather_at(forecasts[cell], hour)
            hour_risk.append(classify(weather, weight_lb)["score"])
            hour_wind.append(weather["wind_mph"] if weather else None)
            hour_rain.append(weather["rain_in"] if weather else None)
            hour_snow.append(weather["snow_in"] if weather else None)
        risk.append(hour_risk)
        wind.append(hour_wind)
        rain.append(hour_rain)
        snow.append(hour_snow)

    return {
        "cells": [[lat, lon] for lat, lon in cells],
        "cell_size": round(step, 4),
        "hours": [hour.isoformat() for hour in hours],
        "risk": risk,
        "wind": wind,
        "rain": rain,
        "snow": snow,
    }


def _corridor_cells(route_points):
    """Grid squares that are within CORRIDOR_MILES of any route point."""
    lats = [point[0] for point in route_points]
    lons = [point[1] for point in route_points]
    south, north = min(lats) - PADDING_DEGREES, max(lats) + PADDING_DEGREES
    west, east = min(lons) - PADDING_DEGREES, max(lons) + PADDING_DEGREES

    step = max(MIN_STEP_DEGREES, max(north - south, east - west) / GRID_CELLS_ACROSS)

    while True:
        cells = []
        lat = south
        while lat <= north:
            lon = west
            while lon <= east:
                if _near_route((lat, lon), route_points):
                    cells.append(round_location(lat, lon))
                lon += step
            lat += step

        if len(cells) <= MAX_CELLS:
            return cells, step
        step *= 1.25  # too many squares, make them bigger and try again


def _near_route(cell, route_points):
    return any(distance_miles(cell, point) <= CORRIDOR_MILES for point in route_points)