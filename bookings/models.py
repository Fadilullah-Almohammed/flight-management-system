from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from datetime import date

class Booking(models.Model):
    # Choices for the booking status (value, label)
    STATUS_CHOICES = [
        ('Confirmed', 'Confirmed'),
        ('Pending', 'Pending'),
        ('Cancelled', 'Cancelled'),
    ]

    # Choices for seat class
    SEAT_CLASS_CHOICES = [
        ('Economy', 'Economy'),
        ('Business', 'Business'),
        ('First', 'First'),
    ]
    
    booking_id = models.AutoField(primary_key=True)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    number_of_passengers = models.PositiveIntegerField(default=1)
    seat_class = models.CharField(max_length=20, choices=SEAT_CLASS_CHOICES, default='Economy')

    # Foreign key relationships with PassengerProfile and Flight models
    passenger = models.ForeignKey('users.PassengerProfile', on_delete=models.RESTRICT)
    flight = models.ForeignKey('flights.Flight', on_delete=models.RESTRICT)

    def total_price(self):
        """Calculate the total price for the booking based on seat class and number of passengers."""
        seat_prices = {
            'Economy': self.flight.economy_price,
            'Business': self.flight.business_price,
            'First': self.flight.first_class_price,
        }
        price = seat_prices.get(self.seat_class)
        if price is None:
            raise ValidationError("Invalid seat class")
        return price * self.number_of_passengers

    def clean(self):
        """Additional validation for fields."""
        if self.number_of_passengers <= 0:
            raise ValidationError("Number of passengers must be greater than zero.")

    
    def __str__(self):
        return f"Booking {self.booking_id}"

    class Meta:
        db_table = 'Booking'
        
    from django.db import models


class Ticket(models.Model):
    ticket_id = models.AutoField(primary_key=True)  # Unique ticket ID
    seat_number = models.CharField(
        max_length=10, 
        validators=[RegexValidator(r'^\d+[A-Za-z]+$', 'Invalid seat number format')]
    )  # Seat number format (e.g., 12A or 25B)
    passenger_name = models.CharField(max_length=100)  # Name of the passenger
    passport = models.CharField(max_length=20, unique=True)  # Passport number of the passenger
    passenger_dob = models.DateField()  # Date of birth of the passenger
    nationality = models.CharField(max_length=50)  # Nationality of the passenger
    
    # Foreign key to link the ticket to a booking
    booking = models.ForeignKey('Booking', on_delete=models.CASCADE, related_name='tickets')  # Each ticket belongs to one booking

    def clean(self):
        """Ensure the passenger is at least 18 years old"""
        if self.passenger_dob > date.today().replace(year=date.today().year - 18):
            raise ValidationError('Passenger must be at least 18 years old.')

    def __str__(self):
        return f"Ticket {self.ticket_id} - {self.seat_number} for {self.passenger_name}"

    class Meta:
        db_table = 'Ticket'  # Define the database table name

