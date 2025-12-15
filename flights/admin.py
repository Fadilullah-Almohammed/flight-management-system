from django.contrib import admin
from .models import *



@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    list_display = ('model', 'economy_class', 'business_class', 'first_class')
    search_fields = ('model',)


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ('airport_code', 'airport_name', 'city', 'country')
    search_fields = ('airport_code', 'city')

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('flight_number', 'departure_airport', 'arrival_airport', 'departure_datetime', 'aircraft')
    list_filter = ('departure_airport', 'arrival_airport')