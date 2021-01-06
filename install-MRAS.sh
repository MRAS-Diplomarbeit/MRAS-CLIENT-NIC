#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Please run as sudo"
  exit
fi

mkdir MRAS
cd MRAS
apt-get install git libasound2-dev libopus-dev libortp-dev libasound2-doc build-essentials python3-pip alsa-base
git clone http://www.pogo.org.uk/~mark/trx.git
cd trx
make
make install
cd ..
python3 -m pip install --user virtualenv
python3 -m venv venv
source venv/bin/activate
pip3 install flask flask_restful pyyaml aiohttp requests grequests