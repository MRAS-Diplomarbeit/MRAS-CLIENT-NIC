from flask import Flask, request
from flask_restful import Api, Resource

import constants as const
import req

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
            for ip in data["device_ips"]:
                data = {'multicast_ip': multicast, 'methode': data['methode']}

                # not running as thread to respond to request from backend
                resp = req.req_listen_get(const.clientClientProtocoll, ip, const.clientClientApiPath, data)
                print(resp)
                if resp is not None and 'ERROR' in resp:
                    err_list.append(resp['ERROR'])
                    dead_ips.append(ip)

            if len(err_list) is not 0:
                print("Error occurred")
                print(err_list)
                return {'error': {'code': 15, 'message': 'Device unavailable'}, 'dead_ips': dead_ips}, 404
                # TODO: send error as response to backend
            # TODO: activate Bluetooth, trx multicast server and send GET to Client-Client\listen with multicast_ip
            return

    def delete(self):
        # TODO: deactivate Bluetooth & send DELETE to Client-Client\listen
        return {"error": "Not Implemented"}


api.add_resource(Playback, "/api/v1/playback")


# @app.route('/')
# def hello_world():
#     return 'Hello World!'


if __name__ == '__main__':
    app.run(port=3010)
