#!/bin/bash
echo "\n########## Welcome! ##########"

camPyScript="https://raw.githubusercontent.com/sven1601/pyCameraAccessPoint/refs/heads/main/python/camera/camera.py"
camSettingsIni="https://raw.githubusercontent.com/sven1601/pyCameraAccessPoint/refs/heads/main/python/camera/settings.ini"
webserverPyScript="https://raw.githubusercontent.com/sven1601/pyCameraAccessPoint/refs/heads/main/python/webserver/webserver.py"
webserverHtmlFiles="https://raw.githubusercontent.com/sven1601/pyCameraAccessPoint/refs/heads/main/python/webserver/templates/files.html"
webserverHtmlIndex="https://raw.githubusercontent.com/sven1601/pyCameraAccessPoint/refs/heads/main/python/webserver/templates/index.html"

echo "\n${GRE}Setting up WiFi Access Point...${NC}"

read -p "Enter your desired ap name: " apName
read -p "Enter your WiFi Countrycode (US, DE, ...): " wifiCode
read -p "Enter your desired password: " pw1
read -p "Enter your desired password (again): " pw2
read -p "Enter your desired ap ip address: " ip

if [ ! "$pw1" == "$pw2" ]; then
    echo "Pasword not equal, please check input"
    exit
elif [ ! $(expr length "$wifiCode") -eq 2 ]; then
    echo "Wrong wifi code, please check your input"
    exit
elif [ ! $(expr length "$pw1") -gt 7 ];  then
    echo "Password too short, please check your input"
    exit
elif [ ! $(expr length "$pw2") -gt 7 ]; then
    echo "Password too short, please check your input"
    exit
elif [ ! $(expr length "$ip") -gt 6 ]; then
    echo "Ip too short, please check your input"
    exit
elif [ ! $(expr length "$apName") -gt 2 ]; then
    echo "AP name too short, please check your input"
    exit
fi

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
sudo nmcli con modify raspiAP 802-11-wireless.powersave disable
sudo nmcli con modify raspiAP ipv4.method shared ipv4.address "$ip"/24
sudo nmcli con modify raspiAP ipv6.method disabled
sudo nmcli con modify raspiAP wifi-sec.key-mgmt wpa-psk
sudo nmcli con modify raspiAP wifi-sec.psk "$pw1"
# Webserver ----------------------------------------------------------------------------------------------------
wget $webserverPyScript
wget $webserverHtmlIndex
wget $webserverHtmlFiles
python -m venv --system-site-packages ~/PythonVenv/Webserver
mkdir ~/PythonVenv/Webserver/templates
mkdir ~/PythonVenv/Webserver/static
mkdir ~/video_files
mv ./webserver.py ~/PythonVenv/Webserver/
mv ./index.html ~/PythonVenv/Webserver/templates/
mv ./files.html ~/PythonVenv/Webserver/templates/    
~/PythonVenv/Webserver/bin/pip install flask-wtf
(crontab -l ; echo "@reboot wait 20;~/PythonVenv/Webserver/bin/python ~/PythonVenv/Webserver/webserver.py > webserverLog.txt 2>&1") | crontab -
# Camera ----------------------------------------------------------------------------------------------------
wget $camPyScript
wget $camSettingsIni
python -m venv --system-site-packages ~/PythonVenv/Cam
mv ./camera.py ~/PythonVenv/Cam/
mv ./settings.ini ~/PythonVenv/Cam/
# Other ----------------------------------------------------------------------------------------------------
sudo sed -i '$a cam ALL=NOPASSWD:/sbin/shutdown' /etc/sudoers
sudo sed -i '$a cam ALL=NOPASSWD:/sbin/reboot' /etc/sudoers
# End ----------------------------------------------------------------------------------------------------
echo "\n\n\n"
echo          "########## All Done! The RPi IP Address is "$ip" ##########"
echo          "########## Please reboot for changes to take effect  ######"
echo "\n\n\n"
read -p "Reboot now? [y/n] " reboot
if [ "$reboot" = "y" ]; then
    sudo reboot
fi





