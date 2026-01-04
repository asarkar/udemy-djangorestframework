from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Course


class CourseListTests(APITestCase):
    def setUp(self) -> None:
        self.url = reverse("course-list")
        self.course1 = Course.objects.create(
            name="Python Basics",
            description="Learn Python from scratch",
            rating=5,
        )
        self.course2 = Course.objects.create(
            name="Django REST Framework",
            description="Build APIs with Django",
            rating=4,
        )

    def test_get_all_courses(self) -> None:
        """Test retrieving all courses."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_courses_empty(self) -> None:
        """Test retrieving courses when none exist."""
        Course.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_post_create_course(self) -> None:
        """Test creating a new course."""
        data: dict[str, str | int] = {
            "name": "Advanced Python",
            "description": "Deep dive into Python",
            "rating": 5,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Advanced Python")
        self.assertEqual(response.data["description"], "Deep dive into Python")
        self.assertEqual(response.data["rating"], 5)
        self.assertEqual(Course.objects.count(), 3)

    def test_post_create_course_invalid_data(self) -> None:
        """Test creating a course with invalid data."""
        data: dict[str, str] = {}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Course.objects.count(), 2)

    def test_post_create_course_partial_data(self) -> None:
        """Test creating a course with partial data."""
        data: dict[str, str] = {"name": "Incomplete Course"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Course.objects.count(), 2)


class CourseDetailTests(APITestCase):
    def setUp(self) -> None:
        self.course = Course.objects.create(
            name="Python Basics",
            description="Learn Python from scratch",
            rating=5,
        )
        self.url = reverse("course-detail", kwargs={"pk": self.course.pk})

    def test_get_course_detail(self) -> None:
        """Test retrieving a single course."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Python Basics")
        self.assertEqual(response.data["description"], "Learn Python from scratch")
        self.assertEqual(response.data["rating"], 5)

    def test_get_course_not_found(self) -> None:
        """Test retrieving a non-existent course."""
        url: str = reverse("course-detail", kwargs={"pk": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_course(self) -> None:
        """Test full update of a course."""
        data: dict[str, str | int] = {
            "name": "Python Advanced",
            "description": "Updated description",
            "rating": 4,
        }
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Python Advanced")
        self.assertEqual(response.data["description"], "Updated description")
        self.assertEqual(response.data["rating"], 4)

    def test_put_course_invalid_data(self) -> None:
        """Test full update with invalid data."""
        data: dict[str, str] = {}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_course(self) -> None:
        """Test partial update of a course."""
        data: dict[str, str] = {"name": "Python Updated"}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Python Updated")
        self.assertEqual(response.data["description"], "Learn Python from scratch")

    def test_delete_course(self) -> None:
        """Test deleting a course."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(pk=self.course.pk).exists())

    def test_delete_course_not_found(self) -> None:
        """Test deleting a non-existent course."""
        url: str = reverse("course-detail", kwargs={"pk": 9999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
