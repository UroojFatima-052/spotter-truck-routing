from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

# Open-Meteo forecasts cover 7 days. The trip and the 48h heatmap must fit inside that window.
MAX_DAYS_AHEAD = 5


class TripRequestSerializer(serializers.Serializer):
    origin = serializers.CharField(max_length=200)
    destination = serializers.CharField(max_length=200)
    departure = serializers.DateTimeField()
    weight_lb = serializers.FloatField(min_value=1, max_value=200000)
    interval_miles = serializers.ChoiceField(choices=[10, 25, 50])

    def validate_departure(self, value):
        now = timezone.now()
        if value < now - timedelta(minutes=5):
            raise serializers.ValidationError("Departure time must be in the future.")
        if value > now + timedelta(days=MAX_DAYS_AHEAD):
            raise serializers.ValidationError(
                f"Weather forecasts only reach 7 days ahead, so please pick a departure within {MAX_DAYS_AHEAD} days."
            )
        return value

    def validate(self, data):
        if data["origin"].strip().lower() == data["destination"].strip().lower():
            raise serializers.ValidationError(
                {"destination": "Origin and destination are the same. Please pick two different places."}
            )
        return data


class HeatmapRequestSerializer(serializers.Serializer):
    points = serializers.ListField(
        child=serializers.ListField(child=serializers.FloatField(), min_length=2, max_length=2),
        min_length=1,
        max_length=2000,
    )
    departure = serializers.DateTimeField()
    weight_lb = serializers.FloatField(min_value=1, max_value=200000)