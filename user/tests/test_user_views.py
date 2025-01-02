from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model


class UserTests(APITestCase):
    def test_create_user(self):
        url = reverse("user:create")
        data = {
            "email": "testuser@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(email="testuser@example.com")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")

    def test_create_user_with_invalid_data(self):
        url = reverse("user:create")
        data = {
            "email": "invaliduser",
            "password": "short",
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class JWTAuthTests(APITestCase):
    def test_obtain_jwt_token(self):
        user_data = {
            "email": "testuser@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
        }
        user = get_user_model().objects.create_user(**user_data)

        url = reverse("user:token_obtain_pair")
        data = {"email": user.email, "password": "password123"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_refresh_jwt_token(self):
        user_data = {
            "email": "testuser@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
        }
        user = get_user_model().objects.create_user(**user_data)

        url = reverse("user:token_obtain_pair")
        data = {"email": user.email, "password": "password123"}
        response = self.client.post(url, data)
        refresh_token = response.data["refresh"]

        url = reverse("user:token_refresh")
        data = {"refresh": refresh_token}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)


class ManageUserTests(APITestCase):
    def setUp(self):
        self.user_data = {
            "email": "testuser@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
        }
        self.user = get_user_model().objects.create_user(**self.user_data)
        self.client.force_authenticate(user=self.user)

    def test_get_user_data(self):
        url = reverse("user:manage")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["first_name"], self.user.first_name)
        self.assertEqual(response.data["last_name"], self.user.last_name)
