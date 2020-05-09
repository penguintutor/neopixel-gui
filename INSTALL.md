# neopixel-gui install guide

Guide to installing the neopixel gui application.

## Hardware requirements

**WARNING: Read carefully before connecting Neopixels to your Raspberry Pi**

The neopixel gui application is designed for use with a Raspberry Pi. It controls a strip of RGB LEDs with integrated controller IC such as WS2811 or WS2812. Adafruit products are named NeoPixels, but other suppliers may refer to these as RGB LEDs, WS2811, WS2812 or WS281x LEDs.

It should work with all current versions of the Raspberry Pi. 

Using the neopixel libarary the neopixels can be driven from the Raspberry Pi GPIO connector. Preference is to use PWM which is available on **GPIO pin 18** (physically pin 12 on the board).

The GPIO port works at 3.3V, but to run Neopixels at full brightness requires a 5v power supply and as a result a 5V data signal. This needs a voltage level shifter circuit to convert the 3.3V output from the Raspberry Pi to 5V.


This can be achieved using Raspberry Pi and level shifter using a 2N7000 MOSFET.
It has been tested with the [MOS-FET inverting level shifter](http://www.penguintutor.com/electronics/neopixels). Using a MOS-FET requires that the LEDinvert be selected.


## Raspberry Pi with Raspbian

These instructions are based on Raspbian. 

[Download the latest version of Raspbian](https://www.raspberrypi.org/downloads/)

## Pre-requisites

The software is written for Python version 3 and needs the NeoPixel library to be installed for Python 3. 

The software is available from [GitHub rpi-ws281x-python](https://github.com/rpi-ws281x/rpi-ws281x-python). 

The simplist way to install is using:

```bash
sudo pip3 install rpi_ws281x
```

from a command shell on the Raspberry Pi.

## Disabling the Raspberry Pi Audio Driver

Before you get around to installing the software there is an issue when trying to control NeoPixels from a Raspberry Pi where sound is enabled. This is because the hardware PWM feature of the Raspberry Pi has to be manipulated by the software library, which is also used by the sound driver.The solution is to disable the sound driver, which unfortunately means not being able to use sound. To disable the sound driver add the snd_bcm2835 module to the blacklist.

```bash
sudo nano cat /etc/modprobe.d/raspi-blacklist.conf 
```

Add an entry

```
blacklist snd_bcm2835
```
Then save and exit (Ctrl-O Ctrl-X)

## Install the Neopixel GUI software

Download the latest stable version from

[PenguinTutor.com](http://www.penguintutor.com)

Change to the /home/pi directory and install using
tar -xvzf neopixelgui-<i>versionnumber</i>.tar.gz

Or for the latest version install the software from git using 

```bash
git clone https://github.com/penguintutor/neopixel-gui.git neopixel
```

Set executable permissions on pixelstrip.py
```bash
chmod +x neopixel/pixelstrip.py
```

you can now run the command using

```bash 
cd neopixel
sudo ./pixelstrip.py
```

To add to a new DJ Start Menu use:
```bash
startmenu/setupmenu.sh
```

## Initial configuration

Once the application is running choose the Config option to set the number of LEDs in your Neopixel LED strip. 

## Corrupt configuration file

If your configuration file has become corrupted, or you have chosen an invalid GPIO port number then the application may not start. In that case delete the file rpnpgp.cfg from the neopixel directory. The application should then start normally and you will be able to create a new configuration using the config option. 

In rare circumstances you may also need to reboot the computer (or if you know what you are doing kill the existing pixelstrip processes), but that is not normally required.

## Upgrade instructions

If you installed the software from git then you can update to the latest version at any time by changing into the neopixel folder and issuing

```bash
git pull
```

Between version 0.1 and version 0.2 the executable changed name from rpnpgp.py to pixelstrip.py. To update the start menu, remove the current menu entry and run the setupmenu.sh file mentioned previously.
Please make sure you check the README.md file in case of any major changes to the configuration.

If you downloaded the package from [PenguinTutor.com](http://www.penguintutor.com) then check there for a new version and any upgrade instructions.


