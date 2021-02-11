import os
import status_codes


def get_sinks():
    lines = os.popen('pactl list sinks | grep Name').readlines()
    # sink_names = {}
    # for sink in sinks:
    #     tmp = sink.split(':')
    #     sink_names.append(tmp[1].replace(' ', ''))
    # return sink_names
    sinks = {}
    tmp_sink = {}
    # Setting first Sink name and removing line of sink name from list
    curr_sink_name = lines[0]
    del lines[0]
    prev_key = None

    for line in lines:
        # testing if new sink, adding the finished sink data to dict and clearing temporary data
        if "Sink" in line:
            sinks[curr_sink_name] = tmp_sink
            curr_sink_name = line
            tmp_sink = {}
        # add current line to dictionary and removing the first space from the value
        elif ':' in line:
            pair = line.split(':')
            tmp_sink[pair[0].replace('\t', '')] = pair[1].replace(' ', '', 1)
            prev_key = pair[0].replace('\t', '')
        # special case for multiline objects
        elif line != '\n':
            tmp_sink[prev_key] = tmp_sink[prev_key]+line.replace('\t', '')
    return sinks


def get_sink_names():
    sinks = get_sinks()
    print(sinks.keys())


def add_sink(name):
    os.system('pactl load-module module-null-sink sink_name=' + name)
    if name in get_sink_names():
        return True
    else:
        return {'code': status_codes.pulse_error, 'message': 'Error creating sink'}

def send_audio(sink, ip):
    ret = os.popen('pactl load-module module-rtp-send source='+sink+'.monitor destination='+ip).readline()
