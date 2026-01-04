from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Customer, Order


class CustomerViewSetTests(APITestCase):
    def setUp(self) -> None:
        self.list_url = reverse("customer-list")
        self.customer1 = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            phone="555-1234",
        )
        self.customer2 = Customer.objects.create(
            first_name="Jane",
            last_name="Smith",
            phone="555-5678",
        )
        self.detail_url = reverse("customer-detail", kwargs={"pk": self.customer1.pk})

    def test_list_customers(self) -> None:
        """Test retrieving all customers."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_customers_empty(self) -> None:
        """Test retrieving customers when none exist."""
        Customer.objects.all().delete()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_create_customer(self) -> None:
        """Test creating a new customer."""
        data: dict[str, str] = {
            "first_name": "Alice",
            "last_name": "Johnson",
            "phone": "555-9999",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["first_name"], "Alice")
        self.assertEqual(response.data["last_name"], "Johnson")
        self.assertEqual(response.data["phone"], "555-9999")
        self.assertEqual(Customer.objects.count(), 3)

    def test_create_customer_invalid_data(self) -> None:
        """Test creating a customer with invalid data."""
        data: dict[str, str] = {}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Customer.objects.count(), 2)

    def test_retrieve_customer(self) -> None:
        """Test retrieving a single customer."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "John")
        self.assertEqual(response.data["last_name"], "Doe")
        self.assertEqual(response.data["phone"], "555-1234")

    def test_retrieve_customer_not_found(self) -> None:
        """Test retrieving a non-existent customer."""
        url = reverse("customer-detail", kwargs={"pk": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_customer(self) -> None:
        """Test full update of a customer."""
        data: dict[str, str] = {
            "first_name": "Johnny",
            "last_name": "Updated",
            "phone": "555-0000",
        }
        response = self.client.put(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Johnny")
        self.assertEqual(response.data["last_name"], "Updated")
        self.assertEqual(response.data["phone"], "555-0000")

    def test_partial_update_customer(self) -> None:
        """Test partial update of a customer."""
        data: dict[str, str] = {"first_name": "Johnny"}
        response = self.client.patch(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Johnny")
        self.assertEqual(response.data["last_name"], "Doe")

    def test_delete_customer(self) -> None:
        """Test deleting a customer."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Customer.objects.filter(pk=self.customer1.pk).exists())

    def test_delete_customer_not_found(self) -> None:
        """Test deleting a non-existent customer."""
        url = reverse("customer-detail", kwargs={"pk": 9999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_customer_with_orders(self) -> None:
        """Test that customer response includes related orders."""
        Order.objects.create(
            customer=self.customer1,
            product="Laptop",
            quantity=1,
        )
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["orders"]), 1)
        self.assertEqual(response.data["orders"][0]["product"], "Laptop")


class OrderViewSetTests(APITestCase):
    def setUp(self) -> None:
        self.list_url = reverse("order-list")
        self.customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            phone="555-1234",
        )
        self.order1 = Order.objects.create(
            customer=self.customer,
            product="Laptop",
            quantity=1,
        )
        self.order2 = Order.objects.create(
            customer=self.customer,
            product="Mouse",
            quantity=2,
        )
        self.detail_url = reverse("order-detail", kwargs={"pk": self.order1.pk})

    def test_list_orders(self) -> None:
        """Test retrieving all orders."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_orders_empty(self) -> None:
        """Test retrieving orders when none exist."""
        Order.objects.all().delete()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_create_order(self) -> None:
        """Test creating a new order."""
        data: dict[str, str | int] = {
            "customer": self.customer.pk,
            "product": "Keyboard",
            "quantity": 1,
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["product"], "Keyboard")
        self.assertEqual(response.data["quantity"], 1)
        self.assertEqual(Order.objects.count(), 3)

    def test_create_order_invalid_data(self) -> None:
        """Test creating an order with invalid data."""
        data: dict[str, str] = {}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 2)

    def test_create_order_invalid_customer(self) -> None:
        """Test creating an order with non-existent customer."""
        data: dict[str, str | int] = {
            "customer": 9999,
            "product": "Keyboard",
            "quantity": 1,
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_order(self) -> None:
        """Test retrieving a single order."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["product"], "Laptop")
        self.assertEqual(response.data["quantity"], 1)

    def test_retrieve_order_not_found(self) -> None:
        """Test retrieving a non-existent order."""
        url = reverse("order-detail", kwargs={"pk": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_order(self) -> None:
        """Test full update of an order."""
        data: dict[str, str | int] = {
            "customer": self.customer.pk,
            "product": "Desktop",
            "quantity": 3,
        }
        response = self.client.put(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["product"], "Desktop")
        self.assertEqual(response.data["quantity"], 3)

    def test_partial_update_order(self) -> None:
        """Test partial update of an order."""
        data: dict[str, int] = {"quantity": 5}
        response = self.client.patch(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["quantity"], 5)
        self.assertEqual(response.data["product"], "Laptop")

    def test_delete_order(self) -> None:
        """Test deleting an order."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(pk=self.order1.pk).exists())

    def test_delete_order_not_found(self) -> None:
        """Test deleting a non-existent order."""
        url = reverse("order-detail", kwargs={"pk": 9999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
