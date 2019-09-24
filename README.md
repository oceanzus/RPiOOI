# RPiOOI
This repository provides examples on how to plot near real-time telemetered and streamed data from OOI platforms.
These examples do not save data on your local machine, but instead plot data from memory and overwrite it on the next animation loop.

These examples were originally written for use on a Raspberry Pi. The idea being that you could display and update near real-time data for viewing or decision-making. These scripts are based in Python 3 and have been tested on the Raspberry Pi Model 3B+ (in Python 3.7.3) and on a Windows 10 machine (in Python 3.7.4) while using the most recent versions of the libraries.

## Setting Up The Pi
There are plenty of examples on how to set up a Raspberry Pi. If you are new to the platform, I recommend starting with NOOBS.
Don't forget to update your Raspberry Pi if you've started it up for the first time. Via Terminal, enter the following commands:

 `sudo apt-get update`

 `sudo apt-get upgrade`

## Cloning The Repository
First, navigate to your default directory. To automatically download the example scripts to your RPi, issue the following commands in the Terminal.

`cd /home/pi/`

`git clone https://github.com/IanTBlack/RPiOOI.git`


### Necessary Libraries
I've created a shell script that automatically installs the required libraries and establishes the appropriate executables. To run it, enter these commands into the Terminal.

1. `cd /home/pi/RPiOOI`
2. `chmod +x RPiOOI.sh`
3. `./RPiOOI.sh`

The script will then download the appropriate libraries.
If you prefer to install libraries on your own, here are the following Python libraries that you will need to install. Depending on the library, you can install these via Terminal using the following command structure (sans <>):

`pip3 install <library>`

or

`sudo apt-get install python3-<library>`

1. pandas
2. numpy
3. datetime
4. matplotlib
5. xarray
6. requests
7. Cython
8. libhdf5-dev
9. netcdf-bin
10. libnetcdf-dev
11. h5py
12. netCDF4

### Extra Downloads
I also recommend installing xscreensaver and unclutter. With xscreensaver you can turn off the RPi screensaver. With unclutter, you can set your mouse pointer to hide when it remains idle for a certain period of time. You can install these with the following commands.

`sudo apt-get install -y xscreensaver`

`sudo apt-get install -y unclutter`



## Setting Up Executable Scripts

Issuing the following commands allows you to call the Python scripts directly from the Terminal instead of having to run them as a module in Python 3 (but you can do that too if you want).

`cd /home/pi/RPiOOI/`

`chmod +x CE01ISSM_MFN_TSDO.py`

`chmod +x CE02SHSM_BEP_TSDO.py`

`chmod +x CE09OSPM_MMP_TS.py`

Then to run one of the scripts, issue the command:

`./"script"`

or

`sudo python3 "script"`

where "script" is CE01ISSM_MFN_TSDO.py, CE02SHSM_BEP_TSDO.py, CE09OSPM_MMP_TS.py, or CP02OSPM_MMP_TS.py


### Tkinter Errors
Each script will throw a "ttk::ThemeChanged" error at the initial run.
This is related to a Tkinter object that is called and destroyed before the plots appear.
This is used to get your screen width and height (in pixels), which is then used to generate a figure that is maximized to the size of your screen. This is under the assumption that there are 100 pixels per inch.

### Issues Getting Data
The frequency that data is telemetered may change through a deployment as operators adjust to power requirements. To know when exactly moorings telemeter data and when that data is available on OOINet, you will need to contact each respective array. If you request data over a small time span and no new data is available, the script may fail and won't make subsequent requests.
