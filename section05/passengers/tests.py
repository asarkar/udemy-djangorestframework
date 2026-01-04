from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Passenger


class PassengerListTests(APITestCase):
    url: str
    passenger1: Passenger
    passenger2: Passenger

    def setUp(self) -> None:
        self.url = reverse("passenger-list")
        self.passenger1 = Passenger.objects.create(
            first_name="John",
            last_name="Doe",
            source="New York",
            destination="Los Angeles",
        )
        self.passenger2 = Passenger.objects.create(
            first_name="Jane",
            last_name="Smith",
            source="Chicago",
            destination="Miami",
        )

    def test_get_all_passengers(self) -> None:
        """Test retrieving all passengers."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_passengers_empty(self) -> None:
        """Test retrieving passengers when none exist."""
        Passenger.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_post_create_passenger(self) -> None:
        """Test creating a new passenger."""
        data: dict[str, str] = {
            "first_name": "Alice",
            "last_name": "Johnson",
            "source": "Boston",
            "destination": "Seattle",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["first_name"], "Alice")
        self.assertEqual(response.data["last_name"], "Johnson")
        self.assertEqual(response.data["source"], "Boston")
        self.assertEqual(response.data["destination"], "Seattle")
        self.assertEqual(Passenger.objects.count(), 3)

    def test_post_create_passenger_invalid_data(self) -> None:
        """Test creating a passenger with invalid data."""
        data: dict[str, str] = {}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Passenger.objects.count(), 2)

    def test_post_create_passenger_partial_data(self) -> None:
        """Test creating a passenger with partial data."""
        data: dict[str, str] = {"first_name": "Alice"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Passenger.objects.count(), 2)


class PassengerDetailTests(APITestCase):
    def setUp(self) -> None:
        self.passenger = Passenger.objects.create(
            first_name="John",
            last_name="Doe",
            source="New York",
            destination="Los Angeles",
        )
        self.url = reverse("passenger-detail", kwargs={"pk": self.passenger.pk})

    def test_get_passenger_detail(self) -> None:
        """Test retrieving a single passenger."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "John")
        self.assertEqual(response.data["last_name"], "Doe")
        self.assertEqual(response.data["source"], "New York")
        self.assertEqual(response.data["destination"], "Los Angeles")

    def test_get_passenger_not_found(self) -> None:
        """Test retrieving a non-existent passenger."""
        url: str = reverse("passenger-detail", kwargs={"pk": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_passenger(self) -> None:
        """Test full update of a passenger."""
        data: dict[str, str] = {
            "first_name": "Johnny",
            "last_name": "Updated",
            "source": "Boston",
            "destination": "Seattle",
        }
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["first_name"], "Johnny")
        self.assertEqual(response.data["last_name"], "Updated")

    def test_put_passenger_invalid_data(self) -> None:
        """Test full update with invalid data."""
        data: dict[str, str] = {}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_passenger(self) -> None:
        """Test partial update of a passenger."""
        data: dict[str, str] = {"first_name": "Johnny"}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Johnny")
        self.assertEqual(response.data["last_name"], "Doe")

    def test_delete_passenger(self) -> None:
        """Test deleting a passenger."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Passenger.objects.filter(pk=self.passenger.pk).exists())

    def test_delete_passenger_not_found(self) -> None:
        """Test deleting a non-existent passenger."""
        url: str = reverse("passenger-detail", kwargs={"pk": 9999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
