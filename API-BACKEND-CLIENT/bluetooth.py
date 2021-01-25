import os
import json
import time
import status_codes


def set_discoverable(isDiscoverable, display_name):
    if not isDiscoverable:
        # stream = os.popen('rfkill -J')
        # interfaces = json.load(stream)['']
        # for interface in interfaces:
        #     print(interface)
        #     if interface['type'] == 'bluetooth' and interface['soft'] == 'blocked':
        #         os.system('rfkill unblock '+str(interface['id']))
        # print(interfaces)
        # time.sleep(2)
        is_powered = __is_powered()
        if type(is_powered) == dict:
            return is_powered
        elif not is_powered:
            os.system('bluetoothctl power on')
        os.system('bluetoothctl discoverable on')
        os.system('bluetoothctl pairable on')
        os.system('bluetoothctl system-alias '+display_name)
    elif isDiscoverable:
        # stream = os.popen('rfkill -J')
        # interfaces = json.load(stream)['']
        # for interface in interfaces:
        #     if interface['type'] == 'bluetooth' and interface['soft'] == 'unblocked':
        #         os.system('rfkill block ' + str(interface['id']))
        is_powered = __is_powered()
        if type(is_powered) == dict:
            return is_powered
        elif is_powered:
            os.system('bluetoothctl power off')
    return


def __get_info():
    lines = os.popen('bluetoothctl show').readlines()
    del lines[0]
    data = {}
    for line in lines:
        tmp = line.split(":")
        data[tmp[0].replace("\t", "")] = tmp[1].replace(" ", "").replace("\n", "")
    if "Powered" not in data or "Discoverable" not in data or 'Alias' not in data:
        return {'code': status_codes.bluetooth_error, 'message': 'Error loading bluetooth info'}
    return data

def __is_powered():
    data = __get_info()
    if data is None:
        return {'error': 'Unknown Error'}
    elif 'code' in data:
        return data
    elif data['Powered'] != "Yes":
        return False
    else:
        return True
