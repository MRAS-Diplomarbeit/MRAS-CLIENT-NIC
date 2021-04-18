screen -dmS bc bash -c "cd mrasclient; python3 /home/pi/mras/mrasclient/API/api.py -c /home/pi/mras/config.yml"
screen -dmS cc bash -c "cd mrasclient; python3 /home/pi/mras/mrasclient/API/client_client.py -c /home/pi/mras/config.yml"
