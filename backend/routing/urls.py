from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.health, name="health"),
    path("geocode/", views.geocode_place, name="geocode"),
    path("trip/", views.trip, name="trip"),
]