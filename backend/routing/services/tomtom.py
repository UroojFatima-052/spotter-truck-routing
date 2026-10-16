from urllib.parse import quote

import requests
from django.conf import settings

BASE_URL = "https://api.tomtom.com"
KG_PER_LB = 0.453592
MILES_PER_METER = 0.000621371


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
    """Ask TomTom for up to 3 truck routes between two places."""
    locations = f"{origin['lat']},{origin['lon']}:{destination['lat']},{destination['lon']}"
    url = f"{BASE_URL}/routing/1/calculateRoute/{locations}/json"
    params = {
        "key": settings.TOMTOM_API_KEY,
        "travelMode": "truck",
        "vehicleCommercial": "true",
        "vehicleWeight": round(weight_lb * KG_PER_LB),
        "maxAlternatives": 2,
        "departAt": depart_at,
        "instructionsType": "coded",
    }
    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    routes = response.json().get("routes", [])
    if not routes:
        raise ValueError("No truck route found between these places")

    return [_simplify_route(index, route) for index, route in enumerate(routes)]


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