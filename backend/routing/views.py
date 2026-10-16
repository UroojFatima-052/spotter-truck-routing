import requests
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .services.tomtom import geocode


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