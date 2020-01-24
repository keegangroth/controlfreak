from django.test import TestCase, Client
from django.contrib.auth.models import User


class WithClient(TestCase):
    def setUp(self):
        super().setUp()
        self.client = Client()


class TestDevices(TestCase):
    def test_devices_view_auth(self):
        response = self.client.get('/devices/')
        self.assertEqual(response.status_code, 403)

    def test_devices_view_auth(self):
        user = User.objects.create_user(username='fred')
        self.client.force_login(user)
        response = self.client.get('/devices/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 0)


class TestRegister(TestCase):
    pass
