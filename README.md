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

Here are the following Python libraries that you will need to install. Depending on the library, you can install these with `pip3 install <library>` or `sudo apt-get install python3-<library>` via the Terminal.

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
