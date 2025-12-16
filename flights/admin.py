from django.contrib import admin
from .models import *


"""Admin configuration for the flights app.

This module sets up how flight-related data like aircrafts, airports,
and flights appear in the Django admin panel.
"""



@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    """Settings for the Aircraft model in the admin page.

    Attributes:
        list_display: Fields to show in the list view (model, seats by class).
        search_fields: Fields that can be searched (model name).
    """
    list_display = ('model', 'economy_class', 'business_class', 'first_class')
    search_fields = ('model',)


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    """Settings for the Airport model in the admin page.

    Attributes:
        list_display: Fields to show in the list view (code, name, location).
        search_fields: Fields that can be searched (code, city).
    """
    list_display = ('airport_code', 'airport_name', 'city', 'country')
    search_fields = ('airport_code', 'city')

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    """Settings for the Flight model in the admin page.

    Attributes:
        list_display: Fields to show in the list view (flight info, locations, time).
        list_filter: Fields to filter the list by (airports).
    """
    list_display = ('flight_number', 'departure_airport', 'arrival_airport', 'departure_datetime', 'aircraft')
    list_filter = ('departure_airport', 'arrival_airport')