import json

from server.tests.fixtures.client import ClientTestCase

from server.models import Device, Log


class TestLogView(ClientTestCase):
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
        device = Device.objects.create(token='foo')
        response = self.client.post('/logs/',
                                    json.dumps({'token': device.token}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_creates_log(self):
        '''Creates a log if none exists'''
        text = 'baz'
        device = Device.objects.create(token='foo')
        response = self.client.post('/logs/',
                                    json.dumps({'token': device.token,
                                                'log': text}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Log.objects.count(), 1)
        self.assertEqual(device.logs.first().text, text)

    def test_updates_existing_log(self):
        '''Appends to log if one already exists'''
        text = 'baz'
        device = Device.objects.create(token='foo')
        Log.objects.create(device=device, text=text)
        response = self.client.post('/logs/',
                                    json.dumps({'token': device.token,
                                                'log': text}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Log.objects.count(), 1)
        self.assertEqual(device.logs.first().text, text*2)


class TestLogCleaarView(ClientTestCase):
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
        device = Device.objects.create(token='foo')
        response = self.client.post('/logs/clear/',
                                    json.dumps({'token': device.token}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_deletes_log(self):
        '''Removes log record'''
        device = Device.objects.create(token='foo')
        Log.objects.create(text='', device=device)
        response = self.client.post('/logs/clear/',
                                    json.dumps({'token': device.token}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(device.logs.count(), 0)
