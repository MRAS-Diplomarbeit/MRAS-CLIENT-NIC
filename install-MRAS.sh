# if [ "$EUID" -ne 0 ]
#   then echo "Please run as sudo"
#   exit
# fi

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

HOSTNAME='mrasserver'

parse_yaml () {
  while read line; do
    echo $line | grep $1 | cut -d' ' -f 2
  done < config.yml
}

print_quest () {
  printf "%s [${GREEN}Y${NC}|${RED}N${NC}](default: ${YELLOW}Y${NC})" "$1"
}

to_lower_case() {
  local lowercase=$(echo $1 | tr '[A-Z]' '[a-z]')
  echo $lowercase
}

get_validate_answer(){
  local temp='init'
  read temp
  temp=$(to_lower_case $temp)
  while [ "$temp" != "y" ] && [ "$temp" != "n" ] && [ "$temp" != "" ];
  do
    print_quest "Please enter a valid option! $1"
    read temp
    temp=$(to_lower_case $temp)
  done
  if [ "$temp" == 'y' ];
  then
    return 1
  fi
  return 0
}


clear
# Testing if this is the first MRAS-Device (Default settings)
if ! ping -c 1 -w 2 $HOSTNAME > /dev/null;
then

  print_quest "Is this the first MRAS-Device in your Network?"
  get_validate_answer "Is this the first MRAS-Device in your Network?"

  if [ $? != 0 ];
  then
    echo Installing Server components
    curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash -
    sudo apt-get install wamerican redis-server mariadb-server nodejs wget -y

    # Change the hostname?
    print_quest "Do you want to automatically change the hostname of this device to automate further installations of Clients?"
    get_validate_answer "Do you want to automatically change the hostname of this device to automate further installations of Clients?"
    if [ $? != 0 ];
    then
      sudo hostname $HOSTNAME
      echo hostname changed
    fi

    mkdir mras
    cd mras
    
    wget -q https://raw.githubusercontent.com/MRAS-Diplomarbeit/MRAS-API-SPEC/main/config/config.yml

    # auto-generating tokens
    accesstoken=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
    refreshtoken=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)

    # asking/ auto-genrating DB user
    print_quest "Do you want to name the mariaDB User?"
    get_validate_answer "Do you want to name the mariaDB User?"
    if [ $? != 0 ];
    then
      echo Enter the username
      read mariaUser
      echo Enter the password
      read -s mariaPW
    else
      mariaUser="mras"
      mariaPW=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
    fi

    # replacing placeholders in config file
    sed -i "s|\[\[ACCESSTOKEN\]\]|$accesstoken|g" config.yml
    sed -i "s|\[\[REFRESHTOKEN\]\]|$refreshtoken|g" config.yml
    sed -i "s|\[\[DBUSER\]\]|$mariaUser|g" config.yml
    sed -i "s|\[\[DBPASSWORD\]\]|$mariaPW|g" config.yml

    # Setting-up MariaDB
    sudo mysql -e "CREATE USER $mariaUser@localhost IDENTIFIED BY '$mariaPW'"
    dbname=$(parse_yaml "dbname")
    sudo mysql -e "CREATE SCHEMA ${dbname//\"}"
    sudo mysql -e "GRANT ALL PRIVILEGES ON ${dbname//\"}.* TO $mariaUser@localhost"
    sudo mysql -e "flush privileges"

    echo installing website
    wget -q https://github.com/MRAS-Diplomarbeit/MRAS_FRONTEND/releases/latest/download/web-build.tar
    tar -xvf web-build.tar

    wget -q https://github.com/MRAS-Diplomarbeit/MRAS-API/releases/download/v0.0.1/mras-api-arm
    sudo chmod +x mras-api-arm

    wget -q https://github.com/MRAS-Diplomarbeit/MRAS-CLIENT-NIC/releases/download/latest/Backend-Services.tar.gz
    tar -xvf Backend-Services.tar.gz
    sudo cp services/mrasbackend.service /etc/systemd/system/
    sudo cp services/mrasweb.service /etc/systemd/system/
    sudo systemctl enable mrasbackend
    sudo systemctl start mrasbackend
    sudo systemctl enable mrasweb
    sudo systemctl start mrasweb

  else
    print_quest "Have you changed the hostname of the inital server?"
    get_validate_answer "Have you changed the hostname of the inital server?"
    if [ $? != 0 ];
    then
      read hostname
      # TODO: set hostname for /discover
    fi
  fi
fi
mkdir mrasclient
cd mrasclient

sudo apt-get install python3 python3-pip python3-venv pulseaudio pulseaudio-utils pulseaudio-module-bluetooth bluez-tools -y
# setup Bluetooth
sudo usermod -a -G bluetooth pi
echo Class = 0x41c | sudo tee -a /etc/bluetooth/main.conf
echo DiscoverableTimeout = 0 | sudo tee -a /etc/bluetooth/main.conf

# Downlaoding and installing python libs
wget -q https://raw.githubusercontent.com/MRAS-Diplomarbeit/MRAS-CLIENT-NIC/main/requirements.txt
pip3 install -r requirements.txt
#Downloading Backend-Client API
wget -q https://github.com/MRAS-Diplomarbeit/MRAS-CLIENT-NIC/releases/latest/download/api.tar.gz
tar -zxvf api.tar.gz

#Downloading discover and discover service and starting it
wget -q https://github.com/MRAS-Diplomarbeit/MRAS-CLIENT-NIC/releases/download/latest/discover.py
wget -q https://github.com/MRAS-Diplomarbeit/MRAS-CLIENT-NIC/releases/download/latest/mrasdiscover.service
sed -i "s|\[\[HOSTNAME\]\]|$hostname|g" mrasdiscover.service
sudo mv mrasdiscover.service /etc/systemd/system/mrasdiscover.service
sudo systemctl start mrasdiscover

# mkdir MRAS
# cd MRAS
# apt-get install git python3-pip python3-venv pulseaudio pulseaudio-utils -y


# Bluetooth set rights
# sudo usermod -a -G bluetooth pi


# python3 -m pip install --user virtualenv
# python3 -m venv venv
# source venv/bin/activate
# pip3 install flask flask_restful pyyaml aiohttp requests grequests