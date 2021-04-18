import requests
import time
import sys

hostname = str(sys.argv[1])

while True:
    requests.get("http://" + hostname + ":3001/discover")
    time.sleep(20)
