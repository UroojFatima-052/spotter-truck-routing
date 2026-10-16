import requests
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .services.tomtom import geocode
from .services.tomtom import geocode, get_truck_routes

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

    summaries = [
        {
            "id": route["id"],
            "distance_miles": route["distance_miles"],
            "duration_hours": round(route["duration_s"] / 3600, 1),
            "arrival_time": route["arrival_time"],
            "point_count": len(route["points"]),
        }
        for route in routes
    ]
    return Response({"origin": origin, "destination": destination, "routes": summaries})
