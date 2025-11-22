from django.urls import path
from . import views


urlpatterns = [
    path('reports/', views.admin_view_reports, name='admin_view_reports'),
    path('add_new_flight/', views.add_new_flight, name='add_new_flight'),
    path('view_flights/', views.view_flights, name='view_flights'),
    path('flight-management/', views.flight_management, name='flight_management'),
]