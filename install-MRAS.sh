if [ "$EUID" -ne 0 ]
  then echo "Please run as sudo"
  exit
fi

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
  #printf "Is this the first MRAS-Device in your Network? [${GREEN}Y${NC}|${RED}N${NC}](default: ${YELLOW}Y${NC}):"
  #read server

  #while [ "$server" != "Y" ] && [ "$server" != "N" ] && [ "$server" != " " ];
  #do
  #  printf "Wrong input: ${RED}$server${NC}. Please choose [${GREEN}Y${NC}|${RED}N${NC}]:"
  #  read server
  #done

  print_quest "Is this the first MRAS-Device in your Network?"
  get_validate_answer "Is this the first MRAS-Device in your Network?"

  if [ $? != 0 ];
  then
    echo Installing Server components
    curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash -
    apt-get install wamerican redis-server mariadb-server nodejs wget -y
    npm install npx

    # Change the hostname?
    print_quest "Do you want to automatically change the hostname of this device to automate further installations of Clients?"
    get_validate_answer "Do you want to automatically change the hostname of this device to automate further installations of Clients?"
    if [ $? != 0 ];
    then
      hostname $HOSTNAME
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
      print "Enter the username"
      read mariaUser
      print "Enter the password"
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
    mysql -e "CREATE USER $mariaUser@localhost IDENTIFIED BY '$mariaPW'"
    dbname=$(parse_yaml "dbname")
    mysql -e "CREATE SCHEMA $dbname"
    mysql -e "GRANT ALL PRIVILEGES ON database_name.$dbname TO $mariaUser@localhost"

    # downlaod website wget GITHUB_RELEASE
    # 
  fi

  # test if it is the first server
  if [ "$server" != "N" ];
  then
    echo install server
    # TODO: install node (webserver)
    # apt-get install wamerican redis-server mariadb-server -y
    hostname $HOSTNAME
    mysql -e "CREATE USER "
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