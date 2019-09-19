cd /home/pi/

echo "Beginning installation..."
sleep 1s

echo "Searching for updates..."
sudo apt-get -y update

echo "Searching for upgrades..."
sudo apt-get -y upgrade

echo "Installing pandas..."
sudo apt-get install -y python3-pandas

echo "Installing xarray..."
pip3 install xarray

echo "Installing numpy..."
sudo apt-get install -y python3-numpy

echo "Installing matplotlib..."
pip3 install matplotlib

echo "Installing datetime..."
pip3 install datetime

echo "Installing requests..."
pip3 install requests

echo "Installing netCDF4..."
pip3 install netCDF4

"Do you want to install xscreensaver?"
select yn in "Y" "N"; do
  case $yn in
      Y ) sudo apt-get install -y xscreensaver; break;;
      N ) exit;;
  esac
done


"Do you want to install unclutter?"
select yn in "Y" "N"; do
  case $yn in
      Y ) sudo apt-get install -y unclutter; break;;
      N ) exit;;
  esac
done

echo "Searching for updates..."
sudo apt-get -y update

echo "Searching for upgrades..."
sudo apt-get -y upgrade

echo "Setting up executables..."
cd /home/pi/RPiOOI
chmod +x CE01ISSM_MFN_TSDO.py
sleep 1s
chmod +x CE02SHBP_BEP_TSDO.py
sleep 1s
chmod +x CE09OSPM_MMP_TS.py
sleep 1s

echo "Installation complete!"
echo "Rebooting the system in 30 seconds..."
sleep 30s
sudo reboot
