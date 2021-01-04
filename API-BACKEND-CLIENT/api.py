# from gevent import monkey as curious_george
# curious_george.patch_all(thread=False, select=False)
from flask import Flask, request
from flask_restful import Api, Resource

import constants as const
import req
import asyncio

app = Flask(__name__)
api = Api(app)


class Playback(Resource):
    def post(self):
        data = request.get_json()

        if data is None:
            return {"error": "No data supplied"}, 400

        elif "methode" not in data or "displayname" not in data or "device_ips" not in data:
            return {"error": "Body must contain methode, displayname, device_ips"}, 400

        else:
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

            # Create parameter for get requests (Client-Client)
            getdata = "multicast_ip=" + multicast + "&methode=" + data['methode']
            for ip in data['device_ips']:
                urls.append(const.clientClientProtocoll + "://" + ip + ":" + str(
                    const.clientClientPort) + const.clientClientApiPath + "?" + getdata)

            # send requests
            # urls.append("http://localhost:3020/api/v1/test")
            resp = req.greq(urls)
            print(resp)
            for num, response in enumerate(resp):
                if response is None:
                    dead_ips.append(data['device_ips'][num])
                elif response.status_code == 500:
                    err_list.append({'code': 500, 'message': 'Internalservererror at: ' + data['device_ips'][num]})
                elif response.status_code != 200:
                    err_list.append({'code': response.status_code, 'message': 'Server probably not running'})
                    dead_ips.append(data['device_ips'][num])

            print(dead_ips)
            print(err_list)

            if len(dead_ips) != 0:
                return {'error': {'code': 15, 'message': 'Device/s unavailable'}, 'dead_ips': dead_ips}, 404

            return

    def delete(self):
        # TODO: deactivate Bluetooth & send DELETE to Client-Client\listen
        return {"error": "Not Implemented"}


api.add_resource(Playback, "/api/v1/playback")

# @app.route('/')
# def hello_world():
#     return 'Hello World!'


if __name__ == '__main__':
    from gevent import monkey
    monkey.patch_all()
    app.run(port=3010)
