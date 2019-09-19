echo "Beginning installation..."
sleep 1s

echo "Searching for updates..."
sudo apt-get -y update

echo "Searching for upgrades..."
sudo apt-get -y upgrade

echo "Installing xarray..."
pip3 install xarray

echo "Installing numpy..."
pip3 install numpy

echo "Installing matplotlib..."
pip3 install matplotlib

echo "Installing pandas..."
pip3 install pandas

echo "Installing datetime..."
pip3 install datetime

echo "Installing requests..."
pip3 install requests

echo "Installing netCDF4..."
pip3 install netCDF4

echo "Installing xscreensaver..."
sudo apt-get install -y xscreensaver

echo "Installing unclutter..."
sudo apt-get install -y unclutter

echo "Searching for updates..."
sudo apt-get -y update

echo "Searching for upgrades..."
sudo apt-get -y upgrade

echo "Setting up executables..."
cd RPiOOI
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
