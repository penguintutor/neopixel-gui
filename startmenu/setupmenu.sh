#!/bin/bash

# Adds start menu for neopixel-gui
# This assumes it is being installed for the pi user
# If not then the configuration files need to be updated as well as the file locations

mkdir -p /home/pi/.config/menus
cp /home/pi/neopixel/startmenu/lxde-pi-applications.menu /home/pi/.config/menus/
mkdir -p /home/pi/.local/share/desktop-directories
cp /home/pi/neopixel/startmenu/dj_menu.directory ~/.local/share/desktop-directories/
mkdir -p /home/pi/.local/share/pixmaps
cp /home/pi/neopixel/startmenu/headphones.png /home/pi/.local/share/pixmaps/
cp /home/pi/neopixel/startmenu/pixelstripicon.png /home/pi/.local/share/pixmaps/
mkdir -p /home/pi/.local/share/applications/
cp /home/pi/neopixel/startmenu/pixelstrip.desktop /home/pi/.local/share/applications/
lxpanelctl restart


