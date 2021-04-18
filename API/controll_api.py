from flask import request
from flask_restful import Resource, reqparse
from tinydb import Query

import pulse_control as pulse
import helper
import status_codes
import constants
from DB.db_access import Access

DB = Access()
query = Query()

class Volume(Resource):
    def post(self):
        data = request.get_json()
        missing_param = helper.data_available(data, ["level", "interface"])
        if missing_param != 0:
            return {'code': status_codes.multiple_param_missing, "message": "Please provide all necessary data " +
                                                                            str(missing_param).replace("'",
                                                                                                      "")}, status_codes.bad_request

        sink_input_id = pulse.get_sink_input_id(constants.loopback_driver)
        pulse.change_volume_sink_input(sink_input_id, data['level']+"%")


class Delay(Resource):
    def get(self):
        data = DB.db.search(query.name == "delay")
        print(data)
        if len(data) > 0:
            return {"delay": data[0]['value']}
        else:
            return {'code': status_codes.no_delay_set, 'message': "No delay set"}
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('delay', type=int, required=True, help="Please provide delay")
        data = parser.parse_args()
        DB = Access()
        query = Query()
        DB.db.upsert({'name':'delay', 'value': data['delay']}, query.name == 'delay')
