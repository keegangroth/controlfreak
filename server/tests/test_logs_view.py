'''Tests of the /logs apis'''

import json

from server.tests.fixtures.client import ClientTestCase
from server.tests.fixtures.token import TokenFixture

from server.models import App, Log


class TestLogView(ClientTestCase, TokenFixture):
    '''Tests of the logs view'''
    def test_non_json(self):
        '''Handle non json request gracefully'''
        response = self.client.post('/logs/', 'hi',
                                    content_type='text/plain')
        self.assertEqual(response.status_code, 415)

    def test_without_token(self):
        '''Returns 404 when no token is provided'''
        response = self.client.post('/logs/',
                                    json.dumps({}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_invalid_token(self):
        '''Returns 404 when the token does not exist'''
        response = self.client.post('/logs/',
                                    json.dumps({'token': 'bogus'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_missing_log(self):
        '''Returns 400 when no log is provided'''
        response = self.client.post('/logs/',
                                    json.dumps({'token': self.token}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_creates_log(self):
        '''Creates a log if none exists'''
        text = 'baz'
        response = self.client.post('/logs/',
                                    json.dumps({'token': self.token,
                                                'log': text}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Log.objects.count(), 1)
        self.assertEqual(self.device.logs.first().text, text)

    def test_creates_log_for_each_app(self):
        '''Creates separate logs for each app'''
        app2 = App.objects.create(name='app2', api_key='blah')
        self.device.logs.create(text='foo', app=app2)
        text = 'baz'
        response = self.client.post('/logs/',
                                    json.dumps({'token': self.token,
                                                'log': text}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Log.objects.count(), 2)
        self.assertEqual(self.device.logs.get(app=self.app).text, text)

    def test_updates_existing_log(self):
        '''Appends to log if one already exists'''
        text = 'baz'
        Log.objects.create(device=self.device, app=self.app, text=text)
        response = self.client.post('/logs/',
                                    json.dumps({'token': self.token,
                                                'log': text}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Log.objects.count(), 1)
        self.assertEqual(self.device.logs.first().text, text*2)


class TestLogCleaarView(ClientTestCase, TokenFixture):
    '''Tests of the logs/clear view'''
    def test_non_json(self):
        '''Handle non json request gracefully'''
        response = self.client.post('/logs/clear/', 'hi',
                                    content_type='text/plain')
        self.assertEqual(response.status_code, 415)

    def test_without_token(self):
        '''Returns 404 when no token is provided'''
        response = self.client.post('/logs/clear/',
                                    json.dumps({}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_invalid_token(self):
        '''Returns 404 when the token does not exist'''
        response = self.client.post('/logs/clear/',
                                    json.dumps({'token': 'bogus'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_with_no_log(self):
        '''Succeeds with no log records'''
        response = self.client.post('/logs/clear/',
                                    json.dumps({'token': self.token}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_deletes_log(self):
        '''Removes log record'''
        app2 = App.objects.create(name='app2', api_key='blah')
        Log.objects.create(text='', device=self.device, app=app2)
        Log.objects.create(text='', device=self.device, app=self.app)
        response = self.client.post('/logs/clear/',
                                    json.dumps({'token': self.token}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.device.logs.count(), 1)
        self.assertEqual(self.device.logs.first().app, app2)
