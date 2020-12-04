from flask import Flask, request
from flask_restful import Api, Resource

import json

app = Flask(__name__)
api = Api(app)

class Playback(Resource):
    def post(self):
        data = request.get_json()
        # print(data["methode"])
        if "methode" in data and "displayname" in data and "device_ips" in data:
            print("jo")
            # activate Bluetooth, trx multicast server and send GET to Client-Client\listen with multicast_ip
            return
        else:
            return {"ERROR":"Wrong JSON"},404

    def delete(self):
        # deactivate Bluetooth & send DELETE to Client-Client\listen
        return {"error":"Not Implemented"}

api.add_resource(Playback,"/api/v1/playback")

# @app.route('/')
# def hello_world():
#     return 'Hello World!'


if __name__ == '__main__':
    app.run(debug=True, port=3100)
