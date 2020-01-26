from django.contrib.auth.models import User
from django.test import TestCase, Client


class ClientTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.client = Client()

class LoggedInTestCase(TestCase):
    def setUp(self):
        super().setUp()
        user = User.objects.create_user(username='fred')
        self.client.force_login(user)
