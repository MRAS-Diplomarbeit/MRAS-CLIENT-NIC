# from gevent import monkey as curious_george
# curious_george.patch_all(thread=False, select=False)
from flask import Flask, request
from flask_restful import Api, Resource
from datetime import datetime, date
from logging.handlers import RotatingFileHandler

import req
import sys
import load_config
import os
import platform
import logging
import status_codes
import bluetooth

app = Flask(__name__)
api = Api(app)

conf_client_backend = load_config.ClientBackend("../.env.yml")
conf_client_client = load_config.ClientClient("../.env.yml")
conf_logfile = load_config.Client("../.env.yml")
logger = None

def create_log(path, size, back_up_count, level):
    global logger
    logger = logging.getLogger()
    logger.setLevel(level),
    handler = RotatingFileHandler(path, maxBytes=size, backupCount=back_up_count)
    handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))
    logger.addHandler(handler)


def err_handling(error, api):
    if type(error) is TypeError:
        print("Please provide all required fields for: " + api + " in the .env.yml")
        logger.error(date.today().strftime("%d/%m/%Y") + "-" + datetime.now().strftime(
            "%H:%M:%S") + " Please provide all required fields for: " + api + " in the .env.yml")
    elif type(error) is KeyError:
        print("Please provide all required fields for: " + api + " in the .env.yml")
        logger.error(date.today().strftime("%d/%m/%Y") + "-" + datetime.now().strftime(
            "%H:%M:%S") + " Please provide all required fields for: " + api + " in the .env.yml")
    else:
        print("Error loading config file. Please provide .env.yml in the project root folder.")
        dir = os.getcwd()
        if platform.system() == 'Linux':
            print("The root folder is: " + dir[0:dir.rfind("/") + 1])
        elif platform.system() == 'Windows':
            print("The root folder is: " + dir[0:dir.rfind("\\") + 1])
        print(error)
    logger.error("Shutting down due to errors at config file")
    sys.exit(-1)


if conf_logfile.error is not None or conf_client_backend.error is not None or conf_client_client.error is not None:
    if conf_logfile.error is not None:
        create_log("../log.txt", 2048000, 5, logging.INFO)
        # logging.basicConfig(filename="../log.txt", level=logging.DEBUG)
        # logging.info(date.today().strftime("%d/%m/%Y") + "-" + datetime.now().strftime(
        #     "%H:%M:%S") + " Please provide a location for the log file")
        logger.info("Please provide a location for the log file")
    else:
        # logging.basicConfig(filename=conf_logfile.logpath, level=logging.DEBUG)
        create_log(conf_logfile.logpath, 2048000, 5, logging.INFO)
    if conf_client_backend.error is not None:
        err_handling(conf_client_backend.error, "client-backend")
    elif conf_client_client.error is not None:
        err_handling(conf_client_client.error, "client-cleint")
else:
    # logging.basicConfig(filename=conf_logfile.logpath, level=logging.DEBUG)
    create_log(conf_logfile.logpath, 2048000, 5, logging.INFO)


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

        # if data is None:
        #     logging.info(date.today().strftime("%d/%m/%Y") + "-" +
        #                  datetime.now().strftime(
        #                      "%H:%M:%S") + str(status_codes.bad_request) + " - Server did not supply data.")
        #     return {"error": "No data supplied"}, status_codes.bad_request
        #
        # elif "method" not in data or "displayname" not in data or "device_ips" not in data:
        #     logging.info(date.today().strftime("%d/%m/%Y") + "-" + datetime.now().strftime("%H:%M:%S") +
        #                  str(status_codes.bad_request) + " - Server did not supply all necessary data.")
        #     return {"error": "Body must contain method, displayname, device_ips"}, status_codes.bad_request

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
            # logging.info(date.today().strftime("%d/%m/%Y") + "-" + datetime.now().strftime("%H:%M:%S") +
            #              " Starting listening session on: " + multicast + " with the interface: " + data[
            #                  'method'] + " on the devices:")
            logger.info("Starting listening session on: " + multicast + " with the interface: " + data['method'] + " on the devices:")
            # Create parameter for get requests (Client-Client)
            getdata = "multicast_ip=" + multicast + "&method=" + data['method']
            for num, ip in enumerate(data['device_ips']):
                urls.append(conf_client_client.protocol + "://" + ip + ":" + str(
                    conf_client_client.port) + conf_client_client.path + "?" + getdata)
                # logging.info("\t" + urls[num])
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
                # TODO: ADD test for status_code 400

            print(dead_ips)
            print(err_list)

            if len(dead_ips) != 0:
                return {'error': {'code': status_codes.client_not_found, 'message': 'Device/s unavailable'},
                        'dead_ips': dead_ips}, status_codes.not_found
            elif len(err_list) != 0:
                ips = []
                for e in err_list:
                    ips.append(e['ip'])
                return {'error': {'code': status_codes.server_error_at_client, 'message': 'Internal Server Error at IPs'}, 'dead_ips': ips}

            # TODO: play audio
            ret = bluetooth.set_discoverable(False, data['displayname'])
            if ret is not None:
                # logging.info(date.today().strftime("%d/%m/%Y") + "-" + datetime.now().strftime(
                #     "%H:%M:%S") + "Error starting Bluetooth")
                logger.error("Error starting Bluetooth")
                return ret, 500
            else:
                # logging.info(date.today().strftime("%d/%m/%Y") + "-" + datetime.now().strftime("%H:%M:%S") + " Started bluetooth listening")
                logger.info("Started bluetooth listening")
                return
        else:
            # Playing audio locally
            ret = bluetooth.set_discoverable(False, data['displayname'])
            if ret is not None:
                # logging.info(date.today().strftime("%d/%m/%Y") + "-" + datetime.now().strftime(
                #     "%H:%M:%S") + "Error starting Bluetooth")
                logger.error("Error starting Bluetooth")
                return ret, 500
            else:
                # logging.info(date.today().strftime("%d/%m/%Y") + "-" + datetime.now().strftime(
                #     "%H:%M:%S") + " Started bluetooth listening")
                logger.info("Started bluetooth listening")
                return

    def delete(self):
        # TODO: deactivate Bluetooth & send DELETE to Client-Client\listen
        data = request.get_json()
        params_present = data_available(data, ['ips'])
        if params_present['code'] != status_codes.ok:
            if params_present['code'] == status_codes.bad_request:
                return {'code': status_codes.single_param_missing, "message": "Please provide all necessary data " + str(params_present['missing']).replace("'", "")}, status_codes.bad_request
        else:
            urls = []
            for num, ip in enumerate(data['ips']):
                urls.append(conf_client_client.protocol+"://"+ip+":"+str(conf_client_client.port) + conf_client_client.path)
            resp = req.greq_delete(urls)
            print(resp)
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
                return {'code': status_codes.client_not_listening, 'message': str(not_listening).replace("'", "") + " is currently not listening"}

            bluetooth.set_discoverable(True, "")
            # logging.info(date.today().strftime("%d/%m/%Y") + "-" + datetime.now().strftime(
            #     "%H:%M:%S") + " Stopped bluetooth listening")
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
    app.run(host="0.0.0.0", port=conf_client_backend.port, debug=False, threaded=True)
