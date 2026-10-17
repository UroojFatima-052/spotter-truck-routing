from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers


class TripRequestSerializer(serializers.Serializer):
    origin = serializers.CharField(max_length=200)
    destination = serializers.CharField(max_length=200)
    departure = serializers.DateTimeField()
    weight_lb = serializers.FloatField(min_value=1, max_value=200000)
    interval_miles = serializers.ChoiceField(choices=[10, 25, 50])

    def validate_departure(self, value):
        if value < timezone.now() - timedelta(minutes=5):
            raise serializers.ValidationError("Departure time must be in the future.")
        return value


class HeatmapRequestSerializer(serializers.Serializer):
    points = serializers.ListField(
        child=serializers.ListField(child=serializers.FloatField(), min_length=2, max_length=2),
        min_length=1,
        max_length=2000,
    )
    departure = serializers.DateTimeField()
    weight_lb = serializers.FloatField(min_value=1, max_value=200000)