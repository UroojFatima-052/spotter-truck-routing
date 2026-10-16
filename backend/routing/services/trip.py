from datetime import datetime

from django.utils import timezone

from .checkpoints import build_checkpoints
from .risk import classify
from .scoring import rank_routes, summarize_risk
from .tomtom import geocode, get_truck_routes
from .weather import get_forecasts, round_location, weather_at

MAX_MAP_POINTS = 1500


def plan_trip(origin, destination, departure, weight_lb, interval_miles):
    """Run the whole trip: places, routes, stops, weather, risk, best route."""
    origin_place = geocode(origin)
    destination_place = geocode(destination)

    depart_at = "now" if departure <= timezone.now() else departure.replace(microsecond=0).isoformat()
    routes = get_truck_routes(origin_place, destination_place, depart_at, weight_lb)

    checkpoints_by_route = {route["id"]: build_checkpoints(route, interval_miles) for route in routes}
    _add_weather_and_risk(checkpoints_by_route, weight_lb)

    for route in routes:
        route["risk_summary"] = summarize_risk(checkpoints_by_route[route["id"]])

    ranked = rank_routes(routes)
    recommended_id = ranked[0]["id"]

    return {
        "origin": origin_place,
        "destination": destination_place,
        "departure": departure.isoformat(),
        "weight_lb": weight_lb,
        "interval_miles": interval_miles,
        "recommended_route_id": recommended_id,
        "routes": [
            _route_result(route, checkpoints_by_route[route["id"]], recommended_id)
            for route in ranked
        ],
    }


def _add_weather_and_risk(checkpoints_by_route, weight_lb):
    """Fetch weather for every stop in one go, then label each stop's risk."""
    all_stops = [stop for stops in checkpoints_by_route.values() for stop in stops]
    forecasts = get_forecasts([round_location(stop["lat"], stop["lon"]) for stop in all_stops])

    for stop in all_stops:
        forecast = forecasts[round_location(stop["lat"], stop["lon"])]
        stop["weather"] = weather_at(forecast, datetime.fromisoformat(stop["eta"]))
        stop["risk"] = classify(stop["weather"], weight_lb)


def _route_result(route, checkpoints, recommended_id):
    """What the frontend gets for one route."""
    return {
        "id": route["id"],
        "recommended": route["id"] == recommended_id,
        "distance_miles": route["distance_miles"],
        "duration_s": route["duration_s"],
        "departure_time": route["departure_time"],
        "arrival_time": route["arrival_time"],
        "risk_summary": route["risk_summary"],
        "points": _thin_points(route["points"]),
        "checkpoints": checkpoints,
    }


def _thin_points(points):
    """Keep about MAX_MAP_POINTS points so the map line draws fast."""
    step = max(1, len(points) // MAX_MAP_POINTS)
    thinned = points[::step]
    if thinned[-1] != points[-1]:
        thinned.append(points[-1])
    return thinned