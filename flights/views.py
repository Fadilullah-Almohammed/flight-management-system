from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def admin_view_reports(request):

    return render(request, 'flights/reports.html')

@login_required
def add_new_flight(request):
    return render(request, 'flights/add_new_flight.html')

@login_required
def view_flights(request):
    return render(request, 'flights/view_flights.html')

@login_required
def flight_management(request):

    return render(request, 'flights/flights_management.html')