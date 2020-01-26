'''Tests of the /credentials api'''

import json

from server.tests.fixtures.client import ClientTestCase
from server.models import Device


class TestLogView(ClientTestCase):
    '''Tests of the logs view'''
    def setUp(self):
        super().setUp()
        self.device = Device.objects.create(token='foo')

    def test_non_json(self):
        '''Handle non json request gracefully'''
        response = self.client.post('/credentials/', 'hi',
                                    content_type='text/plain')
        self.assertEqual(response.status_code, 415)

    def test_without_token(self):
        '''Returns 404 when no token is provided'''
        response = self.client.post('/credentials/',
                                    json.dumps({}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_invalid_token(self):
        '''Returns 404 when the token does not exist'''
        response = self.client.post('/credentials/',
                                    json.dumps({'token': 'bogus'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_missing_target(self):
        '''Returns 400 for missing parameter'''
        request = {'token': self.device.token,
                   'user': 'baz'}
        response = self.client.post('/credentials/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_missing_user(self):
        '''Returns 400 for missing parameter'''
        request = {'token': self.device.token,
                   'target': 'baz'}
        response = self.client.post('/credentials/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_creates_new(self):
        '''Creates a new credential if none exists'''
        request = {'token': self.device.token,
                   'target': 'baz',
                   'user': 'fred',
                   'secret': 'aswd'}
        response = self.client.post('/credentials/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.device.credentials.count(), 1)
        new_credential = self.device.credentials.first()
        self.assertEqual(new_credential.user, 'fred')
        self.assertEqual(new_credential.target, 'baz')
        self.assertEqual(new_credential.secret, 'aswd')

    def test_updates_existing(self):
        '''Updates an existing credential'''
        credential = self.device.credentials.create(target='baz',
                                                    user='fred',
                                                    secret='aswd')
        request = {'token': self.device.token,
                   'target': credential.target,
                   'user': credential.user,
                   'secret': 'new'}
        response = self.client.post('/credentials/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        credential.refresh_from_db()
        self.assertEqual(credential.secret, 'new')
