
import random
from datetime import timedelta, date
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings


from users.models import Admin, PassengerProfile
from flights.models import Airport, Aircraft, Flight
from bookings.models import Booking, Ticket

class Command(BaseCommand):
    """Seed the database with initial data (Users, Airports, Aircrafts, Flights)."""
    help = 'Populate the database with Users, Flights, and Bookings'

    def handle(self, *args, **kwargs):
        """Executes the seed command to populate the database.

        Creates users, passenger profiles, airports, aircrafts, flights, and dummy bookings.
        """
        self.stdout.write("🌱 Starting Database Seeding...")

        self.stdout.write("... Creating Users")
        
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(" - Superuser 'admin' created (pass: admin123)")

        for i in range(1, 3):
            username = f'staff{i}'
            if not User.objects.filter(username=username).exists():
                u = User.objects.create_user(username, f'staff{i}@flight.com', 'staff123')
                u.is_staff = True
                u.save()
                Admin.objects.create(user=u) # Create Admin Profile
                self.stdout.write(f" - Staff '{username}' created")

        passengers = []
        for i in range(1, 11):
            username = f'passenger{i}'
            if not User.objects.filter(username=username).exists():
                u = User.objects.create_user(username, f'p{i}@gmail.com', 'pass123')

                PassengerProfile.objects.create(
                    user=u,
                    passport=f"P{10000+i}",
                    phone_number=f"050000{1000+i}",
                    nationality="Saudi Arabia",
                    date_of_birth=date(1990 + i, 1, 1)
                )
                passengers.append(u)
                self.stdout.write(f" - Passenger '{username}' created")
            else:
                passengers.append(User.objects.get(username=username))

        self.stdout.write("... Creating Infrastructure")

        airports_data = [
            {"code": "DOH", "name": "Hamad International", "city": "Doha", "country": "Qatar"},
            {"code": "RUH", "name": "King Khalid Intl", "city": "Riyadh", "country": "Saudi Arabia"},
            {"code": "JED", "name": "King Abdulaziz Intl", "city": "Jeddah", "country": "Saudi Arabia"},
            {"code": "DMM", "name": "King Fahd Intl", "city": "Dammam", "country": "Saudi Arabia"},
            {"code": "DXB", "name": "Dubai International", "city": "Dubai", "country": "UAE"},
            {"code": "LHR", "name": "Heathrow Airport", "city": "London", "country": "UK"},
            {"code": "CAI", "name": "Cairo International", "city": "Cairo", "country": "Egypt"},
            {"code": "JFK", "name": "John F. Kennedy", "city": "New York", "country": "USA"},
        ]
        
        db_airports = []
        for data in airports_data:
            a, _ = Airport.objects.get_or_create(
                airport_code=data["code"],
                defaults={"airport_name": data["name"], "city": data["city"], "country": data["country"]}
            )
            db_airports.append(a)

        aircraft_data = [
            {"model": "Boeing 777", "eco": 300, "bus": 40, "first": 8},
            {"model": "Airbus A320", "eco": 150, "bus": 12, "first": 0},
            {"model": "Boeing 787", "eco": 200, "bus": 30, "first": 4},
        ]
        
        db_aircrafts = []
        for data in aircraft_data:
            ac, _ = Aircraft.objects.get_or_create(
                model=data["model"],
                defaults={"economy_class": data["eco"], "business_class": data["bus"], "first_class": data["first"]}
            )
            db_aircrafts.append(ac)

        self.stdout.write("... Creating Flights")
        
        base_time = timezone.now() + timedelta(days=1)
        flights_created = []
        
        for i in range(1, 700): # 50 Flights
            origin = random.choice(db_airports)
            dest = random.choice(db_airports)
            while dest == origin:
                dest = random.choice(db_airports)
            
            plane = random.choice(db_aircrafts)
            dep_time = base_time + timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
            arr_time = dep_time + timedelta(hours=random.randint(2, 12))
            
            flight, created = Flight.objects.get_or_create(
                flight_number=f"SV{2000+i}",
                defaults={
                    "departure_airport": origin,
                    "arrival_airport": dest,
                    "aircraft": plane,
                    "departure_datetime": dep_time,
                    "arrival_datetime": arr_time,
                    "economy_price": random.randint(300, 800),
                    "business_price": random.randint(1000, 2500),
                    "first_class_price": random.randint(4000, 8000),
                }
            )
            if created:
                flights_created.append(flight)

        self.stdout.write("... Creating Dummy Bookings")
        
        if flights_created and passengers:
            for _ in range(30): # Create 30 random bookings
                user = random.choice(passengers)
                flight = random.choice(flights_created)
                seat_class = random.choice(['Economy', 'Business'])
                

                price = flight.economy_price if seat_class == 'Economy' else flight.business_price
                
   