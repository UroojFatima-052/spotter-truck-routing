from urllib.parse import quote

import requests
from django.conf import settings

BASE_URL = "https://api.tomtom.com"


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