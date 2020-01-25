from server.tests.fixtures.client import ClientTestCase


class TestIndexView(ClientTestCase):
    '''Test the index view'''
    def test_loads(self):
        '''Make sure it loads at the root path'''
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


class TestHealthView(ClientTestCase):
    '''Test the health view'''
    def test_health_json(self):
        '''Returns 200 with some info about the db'''
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['db'])
