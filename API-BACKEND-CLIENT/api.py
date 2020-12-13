from flask import Flask, request
from flask_restful import Api, Resource

import json

app = Flask(__name__)
api = Api(app)

class Playback(Resource):
    def post(self):
        data = request.get_json()
        # print(data["methode"])
        if data is None:
            return {"error": "No data supplied"}, 400
        if "methode" not in data or "displayname" not in data or "device_ips" not in data:
            return {"error": "Body must contain methode, displayname, device_ips"}, 400
        else:
            # activate Bluetooth, trx multicast server and send GET to Client-Client\listen with multicast_ip
            return

    def delete(self):
        # deactivate Bluetooth & send DELETE to Client-Client\listen
        return {"error":"Not Implemented"}

api.add_resource(Playback,"/api/v1/playback")

# @app.route('/')
# def hello_world():
#     return 'Hello World!'


if __name__ == '__main__':
    app.run(port=3010)
