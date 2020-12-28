#!/bin/bash
if [ "$EUID" -ne 0 ]
  then echo "Please run as sudo"
  exit
fi

apt-get install git libasound2-dev libopus-dev libortp-dev libasound2-doc
git clone http://www.pogo.org.uk/~mark/trx.git
make
make install