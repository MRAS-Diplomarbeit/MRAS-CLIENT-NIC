import os
import json
import time

class Control:
    def set_discoverable(isDiscoverable):
        if not isDiscoverable:
            stream = os.popen('rfkill -J')
            interfaces = json.load(stream)['']
            for interface in interfaces:
                print(interface)
                if interface['type'] == 'bluetooth' and interface['soft'] == 'blocked':
                    os.system('rfkill unblock '+str(interface['id']))
            print(interfaces)
            time.sleep(2)
            os.system('bluetoothctl discoverable on')
            os.system('bluetoothctl pairable on')
        elif isDiscoverable:
            stream = os.popen('rfkill -J')
            interfaces = json.load(stream)['']
            for interface in interfaces:
                if interface['type'] == 'bluetooth' and interface['soft'] == 'unblocked':
                    os.system('rfkill block ' + str(interface['id']))
        return
