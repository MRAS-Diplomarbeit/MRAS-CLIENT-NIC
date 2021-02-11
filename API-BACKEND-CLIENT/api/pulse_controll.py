import os
import status_codes


def get_sinks():
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
            tmp_sink[prev_key] = tmp_sink[prev_key]+line.replace('\t', '').replace('\n', '')
    # add last sink to sinks dict
    sinks[curr_sink_name.replace('\n', '')] = tmp_sink
    return sinks


def get_sink(name):
    sinks = get_sinks()
    # find the position of the name in the generated names array and return the matching part of the dict
    for sink in sinks.values():
        if sink['Name'] == name:
            return sink
    return {'code': status_codes.sink_not_found, 'message': 'Unable to find the sink: '+name + ' in sinks: ' + str(get_sink_names())}


def get_sink_names():
    sinks = get_sinks()
    names = []
    for sink in sinks:
        names.append(sinks[sink]['Name'])
    return names


def add_sink(name):
    os.system('pactl load-module module-null-sink sink_name=' + name)
    # returns true if sink was added successfully
    if sink_exists(name):
        return True
    else:
        return {'code': status_codes.pulse_error, 'message': 'Error creating sink'}


def sink_exists(name):
    if 'code' in get_sink(name):
        return False
    return True


def remove_sink(name):
    sink_id = get_sink(name)['Owner Module']
    os.system('pactl unload-module '+sink_id)
    return not sink_exists(name)


def send_audio(sink, ip):
    os.system('pactl load-module module-rtp-send source='+sink+'.monitor destination='+ip)
