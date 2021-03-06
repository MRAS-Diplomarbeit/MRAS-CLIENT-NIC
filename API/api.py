from flask import Flask
from flask_restful import Api

import load_config
import constants
import log_api
import playback_api
import method_api
import controll_api
import sys

app = Flask(__name__)
api = Api(app)

conf_client_backend = load_config.ClientBackend(constants.confLoc)

if conf_client_backend.error is not None:
    load_config.err_handling(conf_client_backend.error, "client-backend")

api.add_resource(playback_api.Playback, conf_client_backend.path_playback)
api.add_resource(log_api.AllLogs, '/api/v1/log')
api.add_resource(log_api.LogsToLine, '/api/v1/log/<int:lines>')
api.add_resource(method_api.Method, conf_client_backend.path_method)
api.add_resource(controll_api.Volume, '/api/v1/volume')
api.add_resource(controll_api.Delay, '/api/v1/delay')


if __name__ == '__main__':
    from gevent import monkey
    monkey.patch_all()

    app.run(host="0.0.0.0", port=conf_client_backend.port, debug=True, threaded=True)
