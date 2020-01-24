from django.test import TestCase, Client


class WithClient(TestCase):
    def setUp(self):
        super().setUp()
        self.client = Client()


class TestDevices(TestCase):
    def test_devices_view(self):
        response = self.client.get('/devices/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['devices']), 0)


class TestRegister(TestCase):
    pass
