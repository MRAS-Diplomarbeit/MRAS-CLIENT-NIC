from unittest.mock import patch

bluetooth_sh_working = "Controller B8:27:EB:C1:CB:EE (public)\n\tName: raspberrypi\n\tAlias: raspberry\n" \
                    "\tClass: 0x00000000\n\tPowered: no\n\tDiscoverable: no\n\tPairable: no\n" \
                    "\tUUID: Headset AG\t(00001112-0000-1000-8000-00805f9b34fb)\n" \
                    "\tUUID: Generic Attribute Profile\t(00001801-0000-1000-8000-00805f9b34fb)\n" \
                    "\tUUID: A/V Remote Control\t(0000110e-0000-1000-8000-00805f9b34fb)\n" \
                    "\tUUID: Generic Access Profile\t(00001800-0000-1000-8000-00805f9b34fb)\n" \
                    "\tUUID: PnP Information\t(00001200-0000-1000-8000-00805f9b34fb)\n" \
                    "\tUUID: A/V Remote Control Target\t(0000110c-0000-1000-8000-00805f9b34fb)\n" \
                    "\tUUID: Audio Source\t(0000110a-0000-1000-8000-00805f9b34fb)\n" \
                    "\tUUID: Audio Sink\t(0000110b-0000-1000-8000-00805f9b34fb)\n" \
                    "\tUUID: Headset\t(00001108-0000-1000-8000-00805f9b34fb)\n" \
                    "\tModalias: usb:v1D6Bp0246d0532\n\tDiscovering: no"

bluetooth_sh_dict = {'Class': '0x00000000', 'Powered': 'no', 'Discoverable': 'no', 'Pairable': 'no', 'UUID': 'Headset AG(00001112-0000-1000-8000-00805f9b34fb)', 'Modalias': 'usb', 'Discovering': 'no'}

class OSPOPEN:
    def readlines():
        return bluetooth_sh_working.split("\n")


working_bt_sh_popen = patch('os.popen', return_value = OSPOPEN)
os_system = patch('os.system')

