import unittest
from api import app

class MyTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_stop_without_ip_filed(self):
        response = self.app.delete('/api/v1/playback')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['code'],1000)
        self.assertEqual(response.json['message'], "Please provide all necessary data [ips]")

    def test_stop_with_no_ips(self):
        response = self.app.delete('/api/v1/playback', json = {'ips':[ ]})
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
