from typing import overload
import os
import status_codes


# returns a dict of all the sinks with the sink number (Sink #0...) as an key
def get_sinks() -> dict:
    lines = os.popen('pactl list sinks').readlines()
    sinks = {}
    tmp_sink = {}
    # Setting first Sink name and removing line of sink name from list
    curr_sink_name = lines[0]
    del lines[0]
    prev_key = None

    for line in lines:
        # testing if new sink, adding the finished sink data to dict and clearing temporary data
        if "Sink" in line:
            sinks[curr_sink_name.replace('\n', '')] = tmp_sink
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
    # add last sink to sinks dict
    sinks[curr_sink_name.replace('\n', '')] = tmp_sink
    return sinks


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
def send_audio(sink: str, ips: [str]) -> None:
    for ip in ips:
        send_audio(sink, ip)


# sends the audio from a specified sink to an ip
def send_audio(sink: str, ip: str) -> None:
    os.system('pactl load-module module-rtp-send source=' + sink + '.monitor destination=' + ip)


# stops all audio streams by unloading the send module
def stop_audio_stream() -> None:
    os.system('pactl unload module-rtp-send')

# TODO: list modules, get module number of sending streams
