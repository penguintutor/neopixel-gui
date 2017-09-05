#!/usr/bin/pgzrun

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

import os
import sys
import time       
import threading
import configparser

# Local imports must come after adding current path to command path
sys.path.append(os.getcwd())

import ledsettings
#from neopixelcmds import *
from neopixelseq import *
import localsettings
from clientcontroller import *

VERSION = '0.3'

SOCKET_ADDRESS = "/tmp/led-server-socket"

# File containing user config
# If it does not exist then use defaults
configfile = 'mood-pixels.cfg'


# File containing sequences and colour options
# Must exist and have valid entries
sequencefile = 'sequences.cfg'

# Use to send a message to GUI - created during startup
# eg. message = ("Warning", "Insert warning here")
message = ("","")

# default settings if none loaded
defaultLEDSettings = {
    'ledcount': 16,
    'gpiopin': 18,
    'ledfreq': 800000,
    'leddma' : 5,
    'ledmaxbrightness': 255,
    'ledinvert': True 
    }
    
# default hostnames and ports
defaultLocalSettings = {
    'remoteserver' : 'False',
    'hostname': '127.0.0.1',
    'port' : 80,
    'ssl' : 'False',
    'username' : '',
    'password' : '',
    # allow unverified will not check authentication of server
    # This could allow for server spoofing
    'allowunverified': 'False'
    }


# load sequence config    
seqconfig = configparser.ConfigParser()
# configwriter keys are normally case insensitive (converted to lowercase) - override as need case of the keys to match method names
seqconfig.optionxform = str
# Load the sequences
try :
    seqconfig.read(sequencefile)
except (configparser.Error, KeyError) :
    # Can't display warning at this stage so save message for when gui loaded
    message = ("Error", "Sequence.cfg does not exist\n or is missing important values")


config = configparser.ConfigParser()
# load user settings from configfile
try :
    config.read(configfile)
    # Test that config entries loaded by looking at first entry
    hostname = config['Server']['hostname']
except (configparser.Error, KeyError) :
    # Can't display warning at this stage so save message for when gui loaded
    # Don't overwrite error message if there is one
    if (message[0] == '') : 
        message = ("Warning", "No config file found\nUsing default values")
    
    # if load failed then use defaults
    config.add_section('Server')
    for key, value in defaultLocalSettings.items():
        config.set('Server', key, str(value)) 


settings = localsettings.LocalSettings(config)

command = ClientController(settings.remoteserver(), settings.hostname(), settings.port(), settings.ssl(), settings.username(), settings.password(), SOCKET_ADDRESS, settings.allowunverified())


WIDTH = 760
HEIGHT = 380

BUTTON_COLOR = 40,40,200
WHITE = 255, 255, 255

buttonText = (
    u"All On",
    u"All Off",
    u"Flash Alt",
    u"Chaser",
    u"Multi Chaser",
    u"Color Cycle"
)
buttonRect = (
    Rect(50, 100, 120, 40),
    Rect(300, 100, 120, 40),
    Rect(550, 100, 120, 40),
    Rect(50, 200, 120, 40),
    Rect(300, 200, 120, 40),
    Rect(550, 200, 120, 40)  
)

minusRect = Rect(150, 300, 40, 40)
plusRect = Rect(210, 300, 40, 40)

# Delay counts is number of updates before change in 60th of a second
delay_counts = 30 
seq_number = 0
sequence = "All On" # Start with all lights on
timer = 0


# Setup NeoPixel Strip
#strip = Adafruit_NeoPixel(LEDCOUNT, GPIOPIN, FREQ, DMA, INVERT, BRIGHTNESS)
# Intialize the library (must be called once before other functions).
#strip.begin()


def draw():
    screen.fill((80,80,80))

    screen.draw.text(
        "Neopixel Control",
        centerx = 360, top = 30,
        fontsize=40,
        color=WHITE
    )

    box = []
    for i in range(len(buttonRect)):
        box.append(buttonRect[i].inflate (-1, -1))
        screen.draw.filled_rect(box[i], BUTTON_COLOR)
        screen.draw.text(
            buttonText[i],
            centerx = box[i][0] + 60, centery = box[i][1] + 20,
            fontsize=28,
            color=WHITE
        )

    screen.draw.text(
        "Speed",
        (50, 310),
        fontsize=28,
        color=WHITE
        )

    boxMinus = minusRect.inflate(-1, -1)
    screen.draw.filled_rect(boxMinus, BUTTON_COLOR)
    screen.draw.text(
        "-",
        centerx = boxMinus[0] + 20, centery = boxMinus[1] + 20,
        fontsize=32,
        color=WHITE
    )

    boxPlus = plusRect.inflate(-1, -1)
    screen.draw.filled_rect(boxPlus, BUTTON_COLOR)
    screen.draw.text(
        "+",
        centerx = boxPlus[0] + 20, centery = boxPlus[1] + 20,
        fontsize=32,
        color=WHITE
    )


    

def on_mouse_down(button, pos):
    global seq_changed, sequence, delay_counts
    x, y = pos
    # Check position of main buttons
    for i in range(len(buttonRect)):
        if buttonRect[i].collidepoint(x,y) :
            sequence = buttonText[i]
            command.setSequence(sequence)
    # Check position of speed buttons
    if minusRect.collidepoint(x,y) :
        delay_counts = delay_counts + 5
        command.setDelay(delay_counts)
    if plusRect.collidepoint(x,y) :
        delay_counts = delay_counts - 5
        command.setDelay(delay_counts)
    



def update():
    pass

