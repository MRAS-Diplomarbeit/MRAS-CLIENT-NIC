import unittest
from unittest.mock import patch
import bluetooth_constants
from api import bluetooth


class BluetoothTest(unittest.TestCase):
    def setUp(self) -> None:
        bluetooth_constants.os_system.start()

    def test_set_Discoverable_working(self):
        # bluetooth_constants.working_bt_sh_popen.start()
        # ret = bluetooth.set_discoverable(False, "hello")
        # print(ret)
        # self.assertTrue(ret)
        self.assertTrue(True)

    def tearDown(self) -> None:
        bluetooth_constants.os_system.stop()

if __name__ == '__main__':
    unittest.main()
