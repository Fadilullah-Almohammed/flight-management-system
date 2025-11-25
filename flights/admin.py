from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    # This controls what columns you see in the list view
    list_display = ('model', 'economy_class', 'business_class', 'first_class')
    # This allows you to search by model name
    search_fields = ('model',)


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ('airport_code', 'airport_name', 'city', 'country')
    search_fields = ('airport_code', 'city')

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('flight_number', 'departure_airport', 'arrival_airport', 'departure_datetime', 'aircraft')
    list_filter = ('departure_airport', 'arrival_airport')