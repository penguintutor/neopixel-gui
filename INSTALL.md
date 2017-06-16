# neopixel-gui install guide

Guide to installing the neopixel gui application.

## Hardware requirements

**WARNING: Read carefully before connecting Neopixels to your Raspberry Pi**

The neopixel gui application is designed for use with a Raspberry Pi. It controls a strip of RGB LEDs with integrated controller IC such as WS2811 or WS2812. Adafruit products are named NeoPixels, but other suppliers may refer to these as RGB LEDs, WS2811, WS2812 or WS281x LEDs.

It should work with all current versions of the Raspberry Pi. It is recommended that the version of the neopixel library is installed from the link provided in this guide earlier versions of the library do not work with the Raspberry Pi 2.

Using the neopixel libarary the neopixels can be driven from the Raspberry Pi GPIO connector. It needs to use PWM which is available on **GPIO pin 18** (physically pin 12 on the board).

The GPIO port works at 3.3V, but to run Neopixels at full brightness requires a 5v power supply and as a result a 5V data signal. This needs a voltage level shifter circuit to convert the 3.3V output from the Raspberry Pi to 5V.

The recommendation is for a simple MOSFET level shift circuit as explained on the [Penguintutor NeoPixel page](http://www.penguintutor.com/electronics/neopixels)



## Raspberry Pi with Raspbian

These instructions are based on Raspbian Jesse using the November 2015 version of NOOBS. It should work with any recent version of Raspbian. 

[Download the latest version of NOOBS](https://www.raspberrypi.org/downloads/)

## Pre-requisites

The software is written for Python version 3 and needs the NeoPixel library to be installed for Python 3. To work with the Raspberry Pi then the updated version of the NeoPixel needs to be installed (this can be installed on the older Raspberry Pi as well).

First install the developer libraries using
`sudo apt-get install build-essential python-dev python3-dev git scons swig`

(this includes the Python 2 developer libraries which are not required but are useful to install anyway)

Download the neopixel code from github
`git clone https://github.com/jgarff/rpi_ws281x.git`

```bash
cd rpi_ws281x
scons
```

Change to the python directory 
```bash
cd python
```

Install the Python 3 library file using

```bash
sudo python3 setup.py install
```


## Add Python tk
The client interface does not need to be run on the Raspberry Pi. If you are installing onto a Ubuntu computer then you will need to install the Python TK libraries (used for the graphics application). This is done by running

```bash
sudo apt install python3-tk
```

## Add passlib
This is required for password authentication

```bash
sudo pip3 install passlib
```

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

Then save and exit (Ctrl-O Ctrl-X). You will need to reboot for this to take effect which youc an do just prior to running the program.

## Install the Neopixel GUI software

Download the latest stable version from

[PenguinTutor.com](http://www.penguintutor.com)

Change to the /home/pi directory and install using
tar -xvzf neopixelgui-<i>versionnumber</i>.tar.gz

Or for the latest version (which may have more bugs) install the software from git using 

```bash
git clone https://github.com/penguintutor/neopixel-gui.git neopixel
```

you can now run the command using

```bash 
cd neopixel
gksudo python3 rpnpg.py
```

To add to a new DJ Start Menu use:
```bash
startmenu/setupmenu.sh
```

## gksudo warning message

When first running you will get a warning message that the application is running with super user privileges without asking for a password. "Granted permission without asking for password". This is required to be able to access the GPIO ports on the Raspberry Pi. If you tick the "Do not display this message again" box then you will not be warned of this again in future.

## Initial configuration

Once the application is running choose the Config option to set the number of LEDs in your Neopixel LED strip. 

## Corrupt configuration file

If your configuration file has become corrupted, or you have chosen an invalid GPIO port number then the application may not start. In that case delete the file rpnpgp.cfg from the neopixel directory. The application should then start normally and you will be able to create a new configuration using the config option. 

In rare circumstances you may also need to reboot the computer (or if you know what you are doing kill the existing rpnpngp processes), but that is not normally required.

## Upgrade instructions

If you installed the software from git then you can update to the latest version at any time by changing into the neopixel folder and issuing

```bash
git pull
```
Please make sure you check the README.md file in case of any major changes to the configuration.

If you downloaded the package from [PenguinTutor.com](http://www.penguintutor.com) then check there for a new version and install that in place of the existing files.


### Using a web proxy

The program uses the default system proxies.
To enable proxies then use the following command prior to running the client program.

```bash
export http_proxy='http://myproxy.example.com:1234'
```

### Extra steps for upgrading from 0.1

If you have an version 0.1 installed then the program file names have changed.
Delete any existing icons from the start menu or desktop. Rename the rpnpgp.cfg file

`mv rpnpgp.cfg disco-pixels.cfg`
