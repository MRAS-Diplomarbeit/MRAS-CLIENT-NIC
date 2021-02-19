#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Please run as sudo"
  exit
fi

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

HOSTNAME='mrasserver'

clear
# Testing if this is the first MRAS-Device (Default settings)
if ! ping -c 1 -w 2 $HOSTNAME > /dev/null;
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
    # TODO: install node (webserver)
    # apt-get install wamerican redis-server mysql-server -y
    hostname $HOSTNAME
  else
    printf "Have you changed the hostname of the server? [${GREEN}Y${NC}|${RED}N${NC}](default: ${YELLOW}N${NC}):"
    read changedHost
    while [ "$changedHost" != "Y" ] && [ "$changedHost" != "N" ] && [ "$changedHost" != " " ];
      do
      printf "Wrong input: ${RED}$server${NC}. Please choose [${GREEN}Y${NC}|${RED}N${NC}]:"
      read server
    done
    if [ "$changedHost" == "Y" ];
    then
      printf "Please enter the hostname of the initial server"
      read HOSTNAME
    fi
  fi
fi
printf "Installing MRAS-Client"

# mkdir MRAS
# cd MRAS
# apt-get install git python3-pip python3-venv pulseaudio pulseaudio-utils -y


# Bluetooth set rights
# sudo usermod -a -G bluetooth pi


# python3 -m pip install --user virtualenv
# python3 -m venv venv
# source venv/bin/activate
# pip3 install flask flask_restful pyyaml aiohttp requests grequests