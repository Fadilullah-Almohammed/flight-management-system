from django.db import models

class Payment(models.Model):
    """Represents a payment record for a booking.

    Attributes:
        payment_id: The unique identifier for the payment.
        payment_method: The method used for payment (e.g., Credit Card).
        payment_date: The date and time when the payment was made.
        booking: The booking associated with this payment.
    """
    METHOD_CHOICES = [
        ('Credit Card', 'Credit Card'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Cash', 'Cash'),
        ('Wallet', 'Wallet'),
    ]

    payment_id = models.AutoField(primary_key=True)
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    payment_date = models.DateTimeField(auto_now_add=True)
    
    booking = models.OneToOneField('bookings.Booking', on_delete=models.RESTRICT, related_name='payment')

    def get_amount(self):
        """Calculates the payment amount based on the booking's seat class and passenger count.

        Returns:
            The total amount paid.
        """
        if self.booking.seat_class == 'Economy':
            return self.booking.flight.economy_price * self.booking.number_of_passengers
        elif self.booking.seat_class == 'Business':
            return self.booking.flight.business_price * self.booking.number_of_passengers
        elif self.booking.seat_class == 'First':
            return self.booking.flight.first_class_price * self.booking.number_of_passengers
        return 0
    
    def __str__(self):
        """Returns the string representation of the payment.

        Returns:
            str: The string representation of the payment.
        """
        return f"Payment {self.payment_id}"

    class Meta:
        db_table = 'Payment'