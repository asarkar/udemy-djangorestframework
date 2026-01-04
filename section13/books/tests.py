from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Author, Book


class AuthorAuthenticationTests(APITestCase):
    """Test global and view-level authentication for AuthorViewSet."""

    def setUp(self) -> None:
        self.list_url = reverse("author-list")
        self.author = Author.objects.create(first_name="John", last_name="Doe")
        self.detail_url = reverse("author-detail", kwargs={"pk": self.author.pk})

        # Create user with only view permission
        self.viewer = User.objects.create_user(username="viewer", password="testpass123")
        # `ContentType` uniquely identifies a model across the entire Django project,
        # and permissions are linked to models via their content type.
        # Django's permission system creates 4 default permissions per model:
        # - add_author
        # - change_author
        # - delete_author
        # - view_author
        # These are stored in the `Permission` table with a foreign key to `ContentType`.
        # To find a specific permission, we need to specify which model it belongs to.
        # We can get the `ContentType` for the Author model using the `get_for_model` method.
        # This returns a ContentType object representing the `Author` model. It contains:
        # - app_label: "books" (the app name)
        # - model: "author" (the model name, lowercase)
        content_type = ContentType.objects.get_for_model(Author)
        view_permission = Permission.objects.get(codename="view_author", content_type=content_type)
        self.viewer.user_permissions.add(view_permission)

        # Create staff user (has all model permissions via is_staff)
        self.staff = User.objects.create_user(
            username="staff", password="staffpass123", is_staff=True
        )
        all_permissions = Permission.objects.filter(content_type=content_type)
        self.staff.user_permissions.set(all_permissions)

    # --- Unauthenticated access tests (global auth) ---

    def test_unauthenticated_list_denied(self) -> None:
        """Test that unauthenticated users cannot list authors."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_retrieve_denied(self) -> None:
        """Test that unauthenticated users cannot retrieve an author."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_create_denied(self) -> None:
        """Test that unauthenticated users cannot create an author."""
        data = {"first_name": "Jane", "last_name": "Smith"}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_update_denied(self) -> None:
        """Test that unauthenticated users cannot update an author."""
        data = {"first_name": "Updated", "last_name": "Name"}
        response = self.client.put(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_delete_denied(self) -> None:
        """Test that unauthenticated users cannot delete an author."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- View-only user tests (DjangoModelPermissions) ---

    def test_viewer_can_list_authors(self) -> None:
        """Test that user with view permission can list authors."""
        self.client.force_authenticate(user=self.viewer)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_viewer_can_retrieve_author(self) -> None:
        """Test that user with view permission can retrieve an author."""
        self.client.force_authenticate(user=self.viewer)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "John")

    def test_viewer_cannot_create_author(self) -> None:
        """Test that user with only view permission cannot create an author."""
        self.client.force_authenticate(user=self.viewer)
        data = {"first_name": "Jane", "last_name": "Smith"}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_cannot_update_author(self) -> None:
        """Test that user with only view permission cannot update an author."""
        self.client.force_authenticate(user=self.viewer)
        data = {"first_name": "Updated", "last_name": "Name"}
        response = self.client.put(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_cannot_partial_update_author(self) -> None:
        """Test that user with only view permission cannot patch an author."""
        self.client.force_authenticate(user=self.viewer)
        data = {"first_name": "Updated"}
        response = self.client.patch(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_cannot_delete_author(self) -> None:
        """Test that user with only view permission cannot delete an author."""
        self.client.force_authenticate(user=self.viewer)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- Staff user tests (all permissions) ---

    def test_staff_can_create_author(self) -> None:
        """Test that staff user with add permission can create an author."""
        self.client.force_authenticate(user=self.staff)
        data = {"first_name": "Jane", "last_name": "Smith"}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_staff_can_update_author(self) -> None:
        """Test that staff user with change permission can update an author."""
        self.client.force_authenticate(user=self.staff)
        data = {"first_name": "Updated", "last_name": "Name"}
        response = self.client.put(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_staff_can_partial_update_author(self) -> None:
        """Test that staff user with change permission can patch an author."""
        self.client.force_authenticate(user=self.staff)
        data = {"first_name": "Patched"}
        response = self.client.patch(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_staff_can_delete_author(self) -> None:
        """Test that staff user with delete permission can delete an author."""
        self.client.force_authenticate(user=self.staff)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class BookAuthenticationTests(APITestCase):
    """Test global authentication for BookViewSet (no view-level DjangoModelPermissions)."""

    def setUp(self) -> None:
        self.author = Author.objects.create(first_name="John", last_name="Doe")
        self.book = Book.objects.create(title="Test Book", rating=5, author=self.author)
        self.list_url = reverse("book-list")
        self.detail_url = reverse("book-detail", kwargs={"pk": self.book.pk})

        # Create a basic authenticated user (no special permissions needed)
        self.user = User.objects.create_user(username="user", password="testpass123")

    # --- Unauthenticated access tests (global auth) ---

    def test_unauthenticated_list_denied(self) -> None:
        """Test that unauthenticated users cannot list books."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_retrieve_denied(self) -> None:
        """Test that unauthenticated users cannot retrieve a book."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_create_denied(self) -> None:
        """Test that unauthenticated users cannot create a book."""
        data = {"title": "New Book", "rating": 4, "author": self.author.pk}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_update_denied(self) -> None:
        """Test that unauthenticated users cannot update a book."""
        data = {"title": "Updated Book", "rating": 3, "author": self.author.pk}
        response = self.client.put(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_partial_update_denied(self) -> None:
        """Test that unauthenticated users cannot patch a book."""
        data = {"title": "Patched Book"}
        response = self.client.patch(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_delete_denied(self) -> None:
        """Test that unauthenticated users cannot delete a book."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Authenticated user tests (global IsAuthenticated only) ---

    def test_authenticated_user_can_list_books(self) -> None:
        """Test that authenticated user can list books."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_user_can_retrieve_book(self) -> None:
        """Test that authenticated user can retrieve a book."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_user_can_create_book(self) -> None:
        """Test that authenticated user can create a book (no model permissions required)."""
        self.client.force_authenticate(user=self.user)
        data = {"title": "New Book", "rating": 4, "author": self.author.pk}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_authenticated_user_can_update_book(self) -> None:
        """Test that authenticated user can update a book."""
        self.client.force_authenticate(user=self.user)
        data = {"title": "Updated Book", "rating": 3, "author": self.author.pk}
        response = self.client.put(self.detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_user_can_delete_book(self) -> None:
        """Test that authenticated user can delete a book."""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
