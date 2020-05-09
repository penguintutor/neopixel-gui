# neopixel-gui
Simple graphical interface for controlling neopixel RGB LEDs on a Raspberry Pi

## Introduction

This is a graphical interface for controlling NeoPixels and other RGB PixelStrips. It is created using Python and Pygame.

## GUI Layout

The user interface is intentionally basic in appearance using large buttons. This is so that it is suitable for use in a disco environment using a touchscreen (eg. using VNC from a touchscreen laptop).

The Apply button needs to be pressed for the changes to take effect, which allows the user to choose all the appropriate settings prior to applying them.

![NeoPixel GUI screenshot](docs/screenshot-v0-1.png "Screenshot of NeoPixel GUI Version 0.1")



## Supported platform

This is designed to run on a Raspberry Pi with a level-shifter to convert from 3.3V to 5V.
It has been tested with the [MOS-FET inverting level shifter](http://www.penguintutor.com/electronics/neopixels). Using a MOS-FET requires that the LEDinvert be selected.

## Install

This is a summary - full details of how to install the software is included in the file INSTALL.md.

First install the Python 3 library from [GitHub rpi-ws281x-python](https://github.com/rpi-ws281x/rpi-ws281x-python). 

You may also need to disable the sound module snd_bcm2835 if not already done.

Download and extract files into a new folder named /home/pi/neopixel
Copy the appropriate desktop and startmenu files as listed in the INSTALL.md guide. Restart the lxpanel and then the icon should appear on the normal start menu.

A more detailed install guide is provided in the file INSTALL.md


## Changing the sequence

After choosing the appropriate sequence you need to click the Apply button for it to take effect. This allows you to pre-prepare the sequence before making it active.

## More Information 

More information is available at [www.penguintutor.com/projects/pixelstrip](http://www.penguintutor.com/projects/pixelstrip)


