import json

from server.tests.fixtures.client import ClientTestCase
from server.models import Device, DeviceId

class TestRegister(ClientTestCase):
    '''Tests fo the register view'''
    def test_non_json(self):
        '''Handle non json request gracefully'''
        response = self.client.post('/credentials/', 'hi',
                                    content_type='text/plain')
        self.assertEqual(response.status_code, 415)

    def test_missing_device_id(self):
        '''Returns 400 for missing device ids'''
        request = {}
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_missing_id_type(self):
        '''Returns 400 for missing id_type'''
        request = {'value': 'abc'}
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_invalid_id_type(self):
        '''Returns 400 for invalid id_type'''
        request = {'value': 'abc', 'id_type': 'bogus'}
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_missing_vale(self):
        '''Returns 400 for missing value'''
        request = {'id_type': 'GOOGLE_AD_ID'}
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_empty_vale(self):
        '''Returns 400 for empty value'''
        request = {'value': '', 'id_type': 'GOOGLE_AD_ID'}
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_creates_device(self):
        '''Creates a device for new device ids'''
        request = {'value': 'abc', 'id_type': 'GOOGLE_AD_ID'}
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        device = Device.objects.create(token='baz')
        device.device_ids.create(value='other', id_type='GOOGLE_AD_ID')
        self.assertEqual(response.status_code, 201)
        device = Device.objects.first()
        self.assertIsNotNone(device)
        self.assertEqual(response.json()['token'], device.token)
        self.assertEqual(device.device_ids.count(), 1)

    def test_existing_device(self):
        '''Return existing device if ids match'''
        request = {'value': 'abc', 'id_type': 'GOOGLE_AD_ID'}
        device = Device.objects.create(token='baz')
        device.device_ids.create(**request)
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['token'], device.token)


class TestRegisterMultipleIds(ClientTestCase):
    '''Test the register view with multiple device ids'''
    def test_missing_id_type(self):
        '''Returns 400 for missing id_type'''
        request = {'value': 'abc'}
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_invalid_id_type(self):
        '''Returns 400 for invalid id_type'''
        request = {'device_ids': [{'value': 'abc', 'id_type': 'bogus'}]}
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_missing_vale(self):
        '''Returns 400 for missing value'''
        request = {'device_ids': [{'id_type': 'GOOGLE_AD_ID'}]}
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_empty_vale(self):
        '''Returns 400 for empty value'''
        request = {'device_ids': [{'value': '', 'id_type': 'GOOGLE_AD_ID'}]}
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_creates_device(self):
        '''Creates a device for new device ids'''
        request = {'device_ids': [{'value': 'abc', 'id_type': 'GOOGLE_AD_ID'},
                                  {'value': 'efg', 'id_type': 'GOOGLE_AD_ID'}]}
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        device = Device.objects.first()
        self.assertIsNotNone(device)
        self.assertEqual(response.json()['token'], device.token)
        self.assertEqual(device.device_ids.count(), 2)

    def test_creates_device_multiple_fields(self):
        '''Creates a device for new device ids'''
        request = {'device_ids': [{'value': 'abc', 'id_type': 'GOOGLE_AD_ID'}],
                   'value': 'efg', 'id_type': 'GOOGLE_AD_ID'}
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        device = Device.objects.first()
        self.assertIsNotNone(device)
        self.assertEqual(response.json()['token'], device.token)
        self.assertEqual(device.device_ids.count(), 2)

    def test_duplicate_ids_in_request(self):
        '''Handles duplicate ids in the request'''
        request = {'device_ids': [{'value': 'abc', 'id_type': 'GOOGLE_AD_ID'},
                                  {'value': 'abc', 'id_type': 'GOOGLE_AD_ID'}]}
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Device.objects.count(), 0)
        self.assertEqual(DeviceId.objects.count(), 0)

    def test_existing_device(self):
        '''Return existing device if ids match'''
        request = {'device_ids': [{'value': 'abc', 'id_type': 'GOOGLE_AD_ID'},
                                  {'value': 'efg', 'id_type': 'GOOGLE_AD_ID'}]}
        device = Device.objects.create(token='baz')
        Device.objects.create(token='bar')
        device.device_ids.create(**request['device_ids'][0])
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['token'], device.token)

    def test_existing_device_multiple_ids(self):
        '''Return existing device if ids match'''
        request = {'device_ids': [{'value': 'abc', 'id_type': 'GOOGLE_AD_ID'},
                                  {'value': 'efg', 'id_type': 'GOOGLE_AD_ID'}]}
        device = Device.objects.create(token='baz')
        Device.objects.create(token='bar').device_ids.create(value='other',
                                                             id_type='GOOGLE_AD_ID')
        for did in request['device_ids']:
            device.device_ids.create(**did)
        response = self.client.post('/register/',
                                    json.dumps(request),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['token'], device.token)
