from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError


class UserModelTests(TestCase):
    def test_create_user_with_email(self):
        email = "testuser@example.com"
        password = "password123"
        user = get_user_model().objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(
            user.check_password(password)
        )  # Перевірка, що пароль правильно зашифрований

    def test_create_user_with_duplicate_email(self):
        email = "testuser@example.com"
        password = "password123"
        get_user_model().objects.create_user(email=email, password=password)

        with self.assertRaises(IntegrityError):
            get_user_model().objects.create_user(email=email, password="newpassword123")

    def test_user_str_method(self):
        email = "testuser@example.com"
        password = "password123"
        user = get_user_model().objects.create_user(email=email, password=password)

        self.assertEqual(str(user), f"{user.email}: {user.first_name} {user.last_name}")
