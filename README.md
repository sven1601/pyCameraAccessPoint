# pyCameraAccessPoint
 A raspberryPi as Access Point with camera controls

## Setup

1. Setup your Rpi as desired, with Wifi enabled as client, Username "cam", and SSH enabled (recommended) and reboot it.
   An user initiated update after the first boot is not required, as this will be done during the setup process.
2. Connect with SSH to your Rpi
3. Run the following commands:
   - Download the setup script<br>
      `wget https://raw.githubusercontent.com/sven1601/pyCameraAccessPoint/refs/heads/main/setup.sh`
   - Make it executable<br>
      `sudo chmod +x ./setup.sh`
   - Run it<br>
      `./setup.sh`

All necessary data will be queried after the start of the script. 

Tested with:
- Rasperry Pi Zero 2W
- PiCamera V3 Wide
- RaspiOS Bookworm Lite