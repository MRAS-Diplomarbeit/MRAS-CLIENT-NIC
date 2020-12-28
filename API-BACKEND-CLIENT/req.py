import requests


def req_listen_get(PROT, IP, PATH, DATA):
    try:
        # Building URL
        URL = PROT + "://" + IP + PATH
        # Timeout set to 1 sec to not block for long
        resp = requests.get(url=URL, params=DATA, timeout=1)
        if resp.status_code == 400:
            print("[ERROR]-Bad Request: "+resp.json())
            return {'ERROR':'Client not started at: '+IP}
        elif resp.status_code == 500:
            print("[ERROR]-Exception at client: "+IP)
        elif not resp.status_code == 200:
            print("[ERROR]-Unknown response from client: "+IP)
            return {'ERROR': 'Client not started at: ' + IP}
    except (requests.ConnectionError, requests.Timeout, requests.HTTPError):
        print("[ERROR]-Connection Error occurred. IP:" + IP + " is unavailable")
        return {"ERROR": "Connection Error occurred. IP:" + IP + " is unavailable"}
    except requests.exceptions.InvalidURL:
        print("[ERROR]-Invalid url: "+URL)
        # TODO: bad request 400