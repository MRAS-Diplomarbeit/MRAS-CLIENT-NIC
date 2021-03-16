from flask import request
from flask_restful import Resource

import pulse_control
import helper
import status_codes
import constants


class Method(Resource):
    def get(self):
        return {'methods': pulse_control.get_card_names()}

    def put(self):
        data = request.get_json()
        missing_param = helper.data_available(data, ['method'])
        if len(missing_param) != 0:
            return {'code': status_codes.multiple_param_missing, "message": "Please provide all necessary data " +
                                                                            str(missing_param).replace("'", "")}, status_codes.bad_request

        bluetooth_sink_id = pulse_control.get_sink_input_id(constants.loopback_driver)
        card_id = pulse_control.get_card_id(data['method'])
        pulse_control.move_sink_input(bluetooth_sink_id, card_id)

