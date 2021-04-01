from datetime import datetime
import requests
import helper


def log(message) -> str:
    return str(datetime.now()) + message


def send_log(ip: str, log_arr: [str]) -> bool:
    print("Logging to: " + ip)
    try:
        resp = requests.post("http://" + ip + "/log", json={'lines': log_arr})
        return resp.ok
    except:
        print(helper.add_time("ERROR: Server is ignoring /log commands. Logs will not be saved"))
        print(log_arr)
        return False

