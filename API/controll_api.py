from flask import request
from flask_restful import Resource

import pulse_control as pulse
import helper
import status_codes
import constants


class Volume(Resource):
    def post(self):
        data = request.get_json()
        missing_param = helper.data_available(data, ["level", "interface"])
        if missing_param != 0:
            return {'code': status_codes.multiple_param_missing, "message": "Please provide all necessary data " +
                                                                            str(missing_param).replace("'",
                                                                                                      "")}, status_codes.bad_request

        sink_input_id = pulse.get_sink_input_id(constants.loopback_driver)
        pulse.change_volume_sink_input(sink_input_id, 0)

        # TODO: delay
