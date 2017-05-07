#!/usr/bin/env python3
# Server for the NeoPixel GUI
# see http://www.penguintutor.com/
# Copyright Stewart Watkiss 2015-2017


# web-power is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>


import bottle
from bottle import route, request, response, template, static_file
import sys
import math
import random
import threading
from neopixelcmds import *
from neopixelseq import *
import configparser
import time
import ledsettings
from collections import OrderedDict

# New version number for client server architecture
VERSION = '0.3'

# File containing sequences and colour options
# Must exist and have valid entries
sequencefile = 'sequences.cfg'

# File containing user config
# If it does not exist then use defaults
configfile = 'neopixel-server.cfg'

# Use to send a message to Back - created during startup
# eg. message = ("Warning", "Insert warning here")
message = ("","")

# Settings for neopixels
# load from config file or get from client
# these are defaults if no config file found
defaultLEDSettings = {
    'ledcount': 16,
    'gpiopin': 18,
    'ledfreq': 800000,
    'leddma' : 5,
    'ledmaxbrightness': 255,
    'ledinvert': False
    }

DEFAULTSPEED = 50
MINDELAY = 10.0
MAXDELAY = 100.0

# allow on all ip addresses
HOST = ''
# port 80 - standard web port (assumes no other web server installed)
# If using apache or another browser then change this to a different value
PORT = 80

# Folder where this is installed and the index.html file is located
# The index.html file is exposed to the webserver as well as any files in a subdirectory called public (ie. /home/pi/neopixel-gui/public) 
DOCUMENT_ROOT = '/home/pi/git/neopixel-gui'

# Create the bottle web server
app = bottle.Bottle()


# public files
# *** WARNING ANYTHING STORED IN THE PUBLIC FOLDER WILL BE AVAILABLE TO DOWNLOAD BY ANYONE CONNECTED TO THE SAME NETWORK ***
@app.route ('/public/<filename>')
def server_public (filename):
    return static_file (filename, root=DOCUMENT_ROOT+"/public")
    
# Handle switch on request
@app.route ('/allon')
def allon():
    colour = int(request.query.colour)
    print ("Colour " + colour)
    self.command.setCommand("allOn")
      
        
@app.route ('/alloff')
def alloff():
    self.command.setCommand("allOff")
    self.command.setCmdStatus(True)

        

# Serve up the default index.html page
@app.route ('/')
def server_home ():
    return static_file ('index.html', root=DOCUMENT_ROOT)





#Thread for communicating with neopixels
#Simple one-way communication with thread using globals
#checks variables or updates (cmdMessage, cmdColours)
def runPixels(LEDs, command):
    while command.getCommand() != "STOP":
        # run appropriate script
        method = getattr (LEDs, command.getCommand())
        method() 
        



def main():

    global message

    # load settings during startup    
    seqconfig = configparser.ConfigParser()
    # configwriter keys are normally case insensitive (converted to lowercase) - override as need case of the keys to match method names
    seqconfig.optionxform = str
    # Load the sequences
    try :
        seqconfig.read(sequencefile)
    except (configparser.Error, KeyError) :
        # Can't display warning at this stage so save message for when gui loaded
        message = ("Error", "Sequence.cfg does not exist\n or is missing important values")
        
    # iterate over sequences which allows handling of "\n" text to '\n' character
    sequenceOptions = []
    # colourChoice is ordered to maintain order of colours 
    colourChoice = OrderedDict()
    
    for key, value in seqconfig.items('Sequences') :
        sequenceOptions.append ([key, value.replace('\\n', '\n')]) 
    for key, value in seqconfig.items('Colours') :
        colourChoice[key] = value
    
    config = configparser.ConfigParser()
    # load user settings from configfile
    try :
        config.read(configfile)
        # Test that config entries loaded by looking at first entry
        numLEDs = int(config['LEDs']['ledcount'])
    except (configparser.Error, KeyError) :
        # Can't display warning at this stage so save message for when gui loaded
        # Don't overwrite error message if there is one
        if (message[0] == '') : 
            message = ("Warning", "No config file found\nUsing default values")
        
        # if load failed then use defaults
        config.add_section('LEDs')
        for key, value in defaultLEDSettings.items():
            config.set('LEDs', key, str(value)) 


    settings = ledsettings.LEDSettings(config)
    
    command = NeoPixelCmds()
    LEDs = NeoPixelSeq(settings.allSettings(), command)
        
    thread=threading.Thread(target=runPixels, args=(LEDs, command))
    thread.start()

    app.run(host=HOST, port=PORT)    
                                                                          
    
if __name__ == "__main__":

    main()

