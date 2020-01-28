'''Tests of the /credentials api'''

import json

from server.tests.fixtures.client import ClientTestCase
from server.tests.fixtures.token import TokenFixture

from server.models import App, Credential


class TestCredentialView(ClientTestCase, TokenFixture):
    '''Tests of the logs view'''
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
        request = {'token': self.token,
                   'user': 'baz'}
        response = self.client.post('/credentials/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_missing_user(self):
        '''Returns 400 for missing parameter'''
        request = {'token': self.token,
                   'target': 'baz'}
        response = self.client.post('/credentials/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_creates_new(self):
        '''Creates a new credential if none exists'''
        request = {'token': self.token,
                   'target': 'baz',
                   'user': 'fred',
                   'secret': 'aswd'}
        response = self.client.post('/credentials/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.device.credentials.count(), 1)
        new_credential = self.device.credentials.first()
        self.assertEqual(new_credential.user, request['user'])
        self.assertEqual(new_credential.target, request['target'])
        self.assertEqual(new_credential.secret, request['secret'])

    def test_creates_new_for_each_app(self):
        '''Creates separate credential for each app'''
        app2 = App.objects.create(name='app2', api_key='blah')
        self.device.credentials.create(target='zab',
                                       user='fred',
                                       secret='aswd',
                                       app=app2)
        request = {'token': self.token,
                   'target': 'baz',
                   'user': 'fred',
                   'secret': 'aswd'}
        response = self.client.post('/credentials/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Credential.objects.count(), 2)
        new_credential = self.device.credentials.get(app=self.app)
        self.assertEqual(new_credential.user, request['user'])
        self.assertEqual(new_credential.target, request['target'])
        self.assertEqual(new_credential.secret, request['secret'])

    def test_updates_existing(self):
        '''Updates an existing credential'''
        credential = self.device.credentials.create(target='baz',
                                                    user='fred',
                                                    secret='aswd')
        request = {'token': self.token,
                   'target': credential.target,
                   'user': credential.user,
                   'secret': 'new'}
        response = self.client.post('/credentials/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        credential.refresh_from_db()
        self.assertEqual(credential.secret, 'new')

    def test_updates_existing_across_apps(self):
        '''Updates an existing credential'''
        app2 = App.objects.create(name='app2', api_key='blah')
        credential = self.device.credentials.create(app=app2,
                                                    target='baz',
                                                    user='fred',
                                                    secret='aswd')
        request = {'token': self.token,
                   'target': credential.target,
                   'user': credential.user,
                   'secret': 'new'}
        response = self.client.post('/credentials/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        credential.refresh_from_db()
        self.assertEqual(credential.secret, 'new')
        self.assertEqual(credential.app, self.app)
