"""Root URL configuration for the Flight Management System project.

This module defines the top-level URL routing for the entire application.
It includes specific route configurations for different applications within
the project:
*   Users app (authentication, profiles, dashboard)
*   Flights app (flight management, search, reports)
*   Bookings app (booking creation, management, seat selection)
*   Payments app (payment processing)
*   Django Admin interface
"""


from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('flights/', include('flights.urls')),
    path('bookings/', include('bookings.urls')),
    path('payments/', include('payments.urls')),
]
