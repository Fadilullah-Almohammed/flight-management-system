import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from flights.models import Airport, Aircraft, Flight

class Command(BaseCommand):
    help = 'Populate the database with many airports, aircrafts, and dummy flights'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # 1. EXTENSIVE LIST OF AIRPORTS
        airports_data = [
            # --- Middle East ---
            {"code": "DOH", "name": "Hamad International", "city": "Doha", "country": "Qatar"},
            {"code": "RUH", "name": "King Khalid International", "city": "Riyadh", "country": "Saudi Arabia"},
            {"code": "JED", "name": "King Abdulaziz International", "city": "Jeddah", "country": "Saudi Arabia"},
            {"code": "DMM", "name": "King Fahd International", "city": "Dammam", "country": "Saudi Arabia"},
            {"code": "MED", "name": "Prince Mohammad Bin Abdulaziz", "city": "Medina", "country": "Saudi Arabia"},
            {"code": "DXB", "name": "Dubai International", "city": "Dubai", "country": "UAE"},
            {"code": "AUH", "name": "Abu Dhabi International", "city": "Abu Dhabi", "country": "UAE"},
            {"code": "KWI", "name": "Kuwait International", "city": "Kuwait City", "country": "Kuwait"},
            {"code": "BAH", "name": "Bahrain International", "city": "Manama", "country": "Bahrain"},
            {"code": "MCT", "name": "Muscat International", "city": "Muscat", "country": "Oman"},
            {"code": "AMM", "name": "Queen Alia International", "city": "Amman", "country": "Jordan"},
            {"code": "BEY", "name": "Beirut-Rafic Hariri International", "city": "Beirut", "country": "Lebanon"},

            # --- Europe ---
            {"code": "LHR", "name": "Heathrow Airport", "city": "London", "country": "UK"},
            {"code": "CDG", "name": "Charles de Gaulle", "city": "Paris", "country": "France"},
            {"code": "FRA", "name": "Frankfurt Airport", "city": "Frankfurt", "country": "Germany"},
            {"code": "AMS", "name": "Schiphol Airport", "city": "Amsterdam", "country": "Netherlands"},
            {"code": "MAD", "name": "Adolfo Suárez Madrid–Barajas", "city": "Madrid", "country": "Spain"},
            {"code": "FCO", "name": "Leonardo da Vinci–Fiumicino", "city": "Rome", "country": "Italy"},
            {"code": "IST", "name": "Istanbul Airport", "city": "Istanbul", "country": "Turkey"},
            {"code": "ZRH", "name": "Zurich Airport", "city": "Zurich", "country": "Switzerland"},

            # --- Asia ---
            {"code": "HND", "name": "Tokyo Haneda", "city": "Tokyo", "country": "Japan"},
            {"code": "NRT", "name": "Narita International", "city": "Tokyo", "country": "Japan"},
            {"code": "ICN", "name": "Incheon International", "city": "Seoul", "country": "South Korea"},
            {"code": "PEK", "name": "Beijing Capital International", "city": "Beijing", "country": "China"},
            {"code": "HKG", "name": "Hong Kong International", "city": "Hong Kong", "country": "Hong Kong"},
            {"code": "SIN", "name": "Singapore Changi", "city": "Singapore", "country": "Singapore"},
            {"code": "BKK", "name": "Suvarnabhumi Airport", "city": "Bangkok", "country": "Thailand"},
            {"code": "DEL", "name": "Indira Gandhi International", "city": "New Delhi", "country": "India"},
            {"code": "BOM", "name": "Chhatrapati Shivaji Maharaj", "city": "Mumbai", "country": "India"},
            {"code": "KUL", "name": "Kuala Lumpur International", "city": "Kuala Lumpur", "country": "Malaysia"},

            # --- Americas ---
            {"code": "JFK", "name": "John F. Kennedy International", "city": "New York", "country": "USA"},
            {"code": "LAX", "name": "Los Angeles International", "city": "Los Angeles", "country": "USA"},
            {"code": "ORD", "name": "O'Hare International", "city": "Chicago", "country": "USA"},
            {"code": "ATL", "name": "Hartsfield–Jackson Atlanta", "city": "Atlanta", "country": "USA"},
            {"code": "YYZ", "name": "Toronto Pearson", "city": "Toronto", "country": "Canada"},
            {"code": "GRU", "name": "São Paulo/Guarulhos", "city": "São Paulo", "country": "Brazil"},
            {"code": "MEX", "name": "Benito Juárez International", "city": "Mexico City", "country": "Mexico"},

            # --- Africa ---
            {"code": "CAI", "name": "Cairo International", "city": "Cairo", "country": "Egypt"},
            {"code": "JNB", "name": "O. R. Tambo International", "city": "Johannesburg", "country": "South Africa"},
            {"code": "CMN", "name": "Mohammed V International", "city": "Casablanca", "country": "Morocco"},
            {"code": "ADD", "name": "Bole International", "city": "Addis Ababa", "country": "Ethiopia"},

            # --- Oceania ---
            {"code": "SYD", "name": "Sydney Kingsford Smith", "city": "Sydney", "country": "Australia"},
            {"code": "MEL", "name": "Melbourne Airport", "city": "Melbourne", "country": "Australia"},
            {"code": "AKL", "name": "Auckland Airport", "city": "Auckland", "country": "New Zealand"},
        ]

        airports_created = 0
        for data in airports_data:
            airport, created = Airport.objects.get_or_create(
                airport_code=data["code"],
                defaults={
                    "airport_name": data["name"],
                    "city": data["city"],
                    "country": data["country"]
                }
            )
            if created:
                airports_created += 1
        
        self.stdout.write(f" - Processed {len(airports_data)} airports (Created {airports_created} new).")

        # 2. CREATE AIRCRAFTS
        aircraft_data = [
            {"model": "Boeing 777-300ER", "eco": 300, "bus": 40, "first": 8},
            {"model": "Boeing 787-9 Dreamliner", "eco": 200, "bus": 30, "first": 4},
            {"model": "Airbus A380-800", "eco": 400, "bus": 60, "first": 12},
            {"model": "Airbus A320-200", "eco": 150, "bus": 12, "first": 0},
            {"model": "Airbus A350-900", "eco": 250, "bus": 35, "first": 0},
            {"model": "Embraer E190", "eco": 90, "bus": 10, "first": 0},
        ]

        aircraft_list = []
        for data in aircraft_data:
            ac, created = Aircraft.objects.get_or_create(
                model=data["model"],
                defaults={
                    "economy_class": data["eco"],
                    "business_class": data["bus"],
                    "first_class": data["first"]
                }
            )
            aircraft_list.append(ac)

        # 3. GENERATE DUMMY FLIGHTS
        # We will generate 100 random flights starting from tomorrow
        base_time = timezone.now() + timedelta(days=1)
        
        # Fetch all available airports from DB to create random routes
        all_airports = list(Airport.objects.all())
        
        count = 0
        if len(all_airports) > 1:
            for i in range(1, 101): # Generate 100 flights
                # Pick two different airports
                origin = random.choice(all_airports)
                destination = random.choice(all_airports)
                while destination == origin:
                    destination = random.choice(all_airports)
                
                plane = random.choice(aircraft_list)
                
                # Randomize time: Flight starts i days from now + random hours
                # This spreads flights out over the next 3 months (approx)
                days_ahead = random.randint(0, 90)
                dep_time = base_time + timedelta(days=days_ahead, hours=random.randint(0, 23), minutes=random.choice([0, 15, 30, 45]))
                
                # Random duration between 1 and 14 hours
                duration = random.randint(1, 14) 
                arr_time = dep_time + timedelta(hours=duration)
                
                flight_num = f"SV{1000 + i}"

                flight, created = Flight.objects.get_or_create(
                    flight_number=flight_num,
                    defaults={
                        "departure_airport": origin,
                        "arrival_airport": destination,
                        "aircraft": plane,
                        "departure_datetime": dep_time,
                        "arrival_datetime": arr_time,
                        "economy_price": random.randint(200, 1500),
                        "business_price": random.randint(1600, 4000),
                        "first_class_price": random.randint(5000, 12000),
                    }
                )
                
                if created:
                    count += 1
        
        self.stdout.write(self.style.SUCCESS(f"Successfully added {count} new flights! Database now has {Airport.objects.count()} airports."))