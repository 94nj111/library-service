from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

BOOK_URL = reverse("book_service:book-list")


def sample_book(**params):
    data = {
        "title": "New Book",
        "author": "Author",
        "cover": "HARD",
        "inventory": 100,
        "daily_free": "50.00"
    }
    data.update(params)
    return data


class BookViewSetTests(APITestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            "admin@test.com", "adminpass"
        )
        self.user = get_user_model().objects.create_user(
            "user@test.com", "userpass"
        )

    def test_list_books_unauthenticated(self):
        response = self.client.get(BOOK_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_book_unauthenticated(self):
        data = sample_book()
        response = self.client.post(BOOK_URL, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_book_as_user(self):
        self.client.force_authenticate(user=self.user)
        data = sample_book()
        response = self.client.post(BOOK_URL, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_book_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = sample_book()
        response = self.client.post(BOOK_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
