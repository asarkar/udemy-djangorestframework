from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Student


class StudentPaginationTests(APITestCase):
    def setUp(self) -> None:
        self.url = reverse("student-list")
        # Create 5 students to test pagination (page_size is 2)
        for i in range(1, 6):
            Student.objects.create(
                name=f"Student {i}",
                score=Decimal(f"{80 + i}.500"),
            )

    def test_pagination_returns_correct_page_size(self) -> None:
        """Test that pagination returns correct number of items per page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_pagination_response_structure(self) -> None:
        """Test that paginated response has correct structure."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)

    def test_pagination_count(self) -> None:
        """Test that count reflects total number of items."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 5)

    def test_pagination_first_page_has_next_no_previous(self) -> None:
        """Test that first page has next link but no previous."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data["next"])
        self.assertIsNone(response.data["previous"])

    def test_pagination_second_page(self) -> None:
        """Test navigating to second page."""
        response = self.client.get(self.url, {"page": 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertIsNotNone(response.data["next"])
        self.assertIsNotNone(response.data["previous"])

    def test_pagination_last_page(self) -> None:
        """Test last page has previous but no next."""
        response = self.client.get(self.url, {"page": 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)  # Only 1 item on last page
        self.assertIsNone(response.data["next"])
        self.assertIsNotNone(response.data["previous"])

    def test_pagination_invalid_page(self) -> None:
        """Test requesting an invalid page number."""
        response = self.client.get(self.url, {"page": 999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_pagination_empty_results(self) -> None:
        """Test pagination with no items."""
        Student.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(len(response.data["results"]), 0)
        self.assertIsNone(response.data["next"])
        self.assertIsNone(response.data["previous"])

    def test_pagination_single_page(self) -> None:
        """Test pagination when all items fit on one page."""
        Student.objects.all().delete()
        Student.objects.create(name="Solo Student", score=Decimal("90.000"))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIsNone(response.data["next"])
        self.assertIsNone(response.data["previous"])

    def test_pagination_preserves_data_integrity(self) -> None:
        """Test that paginated results contain correct data."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(len(results), 2)
        # Verify each result has expected fields
        for result in results:
            self.assertIn("id", result)
            self.assertIn("name", result)
            self.assertIn("score", result)
