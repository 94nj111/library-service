from rest_framework.test import APITestCase
from user.serializers import UserSerializer


class UserSerializerTests(APITestCase):
    def test_valid_user_serializer(self):
        user_data = {
            "email": "testuser@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
        }
        serializer = UserSerializer(data=user_data)

        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, user_data["email"])
        self.assertTrue(user.check_password(user_data["password"]))

    def test_invalid_user_serializer(self):
        user_data = {
            "email": "invalidemail",
            "password": "short",
            "first_name": "Test",
            "last_name": "User",
        }
        serializer = UserSerializer(data=user_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)
        self.assertIn("password", serializer.errors)
