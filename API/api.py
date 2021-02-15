from flask import Flask, request
from flask_restful import Api, Resource
from datetime import datetime, date

import req
import sys
import load_config
import os
import platform
import logging
import constants
import status_codes
import bluetooth
import rotating_logger
import pulse_control as pulse
import time

app = Flask(__name__)
api = Api(app)

conf_client_backend = load_config.ClientBackend(constants.confLoc)
conf_client_client = load_config.ClientClient(constants.confLoc)
conf_logfile = load_config.Client(constants.confLoc)
logger = None


def err_handling(error, api):
    if type(error) is TypeError or type(error) is KeyError:
        print("Please provide all required fields for: " + api + " in the .env.yml")
        logger.error(date.today().strftime("%d/%m/%Y") + "-" + datetime.now().strftime(
            "%H:%M:%S") + " Please provide all required fields for: " + api + " in the .env.yml")
        print("Error loading config file. Please provide .env.yml in the project root folder.")
        current_dir = os.getcwd()
        if platform.system() == 'Linux':
            print("The root folder is: " + current_dir[0:current_dir.rfind("/") + 1])
        elif platform.system() == 'Windows':
            print("The root folder is: " + current_dir[0:current_dir.rfind("\\") + 1])
        print(error)
    print(error)
    logger.error("Shutting down due to errors at config file")
    sys.exit(-1)


if conf_logfile.error is not None or conf_client_backend.error is not None or conf_client_client.error is not None:
    if conf_logfile.error is not None:
        logger = rotating_logger.create_log("./log.txt", 2048000, 5, logging.INFO)
        logger.info("Please provide a location for the log file")
    else:
        logger = rotating_logger.create_log(conf_logfile.log_path + conf_logfile.log_name, conf_logfile.max_size,
                                            conf_logfile.old_logs, logging.INFO)
    if conf_client_backend.error is not None:
        err_handling(conf_client_backend.error, "client-backend")
    elif conf_client_client.error is not None:
        err_handling(conf_client_client.error, "client-cleint")
else:
    logger = rotating_logger.create_log(conf_logfile.log_path + conf_logfile.log_name, conf_logfile.max_size,
                                        conf_logfile.old_logs, logging.INFO)


class Playback(Resource):
    def post(self):
        data = request.get_json()

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

            # Synchros requests
            # for ip in data["device_ips"]:
            #     data = {'multicast_ip': multicast, 'method': data['method']}
            #     #getdata = "multicast_ip="+multicast+"&method="+data['method']
            #     # resp = await req.req_listen_get_a(const.clientClientProtocoll, ip, const.clientClientApiPath, data)
            #     # not running as thread to respond to request from backend
            #
            #     resp = req.req_listen_get(const.clientClientProtocoll, ip, const.clientClientApiPath, data)
            #     print(resp)
            #     if resp is not None and 'ERROR' in resp:
            #         err_list.append(resp['ERROR'])
            #         dead_ips.append(ip)
            #     print(ip)
            # if len(err_list) is not 0:
            #     print("Error occurred")
            #     print(err_list)
            #     return {'error': {'code': 15, 'message': 'Device unavailable'}, 'dead_ips': dead_ips}, 404
            # TODO: send error as response to backend
            # TODO: activate Bluetooth, trx multicast server and send GET to Client-Client\listen with multicast_ip
            urls = []
            logger.info("Starting listening session on: " + multicast + " with the interface: " + data[
                'method'] + " on the devices:")
            # Create parameter for get requests (Client-Client)
            getdata = "multicast_ip=" + multicast + "&method=" + data['method']
            for num, ip in enumerate(data['device_ips']):
                urls.append(conf_client_client.protocol + "://" + ip + ":" + str(
                    conf_client_client.port) + conf_client_client.path + "?" + getdata)
                logger.info("\t" + urls[num])

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
                return {'error': {'code': status_codes.client_not_found, 'message': 'Device/s unavailable'},
                        'dead_ips': dead_ips}, status_codes.not_found
            elif len(err_list) != 0:
                ips = []
                for e in err_list:
                    ips.append(e['ip'])
                return {
                    'error': {'code': status_codes.server_error_at_client, 'message': 'Internal Server Error at IPs'},
                    'dead_ips': ips}

            # starting the bluetooth interface and looking for errors
            ret = bluetooth.set_discoverable(False, data['displayname'])
            if not ret:
                logger.error("Error starting Bluetooth")
                return ret, 500
            logger.info("Started bluetooth listening")

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
                logger.error("Error starting Bluetooth")
                return ret, 500
            else:
                logger.info("Started bluetooth listening")

    def delete(self):
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
        logger.info("Stopped bluetooth listening")
        return


api.add_resource(Playback, conf_client_backend.path)


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


if __name__ == '__main__':
    from gevent import monkey

    monkey.patch_all()
    app.run(host="0.0.0.0", port=conf_client_backend.port, debug=True, threaded=True)
