from typing import overload
import os
import status_codes


def parse_list(list: [str], type: str) -> dict:
    devices = {}
    tmp_sink = {}
    # Setting first device name and removing line of sink name from list
    curr_sink_name = list[0]
    del list[0]
    prev_key = None

    for line in list:
        # testing if new device, adding the finished device data to dict and clearing temporary data
        if type in line:
            devices[curr_sink_name.replace('\n', '')] = tmp_sink
            curr_sink_name = line
            tmp_sink = {}
        # add current line to dictionary and removing the first space from the value
        elif ':' in line:
            pair = line.split(':')
            tmp_sink[pair[0].replace('\t', '')] = pair[1].replace(' ', '', 1).replace('\n', '')
            prev_key = pair[0].replace('\t', '')
        # special case for multiline objects
        elif line != '\n':
            tmp_sink[prev_key] = tmp_sink[prev_key] + line.replace('\t', '').replace('\n', '')
    # add last device to sinks dict
    devices[curr_sink_name.replace('\n', '')] = tmp_sink
    return devices


# returns a dict of all the sinks with the sink number (Sink #0...) as an key
def get_sinks() -> dict:
    lines = os.popen('pactl list sinks').readlines()
    return parse_list(lines, "Sink")


def get_sources() -> dict:
    lines = os.popen('pactl list sources').readlines()
    return parse_list(lines, "Source")


def get_modules() -> dict:
    lines = os.popen('pactl list modules').readlines()
    return parse_list(lines, "Module")


# returns one sink as an dict
def get_sink(name: str) -> dict:
    sinks = get_sinks()
    # find the position of the name in the generated names array and return the matching part of the dict
    for sink in sinks.values():
        if sink['Name'] == name:
            return sink
    return {'code': status_codes.sink_not_found,
            'message': 'Unable to find the sink: ' + name + ' in sinks: ' + str(get_sink_names())}


# returns an list of names from the sinks
def get_sink_names() -> [str]:
    sinks = get_sinks()
    names = []
    for sink in sinks:
        names.append(sinks[sink]['Name'])
    return names


def get_source_names() -> [str]:
    sources = get_sources()
    names = []
    for source in sources:
        names.append(source[source]['Name'])
    return names


def get_source_drivers() -> [str]:
    sources = get_sources()
    driver = []
    for source in sources:
        driver.append(source[source]['Driver'])
    return driver


# returns the number of the source
def get_source_number(driver: str) -> int:
    sources = get_sources()
    for source in sources:
        if sources[source]['Driver'] == driver:
            # substring to get X from the String (Sources #X)
            return source[8:]


# adds a sink with a specified name
def add_sink(name: str):
    os.system('pactl load-module module-null-sink sink_name=' + name)
    # returns true if sink was added successfully
    if sink_exists(name):
        return True
    else:
        return {'code': status_codes.pulse_error, 'message': 'Error creating sink'}


# uses get_sink and looks for an dict with an key code for errors,
# returns True if the sink exists
def sink_exists(name) -> bool:
    if 'code' in get_sink(name):
        return False
    return True


# delete sink and test if sink got deleted,
# returns true if the sink got deleted
def remove_sink(name) -> bool:
    sink_id = get_sink(name)['Owner Module']
    os.system('pactl unload-module ' + sink_id)
    return not sink_exists(name)


@overload
def send_audio_sink(sink: str, ips: [str]) -> None:
    for ip in ips:
        send_audio_sink(sink, ip)


# sends the audio from a specified sink to an ip
def send_audio_sink(sink: str, ip: str) -> None:
    os.system('pactl load-module module-rtp-send source=' + sink + '.monitor destination=' + ip)


def send_audio_source(source_id: int, ip: str) -> None:
    print(source_id)
    print(ip)
    os.system('pactl load-module module-rtp-send source=' + str(source_id) + ' destination=' + ip)


# stops all audio streams by unloading the send module
def stop_outgoing_stream() -> bool:
    return unload_module('module-rtp-send')


def stop_incoming_stream() -> bool:
    return unload_module('module-rtp-recv')


def listen_to_stream(ip: str, latency: int) -> None:
    os.system('pactl load-module module-rtp-recv latency_msec=' + str(latency) + 'sap_address=' + ip)


def unload_module(module: str) -> bool:
    ret = os.popen('pactl unload-module ' + module).readline()
    if ret is not None:
        return False
    else:
        return True

# TODO: list modules, get module number of sending streams
