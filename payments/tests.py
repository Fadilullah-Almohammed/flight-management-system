from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Payment
from bookings.models import Booking
from flights.models import Flight, Airport, Aircraft
from users.models import PassengerProfile

class PaymentTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = get_user_model().objects.create_user(username='testuser', password='password')
        self.other_user = get_user_model().objects.create_user(username='hacker', password='password')
        self.client.login(username='testuser', password='password')


        self.airport = Airport.objects.create(airport_code="DXB", airport_name="Dubai Int", city="Dubai", country="UAE")
        self.aircraft = Aircraft.objects.create(model="A380")
        self.flight = Flight.objects.create(
            flight_number="EK101",
            departure_datetime=timezone.now() + timedelta(days=1),
            arrival_datetime=timezone.now() + timedelta(days=1, hours=8),
            economy_price=100.00,
            business_price=500.00,
            first_class_price=1000.00,
            departure_airport=self.airport,
            arrival_airport=self.airport,
            aircraft=self.aircraft
        )
        self.passenger = PassengerProfile.objects.create(user=self.user)
        

        self.booking = Booking.objects.create(
            flight=self.flight,
            passenger=self.passenger,
            seat_class='Economy',
            number_of_passengers=2,
            status='Pending'
        )


    def test_get_amount_economy(self):
        payment = Payment(booking=self.booking)
        self.assertEqual(payment.get_amount(), 200.00)

    def test_payment_page_load(self):
        url = reverse('process_payment', args=[self.booking.booking_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_process_payment_success(self):
        url = reverse('process_payment', args=[self.booking.booking_id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Payment.objects.filter(booking=self.booking).exists())
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'Confirmed')

    def test_redirect_if_already_confirmed(self):
        self.booking.status = 'Confirmed'
        self.booking.save()
        url = reverse('process_payment', args=[self.booking.booking_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_cannot_pay_others_booking(self):
        self.client.login(username='hacker', password='password')
        url = reverse('process_payment', args=[self.booking.booking_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)



    def test_get_amount_business_class(self):

        biz_booking = Booking.objects.create(
            flight=self.flight, passenger=self.passenger, seat_class='Business', number_of_passengers=1
        )
        payment = Payment(booking=biz_booking)

        self.assertEqual(payment.get_amount(), 500.00)

    def test_get_amount_first_class(self):

        first_booking = Booking.objects.create(
            flight=self.flight, passenger=self.passenger, seat_class='First', number_of_passengers=3
        )
        payment = Payment(booking=first_booking)

        self.assertEqual(payment.get_amount(), 3000.00)

    def test_get_amount_invalid_class_returns_zero(self):

        bad_booking = Booking.objects.create(
            flight=self.flight, passenger=self.passenger, seat_class='Invalid', number_of_passengers=1
        )
        payment = Payment(booking=bad_booking)
        self.assertEqual(payment.get_amount(), 0)

    def test_payment_str_method(self):

        payment = Payment.objects.create(booking=self.booking, payment_method='Credit Card')
        self.assertEqual(str(payment), f"Payment {payment.payment_id}")

    def test_payment_creation_sets_date(self):

        payment = Payment.objects.create(booking=self.booking, payment_method='Cash')
        self.assertIsNotNone(payment.payment_date)
        self.assertAlmostEqual(payment.payment_date, timezone.now(), delta=timedelta(seconds=10))

    def test_pay_for_cancelled_booking_fails(self):

        self.booking.status = 'Cancelled'
        self.booking.save()
        url = reverse('process_payment', args=[self.booking.booking_id])
        
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302) 

    def test_payment_method_choices(self):

        payment = Payment(booking=self.booking, payment_method='Wallet')

        self.assertIn('Wallet', dict(Payment.METHOD_CHOICES))

    def test_payment_updates_related_booking_only(self):

        booking_b = Booking.objects.create(flight=self.flight, passenger=self.passenger, status='Pending')
        
        url = reverse('process_payment', args=[self.booking.booking_id])
        self.client.post(url)
        
        booking_b.refresh_from_db()
        self.assertEqual(booking_b.status, 'Pending') # Should remain Pending

    def test_unauthenticated_user_access(self):
        self.client.logout()
        url = reverse('process_payment', args=[self.booking.booking_id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_post_payment_idempotency(self):

        url = reverse('process_payment', args=[self.booking.booking_id])
        self.client.post(url) # First pay
        

        response = self.client.post(url)
        

        self.assertEqual(response.status_code, 302)

        self.assertEqual(Payment.objects.filter(booking=self.booking).count(), 1)