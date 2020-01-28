'''Tests of the /register api'''

import json

from server.tests.fixtures.client import ClientTestCase
from server.models import App, Device, DeviceId, Token

class TestRegister(ClientTestCase):
    '''Tests fo the register view'''
    def setUp(self):
        super().setUp()
        self.app = App.objects.create(name='foo', api_key='bar')

    def test_non_json(self):
        '''Handle non json request gracefully'''
        response = self.client.post('/credentials/', 'hi',
                                    content_type='text/plain')
        self.assertEqual(response.status_code, 415)

    def test_missing_app_guid(self):
        '''Returns 403 for missing device ids'''
        request = {}
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_invalid_app_guid(self):
        '''Returns 403 for missing device ids'''
        request = {'app_guid': 'bogus'}
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_missing_device_id(self):
        '''Returns 400 for missing device ids'''
        request = {'app_guid': self.app.api_key}
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertTrue('device_ids' in response.json())

    def test_missing_id_type(self):
        '''Returns 400 for missing id_type'''
        request = {'app_guid': self.app.api_key,
                   'value': 'abc'}
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertTrue('device_ids' in response.json())

    def test_invalid_id_type(self):
        '''Returns 400 for invalid id_type'''
        request = {'app_guid': self.app.api_key,
                   'value': 'abc',
                   'id_type': 'bogus'}
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertTrue('device_ids' in response.json())

    def test_missing_value(self):
        '''Returns 400 for missing value'''
        request = {'app_guid': self.app.api_key,
                   'id_type': 'GOOGLE_AD_ID'}
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertTrue('device_ids' in response.json())

    def test_empty_value(self):
        '''Returns 400 for empty value'''
        request = {'app_guid': self.app.api_key,
                   'value': '',
                   'id_type': 'GOOGLE_AD_ID'}
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertTrue('device_ids' in response.json())

    def test_creates_device(self):
        '''Creates a device for new device ids'''
        request = {'app_guid': self.app.api_key,
                   'value': 'abc',
                   'id_type': 'GOOGLE_AD_ID'}
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        device = Device.objects.first()
        token = device.tokens.get(app=self.app)
        self.assertIsNotNone(device)
        self.assertEqual(response.json()['token'], token.token)
        self.assertEqual(response.json()['id'], device.pk)
        self.assertEqual(device.device_ids.count(), 1)

    def test_existing_device(self):
        '''Return existing device if ids match'''
        request = {'app_guid': self.app.api_key,
                   'value': 'abc',
                   'id_type': 'GOOGLE_AD_ID'}
        # create a "wrong" device it should not find
        Device.objects.create()
        device = Device.objects.create()
        token = device.tokens.create(app=self.app, token='baz')
        device.device_ids.create(value=request['value'],
                                 id_type=request['id_type'])
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['token'], token.token)
        self.assertEqual(response.json()['id'], device.pk)

    def test_existing_device_new_token(self):
        '''Return existing device if ids match'''
        request = {'app_guid': self.app.api_key,
                   'value': 'abc',
                   'id_type': 'GOOGLE_AD_ID'}
        device = Device.objects.create()
        device.device_ids.create(value=request['value'],
                                 id_type=request['id_type'])
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        token = device.tokens.get(app=self.app)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['token'], token.token)
        self.assertEqual(response.json()['id'], device.pk)

    def test_multiple_apps(self):
        '''Return existing device if ids match'''
        request = {'app_guid': self.app.api_key,
                   'value': 'abc',
                   'id_type': 'GOOGLE_AD_ID'}
        device = Device.objects.create()
        device.device_ids.create(value=request['value'],
                                 id_type=request['id_type'])
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        token = device.tokens.get(app=self.app)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['token'], token.token)
        self.assertEqual(response.json()['id'], device.pk)
        app2 = App.objects.create(name='oof', api_key='rab')
        request['app_guid'] = app2.api_key
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        token2 = device.tokens.get(app=app2)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['token'], token2.token)
        self.assertEqual(response.json()['id'], device.pk)
        self.assertNotEqual(token.token, token2.token)


class TestRegisterMultipleIds(ClientTestCase):
    '''Test the register view with multiple device ids'''
    def setUp(self):
        super().setUp()
        self.app = App.objects.create(name='foo', api_key='bar')

    def test_missing_id_type(self):
        '''Returns 400 for missing id_type'''
        request = {'app_guid': self.app.api_key,
                   'device_ids': [{'value': 'abc'}]}
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertTrue('device_ids' in response.json())

    def test_invalid_id_type(self):
        '''Returns 400 for invalid id_type'''
        request = {'app_guid': self.app.api_key,
                   'device_ids': [{'value': 'abc', 'id_type': 'bogus'}]}
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertTrue('device_ids' in response.json())

    def test_missing_value(self):
        '''Returns 400 for missing value'''
        request = {'app_guid': self.app.api_key,
                   'device_ids': [{'id_type': 'GOOGLE_AD_ID'}]}
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertTrue('device_ids' in response.json())

    def test_empty_value(self):
        '''Returns 400 for empty value'''
        request = {'app_guid': self.app.api_key,
                   'device_ids': [{'value': '', 'id_type': 'GOOGLE_AD_ID'}]}
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertTrue('device_ids' in response.json())

    def test_creates_device(self):
        '''Creates a device for new device ids'''
        request = {'app_guid': self.app.api_key,
                   'device_ids': [{'value': 'abc', 'id_type': 'GOOGLE_AD_ID'},
                                  {'value': 'efg', 'id_type': 'GOOGLE_AD_ID'}]}
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        device = Device.objects.first()
        token = device.tokens.get(app=self.app)
        self.assertIsNotNone(device)
        self.assertEqual(response.json()['token'], token.token)
        self.assertEqual(response.json()['id'], device.pk)
        self.assertEqual(device.device_ids.count(), 2)

    def test_creates_device_multiple_fields(self):
        '''Creates a device for new device ids'''
        request = {'app_guid': self.app.api_key,
                   'device_ids': [{'value': 'abc', 'id_type': 'GOOGLE_AD_ID'}],
                   'value': 'efg', 'id_type': 'GOOGLE_AD_ID'}
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        device = Device.objects.first()
        token = device.tokens.get(app=self.app)
        self.assertIsNotNone(device)
        self.assertEqual(response.json()['token'], token.token)
        self.assertEqual(response.json()['id'], device.pk)
        self.assertEqual(device.device_ids.count(), 2)

    def test_duplicate_ids_in_request(self):
        '''Handles duplicate ids in the request'''
        request = {'app_guid': self.app.api_key,
                   'device_ids': [{'value': 'abc', 'id_type': 'GOOGLE_AD_ID'},
                                  {'value': 'abc', 'id_type': 'GOOGLE_AD_ID'}]}
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertTrue('errors' in response.json())
        self.assertEqual(Device.objects.count(), 0)
        self.assertEqual(Token.objects.count(), 0)
        self.assertEqual(DeviceId.objects.count(), 0)

    def test_existing_device(self):
        '''Return existing device if ids match'''
        request = {'app_guid': self.app.api_key,
                   'device_ids': [{'value': 'abc', 'id_type': 'GOOGLE_AD_ID'},
                                  {'value': 'efg', 'id_type': 'GOOGLE_AD_ID'}]}
        # create a "wrong" device it should not find
        Device.objects.create()
        device = Device.objects.create()
        device.device_ids.create(**request['device_ids'][0])
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        token = device.tokens.get(app=self.app)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['token'], token.token)
        self.assertEqual(response.json()['id'], device.pk)

    def test_existing_device_multiple_ids(self):
        '''Return existing device if ids match'''
        request = {'app_guid': self.app.api_key,
                   'device_ids': [{'value': 'abc', 'id_type': 'GOOGLE_AD_ID'},
                                  {'value': 'efg', 'id_type': 'GOOGLE_AD_ID'}]}
        device = Device.objects.create()
        Device.objects.create().device_ids.create(value='other',
                                                  id_type='GOOGLE_AD_ID')
        for did in request['device_ids']:
            device.device_ids.create(**did)
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        token = device.tokens.get(app=self.app)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['token'], token.token)
        self.assertEqual(response.json()['id'], device.pk)
