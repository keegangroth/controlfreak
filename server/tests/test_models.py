from django.test import TestCase
from django.db.utils import IntegrityError

from server.models import Device


class TestDevice(TestCase):
    def test_device_create(self):
        Device.objects.create(token='abc')
        self.assertIsNotNone(Device.objects.get(token='abc'))

    def test_create_ids(self):
        device = Device.objects.create(token='abc')
        device.create_device_ids([{'value': 'foo', 'id_type': 'GOOGLE_AD_ID'}])
        self.assertTrue(device.device_ids)

    def test_create_ids_validates(self):
        device = Device.objects.create(token='abc')
        with self.assertRaises(IntegrityError):
            device.create_device_ids([{'value': '', 'id_type': 'GOOGLE_AD_ID'}])


class TestDeviceId(TestCase):
    pass


class TestCredential(TestCase):
    pass


class TestLog(TestCase):
    pass
