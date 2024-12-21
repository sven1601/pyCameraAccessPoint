#!/bin/sh
CYAN='\033[0;36m'
NC='\033[0m'
GRE='\033[0;32m'
echo "\n${CYAN}########## Welcome! ##########"

#source config.sh

echo "\n${GRE}Setting up WiFi Access Point...${NC}"

read -p "Enter your desired WiFi Network Name: " ssid
read -p "Enter your WiFi Countrycode (US, DE, ...): " wifiCode
read -p "Enter your desired password: " pw1
read -p "Enter your desired password (again): " pw2
read -p "Enter your desired ap ip address: " ip
read -p "Enter your desired ap name: " apName
read -p "Should the camera recording directly be started after boot? [y/n] " camAutostart

if [[ "$pw1" == "$pw2" ]] && \
   [[ $(expr length "$ssid") -gt 0 ]] && \
   [[ $(expr length "$wifiCode") -gt 0 ]] && \
   [[ $(expr length "$pw1") -gt 7 ]] && \
   [[ $(expr length "$pw2") -gt 7 ]] && \
   [[ $(expr length "$ip") -gt 0 ]] && \
   [[ $(expr length "$apName") -gt 0 ]] && \
   [[ $(expr length "$camAutostart") -eq 1 ]] && ([[ "$camAutostart" == "y" ]] || [[ "$camAutostart" == "n" ]]) \
   ; 
then

    # Access Point ----------------------------------------------------------------------------------------------------    
    sudo raspi-config nonint do_wifi_country "$wifiCode"
    sudo apt update
    sudo apt upgrade -y
    sudo apt install -y dnsmasq python3-picamera2 ffmpeg
    sudo systemctl disable dnsmasq
    sudo systemctl stop dnsmasq
    sudo sed -i '/\[main\]/a dns=dnsmasq' /etc/NetworkManager/NetworkManager.conf
    sudo nmcli con add type wifi ifname wlan0 mode ap con-name "$apName" ssid "$apName" autoconnect true
    sudo nmcli con modify raspiAP 802-11-wireless.band bg
    sudo nmcli con modify raspiAP 802-11-wireless.channel 3
    sudo nmcli con modify raspiAP 802-11-wireless.cloned-mac-address 00:12:34:56:78:9a
    sudo nmcli con modify raspiAP ipv4.method shared ipv4.address "$ip"/24
    sudo nmcli con modify raspiAP ipv6.method disabled
    sudo nmcli con modify raspiAP wifi-sec.key-mgmt wpa-psk
    sudo nmcli con modify raspiAP wifi-sec.psk "$pw1"

    # Webserver ----------------------------------------------------------------------------------------------------
    wget https://raw.githubusercontent.com/sven1601/...../webserver.py
    python -m venv --system-site-packages ~/PythonVenv/Webserver
    mv ~/webserver/* ~/PythonVenv/Webserver/
    mkdir ~/video_files
    ~/PythonVenv/Webserver/bin/pip install flask-wtf
    (crontab -l ; echo "@reboot ~/PythonVenv/Webserver/bin/python ~/PythonVenv/Webserver/webserver.py > webserverLog.txt 2>&1") | crontab -

    # Camera ----------------------------------------------------------------------------------------------------
    wget https://raw.githubusercontent.com/sven1601/...../camera.py
    python -m venv --system-site-packages ~/PythonVenv/Cam
    mv ~/camera/* ~/PythonVenv/Cam/
    if [[ "$camAutostart" == "y" ]]
        (crontab -l ; echo "@reboot ~/PythonVenv/Cam/bin/python ~/PythonVenv/Cam/camera.py > cameraLog.txt 2>&1") | crontab -
    
    echo "\n\n\n"
    echo          "########## All Done! The RPi IP Address is "$ip" ##########"
    echo          "########## Please reboot for changes to take effect  ######"
    echo "\n\n\n"

else
    echo "Parameter error, please check your input"
    exit
fi