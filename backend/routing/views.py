import logging

import requests
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import HeatmapRequestSerializer, TripRequestSerializer
from .services.heatmap import build_heatmap
from .services.tomtom import geocode
from .services.trip import plan_trip

logger = logging.getLogger(__name__)


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
        logger.exception("Geocoding failed for %r", query)
        return Response({"error": "Location service is unavailable"}, status=status.HTTP_502_BAD_GATEWAY)

    return Response(place)


@api_view(["POST"])
def trip(request):
    serializer = TripRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        result = plan_trip(**serializer.validated_data)
    except ValueError as error:
        return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
    except requests.RequestException:
        logger.exception("External service failed while planning a trip")
        return Response(
            {"error": "A map or weather service is unavailable. Please try again."},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    except Exception:
        logger.exception("Unexpected error while planning a trip")
        return Response(
            {"error": "Something unexpected went wrong while planning this trip. Please try different places."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(result)


@api_view(["POST"])
def heatmap(request):
    serializer = HeatmapRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        result = build_heatmap(
            serializer.validated_data["points"],
            serializer.validated_data["departure"],
            serializer.validated_data["weight_lb"],
        )
    except requests.RequestException:
        logger.exception("Weather service failed while building the heatmap")
        return Response({"error": "Weather service is unavailable"}, status=status.HTTP_502_BAD_GATEWAY)
    except Exception:
        logger.exception("Unexpected error while building the heatmap")
        return Response({"error": "Could not build the weather forecast"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(result)