#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Please run as sudo"
  exit
fi

mkdir MRAS
cd MRAS
apt-get install git python3-pip python3-venv pulseaudio pulseaudio-utils -y


# Bluetooth set rights
sudo usermod -a -G bluetooth pi


python3 -m pip install --user virtualenv
python3 -m venv venv
source venv/bin/activate
pip3 install flask flask_restful pyyaml aiohttp requests grequests