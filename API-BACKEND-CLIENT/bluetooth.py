import os
import status_codes


def set_discoverable(isDiscoverable, display_name):
    if not isDiscoverable:
        is_powered = __is_powered()
        if type(is_powered) == dict:
            return is_powered
        elif not is_powered:
            os.system('bluetoothctl power on')

        is_discoverable = __is_discoverable()
        if type(is_discoverable) == dict:
            return is_discoverable
        elif not is_discoverable:
            os.system('bluetoothctl discoverable on')

        is_pairable = __is_pairable()
        if type(is_pairable) == dict:
            return is_pairable
        elif not is_pairable:
            os.system('bluetoothctl pairable on')

        alias = __get_alias()
        if type(alias) == dict:
            return alias
        elif alias != display_name:
            os.system('bluetoothctl system-alias \"'+display_name+"\"")

    elif isDiscoverable:
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
    if 'Powered' not in data or 'Discoverable' not in data or 'Alias' not in data or 'Pairable' not in data:
        return {'code': status_codes.bluetooth_error, 'message': 'Error loading bluetooth info'}
    return data

def __is_powered():
    data = __get_info()
    if data is None:
        return {'error': 'Unknown Error'}
    elif 'code' in data:
        return data
    elif data['Powered'] != "yes":
        return False
    else:
        return True

def __get_alias():
    data = __get_info()
    if data is None:
        return {'error': 'Unknown Error'}
    elif 'code' in data:
        return data
    else:
        return data['Alias']

def __is_discoverable():
    data = __get_info()
    if data is None:
        return {'error': 'Unknown Error'}
    elif 'code' in data:
        return data
    elif data['Discoverable'] != "yes":
        return False
    else:
        return True

def __is_pairable():
    data = __get_info()
    if data is None:
        return {'error': 'Unknown Error'}
    elif 'code' in data:
        return data
    elif data['Pairable'] != "yes":
        return False
    else:
        return True