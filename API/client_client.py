from flask import Flask, request
from flask_restful import Api, Resource

import pulse_control as pulse
import constants as const

app = Flask(__name__)
api = Api(app)

# TODO: Not Thread safe
is_listening = False


class Listen(Resource):
    def get(self):
        global is_listening
        if is_listening:
            return {'code': 400, 'message': 'Please stop listening before starting new session'}, 400
        data = request.args
        if data is None:
            return {'code': 400, 'message': 'Please provide data'}, 400
        elif 'multicast_ip' not in data or 'method' not in data:
            print("error")
            return 400
        # TODO: Listen to multicast ip

        pulse.listen_to_stream(data['multicast_ip'], const.default_latency)
        is_listening = True

    def delete(self):
        # TODO: Stop listening
        global is_listening
        if not is_listening:
            return {'code': 400, 'message': 'Currently not listening'}, 400
        is_listening = False
        pulse.stop_incoming_stream()


api.add_resource(Listen, '/api/v1/listen')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3020, debug=False, threaded=False)
