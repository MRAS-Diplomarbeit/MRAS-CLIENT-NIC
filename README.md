 # Install
 - To install just download and run the install script from the folder where you would like to intstall 
 #### Automatic
 - To download and run automatically as ROOT:
 ```bash
 sudo su -c "bash <(wget -qO- https://raw.githubusercontent.com/MRAS-Diplomarbeit/MRAS-CLIENT-NIC/main/install-MRAS.sh)" root
 ```
 #### Manual
 - Download the script and run as ROOT:
 ```
 wget https://raw.githubusercontent.com/MRAS-Diplomarbeit/MRAS-CLIENT-NIC/main/install-MRAS.sh
 sudo chmod 700 install-MRAS.sh
 sudo ./install-MRAS.sh 
 ```

# Client
Install script for the MRAS Project

### Error Codes
| Code | meaning | API |
|:-:|:-:|:-:|
| 200 | Ok | *
| 400 | Bad Request | *
| 404 | Not Found | *
| 500 | Internal Server Error | *
| 1000 | One parameter is missing | *
| 1001 | Multiple parameters are missing | *
| 1101 | Client not found | POST /playback
| 1102 | Client is currently not listening | DELETE /playback
| 1103 | Bluetooth error | POST /playback
| 1104 | Pulseaudio error | POST /playback
| 1105 | The sink was not found |
| 1106 | Requested to many lines | GET /log/<lines[INT]>
| 1107 | Error reading log file | GET /log

### Info
 - Decompress with
 ```bash
 gzip -d log.txt.1.gz
 ```



