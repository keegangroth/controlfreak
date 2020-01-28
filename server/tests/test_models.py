'''Tests of the db models'''

from django.test import TestCase
from django.db.utils import IntegrityError

from server.models import App, Credential, Device, DeviceId, Log, Token


class TestDevice(TestCase):
    '''Tests of the Device model'''
    def test_create(self):
        '''Create and get work'''
        Device.objects.create()
        self.assertIsNotNone(Device.objects.get())

    def test_create_ids(self):
        '''Given a hash, creates a new device id'''
        device = Device.objects.create()
        device.create_device_ids([{'value': 'foo', 'id_type': 'GOOGLE_AD_ID'}])
        self.assertEqual(device.device_ids.count(), 1)

    def test_create_ids_validates(self):
        '''Create device ids should trigger device id validations'''
        device = Device.objects.create()
        with self.assertRaises(IntegrityError):
            device.create_device_ids([{'value': '', 'id_type': 'GOOGLE_AD_ID'}])

    def test_token_association(self):
        '''Association with tokens is properly named'''
        device = Device.objects.create()
        app = App.objects.create()
        token = Token.objects.create(token='foo bar baz',
                                     device=device,
                                     app=app)
        self.assertEqual(device.tokens.count(), 1)
        self.assertEqual(device.tokens.first(), token)

    def test_log_association(self):
        '''Association with logs is properly named'''
        device = Device.objects.create()
        log = Log.objects.create(text='foo bar baz',
                                 device=device)
        self.assertEqual(device.logs.count(), 1)
        self.assertEqual(device.logs.first(), log)

    def test_credential_association(self):
        '''Association with credentials is properly named'''
        device = Device.objects.create()
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
        device = Device.objects.create()
        DeviceId.objects.create(device=device,
                                id_type='GOOGLE_AD_ID',
                                value='baz')
        self.assertEqual(DeviceId.objects.count(), 1)
        device.delete()
        self.assertEqual(DeviceId.objects.count(), 0)

    def test_requires_value(self):
        '''Requires non-empty value'''
        device = Device.objects.create()
        with self.assertRaises(IntegrityError):
            DeviceId.objects.create(device=device,
                                    id_type='GOOGLE_AD_ID')
        with self.assertRaises(IntegrityError):
            DeviceId.objects.create(device=device,
                                    id_type='GOOGLE_AD_ID',
                                    value='')

    def test_requires_id_type(self):
        '''Requires non-empty id_type'''
        device = Device.objects.create()
        with self.assertRaises(IntegrityError):
            DeviceId.objects.create(device=device,
                                    value='1')
        with self.assertRaises(IntegrityError):
            DeviceId.objects.create(device=device,
                                    value='1',
                                    id_type='')

    def test_validates_id_type(self):
        '''Requires id_type to be one of the choices'''
        device = Device.objects.create()
        with self.assertRaises(IntegrityError):
            DeviceId.objects.create(device=device,
                                    value='1',
                                    id_type='bogus')

    def test_uniqueness(self):
        '''The combination of id_type + value must be unique'''
        value = 'baz'
        device = Device.objects.create()
        DeviceId.objects.create(device=device,
                                id_type='GOOGLE_AD_ID',
                                value=value)
        with self.assertRaises(IntegrityError):
            DeviceId.objects.create(device=device,
                                    id_type='GOOGLE_AD_ID',
                                    value=value)


class TestCredential(TestCase):
    '''Tests of the Credential model'''
    def test_cascade_device_delete(self):
        '''Is deleted when the device is'''
        device = Device.objects.create()
        Credential.objects.create(device=device,
                                  user='foo',
                                  secret='bar',
                                  target='baz')
        self.assertEqual(Credential.objects.count(), 1)
        device.delete()
        self.assertEqual(Credential.objects.count(), 0)

    def test_app_delete(self):
        '''Is not deleted when the app is'''
        device = Device.objects.create()
        app = App.objects.create()
        cred = Credential.objects.create(device=device,
                                         app=app,
                                         user='foo',
                                         secret='bar',
                                         target='baz')
        self.assertEqual(Credential.objects.count(), 1)
        self.assertEqual(cred.app, app)
        app.delete()
        cred.refresh_from_db()
        self.assertEqual(Credential.objects.count(), 1)
        self.assertIsNone(cred.app)

    def test_uniqueness(self):
        '''Per device, target + user is unique'''
        device = Device.objects.create()
        Credential.objects.create(device=device,
                                  user='foo',
                                  secret='bar',
                                  target='baz')
        with self.assertRaises(IntegrityError):
            Credential.objects.create(device=device,
                                      user='foo',
                                      secret='b',
                                      target='baz')

    def test_uniqueness_multiple_apps(self):
        '''Per device, target + user is unique even with multiple apps'''
        device = Device.objects.create()
        app = App.objects.create(name='oof', api_key='zab')
        Credential.objects.create(device=device,
                                  app=app,
                                  user='foo',
                                  secret='bar',
                                  target='baz')
        app2 = App.objects.create(name='rab', api_key='key')
        with self.assertRaises(IntegrityError):
            Credential.objects.create(device=device,
                                      app=app2,
                                      user='foo',
                                      secret='b',
                                      target='baz')

    def test_uniqueness_multiple_devices(self):
        '''The target + user does not have to be unique across multiple devices'''
        device = Device.objects.create()
        Credential.objects.create(device=device,
                                  user='foo',
                                  secret='bar',
                                  target='baz')
        device2 = Device.objects.create()
        Credential.objects.create(device=device2,
                                  user='foo',
                                  secret='b',
                                  target='baz')
        self.assertEqual(Credential.objects.count(), 2)


class TestLog(TestCase):
    '''Tests of the Log model'''
    def test_cascade_device_delete(self):
        '''Is deleted when the device is'''
        device = Device.objects.create()
        Log.objects.create(device=device, text='')
        self.assertEqual(Log.objects.count(), 1)
        device.delete()
        self.assertEqual(Log.objects.count(), 0)

    def test_app_delete(self):
        '''Is not deleted when the app is'''
        device = Device.objects.create()
        app = App.objects.create()
        log = Log.objects.create(device=device,
                                 app=app,
                                 text='baz')
        self.assertEqual(Log.objects.count(), 1)
        self.assertEqual(log.app, app)
        app.delete()
        log.refresh_from_db()
        self.assertEqual(Log.objects.count(), 1)
        self.assertIsNone(log.app)

    def test_text_empty(self):
        '''The text field can be empty'''
        device = Device.objects.create()
        log = Log.objects.create(device=device, text='')
        self.assertFalse(log.text)


class TestToken(TestCase):
    '''Tests of the Token model'''
    def test_cascade_device_delete(self):
        '''Is deleted when the device is'''
        device = Device.objects.create()
        app = App.objects.create(name='foo', api_key='bar')
        Token.objects.create(device=device, app=app, token='baz')
        self.assertEqual(Token.objects.count(), 1)
        device.delete()
        self.assertEqual(Token.objects.count(), 0)

    def test_cascade_app_delete(self):
        '''Is deleted when the app is'''
        device = Device.objects.create()
        app = App.objects.create(name='foo', api_key='bar')
        Token.objects.create(device=device, app=app, token='baz')
        self.assertEqual(Token.objects.count(), 1)
        app.delete()
        self.assertEqual(Token.objects.count(), 0)

    def test_device_app_uniqueness(self):
        '''The device + app combination must be unique'''
        device = Device.objects.create()
        app = App.objects.create(name='foo', api_key='bar')
        Token.objects.create(device=device, app=app, token='baz')
        with self.assertRaises(IntegrityError):
            Token.objects.create(device=device, app=app, token='fred')

    def test_device_token_uniqueness(self):
        '''Each token must have a unique value'''
        device = Device.objects.create()
        app = App.objects.create(name='foo', api_key='bar')
        Token.objects.create(device=device, app=app, token='baz')
        device2 = Device.objects.create()
        with self.assertRaises(IntegrityError):
            Token.objects.create(device=device2, app=app, token='baz')


class TestApp(TestCase):
    '''Test of the App model'''
    def test_name_unique(self):
        '''Name must be unique'''
        App.objects.create(name='foo', api_key='bar')
        with self.assertRaises(IntegrityError):
            App.objects.create(name='foo', api_key='baz')

    def test_api_key_unique(self):
        '''Api key must be unique'''
        App.objects.create(name='foo', api_key='bar')
        with self.assertRaises(IntegrityError):
            App.objects.create(name='baz', api_key='bar')
