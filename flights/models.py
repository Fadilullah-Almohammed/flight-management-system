from django.db import models
from django.core.exceptions import ValidationError
from bookings.models import Booking


class Airport(models.Model):
    """Represents an airport with its code, name, and location details.

    Attributes:
        airport_code: The 3-letter IATA code of the airport.
        airport_name: The full name of the airport.
        city: The city where the airport is located.
        country: The country where the airport is located.
    """
    airport_code = models.CharField(primary_key=True, max_length=3)
    airport_name = models.CharField(max_length=100, null=False)
    city = models.CharField(max_length=50, null=False)
    country = models.CharField(max_length=50, null=False)

    def __str__(self):
        """Returns the string representation of the airport.

        Returns:
            str: The airport name and code.
        """
        return f"{self.airport_name} ({self.airport_code})"

    class Meta:
        db_table = 'Airport'


class Aircraft(models.Model):
    """Represents an aircraft model and its seating capacity configuration.

    Attributes:
        aircraft_id: The unique identifier for the aircraft.
        model: The model name of the aircraft.
        economy_class: The number of economy class seats.
        business_class: The number of business class seats.
        first_class: The number of first class seats.
    """
    aircraft_id = models.AutoField(primary_key=True)
    model = models.CharField(max_length=50, null=False)
    economy_class = models.PositiveIntegerField(default=150)
    business_class = models.PositiveIntegerField(default=16)
    first_class = models.PositiveIntegerField(default=8)

    def __str__(self):
        """Returns the model name of the aircraft.

        Returns:
            str: The aircraft model.
        """
        return self.model

    class Meta:
        db_table = 'Aircraft'


class Flight(models.Model):
    """Represents a scheduled flight.

    Attributes:
        flight_number: The unique flight number.
        departure_datetime: The scheduled departure date and time.
        arrival_datetime: The scheduled arrival date and time.
        economy_price: The price for an economy class ticket.
        business_price: The price for a business class ticket.
        first_class_price: The price for a first class ticket.
        departure_airport: The airport from which the flight departs.
        arrival_airport: The airport at which the flight arrives.
        aircraft: The aircraft assigned to the flight.
        status: The current status of the flight.
    """

    flight_number = models.CharField(primary_key=True, max_length=10)
    departure_datetime = models.DateTimeField()
    arrival_datetime = models.DateTimeField()
    economy_price = models.DecimalField(max_digits=10, decimal_places=2, default=300.00)
    business_price = models.DecimalField(max_digits=10, decimal_places=2, default=800.00)
    first_class_price = models.DecimalField(max_digits=10, decimal_places=2, default=1500.00)
    departure_airport = models.ForeignKey(Airport, on_delete=models.PROTECT, related_name='departing_flights')
    arrival_airport = models.ForeignKey(Airport, on_delete=models.PROTECT, related_name='arriving_flights')
    aircraft = models.ForeignKey(Aircraft, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, default='Scheduled', choices=[
        ('Scheduled', 'Scheduled'),
        ('Delayed', 'Delayed'),
        ('Cancelled', 'Cancelled'),
        ('Landed', 'Landed'),
    ])


    def available_seats_dynamic(self):
        """Calculates the number of available seats on the flight.

        Returns:
            int: The total number of unbooked seats across all classes.
        """

        booked_economy = Booking.objects.filter(flight=self, seat_class='Economy').count()
        booked_business = Booking.objects.filter(flight=self, seat_class='Business').count()
        booked_first_class = Booking.objects.filter(flight=self, seat_class='First').count()
        total_seats = self.aircraft.economy_class + self.aircraft.business_class + self.aircraft.first_class
        booked_seats = booked_economy + booked_business + booked_first_class
        return total_seats - booked_seats

    def flight_time(self):
        """Calculates the duration of the flight.

        Returns:
            str: A string describing the flight duration in hours and minutes, or None if times are missing.
        """

        if self.departure_datetime and self.arrival_datetime:
            diff = self.arrival_datetime - self.departure_datetime
            total_seconds = diff.total_seconds()
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{int(hours)} hours and {int(minutes)} minutes"
        return None

    def check_flight(self):
        """Validates the flight details.

        Raises:
            ValidationError: If departure/arrival times are invalid, airports are the same, or prices are negative.
        """

        if self.departure_datetime >= self.arrival_datetime:
            raise ValidationError("Departure time must be before arrival time.")
        if self.departure_airport == self.arrival_airport:
            raise ValidationError("Departure and arrival airports cannot be the same.")
        if any(p < 0 for p in [self.economy_price, self.business_price, self.first_class_price]):
            raise ValidationError("Prices must be positive.")

    def __str__(self):
        """Returns the flight number.

        Returns:
            str: The flight number.
        """
        return f"{self.flight_number}"

    class Meta:
        db_table = 'Flight'
