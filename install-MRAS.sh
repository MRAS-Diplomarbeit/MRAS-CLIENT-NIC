#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Please run as sudo"
  exit
fi

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

HOSTNAME='localhost'

clear
if [ $(ping localhost) != 0 ];
then
  printf "Is this the first MRAS-Device in your Network? [${GREEN}Y${NC}|${RED}N${NC}](default: ${YELLOW}Y${NC}):"
  read server

  while [ "$server" != "Y" ] && [ "$server" != "N" ] && [ "$server" != " " ];
  do
    printf "Wrong input: ${RED}$server${NC}. Please choose [${GREEN}Y${NC}|${RED}N${NC}]:"
    read server
  done

  # test if it is the first server
  if [ "$server" != "N" ];
  then
    echo install server
    # TODO: install server parts
  fi
fi
printf "Please enter "

mkdir MRAS
cd MRAS
apt-get install git python3-pip python3-venv pulseaudio pulseaudio-utils -y


# Bluetooth set rights
sudo usermod -a -G bluetooth pi


python3 -m pip install --user virtualenv
python3 -m venv venv
source venv/bin/activate
pip3 install flask flask_restful pyyaml aiohttp requests grequests