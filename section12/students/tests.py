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
        response = self.client.get(self.url, {"page": "2"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertIsNotNone(response.data["next"])
        self.assertIsNotNone(response.data["previous"])

    def test_pagination_last_page(self) -> None:
        """Test last page has previous but no next."""
        response = self.client.get(self.url, {"page": "3"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)  # Only 1 item on last page
        self.assertIsNone(response.data["next"])
        self.assertIsNotNone(response.data["previous"])

    def test_pagination_invalid_page(self) -> None:
        """Test requesting an invalid page number."""
        response = self.client.get(self.url, {"page": "999"})
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


class StudentSearchFilterTests(APITestCase):
    def setUp(self) -> None:
        self.url = reverse("student-list")
        Student.objects.create(name="Alice Johnson", score=Decimal("95.500"))
        Student.objects.create(name="Bob Smith", score=Decimal("87.250"))
        Student.objects.create(name="Charlie Brown", score=Decimal("92.000"))
        Student.objects.create(name="Alice Williams", score=Decimal("88.750"))

    def test_search_by_name(self) -> None:
        """Test searching students by name."""
        response = self.client.get(self.url, {"search": "Alice"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        for result in response.data["results"]:
            self.assertIn("Alice", result["name"])

    def test_search_by_partial_name(self) -> None:
        """Test searching with partial name match."""
        response = self.client.get(self.url, {"search": "son"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "Alice Johnson")

    def test_search_case_insensitive(self) -> None:
        """Test that search is case insensitive."""
        response = self.client.get(self.url, {"search": "alice"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_search_by_score(self) -> None:
        """Test searching by score field."""
        response = self.client.get(self.url, {"search": "95.5"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "Alice Johnson")

    def test_search_no_results(self) -> None:
        """Test search with no matching results."""
        response = self.client.get(self.url, {"search": "Nonexistent"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(len(response.data["results"]), 0)

    def test_search_empty_query(self) -> None:
        """Test search with empty query returns all results."""
        response = self.client.get(self.url, {"search": ""})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 4)


class StudentOrderingFilterTests(APITestCase):
    def setUp(self) -> None:
        self.url = reverse("student-list")
        Student.objects.create(name="Charlie", score=Decimal("85.000"))
        Student.objects.create(name="Alice", score=Decimal("95.000"))
        Student.objects.create(name="Bob", score=Decimal("90.000"))

    def test_ordering_by_name_ascending(self) -> None:
        """Test ordering by name ascending."""
        response = self.client.get(self.url, {"ordering": "name"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [r["name"] for r in response.data["results"]]
        self.assertEqual(names, ["Alice", "Bob"])  # page_size is 2

    def test_ordering_by_name_descending(self) -> None:
        """Test ordering by name descending."""
        response = self.client.get(self.url, {"ordering": "-name"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [r["name"] for r in response.data["results"]]
        self.assertEqual(names, ["Charlie", "Bob"])

    def test_ordering_by_score_ascending(self) -> None:
        """Test ordering by score ascending."""
        response = self.client.get(self.url, {"ordering": "score"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        scores = [r["score"] for r in response.data["results"]]
        self.assertEqual(scores, ["85.000", "90.000"])

    def test_ordering_by_score_descending(self) -> None:
        """Test ordering by score descending."""
        response = self.client.get(self.url, {"ordering": "-score"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        scores = [r["score"] for r in response.data["results"]]
        self.assertEqual(scores, ["95.000", "90.000"])

    def test_ordering_invalid_field_ignored(self) -> None:
        """Test that ordering by invalid field is ignored."""
        response = self.client.get(self.url, {"ordering": "invalid_field"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Falls back to default ordering (by id)
        self.assertEqual(response.data["count"], 3)

    def test_default_ordering(self) -> None:
        """Test default ordering when no ordering param provided."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Default ordering is by id (from model Meta)
        ids = [r["id"] for r in response.data["results"]]
        self.assertEqual(ids, sorted(ids))


class StudentCombinedFilterTests(APITestCase):
    def setUp(self) -> None:
        self.url = reverse("student-list")
        Student.objects.create(name="Alice Johnson", score=Decimal("95.000"))
        Student.objects.create(name="Alice Smith", score=Decimal("85.000"))
        Student.objects.create(name="Bob Johnson", score=Decimal("90.000"))
        Student.objects.create(name="Alice Brown", score=Decimal("92.000"))

    def test_search_and_ordering_combined(self) -> None:
        """Test combining search and ordering filters."""
        response = self.client.get(self.url, {"search": "Alice", "ordering": "-score"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)
        results = response.data["results"]
        # Should be Alice entries ordered by score descending
        self.assertEqual(results[0]["name"], "Alice Johnson")  # 95
        self.assertEqual(results[1]["name"], "Alice Brown")  # 92

    def test_search_ordering_and_pagination(self) -> None:
        """Test search, ordering, and pagination together."""
        response = self.client.get(self.url, {"search": "Alice", "ordering": "score", "page": "2"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 3 Alice entries, page_size 2, page 2 should have 1 result
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Alice Johnson")  # highest score
