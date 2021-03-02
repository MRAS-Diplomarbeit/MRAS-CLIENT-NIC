from flask import request
from flask_restful import Resource
from datetime import datetime

import platform
import sys
import os
import status_codes
import load_config
import req
import bluetooth
import pulse_control as pulse
import time
import logger
import constants

conf_client_backend = load_config.ClientBackend(constants.confLoc)
conf_client_client = load_config.ClientClient(constants.confLoc)
conf_logfile = load_config.Client(constants.confLoc)


def err_handling(error, api_path):
    if type(error) is TypeError or type(error) is KeyError:
        print("Please provide all required fields for: " + api_path + " in the .env.yml")
        print("Error loading config file. Please provide .env.yml in the project root folder.")
        current_dir = os.getcwd()
        if platform.system() == 'Linux':
            print("The root folder is: " + current_dir[0:current_dir.rfind("/") + 1])
        elif platform.system() == 'Windows':
            print("The root folder is: " + current_dir[0:current_dir.rfind("\\") + 1])
        print(error)
    print(error)
    sys.exit(-1)


if conf_client_backend.error is not None or conf_client_client.error is not None:
    if conf_client_backend.error is not None:
        err_handling(conf_client_backend.error, "client-backend")
    elif conf_client_client.error is not None:
        err_handling(conf_client_client.error, "client-cleint")


class Playback(Resource):
    def post(self):
        log = []
        data = request.get_json()
        print(request.remote_addr)
        # Test if all params are included
        params_present = data_available(data, ["method", "displayname", "device_ips"])
        if params_present['code'] != status_codes.ok:
            if params_present['code'] == status_codes.bad_request:
                if len(params_present['missing']) == 1:
                    return {'code': status_codes.single_param_missing,
                            "message": "Please provide all necessary data " + str(params_present['missing']).replace(
                                "'", "")}, status_codes.bad_request
                else:
                    return {'code': status_codes.multiple_param_missing,
                            "message": "Please provide all necessary data " + str(params_present['missing']).replace(
                                "'", "")}, status_codes.bad_request

        elif len(data['device_ips']) != 0:
            print(data["device_ips"])
            multicast = "127.0.0.1"  # TODO: set real multicast ip
            err_list = []
            dead_ips = []

            # TODO: send error as response to backend
            # TODO: activate Bluetooth, trx multicast server and send GET to Client-Client\listen with multicast_ip
            urls = []
            log.append(logger.log("Starting listening session on: " + multicast + " with the interface: " + data[
                'method'] + " on the devices:"))
            # Create parameter for get requests (Client-Client)
            getdata = "multicast_ip=" + multicast + "&method=" + data['method']
            for num, ip in enumerate(data['device_ips']):
                urls.append(conf_client_client.protocol + "://" + ip + ":" + str(
                    conf_client_client.port) + conf_client_client.path + "?" + getdata)
                logger.log("\t" + urls[num])

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
                logger.send_log(request.remote_addr, log)
                return {'error': {'code': status_codes.client_not_found, 'message': 'Device/s unavailable'},
                        'dead_ips': dead_ips}, status_codes.not_found
            elif len(err_list) != 0:
                ips = []
                for e in err_list:
                    ips.append(e['ip'])
                logger.send_log(request.remote_addr, log)
                return {
                    'error': {'code': status_codes.server_error_at_client, 'message': 'Internal Server Error at IPs'},
                    'dead_ips': ips
                }

            # starting the bluetooth interface and looking for errors
            ret = bluetooth.set_discoverable(False, data['displayname'])
            if not ret:
                logger.log("Error starting Bluetooth")
                logger.send_log(request.remote_addr, log)
                return ret, 500
            logger.log("Started bluetooth listening")

            # get the number of the source from the bluetooth audio and start the audio transmission
            source_id = pulse.get_source_number(constants.bluetooth_driver)
            while source_id is None:
                time.sleep(2)
                source_id = pulse.get_source_number(constants.bluetooth_driver)

            for ip in data['device_ips']:
                pulse.send_audio_source(source_id, ip)
        else:
            # Playing audio locally
            ret = bluetooth.set_discoverable(False, data['displayname'])
            if not ret:
                logger.log("Error starting Bluetooth")
                logger.send_log(request.remote_addr, log)
                return ret, 500
            else:
                logger.log("Started bluetooth listening")

    def delete(self):
        log = []
        data = request.get_json()
        params_present = data_available(data, ['ips'])
        if params_present['code'] != status_codes.ok:
            if params_present['code'] == status_codes.bad_request:
                return {'code': status_codes.single_param_missing,
                        "message": "Please provide all necessary data " + str(params_present['missing']).replace("'",
                                                                                                                 "")}, status_codes.bad_request
        elif len(data['ips']) > 0:
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
        bluetooth.set_discoverable(True, "")
        log.append(logger.log("Stopped bluetooth listening"))
        logger.send_log(request.remote_addr,log)
        return


def add_time(message: str) -> str:
    return str(datetime.now()) + message


def data_available(data, should_include):
    if data is None:
        return {'code': status_codes.bad_request, 'missing': should_include}
    missing_param = []
    for param in should_include:
        if param not in data:
            missing_param.append(param)
    if len(missing_param) != 0:
        return {'code': status_codes.bad_request, 'missing': missing_param}
    else:
        return {'code': status_codes.ok}