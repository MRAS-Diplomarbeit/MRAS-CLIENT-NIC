from flask import request
from flask_restful import Resource
from datetime import datetime
from excep import ElementNotFoundException

import status_codes
import load_config
import req
import bluetooth
import pulse_control as pulse
import time
import logger
import constants
import helper


conf_client_backend = load_config.ClientBackend(constants.confLoc)
conf_client_client = load_config.ClientClient(constants.confLoc)
conf_logfile = load_config.Client(constants.confLoc)


if conf_client_backend.error is not None or conf_client_client.error is not None:
    if conf_client_backend.error is not None:
        load_config.err_handling(conf_client_backend.error, "client-backend")
    elif conf_client_client.error is not None:
        load_config.err_handling(conf_client_client.error, "client-cleint")


class Playback(Resource):
    def post(self):
        log = []
        data = request.get_json()

        # Test if all params are included
        params_present = helper.data_available(data, ["method", "displayname", "device_ips", "multicast_ip"])
        if len(params_present) == 1:
            return {'code': status_codes.single_param_missing, "message": "Please provide all necessary data " +
                                                                          str(params_present).replace("'", "")}, status_codes.bad_request
        elif len(params_present) > 1:
            return {'code': status_codes.multiple_param_missing, "message": "Please provide all necessary data " +
                                                                            str(params_present).replace("'", "")}, status_codes.bad_request

        if len(data['device_ips']) != 0:
            print(data["device_ips"])
            multicast = "224.1.1.1"  # TODO: set real multicast ip
            err_list = []
            dead_ips = []

            # TODO: send error as response to backend
            # TODO: activate Bluetooth, trx multicast server and send GET to Client-Client\listen with multicast_ip
            urls = []
            log.append(logger.log("Starting listening session on: " + multicast + " with the interface: " + data[
                'method'] + " on the devices:"))
            # Create parameter for get requests (Client-Client)
            getdata = "multicast_ip=" + multicast + "&method=" + data['method'].replace(" ", "%20")
            for num, ip in enumerate(data['device_ips']):
                urls.append(conf_client_client.protocol + "://" + ip + ":" + str(
                    conf_client_client.port) + conf_client_client.path + "?" + getdata)
                log.append(logger.log("\t" + urls[num]))

            # send requests
            resp = req.greq_post(urls)
            print(resp)
            for num, response in enumerate(resp):
                if response is None:
                    dead_ips.append(data['device_ips'][num])
                elif response.status_code == status_codes.internal_server_error:
                    err_list.append({'code': status_codes.server_error_at_client, 'ip': data['device_ips'][num]})
                elif response.status_code != status_codes.ok:
                    err_list.append({'code': response.status_code, 'message': 'Server probably not running'})
                    dead_ips.append(data['device_ips'][num])
                # TODO: ADD tests for status_code 400

            print(dead_ips)
            print(err_list)

            if len(dead_ips) != 0:
                logger.send_log("http://" + request.remote_addr + ":" + str(conf_logfile.update_port) + "/log", log)
                return {'error': {'code': status_codes.client_not_found, 'message': 'Device/s unavailable'},
                        'dead_ips': dead_ips}, status_codes.not_found
            elif len(err_list) != 0:
                ips = []
                for e in err_list:
                    ips.append(e['ip'])
                logger.send_log("http://" + request.remote_addr + ":" + str(conf_logfile.update_port) + "/log", log)
                return {
                    'error': {'code': status_codes.server_error_at_client, 'message': 'Internal Server Error at IPs'},
                    'dead_ips': ips
                }

            # starting the bluetooth interface and looking for errors
            ret = bluetooth.set_discoverable(False, data['displayname'])
            if not ret:
                log.append(logger.log("Error starting Bluetooth"))
                logger.send_log("http://" + request.remote_addr + ":" + str(conf_logfile.update_port) + "/log", log)
                return ret, 500
            log.append(logger.log("Started bluetooth listening"))

            # get the number of the source from the bluetooth audio and start the audio transmission
            source_id = pulse.get_source_number(constants.bluetooth_driver)
            while source_id is None:
                time.sleep(2)
                source_id = pulse.get_source_number(constants.bluetooth_driver)

            # send to all individual ips
            # for ip in data['device_ips']:
            #     pulse.send_audio_source(source_id, ip)

            # send the source to an multicast ip and to the local ip
            try:
                pulse.send_audio_source(source_id, multicast)
                pulse.send_audio_source(source_id, "127.0.0.1")

                # changing volume of loopback adapter to 0 and listening to own stream with an equal delay
                sink_input_id = None
                while sink_input_id is None:
                    try:
                        sink_input_id = pulse.get_sink_input_id(constants.loopback_driver)
                        pulse.change_volume_sink_input(sink_input_id, 0)
                        pulse.listen_to_stream("127.0.0.1", constants.default_latency)
                    except:
                        print("Not loaded")
                        log.append(logger.log("Not loaded"))

                # move rtp listener to the given interface
                time.sleep(5)  # TODO: Fix error (driver not found) and remove sleep
                pulse.move_sink_input(pulse.get_sink_input_id(constants.rtp_recv_driver),
                                      pulse.get_card_id(data['method']))
            except ElementNotFoundException as err:
                logger.send_log("http://" + request.remote_addr + ":" + str(conf_logfile.update_port) + "/log", log)
                return{'code': status_codes.sink_not_found, 'message': str(err)}, 400
            logger.send_log("http://" + request.remote_addr + ":" + str(conf_logfile.update_port) + "/log", log)
            # TODO: move playback to write method
        else:
            # Playing audio locally
            ret = bluetooth.set_discoverable(False, data['displayname'])
            if not ret:
                log.append(logger.log("Error starting Bluetooth"))
                logger.send_log("http://" + request.remote_addr + ":" + str(conf_logfile.update_port) + "/log", log)
                return ret, 500
            else:
                log.append(logger.log("Started bluetooth listening"))
                source_id = pulse.get_source_number(constants.bluetooth_driver)
                while source_id is None:
                    time.sleep(0.5)
                    source_id = pulse.get_source_number(constants.bluetooth_driver)
                try:
                    pulse.move_sink_input(pulse.get_sink_input_id(constants.loopback_driver),
                                      pulse.get_card_id(data['method']))
                    pulse.change_volume_sink_input(pulse.get_sink_input_id(constants.loopback_driver), 100)
                except ElementNotFoundException as err:
                    print(err)
                    logger.send_log("http://" + request.remote_addr + ":" + str(conf_logfile.update_port) + "/log", log)
                    return{'code': status_codes.sink_not_found, 'message': str(err)}, 400
                logger.send_log("http://" + request.remote_addr + ":" + str(conf_logfile.update_port) + "/log", log)

    def delete(self):
        log = []
        data = request.get_json()
        params_present = helper.data_available(data, ['ips'])

        if len(params_present) != 0:
            return {'code': status_codes.single_param_missing,"message": "Please provide all necessary data " +
                                                                         str(params_present).replace("'", "")}, status_codes.bad_request

        if len(data['ips']) > 1:
            urls = []

            for num, ip in enumerate(data['ips']):
                urls.append(conf_client_client.protocol + "://" + ip + ":" + str(
                    conf_client_client.port) + conf_client_client.path)
            resp = req.greq_delete(urls)
            dead_ip = []
            not_listening = []
            for num, response in enumerate(resp):
                if response is None:
                    dead_ip.append(data['ips'][num])
                elif response.status_code == status_codes.bad_request:
                    not_listening.append(data['ips'][num])
                elif response.status_code != status_codes.ok:
                    dead_ip.append(data['ips'][num])

            if len(not_listening) != 0:
                return {'code': status_codes.client_not_listening,
                        'message': str(not_listening).replace("'", "") + " is currently not listening"}

            pulse.stop_outgoing_stream()
            pulse.stop_incoming_stream()

        bluetooth.set_discoverable(True, "")
        log.append(logger.log("Stopped bluetooth listening"))
        print("Log: "+str(logger.send_log("http://" + request.remote_addr + ":" + str(conf_logfile.update_port) + "/log", log)))
        return


def add_time(message: str) -> str:
    return str(datetime.now()) + message

