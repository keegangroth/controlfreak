'''Tests of the /devices apis'''

from server.tests.fixtures.client import ClientTestCase, LoggedInTestCase

from server.models import Device


class TestDevicesLoggedOut(ClientTestCase):
    '''Tests that the devices views are properly protected'''
    def test_devices(self):
        '''Devices view should return 403 when not logged in'''
        response = self.client.get('/devices/')
        self.assertEqual(response.status_code, 403)

    def test_devices_detail(self):
        '''Devices detail view should return 403 when not logged in'''
        response = self.client.get('/devices/42/')
        self.assertEqual(response.status_code, 403)

    def test_devices_live(self):
        '''Devices live view should return 403 when not logged in'''
        response = self.client.get('/devices/42/live/')
        self.assertEqual(response.status_code, 403)


class TestDevices(LoggedInTestCase):
    '''Tests of the devices view'''
    def test_rejects_post(self):
        '''Does not accept POSTs'''
        response = self.client.post('/devices/')
        self.assertEqual(response.status_code, 405)

    def test_no_devices(self):
        '''Returns 200 and a response even with no devices'''
        response = self.client.get('/devices/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 0)
        self.assertEqual(response.json()['count'], 0)

    def test_devices(self):
        '''With devices, returns them in the expected format'''
        Device.objects.create(token='foo')
        Device.objects.create(token='bar')
        response = self.client.get('/devices/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 2)
        self.assertEqual(response.json()['count'], 2)
        tokens = [r['token'] for r in response.json()['results']]
        # fancy wy of checking that no records are repeated
        self.assertEqual(sorted(tokens), sorted([*{*tokens}]))
        for result_device in response.json()['results']:
            self.assertIsNotNone(Device.objects.get(token=result_device['token']))


class TestDevicesDetail(LoggedInTestCase):
    '''Tests of the devices detail view'''
    def test_rejects_post(self):
        '''Does not accept POSTs'''
        response = self.client.post('/devices/42/')
        self.assertEqual(response.status_code, 405)

    def test_invalid_id(self):
        '''Returns 404 when device does not exist'''
        response = self.client.get('/devices/42/')
        self.assertEqual(response.status_code, 404)

    def test_devices_detail(self):
        '''Returns device info and associations'''
        device = Device.objects.create(token='foo')
        response = self.client.get('/devices/%s/' % device.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['token'], device.token)
        self.assertEqual(response.json()['device_ids'], [])
        self.assertEqual(response.json()['logs'], [])
        self.assertEqual(response.json()['credentials'], [])

    def test_device_logs(self):
        '''Returns device logs'''
        device = Device.objects.create(token='foo')
        device.logs.create(text='bar')
        response = self.client.get('/devices/%s/' % device.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['logs'], ['bar'])

    def test_device_credentials(self):
        '''Returns device credentials'''
        device = Device.objects.create(token='foo')
        creds = {'user': 'bar', 'target': 'baz', 'secret': '123'}
        device.credentials.create(**creds)
        response = self.client.get('/devices/%s/' % device.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['credentials'], [creds])

    def test_device_device_ids(self):
        '''Returns device device_ids'''
        device = Device.objects.create(token='foo')
        device_id = {'id_type': 'GOOGLE_AD_ID', 'value': 'bar'}
        device.device_ids.create(**device_id)
        response = self.client.get('/devices/%s/' % device.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['device_ids'], [device_id])


class TestDevicesLive(LoggedInTestCase):
    '''Tests of the devices live view'''
    def test_rejects_post(self):
        '''Does not accept POSTs'''
        response = self.client.post('/devices/42/live/')
        self.assertEqual(response.status_code, 405)

    def test_invalid_id(self):
        '''Returns 404 when device does not exist'''
        response = self.client.get('/devices/42/live/')
        self.assertEqual(response.status_code, 404)

    def test_device_live(self):
        '''Renders the proper template'''
        device = Device.objects.create(token='foo')
        response = self.client.get('/devices/%s/live/' % device.pk)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'controlfreak/live_device.html')
