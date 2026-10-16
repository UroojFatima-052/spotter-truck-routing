from datetime import datetime

import requests
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .services.checkpoints import build_checkpoints
from .services.tomtom import geocode, get_truck_routes
from .services.risk import classify
from .services.weather import get_forecasts, round_location, weather_at



@api_view(["GET"])
def health(request):
    return Response({"status": "ok"})


@api_view(["GET"])
def geocode_place(request):
    query = request.query_params.get("q", "").strip()
    if not query:
        return Response({"error": "Please provide a place with ?q="}, status=status.HTTP_400_BAD_REQUEST)

    try:
        place = geocode(query)
    except ValueError as error:
        return Response({"error": str(error)}, status=status.HTTP_404_NOT_FOUND)
    except requests.RequestException:
        return Response({"error": "Location service is unavailable"}, status=status.HTTP_502_BAD_GATEWAY)

    return Response(place)


@api_view(["GET"])
def truck_routes(request):
    origin_query = request.query_params.get("origin", "").strip()
    destination_query = request.query_params.get("destination", "").strip()

    try:
        weight_lb = float(request.query_params.get("weight", "0"))
    except ValueError:
        return Response({"error": "Weight must be a number"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        interval = int(request.query_params.get("interval", "25"))
    except ValueError:
        interval = 0
    if interval not in (10, 25, 50):
        return Response({"error": "Interval must be 10, 25 or 50"}, status=status.HTTP_400_BAD_REQUEST)

    if not origin_query or not destination_query:
        return Response({"error": "Please provide origin and destination"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        origin = geocode(origin_query)
        destination = geocode(destination_query)
        routes = get_truck_routes(origin, destination, "now", weight_lb)
    except ValueError as error:
        return Response({"error": str(error)}, status=status.HTTP_404_NOT_FOUND)
    except requests.RequestException:
        return Response({"error": "Routing service is unavailable"}, status=status.HTTP_502_BAD_GATEWAY)

    checkpoints_by_route = {route["id"]: build_checkpoints(route, interval) for route in routes}

    locations = [
        round_location(stop["lat"], stop["lon"])
        for stops in checkpoints_by_route.values()
        for stop in stops
    ]
    try:
        forecasts = get_forecasts(locations)
    except requests.RequestException:
        return Response({"error": "Weather service is unavailable"}, status=status.HTTP_502_BAD_GATEWAY)

    for stops in checkpoints_by_route.values():
        for stop in stops:
            forecast = forecasts[round_location(stop["lat"], stop["lon"])]
            stop["weather"] = weather_at(forecast, datetime.fromisoformat(stop["eta"]))
            stop["risk"] = classify(stop["weather"], weight_lb)

    summaries = []
    for route in routes:
        checkpoints = checkpoints_by_route[route["id"]]
        summaries.append({
            "id": route["id"],
            "distance_miles": route["distance_miles"],
            "duration_hours": round(route["duration_s"] / 3600, 1),
            "arrival_time": route["arrival_time"],
            "checkpoint_count": len(checkpoints),
            "first_checkpoints": checkpoints[:3],
            "last_checkpoint": checkpoints[-1],
        })
    return Response({"origin": origin, "destination": destination, "routes": summaries})