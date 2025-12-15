from django.utils import timezone
from datetime import timedelta
from bookings.models import Booking

def delete_expired_bookings():
    """Identifies and cancels expired pending bookings to release seats.

    Finds bookings that have been in 'Pending' status for more than the allowed
    duration (e.g., 5 minutes) and marks them as 'Cancelled'.
    """
    cutoff_time = timezone.now() - timedelta(minutes=5)
    
    expired_bookings = Booking.objects.filter(
        status='Pending',
        booking_date__lt=cutoff_time
    )
    
    count = expired_bookings.count()
    
    if count > 0:

        expired_bookings.update(status='Cancelled')
        print(f"[Auto-Scheduler] Cancelled {count} expired bookings. Seats released.")
    else:
        print("[Auto-Scheduler] No expired bookings found.")