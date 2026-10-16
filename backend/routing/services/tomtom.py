from urllib.parse import quote

import requests
from django.conf import settings

BASE_URL = "https://api.tomtom.com"
KG_PER_LB = 0.453592
MILES_PER_METER = 0.000621371
ROUTES_WANTED = 3
DETOUR_SIZE = 0.15  # how far sideways the detour point goes, as a share of the trip


def geocode(query):
    """Turn a place name like 'Dallas, TX' into coordinates."""
    url = f"{BASE_URL}/search/2/geocode/{quote(query)}.json"
    params = {
        "key": settings.TOMTOM_API_KEY,
        "limit": 1,
        "countrySet": "US",
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    results = response.json().get("results", [])
    if not results:
        raise ValueError(f"Could not find a place called '{query}'")

    top = results[0]
    return {
        "name": top["address"]["freeformAddress"],
        "lat": top["position"]["lat"],
        "lon": top["position"]["lon"],
    }


def get_truck_routes(origin, destination, depart_at, weight_lb):
    """Get 3 different truck routes, using backups if TomTom gives fewer."""
    base_params = {
        "key": settings.TOMTOM_API_KEY,
        "travelMode": "truck",
        "vehicleCommercial": "true",
        "vehicleWeight": round(weight_lb * KG_PER_LB),
        "departAt": depart_at,
        "instructionsType": "coded",
    }

    # 1. Fastest route plus TomTom's own alternatives
    routes = _fetch_routes([origin, destination], {**base_params, "maxAlternatives": 2})
    if not routes:
        raise ValueError("No truck route found between these places")

    # 2. Backup: try other route types
    for route_type in ("shortest", "eco"):
        if len(routes) >= ROUTES_WANTED:
            break
        extra = _fetch_optional([origin, destination], {**base_params, "routeType": route_type})
        _add_new_routes(routes, extra)

    # 3. Last backup: force a detour through a side point
    if len(routes) < ROUTES_WANTED:
        via = _detour_point(origin, destination, routes[0])
        extra = _fetch_optional([origin, via, destination], base_params)
        _add_new_routes(routes, extra)

    return [_simplify_route(index, route) for index, route in enumerate(routes)]


def _fetch_routes(stops, params):
    """Call TomTom routing for a list of stops (start, optional via, end)."""
    locations = ":".join(f"{stop['lat']},{stop['lon']}" for stop in stops)
    url = f"{BASE_URL}/routing/1/calculateRoute/{locations}/json"
    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    return response.json().get("routes", [])


def _fetch_optional(stops, params):
    """Same as _fetch_routes, but a failed backup call shouldn't break everything."""
    try:
        return _fetch_routes(stops, params)
    except requests.RequestException:
        return []


def _add_new_routes(routes, candidates):
    """Add candidates that aren't copies of a route we already have."""
    for candidate in candidates:
        if len(routes) >= ROUTES_WANTED:
            return
        if not any(_is_same_route(candidate, existing) for existing in routes):
            routes.append(candidate)


def _is_same_route(route_a, route_b):
    """Treat two routes as the same if their lengths are within 1%."""
    length_a = route_a["summary"]["lengthInMeters"]
    length_b = route_b["summary"]["lengthInMeters"]
    return abs(length_a - length_b) / max(length_a, length_b) < 0.01


def _detour_point(origin, destination, main_route):
    """A point to the side of the main route's middle, to force a different road."""
    points = [point for leg in main_route["legs"] for point in leg["points"]]
    middle = points[len(points) // 2]

    # Direction of the trip, turned 90 degrees, gives the "sideways" direction
    lat_change = destination["lat"] - origin["lat"]
    lon_change = destination["lon"] - origin["lon"]

    return {
        "lat": middle["latitude"] - lon_change * DETOUR_SIZE,
        "lon": middle["longitude"] + lat_change * DETOUR_SIZE,
    }


def _simplify_route(index, route):
    """Keep only the parts of TomTom's big response that we need."""
    summary = route["summary"]

    points = [
        [point["latitude"], point["longitude"]]
        for leg in route["legs"]
        for point in leg["points"]
    ]

    progress = [
        {
            "distance_m": step["routeOffsetInMeters"],
            "time_s": step["travelTimeInSeconds"],
        }
        for step in route.get("guidance", {}).get("instructions", [])
    ]

    return {
        "id": index,
        "distance_miles": round(summary["lengthInMeters"] * MILES_PER_METER, 1),
        "duration_s": summary["travelTimeInSeconds"],
        "departure_time": summary["departureTime"],
        "arrival_time": summary["arrivalTime"],
        "points": points,
        "progress": progress,
    }