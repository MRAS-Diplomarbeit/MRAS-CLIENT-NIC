from datetime import datetime
import requests
import helper


def log(message) -> str:
    return str(datetime.now()) + message


def send_log(ip: str, log_arr: [str]) -> bool:
    print("Logging to: " + ip)
    print(log_arr)
    # TODO: replace mock server with real ip
    # resp = requests.post("http://ad21d7ee-c4d7-4dc2-8b0c-35b2083b27c5.mock.pstmn.io/log", json={'lines': log_arr})
    try:
        resp = requests.post("http://" + ip + "/log", json={'lines': log_arr})
        return resp.ok
    except:
        print(helper.add_time("ERROR: Server is ignoring /log commands. Logs will not be saved"))
        print(log_arr)
        return False

