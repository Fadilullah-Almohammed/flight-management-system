from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from bookings.models import *
from flights.models import Flight, Airport
from users.models import PassengerProfile
from .forms import *
from django.template.loader import get_template
from django.utils import timezone

from xhtml2pdf import pisa
import math



@login_required
def my_bookings(request):
    """Displays a list of bookings for the currently logged-in user.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered 'my_bookings' page with the user's booking history.
    """

    try:
            passenger = request.user.passenger_profile
            now = timezone.now()
            

            all_bookings = Booking.objects.filter(passenger=passenger).select_related('flight').order_by('-booking_date')


            upcoming_bookings = all_bookings.filter(flight__departure_datetime__gte=now)
            past_bookings = all_bookings.filter(flight__departure_datetime__lt=now)
            
    except Exception:
        upcoming_bookings = []
        past_bookings = []

    context = {
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings
    }
    return render(request, 'bookings/my_bookings.html', context)


@login_required
def seat_selection(request, flight_id, seat_class):
    """Handles seat selection for a specific flight and seat class.

    Retrieves the flight and aircraft details, calculates available and taken seats,
    and organizes them into class-specific row ranges for the template.

    Args:
        request (HttpRequest): The HTTP request object.
        flight_id: The unique identifier for the flight.
        seat_class: The class of seat selected (e.g., 'Economy').

    Returns:
        HttpResponse: The rendered 'seat_selection' page.
    """
    flight = get_object_or_404(Flight, flight_number=flight_id)
    aircraft = flight.aircraft


    try:
        adults = int(request.GET.get('adults', 1))
        children = int(request.GET.get('children', 0))
    except ValueError:
        adults = 1
        children = 0
    total_passengers = adults + children

    taken_seats = list(Ticket.objects.filter(booking__flight=flight).values_list('seat_number', flat=True))

    seats_per_row = 6
    
    first_rows_count = math.ceil(aircraft.first_class / seats_per_row)
    bus_rows_count = math.ceil(aircraft.business_class / seats_per_row)
    eco_rows_count = math.ceil(aircraft.economy_class / seats_per_row)


    first_start = 1
    first_end = first_rows_count
    
    bus_start = first_end + 1
    bus_end = first_end + bus_rows_count
    
    eco_start = bus_end + 1
    eco_end = bus_end + eco_rows_count

    first_range = range(first_start, first_end + 1) if first_rows_count > 0 else None
    bus_range = range(bus_start, bus_end + 1) if bus_rows_count > 0 else None
    eco_range = range(eco_start, eco_end + 1) if eco_rows_count > 0 else None

    context = {
        'flight': flight,
        'first_range': first_range,
        'bus_range': bus_range,
        'eco_range': eco_range,
        'taken_seats': taken_seats,
        'total_passengers': total_passengers,
        'seat_class': seat_class,
    }
    
    request.session['adults'] = adults
    request.session['children'] = children

    return render(request, 'bookings/seat_selection.html', context)


@login_required
def passenger_details(request):
    """Handles the submission of passenger details for selected seats.

    Processes seat selection data, calculates ticket prices, and generates simple
    forms for each passenger's details.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered 'passenger_details' page or a redirect.
    """
    if request.method == 'POST':
        flight_id = request.POST.get('flight_id')
        seats_str = request.POST.get('selected_seats')
        
        seat_class = request.POST.get('seat_class', 'Economy').capitalize()

        
        if not flight_id or not seats_str:
            messages.error(request, "Please select seats first!")
            return redirect('passenger_dashboard')
            
        flight = get_object_or_404(Flight, flight_number=flight_id)
        seats_list = seats_str.split(',')
        
        if seat_class == 'Business':
            ticket_price = flight.business_price
        elif seat_class == 'First':
            ticket_price = flight.first_class_price
        else:
            ticket_price = flight.economy_price
            
        total_price = ticket_price * len(seats_list)
        
        forms_list = []
        for seat in seats_list:
            form = TicketForm(prefix=seat)
            forms_list.append((seat, form))
            
        context = {
            'flight': flight,
            'forms_list': forms_list, 
            'seats_str': seats_str,
            'seat_class': seat_class, 
            'total_price': total_price
        }
        return render(request, 'bookings/passenger_details.html', context)
    
    return redirect('passenger_dashboard')


@login_required
def create_booking(request):
    """Creates a new booking and associated tickets.

    Validates the submitted forms, creates a Booking record, and saves Ticket records
    for each seat.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: A redirect to the payment process or back to the dashboard on failure.
    """
    if request.method == 'POST':
        flight_id = request.POST.get('flight_id')
        seats_str = request.POST.get('seats_str')
        
        seat_class = request.POST.get('seat_class', 'Economy')
        seat_class = seat_class.capitalize()
        
        
        seats_list = seats_str.split(',')
        flight = get_object_or_404(Flight, flight_number=flight_id)
        
        if seat_class == 'Business':
            ticket_price = flight.business_price
        elif seat_class == 'First':
            ticket_price = flight.first_class_price
        else:
            ticket_price = flight.economy_price

        valid_forms = []
        all_valid = True
        forms_list_for_template = []
        
        for seat in seats_list:
            form = TicketForm(request.POST, prefix=seat)
            forms_list_for_template.append((seat, form))
            if form.is_valid():
                valid_forms.append((seat, form))
            else:
                all_valid = False
        
        if not all_valid:
            messages.error(request, "Please correct the errors below.")
            total_price = ticket_price * len(seats_list)
            return render(request, 'bookings/passenger_details.html', {
                'flight': flight,
                'forms_list': forms_list_for_template, 
                'seats_str': seats_str,
                'seat_class': seat_class, 
                'total_price': total_price
            })

        try:
            profile = request.user.passenger_profile
        except PassengerProfile.DoesNotExist:
            profile = None

        booking = Booking.objects.create(
            flight=flight,
            status='Pending',
            number_of_passengers=len(seats_list),
            seat_class=seat_class,
            passenger=profile
        )

        for seat, form in valid_forms:
            ticket = form.save(commit=False) 
            ticket.booking = booking         
            ticket.seat_number = seat
            ticket.save()                    
            
        messages.success(request, "Booking created! Redirecting to payment...")
        return redirect('process_payment', booking_id=booking.booking_id)
    
    return redirect('passenger_dashboard')


@login_required
def booking_details(request, booking_id):
    """Show details of a specific booking and list its tickets.

    Args:
        request (HttpRequest): The HTTP request object.
        booking_id: The unique identifier of the booking.

    Returns:
        HttpResponse: The rendered 'booking_details' page.

    Raises:
        Http404: If the passenger profile does not exist.
    """
    try:
        passenger = request.user.passenger_profile
        booking = get_object_or_404(Booking, booking_id=booking_id, passenger=passenger)
        
        tickets = Ticket.objects.filter(booking=booking)
        
        context = {
            'booking': booking,
            'tickets': tickets
        }
        return render(request, 'bookings/booking_details.html', context)
        
    except PassengerProfile.DoesNotExist:
        raise Http404('Passenger profile not found for this user!')

@login_required
def cancel_ticket(request, ticket_id):
    """Cancel a specific ticket. If it's the last ticket, cancel the booking.

    Args:
        request (HttpRequest): The HTTP request object.
        ticket_id: The unique identifier of the ticket.

    Returns:
        HttpResponse: A redirect to the booking details or my bookings page.
    """
    try:
        passenger = request.user.passenger_profile
        ticket = get_object_or_404(Ticket, ticket_id=ticket_id, booking__passenger=passenger)
        booking = ticket.booking
        
        if booking.status == 'Cancelled':
            messages.warning(request, "This booking is already cancelled.")
            return redirect('booking_details', booking_id=booking.booking_id)

        if booking.flight.departure_datetime < timezone.now():
            messages.error(request, "Cannot cancel a ticket for a past flight.")
            return redirect('booking_details', booking_id=booking.booking_id)

        if request.method == 'POST':
            remaining_count = booking.tickets.count()
            passenger_name = ticket.passenger_name
            
            ticket.delete()
            
            if remaining_count <= 1:
                booking.status = 'Cancelled'
                booking.save()
                messages.success(request, f"Ticket for {passenger_name} cancelled. Booking marked as Cancelled.")
                return redirect('my_bookings')
            else:
                messages.success(request, f"Ticket for {passenger_name} cancelled.")
                return redirect('booking_details', booking_id=booking.booking_id)

    except Exception:
        messages.error(request, "An error occurred.")
    
    return redirect('my_bookings')


@login_required
def download_ticket_pdf(request, booking_id):
    """Generates and downloads a PDF ticket for a specific booking.

    Args:
        request (HttpRequest): The HTTP request object.
        booking_id: The unique identifier of the booking.

    Returns:
        HttpResponse: A PDF file download or an error message.
    """
    booking = get_object_or_404(Booking, booking_id=booking_id, passenger__user=request.user)
    
    template_path = 'bookings/ticket_pdf.html' 
    
    context = {'booking': booking}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{booking.booking_id}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
        
    return response

@login_required
def passenger_dashboard(request):
    """Renders the passenger dashboard with flight search and upcoming bookings.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered passenger dashboard.
    """
    
    airports = Airport.objects.all().order_by('city')

    now = timezone.now()
    
    upcoming_bookings = Booking.objects.filter(
        passenger__user=request.user,     
        flight__departure_datetime__gt=now  
    ).exclude(
        status='Cancelled'                  
    ).order_by('flight__departure_datetime')[:3] 

    context = {
        'airports': airports,
        'upcoming_bookings': upcoming_bookings
    }

    return render(request, 'users/passenger_dashboard.html', context)