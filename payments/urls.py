"""URL configuration for the payments application.

This module handles URL routing for payment processing views, specifically
initiating payments for confirmed bookings.
"""
from django.urls import path
from . import views


urlpatterns = [
    path('process-payment/<int:booking_id>', views.process_payment, name='process_payment'),
]