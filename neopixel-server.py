#!/usr/bin/env python3
# Server for the NeoPixel GUI
# see http://www.penguintutor.com/
# Copyright Stewart Watkiss 2015-2017


# This code is free software: you can redistribute it and/or modify
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

# Command is defined globally as it provides the main interface to the NeoPixels
# which needs to be accessible from the webserver code as well as being passed
# as a parameter to the thread for handling the update of the NeoPixels
# This is an alternative to using a singleton, but without the extra overhead 
global command, settings

# File containing sequences and colour options
# Must exist and have valid entries
sequencefile = 'sequences.cfg'

# File containing user config
# If it does not exist then use defaults
configfile = 'neopixel-server.cfg'

# Settings for neopixels
# load from config file or get from client
# these are defaults if no config file found
# Default of ledinvert is True for compatibility with the
# FET based NeoPixel circuit provided at http://www.penguintutor.com/electronics/neopixels
# If using a non-inverting buffer then that should be set to False
defaultLEDSettings = {
    'ledcount': 16,
    'gpiopin': 18,
    'ledfreq': 800000,
    'leddma' : 5,
    'ledmaxbrightness': 255,
    'ledinvert': True
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


# These are used to provide settings to the NeoPixels and the web interface
# This is the list of sequences that can be selected, key = methodname, value = user friendly string
sequenceOptions = dict()
config = configparser.ConfigParser()



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
    colour = request.query.colour
    # Only limited colours defined
    # For other colours then use /setcolour instead
    if (colour == "white"):
        command.setColours([Color(255,255,255)])
    elif (colour == "red"):
        command.setColours([Color(0,255,0)])
    elif (colour == "green"):
        command.setColours([Color(255,0,0)])
    elif (colour == "blue"):
        command.setColours([Color(0,0,255)])
    command.setCommand("allOn")
    command.setCmdStatus(True)
      
# Handle sequence request
# eg /sequence?seq=rainbow - or other sequence from sequence.cfg
# eg chaser / disco 
@app.route ('/sequence')
def rainbow():
    seq = request.query.seq
    # For security reasons check that it is a valid sequence
    if not seq in sequenceOptions.keys(): 
        return
    command.setCommand(seq)
    command.setCmdStatus(True)
    

# Handle switch off
@app.route ('/alloff')
def alloff():
    command.setCommand("allOff")
    command.setCmdStatus(True)

@app.route ('/status')
def status():
    pass

# provide a comma separated list of rgb colours eg. /setcolours?colours=000000,ffffff 
# Note that # isn't used in the url as that has a different use to jump to a part of the page
@app.route ('/setcolours')
def setcolours():
    colours = request.query.colours
    colourlist = colours.split(",")
    intcolours = []
    
    # Check that all colours are valid and convert them into Colors 
    # If any are not valid then quit without changing any colours
    
    #for (thiscolour: colourlist):
    for (i =0; i< colourlist.size(); i++)
        try:
            intcolours[i] = (int(colourlist[i], 16))
        except ValueError as err:
            return
        except Exception as e:
            print "Unknown exception has occurred setting colours"
            return

    # Now have an array of int values 
    command.setColours(intcolours)



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

    global command, settings

    # load settings during startup    
    seqconfig = configparser.ConfigParser()
    # configwriter keys are normally case insensitive (converted to lowercase) - override as need case of the keys to match method names
    seqconfig.optionxform = str
    # Load the sequences
    try :
        seqconfig.read(sequencefile)
    except (configparser.Error, KeyError) :
        # Error loading the sequences
        sys.exit ("Error Sequence.cfg does not exist\n or is missing important values")
        
    # iterate over sequences which allows handling of "\n" text to '\n' character
    # colourChoice is ordered to maintain order of colours 
    # legacy option - not needed if using colour wheel chooser
    colourChoice = OrderedDict()
    
    for key, value in seqconfig.items('Sequences') :
        sequenceOptions.append ([key, value.replace('\\n', '\n')]) 
    for key, value in seqconfig.items('Colours') :
        colourChoice[key] = value
    
    
    # load user settings from configfile
    try :
        config.read(configfile)
        # Test that config entries loaded by looking at first entry
        numLEDs = int(config['LEDs']['ledcount'])
    except (configparser.Error, KeyError) :
        # Give warning message
        print ("Warning: No config file found\nUsing default values")
        
        # if load failed then use defaults
        config.add_section('LEDs')
        for key, value in defaultLEDSettings.items():
            config.set('LEDs', key, str(value)) 


    settings = ledsettings.LEDSettings(config)
    
    command = NeoPixelCmds()
    LEDs = NeoPixelSeq(settings.allSettings(), command)
    
    # Spawn separate thread for handling the updates to the Pixels
    thread=threading.Thread(target=runPixels, args=(LEDs, command))
    thread.start()

    # Start the Bottle web server 
    app.run(host=HOST, port=PORT)    
                                                                          
    
if __name__ == "__main__":

    main()

