from django.test import TestCase
from django.db.utils import IntegrityError

from server.models import Device, Log, Credential, DeviceId


class TestDevice(TestCase):
    '''Tests of the Device model'''
    def test_create(self):
        '''Create and get work'''
        Device.objects.create(token='abc')
        self.assertIsNotNone(Device.objects.get(token='abc'))

    def test_token_unique(self):
        '''Create should reject duplicate tokens'''
        Device.objects.create(token='abc')
        with self.assertRaises(IntegrityError):
            Device.objects.create(token='abc')

    def test_create_ids(self):
        '''Given a hash, creates a new device id'''
        device = Device.objects.create(token='abc')
        device.create_device_ids([{'value': 'foo', 'id_type': 'GOOGLE_AD_ID'}])
        self.assertEqual(device.device_ids.count(), 1)

    def test_create_ids_validates(self):
        '''Create device ids should trigger device id validations'''
        device = Device.objects.create(token='abc')
        with self.assertRaises(IntegrityError):
            device.create_device_ids([{'value': '', 'id_type': 'GOOGLE_AD_ID'}])

    def test_log_association(self):
        '''Association with logs is properly named'''
        device = Device.objects.create(token='abc')
        log = Log.objects.create(text='foo bar baz',
                                 device=device)
        self.assertEqual(device.logs.count(), 1)
        self.assertEqual(device.logs.first(), log)

    def test_credential_association(self):
        '''Association with credentials is properly named'''
        device = Device.objects.create(token='abc')
        cred = Credential.objects.create(user='john',
                                         secret='pw',
                                         target='site.com',
                                         device=device)
        self.assertEqual(device.credentials.count(), 1)
        self.assertEqual(device.credentials.first(), cred)


class TestDeviceId(TestCase):
    '''Tests of the DeviceId model'''
    def test_requires_device(self):
        '''Must be associated to a device'''
        with self.assertRaises(IntegrityError):
            DeviceId.objects.create(value='1',
                                    id_type='GOOGLE_AD_ID')

    def test_cascade_delete(self):
        '''Is deleted when the device is'''
        device = Device.objects.create(token='foo')
        DeviceId.objects.create(device=device,
                                id_type='GOOGLE_AD_ID',
                                value='baz')
        self.assertEqual(DeviceId.objects.count(), 1)
        device.delete()
        self.assertEqual(DeviceId.objects.count(), 0)

    def test_requires_value(self):
        '''Requires non-empty value'''
        device = Device.objects.create(token='foo')
        with self.assertRaises(IntegrityError):
            DeviceId.objects.create(device=device,
                                    id_type='GOOGLE_AD_ID')
        with self.assertRaises(IntegrityError):
            DeviceId.objects.create(device=device,
                                    id_type='GOOGLE_AD_ID',
                                    value='')

    def test_requires_id_type(self):
        '''Requires non-empty id_type'''
        device = Device.objects.create(token='foo')
        with self.assertRaises(IntegrityError):
            DeviceId.objects.create(device=device,
                                    value='1')
        with self.assertRaises(IntegrityError):
            DeviceId.objects.create(device=device,
                                    value='1',
                                    id_type='')

    def test_validates_id_type(self):
        '''Requires id_type to be one of the choices'''
        device = Device.objects.create(token='foo')
        with self.assertRaises(IntegrityError):
            DeviceId.objects.create(device=device,
                                    value='1',
                                    id_type='bogus')

    def test_uniqueness(self):
        '''The combination of id_type + value must be unique'''
        value = 'baz'
        device = Device.objects.create(token='foo')
        DeviceId.objects.create(device=device,
                                id_type='GOOGLE_AD_ID',
                                value=value)
        with self.assertRaises(IntegrityError):
            DeviceId.objects.create(device=device,
                                    id_type='GOOGLE_AD_ID',
                                    value=value)

class TestCredential(TestCase):
    '''Tests of the Credential model'''
    def test_cascade_delete(self):
        '''Is deleted when the device is'''
        device = Device.objects.create(token='foo')
        Credential.objects.create(device=device,
                                  user='foo',
                                  secret='bar',
                                  target='baz')
        self.assertEqual(Credential.objects.count(), 1)
        device.delete()
        self.assertEqual(Credential.objects.count(), 0)

    def test_uniqueness(self):
        '''Per device, target + user is unique'''
        device = Device.objects.create(token='foo')
        Credential.objects.create(device=device,
                                  user='foo',
                                  secret='bar',
                                  target='baz')
        with self.assertRaises(IntegrityError):
            Credential.objects.create(device=device,
                                      user='foo',
                                      secret='b',
                                      target='baz')

    def test_uniqueness_multiple_devices(self):
        '''The target + user does not have to be unique across multiple devices'''
        device = Device.objects.create(token='foo')
        Credential.objects.create(device=device,
                                  user='foo',
                                  secret='bar',
                                  target='baz')
        device2 = Device.objects.create(token='foo2')
        Credential.objects.create(device=device2,
                                  user='foo',
                                  secret='b',
                                  target='baz')
        self.assertEqual(Credential.objects.count(), 2)


class TestLog(TestCase):
    '''Tests of the Log model'''
    def test_cascade_delete(self):
        '''Is deleted when the device is'''
        device = Device.objects.create(token='foo')
        Log.objects.create(device=device, text='')
        self.assertEqual(Log.objects.count(), 1)
        device.delete()
        self.assertEqual(Log.objects.count(), 0)

    def test_text_empty(self):
        '''The text field can be empty'''
        device = Device.objects.create(token='foo')
        log = Log.objects.create(device=device, text='')
        self.assertFalse(log.text)
