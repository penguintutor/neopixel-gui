# neopixel-gui install guide

Guide to installing the neopixel gui application.

## Hardware requirements

**WARNING: Read carefully before connecting Neopixels to your Raspberry Pi**

The neopixel gui application is designed for use with a Raspberry Pi. It controls a strip of RGB LEDs with integrated controller IC such as WS2811 or WS2812. Adafruit products are named NeoPixels, but other suppliers may refer to these as RGB LEDs, WS2811, WS2812 or WS281x LEDs.

It should work with all current versions of the Raspberry Pi. It is recommended that the version of the neopixel library is installed from the link provided in this guide earlier versions of the library do not work with the Raspberry Pi 2 or later.

Using the neopixel library the neopixels can be driven from the Raspberry Pi GPIO connector. It needs to use PWM which is available on **GPIO pin 18** (physically pin 12 on the board).

The GPIO port works at 3.3V, but to run Neopixels at full brightness requires a 5v power supply and as a result a 5V data signal. This needs a voltage level shifter circuit to convert the 3.3V output from the Raspberry Pi to 5V.

The recommendation is for a simple MOSFET level shift circuit as explained on the [Penguintutor NeoPixel page](http://www.penguintutor.com/electronics/neopixels)


## Client Server

From version 0.3 onwards the software is designed to run in a client server configuration. This means that the graphical interface (client) does not need to be installed on the same computer that the NeoPixels are connected to (server).

At the moment the client and server software still needs to be installed, but only run the server on the computer with the NeoPixels physically connected. 

The client can also be installed on a different Linux computer such as Ubuntu. If using a non-Debian Linux then the instructions will need to be changed to reflect the software package tools on your particular version of Linux. 

The client functionality is also available through a simple web browser interface.



## Raspberry Pi with Raspbian

These instructions are based on Raspbian Jesse using the July 2017 version of NOOBS. It should work with any recent version of Raspbian. 

[Download the latest version of NOOBS](https://www.raspberrypi.org/downloads/)

### Pre-requisites

There are a number of pre-requisites that need to be installed. Some of these are required for the server, some for the client and some for both. There is no harm in installing all the pre-requisites on both (assuming the libraries are available for your choice of operating system).

## NeoPixel library

The software is written for Python version 3 and needs the NeoPixel library to be installed for Python 3. To work with the Raspberry Pi then the updated version of the NeoPixel needs to be installed (this can be installed on the older Raspberry Pi as well).

First install the developer libraries using:
`sudo apt-get install build-essential python3-dev git scons swig`

Download the neopixel code from github:
`git clone https://github.com/jgarff/rpi_ws281x.git`

Compile the software library:
```bash
cd rpi_ws281x
scons
```

Change to the python directory:
```bash
cd python
```

Install the Python 3 library file using
```bash
sudo python3 setup.py install
```


## Add Python Tk

The Python Tk libraries are included in the Raspberry Pi. If you are installing the client onto a Ubuntu computer (or similar) then you will need to install the Python TK libraries (used for the graphics application). This is done by running:

```bash
sudo apt install python3-tk
```

## Add passlib
This is required for password authentication

```bash
sudo pip3 install passlib
```

Note if installing the client on Ubuntu this is easier installed as 
sudo apt install python3-passlib


## Disable audio on the Raspberry Pi

There is a conflict between the sound driver and the PCM used to control the NeoPixels. 

To disable the sound driver create a new blacklist file using

```bash
sudo nano /etc/modprobe.d/snd-blacklist.conf
```

Add an entry

```
blacklist snd_bcm2835
```

Then save and exit (Ctrl-O Ctrl-X). You will need to reboot for this to take effect which you can do just prior to running the program.

## Install the Neopixel GUI software

Download the latest stable version from

[PenguinTutor.com/neopixels](http://www.penguintutor.com/neopixels)

Change to the /home/pi directory and install using
tar -xvzf neopixelgui-<i>versionnumber</i>.tar.gz

Or for the latest version (which is considered less stable) install the software from git using 

```bash
git clone https://github.com/penguintutor/neopixel-gui.git neopixel
```

## Starting the Server

The server code needs to be run first. This can be run from the command line using:

```bash 
cd ~/neopixel
sudo ./neopixel-server.py
```
or using a systemd startup script (details coming soon).

## Running the Disco Pixel Client

When the server is running run the disco client as:
```bash
cd ~/neopixel
./disco-pixel.py
```

To add to a new DJ Start Menu use:
```bash
startmenu/setupmenu.sh
```

## Initial configuration

Once the application is running choose the Config option to set the number of LEDs in your Neopixel LED strip. 


## Upgrade instructions

If you installed the software from git then you can update to the latest version at any time by changing into the neopixel folder and issuing

```bash
git pull
```
Please make sure you check the README.md file in case of any major changes to the configuration.

If you downloaded the package from [PenguinTutor.com](http://www.penguintutor.com) then check there for a new version and install that in place of the existing files.

### Upgrade to version 0.3

Due to significant changes when moving to version 0.3 you will need to reconfigure the software after install (follow the normal install instructions in this document).
You should also remove any of the start menu scripts that were previously installed.


### Using a web proxy

The client program uses the default system proxies.
To enable proxies then use the following command prior to running the client program.

```bash
export http_proxy='http://myproxy.example.com:1234'
```
