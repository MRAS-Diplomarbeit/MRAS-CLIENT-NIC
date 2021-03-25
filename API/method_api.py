from flask import request
from flask_restful import Resource
from tinydb import where, Query

import constants
import helper
import pulse_control
import status_codes
from DB.db_access import Access
from excep import NoSinkInputsFoundException, NoCardsFoundException, ElementNotFoundException


class Method(Resource):
    def get(self):
        return {'methods': pulse_control.get_card_names()}

    def put(self):
        data = request.get_json()
        missing_param = helper.data_available(data, ['method'])
        if len(missing_param) != 0:
            return {'code': status_codes.multiple_param_missing, "message": "Please provide all necessary data " +
                                                                            str(missing_param).replace("'",
                                                                                                       "")}, status_codes.bad_request

        DB = Access()
        res = Query()
        if len(DB.db.search((res.name == constants.db_interface_name) & (res.value == data['method']))) > 0:
            return {'code': status_codes.already_on_interface, 'message': "Interface is already in use"}

        # try to switch audio interface on current session
        try:
            bluetooth_sink_id = pulse_control.get_sink_input_id(constants.loopback_driver)
            card_id = pulse_control.get_card_id(data['method'])
            pulse_control.move_sink_input(bluetooth_sink_id, card_id)
        except NoSinkInputsFoundException:
            pass
            # Ignoring error since the method can be changed while there is no one listening
        except NoCardsFoundException:
            return {'code': status_codes.interface_not_found, 'message': "The interface: " + data['method']
                                                                         + " is not available"}
        except ElementNotFoundException:
            return {}, 400  # Should not be called, NoSinkInputsFoundException should be raised first

        # test if card is valid and changing audio output device, while no bluetooth device is connected
        try:
            pulse_control.get_card_id(data['method'])
            DB.db.update({"name": constants.db_interface_name, "value": data['method']})
        except NoCardsFoundException:
            return {'code': status_codes.interface_not_found, 'message': "The interface: " + data['method']
                                                                         + " is not available"}
