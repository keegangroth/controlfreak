from django.test import TestCase, Client


class ClientTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.client = Client()
