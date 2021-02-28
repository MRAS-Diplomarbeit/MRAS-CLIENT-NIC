from flask_restful import Api, Resource
import load_config as conf
import status_codes
import constants

config = conf.Client(constants.confLoc)

class AllLogs(Resource):
    def get(self):
        try:
            log_arr = read_log()
            return {'lines': log_arr}
        except:
            return {'code': status_codes.err_reading_log, 'message': 'Error reading log file'}, 500


class LogsToLine(Resource):
    def get(self, lines):
        try:
            log_arr = read_log()
            if lines > len(log_arr):
                return {'code': status_codes.too_many_lines,
                        'message': 'Too many lines requested, current log lines:' + str(len(log_arr))}, 400
            return {'lines': log_arr[len(log_arr) - lines: len(log_arr)]}, 200
        except:
            return {'code': status_codes.err_reading_log, 'message': 'Error reading log file'}, 500


def read_log() -> list:
    with open(config.log_path+config.log_name, "r") as f:
        return list(f)
