from django.contrib.auth.models import User
from server.tests.fixtures.client import ClientTestCase

class TestDevices(ClientTestCase):
    def test_devices_view_no_auth(self):
        response = self.client.get('/devices/')
        self.assertEqual(response.status_code, 403)

    def test_devices_view_auth(self):
        user = User.objects.create_user(username='fred')
        self.client.force_login(user)
        response = self.client.get('/devices/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 0)
