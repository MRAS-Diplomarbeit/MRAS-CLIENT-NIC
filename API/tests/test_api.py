import unittest
import os
import sys

# testing from different folder
if not os.getcwd() + "/api/" in sys.path:
    sys.path.append(os.getcwd() + "/api/")
from api import app
from unittest.mock import patch


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
        self.assertEqual(response.json['code'], 1000)
        self.assertEqual(response.json['message'], "Please provide all necessary data [ips]")

    def test_stop_with_no_ips(self):
        with patch('api.bluetooth.set_discoverable', return_value=True) as mocked:
            response = self.app.delete('/api/v1/playback', json={'ips': []})
            self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
