from django.test import TestCase

from server.models import App, Device


class TokenFixture(TestCase):
    '''Fixture to create a token for api requests'''
    def setUp(self):
        super().setUp()
        self.app = App.objects.create(name='app', api_key='appapikey')
        self.device = Device.objects.create()
        self.token = self.device.tokens.create(app=self.app, token='foo').token
