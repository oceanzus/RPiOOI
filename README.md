# RPiOOI
This repository provides examples for how to plot and update telemetered and streamed data from OOI platforms.
These examples do not save data on your local machine, but instead plot data from memory.

These examples were written for use on a Raspberry Pi, the idea being that you could display and update near real-time data for viewing.
They can easily be modified for use on other machines. These scripts are based in Python 3.

##Setting Up The Pi

There are plenty of example on how to set up a Raspberry Pi. If you are new to the platform, I recommend starting with NOOBS.
First, I recommend updating you Raspberry Pi. Via Terminal, enter the following commands:

 `sudo apt-get update`

 `sudo apt-get upgrade`

Here are the following Python libraries that you will need to install. Depending on the library, you can install these via the Terminal using the following command structure (sans <>):

`pip3 install <library>`

`sudo apt-get install python3-<library>`

1. pandas
2. numpy
3. datetime
4. matplotlib
5. xarray
6. netCDF4
7. requests

I also recommend installing xscreensaver and unclutter. With xscreensaver you can turn off the RPi screensaver. With unclutter, you can set your mouse pointer to hide when it remains idle for a certain period of time. You can install these with the following commands.

`sudo apt-get install -y xscreensaver`

`sudo apt-get install -y unclutter`


## Cloning The Repository

To automatically download the example scripts to your RPi, issue the following command in the Terminal.

`git clone https://github.com/IanTBlack/RPiOOI.git`

There is also a shell script that automatically installs the required libraries and establishes the appropriate executables.
However, I've tested this script on two different RPis. It worked on one, and the other has issues. It might be easiest to download each library individually if you are new to the Raspberry Pi.


## Setting Up Executable Scripts

Issuing the following commands allows you to call the python scripts directly from the Terminal instead of having to run them as a module in Python 3.

`cd /home/pi/RPiOOI/`

`chmod +x CE01ISSM_MFN_TSDO.py`

`chmod +x CE02SHSM_BEP_TSDO.py`

`chmod +x CE09OSPM_MMP_TS.py`

Then to run one of the scripts, issue the command:

`./"script"`

or

`sudo python3 "script"`

where "script" is CE01ISSM_MFN_TSDO.py, CE02SHSM_BEP_TSDO.py, or CE09OSPM_MMP_TS.py


### Tkinter Errors
If run in the Terminal, each script will throw a "ThemeChanged" error.
This is related a Tkinter object that is called and destroyed before the plots appear.
This Tkinter object is used to get your screen width and height (in pixels), which is then used to generate a figure that is maximized to the size of your screen.
This is under the assumption that there are 100 pixels per inch.

If you run a script in the Python shell, this error does not appear in the output.
