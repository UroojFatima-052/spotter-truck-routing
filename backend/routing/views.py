import requests
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import TripRequestSerializer
from .services.tomtom import geocode
from .services.trip import plan_trip


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


@api_view(["POST"])
def trip(request):
    serializer = TripRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        result = plan_trip(**serializer.validated_data)
    except ValueError as error:
        return Response({"error": str(error)}, status=status.HTTP_404_NOT_FOUND)
    except requests.RequestException:
        return Response(
            {"error": "A map or weather service is unavailable. Please try again."},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    return Response(result)