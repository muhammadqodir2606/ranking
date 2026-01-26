from django.contrib.auth import get_user_model
from django.core import mail
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

User = get_user_model()


class RegisterTest(APITestCase):

    def test_register_sends_email(self):
        url = reverse("register")

        data = {
            "email": "test@mail.com",
            "username": "test",
            "password": "A12345678",
            "first_name": "Muhammadqodir",
            "last_name": "Jalilov"
        }

        r1 = self.client.post(url, data)
        self.assertEqual(r1.status_code, status.HTTP_200_OK)

        user = User.objects.get(email="test@mail.com")
        self.assertFalse(user.is_verified)
        self.assertFalse(user.is_active)

        r2 = self.client.post(url, data)
        self.assertEqual(r2.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(r2.data.get('message'), "Verification already sent, please wait.")


class LoginTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test",
            first_name="Muhammadqodir",
            last_name="jalilov",
            email="jalilovm54@gmail.com"
        )
        self.user.set_password("A12345678")
        self.user.save()

    def test_login_successful(self):
        url = reverse("login")
        data = {
            "username": "test",
            "password": "A12345678"
        }
        r = self.client.post(url, data)

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertSetEqual(
            set(r.data.keys()),
            {"access", "refresh"}
        )

    def test_login_invalid_password(self):
        url = reverse("login")
        data = {
            "username": "test",
            "password": "B87654321"
        }
        r = self.client.post(url, data)
        print(r.data)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

