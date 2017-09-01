# neopixel-gui
Simple graphical interface for controlling neopixel RGB LEDs on a Raspberry Pi

Gainpix

## Introduction

This software provides graphical interfaces for controlling NeoPixel and similar RGB LEDs on a Raspberry Pi. It includes a disco GUI for use in a disco or theatre lighting environment and a mood light GUI which allows the lights to be controlled for room lighting etc.
There's even a version included to work with artificial intelligence voice activatation using the Google AIY project.

From version 0.3 onwards the software is designed to run in a client server configuration. This means that the graphical interface (client) does not need to be installed on the same computer that the NeoPixels are connected to (server).

## GUI Layout

The user interfaces are intentionally basic in appearance using large buttons. This is so that it is suitable for use in a disco environment using a touchscreen (eg. using VNC from a touchscreen laptop) or for a wall mounted touchscreen for the mood lighting.

The Apply button needs to be pressed for the changes to take effect, which allows the user to choose all the appropriate settings prior to applying them.

![NeoPixel GUI screenshot](docs/screenshot-v0-1.png "Screenshot of NeoPixel GUI Version 0.1")


## Supported platform

The server code is designed to run on a Raspberry Pi with a level shifter to control the NeoPixels.
A suitable circuit is available on the [Penguintutor NeoPixel page](http://www.penguintutor.com/electronics/neopixels)

The client code can be run on the same Raspberry Pi as the server, or it should work on any Linux computer. There is also a web interface which can be accessed using a web browser.


## Install Instructions

Please see the file INSTALL.md for detailed installation instructions.


## Advanced 

The software implements a network based client server model between the GUI client and the web server. 
In theory multiple clients can be used at the same time, but that will mean that they will override each others settings
and so the status may not be correct. 

At a lower level the web server and the led server communicate using IPC which is one-directional. There should only
be a single web server attempting to access the message queue (and/or direct client) and there is noway to know the 
status of the led-server from the web-server at this time. That may be added later using signals and/or a separate 
message queue, but doing so could result in problems if there are two web servers / clients trying to access the message
queue at the same time.


## More Information 

More information will be provided on [www.penguintutor.com](http://www.penguintutor.com)


