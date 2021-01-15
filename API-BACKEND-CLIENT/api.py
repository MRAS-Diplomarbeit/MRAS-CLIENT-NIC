# from gevent import monkey as curious_george
# curious_george.patch_all(thread=False, select=False)
from flask import Flask, request
from flask_restful import Api, Resource
from datetime import datetime, date

import req
import sys
import load_config
import os
import platform
import logging
import status_codes

app = Flask(__name__)
api = Api(app)

conf_client_backend = load_config.ClientBackend("../.env.yml")
conf_client_client = load_config.ClientClient("../.env.yml")
conf_logfile = load_config.Client("../.env.yml")


def errHandling(error, api):
    if type(error) is TypeError:
        print("Please provide all required fields for: " + api + " in the .env.yml")
        logging.error(date.today().strftime("%d/%m/%Y") + "-" + datetime.now().strftime(
            "%H:%M:%S") + " Please provide all required fields for: " + api + " in the .env.yml")
    elif type(error) is KeyError:
        print("Please provide all required fields for: " + api + " in the .env.yml")
        logging.error(date.today().strftime("%d/%m/%Y") + "-" + datetime.now().strftime(
            "%H:%M:%S") + " Please provide all required fields for: " + api + " in the .env.yml")
    else:
        print("Error loading config file. Please provide .env.yml in the project root folder.")
        dir = os.getcwd()
        if platform.system() == 'Linux':
            print("The root folder is: " + dir[0:dir.rfind("/") + 1])
        elif platform.system() == 'Windows':
            print("The root folder is: " + dir[0:dir.rfind("\\") + 1])
        print(error)
    logging.error("Shutting down due to errors at config file")
    sys.exit(-1)


if conf_logfile.error is not None or conf_client_backend.error is not None or conf_client_client.error is not None:
    if conf_logfile.error is not None:
        logging.basicConfig(filename="../log.txt", level=logging.DEBUG)
        logging.info(date.today().strftime("%d/%m/%Y") + "-" + datetime.now().strftime(
            "%H:%M:%S") + " Please provide a location for the log file")
    else:
        logging.basicConfig(filename=conf_logfile.logpath, level=logging.DEBUG)
    if conf_client_backend.error is not None:
        errHandling(conf_client_backend.error, "client-backend")
    elif conf_client_client.error is not None:
        errHandling(conf_client_client.error, "client-cleint")
else:
    logging.basicConfig(filename=conf_logfile.logpath, level=logging.DEBUG)


class Playback(Resource):
    def post(self):
        data = request.get_json()

        if data is None:
            logging.info(date.today().strftime("%d/%m/%Y") + "-" +
                         datetime.now().strftime("%H:%M:%S") + status_codes.bad_request + " - Server did not supply data.")
            return {"error": "No data supplied"}, status_codes.bad_request

        elif "methode" not in data or "displayname" not in data or "device_ips" not in data:
            logging.info(date.today().strftime("%d/%m/%Y")+"-"+datetime.now().strftime("%H:%M:%S") +
                         status_codes.bad_request+" - Server did not supply all necessary data.")
            return {"error": "Body must contain methode, displayname, device_ips"}, status_codes.bad_request

        elif len(data['device_ips'])!=0:
            print(data["device_ips"])
            multicast = "127.0.0.1"  # TODO: set real multicast ip
            err_list = []
            dead_ips = []

            # Synchros requests
            # for ip in data["device_ips"]:
            #     data = {'multicast_ip': multicast, 'methode': data['methode']}
            #     #getdata = "multicast_ip="+multicast+"&methode="+data['methode']
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
            logging.info(date.today().strftime("%d/%m/%Y") + "-" + datetime.now().strftime("%H:%M:%S") +
                         " Starting listening session on: " + multicast + " with the interface: " + data[
                             'methode'] + " on the devices:")
            # Create parameter for get requests (Client-Client)
            getdata = "multicast_ip=" + multicast + "&methode=" + data['methode']
            for num, ip in enumerate(data['device_ips']):
                urls.append(conf_client_client.protocol + "://" + ip + ":" + str(
                    conf_client_client.port) + conf_client_client.path + "?" + getdata)
                logging.info("\t" + urls[num])

            # send requests
            # urls.append("http://localhost:3020/api/v1/test")
            resp = req.greq(urls)
            print(resp)
            for num, response in enumerate(resp):
                if response is None:
                    dead_ips.append(data['device_ips'][num])
                elif response.status_code == status_codes.internal_server_error:
                    err_list.append({'code': status_codes.internal_server_error, 'message': 'Internalservererror at: ' + data['device_ips'][num]})
                elif response.status_code != status_codes.ok:
                    err_list.append({'code': response.status_code, 'message': 'Server probably not running'})
                    dead_ips.append(data['device_ips'][num])

            print(dead_ips)
            print(err_list)

            if len(dead_ips) != 0:
                return {'error': {'code': status_codes.not_found, 'message': 'Device/s unavailable'}, 'dead_ips': dead_ips}, status_codes.not_found

            return
        else:
            # TODO: Activate Bluetooth and play on local pi
            return
    def delete(self):
        # TODO: deactivate Bluetooth & send DELETE to Client-Client\listen
        return {"error": "Not Implemented"}


api.add_resource(Playback, conf_client_backend.path)


if __name__ == '__main__':
    from gevent import monkey

    monkey.patch_all()
    app.run(host="0.0.0.0", port=conf_client_backend.port, debug=False, threaded=True)
