from django.shortcuts import render

# Create your views here.


def my_bookings(request):
    return render(request, 'bookings/my_bookings.html')