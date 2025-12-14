from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from django.db.models.functions import Length
from .forms import *
from .models import *
from datetime import datetime
from bookings.models import Ticket
from xhtml2pdf import pisa


# Create your views here.

@login_required
def admin_view_reports(request):

    return render(request, 'flights/reports.html')

@login_required
def add_new_flight(request):


    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page !')
        return redirect('passenger_dashboard')
    
    
    if request.method == 'POST':
        
        flight_form = NewFlightForm(request.POST)

        if flight_form.is_valid():
            flight_form.save()

            messages.success(request, 'Flight has been created successfully.')
        else:
            messages.error(request, 'Please check the error below !')

    else:
        flight_form = NewFlightForm()



    return render(request, 'flights/add_new_flight.html', context={'form': flight_form})

@login_required
def view_flights(request):

    search_query = request.GET.get('search', '')
    

    flights = Flight.objects.all().order_by('departure_datetime')


    if search_query:
        flights = flights.filter(
            Q(flight_number__icontains=search_query) |
            Q(departure_airport__airport_code__icontains=search_query) |
            Q(departure_airport__city__icontains=search_query) |
            Q(arrival_airport__airport_code__icontains=search_query) |
            Q(arrival_airport__city__icontains=search_query) |
            Q(aircraft__model__icontains=search_query)
        )

    context = {
        'flights': flights,
        'search_query': search_query  
    }
    return render(request, 'flights/view_flights.html', context)

@login_required
def delete_flight(request, flight_id):

    if not request.user.is_staff:
        messages.error(request, 'Access denied')
        return redirect('passenger_dashboard')
    
    flight = get_object_or_404(Flight, flight_number=flight_id)

    if request.method == 'POST':
        flight.delete()

        messages.success(request, 'Flight deleted successfully')

    return redirect('view_flights')


@login_required
def search_flight(request):
    departure_code = request.GET.get('origin')
    destination_code = request.GET.get('destination')
    date_from_str = request.GET.get('date_from')
    date_to_str = request.GET.get('date_to')
    cabin_class = request.GET.get('cabin_class', 'economy').lower()
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    flights = []
    departure_city = 'Unknown'
    destination_city = 'Unknown'

    if departure_code and destination_code and date_from_str and date_to_str:
        try:
            search_date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
            search_date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
            
            # Base query: Route and Date
            flights = Flight.objects.filter(
                departure_airport__airport_code=departure_code,
                arrival_airport__airport_code=destination_code,
                departure_datetime__date__range=[search_date_from, search_date_to]
            )

            # --- Capacity Check: Hide flights if class capacity is 0 ---
            if cabin_class == 'first':
                flights = flights.filter(aircraft__first_class__gt=0)
            elif cabin_class == 'business':
                flights = flights.filter(aircraft__business_class__gt=0)
            else:
                flights = flights.filter(aircraft__economy_class__gt=0)

            # --- Price Filter ---
            if min_price:
                if cabin_class == 'business': flights = flights.filter(business_price__gte=min_price)
                elif cabin_class == 'first': flights = flights.filter(first_class_price__gte=min_price)
                else: flights = flights.filter(economy_price__gte=min_price)
            
            if max_price:
                if cabin_class == 'business': flights = flights.filter(business_price__lte=max_price)
                elif cabin_class == 'first': flights = flights.filter(first_class_price__lte=max_price)
                else: flights = flights.filter(economy_price__lte=max_price)
            
            flights = flights.order_by('departure_datetime')
            
            # Fetch city names for display
            if flights.exists():
                departure_city = flights[0].departure_airport.city
                destination_city = flights[0].arrival_airport.city
            else:
                try:
                    departure_city = Airport.objects.get(airport_code=departure_code).city
                    destination_city = Airport.objects.get(airport_code=destination_code).city
                except Airport.DoesNotExist: 
                    pass

        except ValueError: 
            pass

    context = {
        'flights': flights, 
        'departure_code': departure_code, 
        'destination_code': destination_code,
        'cabin_class': cabin_class, 
        'min_price': min_price, 
        'max_price': max_price,
        'departure_city': departure_city, 
        'destination_city': destination_city,
        'date_from': date_from_str, 
        'date_to': date_to_str, 
        'result_count': len(flights)
    }
    return render(request, 'flights/search_flight.html', context)


@login_required
def flight_details(request, flight_id):

    flight = get_object_or_404(Flight, flight_number=flight_id)

    seat_class = request.GET.get('seat_class', 'Economy')

    return render(request, 'flights/flight_details.html', {'flight': flight, 'seat_class': seat_class})


def is_admin(user):
    return user.is_superuser or user.is_staff

@login_required
@user_passes_test(is_admin)
def edit_flight(request, flight_id):
    """
    Allows admin to edit an existing flight.
    Args:
        flight_id (str): The flight number (e.g., 'SV2010') passed from the URL.
    """
    # 1. Fetch the flight using flight_number (handles 'SV2010')
    flight = get_object_or_404(Flight, flight_number=flight_id)
    
    # 2. Handle Form Submission
    if request.method == 'POST':
        form = FlightForm(request.POST, instance=flight)
        if form.is_valid():
            form.save()
            messages.success(request, f"Flight {flight.flight_number} updated successfully!")
            return redirect('view_flights') # Ensure this matches your URL name in urls.py
        else:
            messages.error(request, "Please correct the errors below.")
    
    # 3. Handle Initial Page Load (Pre-fill form)
    else:
        form = FlightForm(instance=flight)
    
    return render(request, 'flights/edit_flight.html', {'form': form, 'flight': flight})

@login_required
def flight_manifest(request, flight_id):
    
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('passenger_dashboard')
    
    flight = get_object_or_404(Flight, flight_number=flight_id)

    search_query = request.GET.get('search', '')
    

    tickets = Ticket.objects.filter(booking__flight=flight).exclude(booking__status='Cancelled').select_related('booking')


    if search_query:
        tickets = tickets.filter(
            Q(passenger_name__icontains=search_query) |
            Q(passport__icontains=search_query) |
            Q(booking__booking_id__icontains=search_query) |
            Q(booking__seat_class__icontains=search_query)
        )


    sort_param = request.GET.get('sort', 'seat')

    if sort_param == 'name':
        tickets = tickets.order_by('passenger_name')
    else:

        tickets = tickets.annotate(seat_len=Length('seat_number')).order_by('seat_len', 'seat_number')

    total_seats = flight.aircraft.economy_class + flight.aircraft.business_class + flight.aircraft.first_class
    occupied_seats = tickets.count()

    context = {
        'flight': flight,
        'tickets': tickets,
        'occupied_seats': occupied_seats,
        'total_seats': total_seats,
        'search_query': search_query,
        'sort_param': sort_param
    }

    return render(request, 'flights/flight_manifest.html', context)


@login_required
def remove_passenger(request, ticket_id):

    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('passenger_dashboard')
    
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    flight_id = ticket.booking.flight.flight_number

    if request.method == 'POST':
        booking = ticket.booking

        if booking.tickets.count() <= 1:
            booking.status = 'Cancelled'
            booking.save()
            ticket.delete()
        else:
            ticket.delete()

        messages.success(request, f"Passenger {ticket.passenger_name} removed successfully.")
    
    return redirect('flight_manifest', flight_id=flight_id)


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="flight_report.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@login_required
def admin_view_reports(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('passenger_dashboard')

    # Security Check (still useful for the table column)
    show_financials = request.user.is_superuser 

    flights = Flight.objects.all().select_related('aircraft', 'departure_airport', 'arrival_airport')
    all_valid_tickets = Ticket.objects.exclude(booking__status='Cancelled').select_related('booking', 'booking__flight')

    total_tickets_sold = all_valid_tickets.count()
    total_flights_count = flights.count()
    
    flight_reports = []

    for flight in flights:
        flight_tickets = all_valid_tickets.filter(booking__flight=flight)
        
        # Operational Stats
        total_sold = flight_tickets.count()
        total_capacity = flight.aircraft.economy_class + flight.aircraft.business_class + flight.aircraft.first_class
        
        occupancy_rate = 0
        if total_capacity > 0:
            occupancy_rate = round((total_sold / total_capacity) * 100, 1)

        # Financial Stats (Per flight only)
        flight_revenue = 0
        if show_financials:
            eco_sold = flight_tickets.filter(booking__seat_class='Economy').count()
            bus_sold = flight_tickets.filter(booking__seat_class='Business').count()
            first_sold = flight_tickets.filter(booking__seat_class='First').count()
            
            flight_revenue = (eco_sold * flight.economy_price) + \
                             (bus_sold * flight.business_price) + \
                             (first_sold * flight.first_class_price)

        flight_reports.append({
            'flight_obj': flight,
            'revenue': flight_revenue,
            'sold': total_sold,
            'capacity': total_capacity,
            'occupancy': occupancy_rate,
            'status': flight.status
        })

    if show_financials:
        flight_reports.sort(key=lambda x: x['revenue'], reverse=True)
    else:
        flight_reports.sort(key=lambda x: x['sold'], reverse=True)

    context = {
        'total_tickets': total_tickets_sold,
        'total_flights': total_flights_count,
        'flight_reports': flight_reports,
        'today': datetime.now(),
        'show_financials': show_financials 
    }

    return render(request, 'flights/reports.html', context)

@login_required
def generate_report_pdf(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('passenger_dashboard')

    report_type = request.GET.get('report_type', 'general')
    
    if report_type == 'financial' and not request.user.is_superuser:
        messages.error(request, "You are not authorized to export financial reports.")
        return redirect('admin_view_reports')

    flights = Flight.objects.all().select_related('aircraft', 'departure_airport', 'arrival_airport').order_by('departure_datetime')
    all_valid_tickets = Ticket.objects.exclude(booking__status='Cancelled').select_related('booking', 'booking__flight')
    
    flight_data = []
    total_tickets = all_valid_tickets.count()
    show_financials = request.user.is_superuser

    for flight in flights:
        tickets = all_valid_tickets.filter(booking__flight=flight)
        
        eco = tickets.filter(booking__seat_class='Economy').count()
        bus = tickets.filter(booking__seat_class='Business').count()
        first = tickets.filter(booking__seat_class='First').count()
        
        revenue = (eco * flight.economy_price) + (bus * flight.business_price) + (first * flight.first_class_price)
        
        total_sold = eco + bus + first
        capacity = flight.aircraft.economy_class + flight.aircraft.business_class + flight.aircraft.first_class
        occupancy = round((total_sold / capacity) * 100, 1) if capacity > 0 else 0

        # Build data row
        if report_type == 'financial':
            flight_data.append({
                'flight': flight,
                'revenue': revenue,
                'eco_sold': eco,
                'bus_sold': bus,
                'first_sold': first
            })
        elif report_type == 'occupancy':
            flight_data.append({
                'flight': flight,
                'capacity': capacity,
                'sold': total_sold,
                'occupancy': occupancy
            })
        else: # general
            data_row = {
                'flight': flight,
                'sold': total_sold,
                'occupancy': occupancy,
                'status': flight.status
            }
            if show_financials:
                data_row['revenue'] = revenue
            
            flight_data.append(data_row)

    context = {
        'report_type': report_type,
        'generated_at': datetime.now(),
        'flight_data': flight_data,
        'total_flights': flights.count(),
        'total_tickets': total_tickets,
        'user': request.user,
        'show_financials': show_financials
    }

    return render_to_pdf('flights/report_pdf.html', context)