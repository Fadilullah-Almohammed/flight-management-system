from apscheduler.schedulers.background import BackgroundScheduler
from .tasks import delete_expired_bookings

def start():
    """Starts the background scheduler for periodic tasks."""
    scheduler = BackgroundScheduler()
    
    scheduler.add_job(delete_expired_bookings, 'interval', minutes=1)

    scheduler.start()