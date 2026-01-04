from datetime import date, time

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Flight, Passenger, Reservation


class FlightFilterTests(APITestCase):
    """Tests for finding flights with filtering."""

    def setUp(self) -> None:
        self.url = reverse("flight-list")
        self.flight1 = Flight.objects.create(
            flight_number="AA100",
            airline="American",
            origin="NYC",
            destination="LAX",
            departure_date=date(2026, 1, 15),
            departure_time=time(10, 30),
        )
        self.flight2 = Flight.objects.create(
            flight_number="UA200",
            airline="United",
            origin="NYC",
            destination="LAX",
            departure_date=date(2026, 1, 16),
            departure_time=time(14, 0),
        )
        self.flight3 = Flight.objects.create(
            flight_number="DL300",
            airline="Delta",
            origin="LAX",
            destination="NYC",
            departure_date=date(2026, 1, 15),
            departure_time=time(8, 0),
        )

    def test_list_all_flights_no_filter(self) -> None:
        """Test listing all flights without filters."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_filter_flights_all_params(self) -> None:
        """Test filtering flights with all required params."""
        response = self.client.get(
            self.url,
            {"origin": "NYC", "destination": "LAX", "departure_date": "2026-01-15"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["flight_number"], "AA100")

    def test_filter_flights_case_insensitive(self) -> None:
        """Test that source and destination filters are case-insensitive."""
        response = self.client.get(
            self.url,
            {"origin": "nyc", "destination": "lax", "departure_date": "2026-01-15"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_flights_partial_params_error(self) -> None:
        """Test that partial params return an error."""
        response = self.client.get(self.url, {"origin": "NYC"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_filter_flights_two_params_error(self) -> None:
        """Test that two of three params return an error."""
        response = self.client.get(self.url, {"origin": "NYC", "destination": "LAX"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_flights_no_results(self) -> None:
        """Test filtering with no matching flights."""
        response = self.client.get(
            self.url,
            {"origin": "NYC", "destination": "LAX", "departure_date": "2026-12-25"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_filter_multiple_flights_same_route_date(self) -> None:
        """Test filtering returns multiple flights on same route and date."""
        Flight.objects.create(
            flight_number="AA101",
            airline="American",
            origin="NYC",
            destination="LAX",
            departure_date=date(2026, 1, 15),
            departure_time=time(18, 0),
        )
        response = self.client.get(
            self.url,
            {"origin": "NYC", "destination": "LAX", "departure_date": "2026-01-15"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class ReservationCreateTests(APITestCase):
    """Tests for creating reservations."""

    def setUp(self) -> None:
        self.url = reverse("reservation-list")
        self.flight = Flight.objects.create(
            flight_number="AA100",
            airline="American",
            origin="NYC",
            destination="LAX",
            departure_date=date(2026, 1, 15),
            departure_time=time(10, 30),
        )

    def test_create_reservation_new_passenger(self) -> None:
        """Test creating a reservation with a new passenger."""
        data = {
            "flight_id": self.flight.pk,
            "passenger": {
                "first_name": "John",
                "last_name": "Doe",
                "middle_name": "M",
                "email": "john@example.com",
                "phone": "555-1234",
            },
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reservation.objects.count(), 1)
        self.assertEqual(Passenger.objects.count(), 1)
        passenger = Passenger.objects.get(email="john@example.com")
        self.assertEqual(passenger.email, "john@example.com")

    def test_create_reservation_existing_passenger(self) -> None:
        """Test creating a reservation reuses existing passenger by email."""
        existing_passenger = Passenger.objects.create(
            first_name="Jane",
            last_name="Doe",
            middle_name="A",
            email="jane@example.com",
            phone="555-0000",
        )
        data = {
            "flight_id": self.flight.pk,
            "passenger": {
                "first_name": "Janet",  # Different name, same email
                "last_name": "Smith",
                "middle_name": "B",
                "email": "jane@example.com",  # Same email
                "phone": "555-9999",
            },
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Passenger.objects.count(), 1)  # No new passenger created
        # Original passenger data preserved
        passenger = Passenger.objects.get(email="jane@example.com")
        self.assertEqual(passenger.first_name, "Jane")
        self.assertEqual(passenger.pk, existing_passenger.pk)

    def test_create_reservation_invalid_flight(self) -> None:
        """Test creating a reservation with non-existent flight."""
        data = {
            "flight_id": 9999,
            "passenger": {
                "first_name": "John",
                "last_name": "Doe",
                "middle_name": "M",
                "email": "john@example.com",
                "phone": "555-1234",
            },
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("flight_id", response.data)

    def test_create_reservation_missing_flight_id(self) -> None:
        """Test creating a reservation without flight_id."""
        data = {
            "passenger": {
                "first_name": "John",
                "last_name": "Doe",
                "middle_name": "M",
                "email": "john@example.com",
                "phone": "555-1234",
            },
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("flight_id", response.data)

    def test_create_reservation_missing_passenger(self) -> None:
        """Test creating a reservation without passenger data."""
        data = {"flight_id": self.flight.pk}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("passenger", response.data)

    def test_create_reservation_invalid_email(self) -> None:
        """Test creating a reservation with invalid email."""
        data = {
            "flight_id": self.flight.pk,
            "passenger": {
                "first_name": "John",
                "last_name": "Doe",
                "middle_name": "M",
                "email": "not-an-email",
                "phone": "555-1234",
            },
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_reservation_missing_required_passenger_field(self) -> None:
        """Test creating a reservation with missing required passenger field."""
        data = {
            "flight_id": self.flight.pk,
            "passenger": {
                "first_name": "John",
                # Missing last_name, email, phone
            },
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_reservations(self) -> None:
        """Test listing reservations returns ReservationSerializer format."""
        passenger = Passenger.objects.create(
            first_name="John",
            last_name="Doe",
            middle_name="M",
            email="john@example.com",
            phone="555-1234",
        )
        Reservation.objects.create(flight=self.flight, passenger=passenger)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn("flight", response.data[0])
        self.assertIn("passenger", response.data[0])
