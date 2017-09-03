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

import sys
import math
import random
from ledcmds import *
from lightseq import *
import configparser
import time
import ledsettings
from collections import OrderedDict
from neopixelhtmlgen import *
from response import Response
import numbers
import securitychecks
from sslwsgirefserver import *
import password
import os.path
import posix_ipc


# Version number added for client server architecture
# Config file can have different version number as long as it includes same features
version = '0.3'

# Level of debugging shown on the console 
# 1 = normal - errors only
# 3 = detailed debugging (any malformed requests show)
# 5 = very detailed debugging includes allowed operations
DEBUG = 5


#SOCKET_PORT = 321
MSG_QUEUE_NAME = "/LED_SHARED_MEMORY_6"

## Command is defined globally as it provides the main interface to the 
# NeoPixels which needs to be accessible 
# This is an alternative to using a singleton, but without the extra overhead 
## Settings is used to hold the settings so that they can be read / updated by 
# the webserver - similar to the command
## LEDs allows us to call updSettings from the web server 
global command, settings, LEDs


# File containing sequences and colour options
# Must exist and have valid entries
sequencefile = 'sequences.cfg'

# File containing user config
# If it does not exist then use defaults
# config is shared with the webserver applets
configfile = 'led-server.cfg'

# File containing passwords (will be generated if doesn't exist)
# Only used if LOGINREQ = True
passwordfile = 'users.cfg'


DEFAULTSPEED = 50
MINDELAY = 10.0
MAXDELAY = 100.0



## Configuration options - default settings
## Any changes will require a server restart
defaultServerSettings = {
    'version': version,
    # hardware eg. neopixel (generic for testing only)
    'hardware': 'neopixel',
    # if login mandatory
    'loginreq': 'False',
    # host normally blank (any address) can pin to specific interface
    'host': '',
    # For non-secure normally port 80, for secure port 443
    'port': 80,   
    # Enable ssl - ie secure connection (use 443)
    'enablessl': 'False',
    # Folder where documents are stored 
    # WARNING any files in this will be publically accessible
    'document_root': '/home/pi/neopixel/public', 
    'certificatefile': "/home/pi/neopixel/server.pem"
    }
    

# Settings for neopixels
# load from config file or get from client
# these are defaults if no config file found
# Default of ledinvert is True for compatibility with the
# FET based NeoPixel circuit provided at http://www.penguintutor.com/electronics/neopixels
# If using a non-inverting buffer then that should be set to False
# RGB True indicates red first on LED sequence, RGB False indicates Green first (ie GRB) 
defaultLEDSettings = {
    'ledcount': 16,
    'gpiopin': 18,
    'ledfreq': 800000,
    'leddma' : 5,
    'ledmaxbrightness': 255,
    'ledinvert': True,
    'rgb': False
    }


############### End of configuration options


# These are used to provide settings to the NeoPixels and the web interface
# This is the list of sequences that can be selected, key = methodname, value = user friendly string
sequenceOptions = dict()
config = configparser.ConfigParser()



def main():

    global command, settings, LEDs, passwords

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
        sequenceOptions[key] = value.replace('\\n', '\n') 
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
            
    # If no server setting then add default server settings
    if  not config.has_section('Server'):
        config.add_section('Server')
        for key, value in defaultServerSettings.items():
            config.set('Server', key, str(value)) 
            
        # If didn't previously have a config file - or it didn't include server then save it
        try:
            with open(configfile, 'w') as cfgfile:
                config.write(cfgfile)
                # tell user config saved
                print ("New configuration file saved")
        except : 
            # If unable to save then continue with the default values
            print ("Warning: Unable to save config file") 
        


    settings = ledsettings.LEDSettings(config)
    
    
    # Setup the password object if required
    if (config.getboolean('Server','loginreq') == True):
        passwords = password.Password(passwordfile)
    


    # Setup LEDs and cmd
    
    cmd = LEDCmds()
    LEDs = LightSeq(config['Server']['hardware'], settings.allSettings(), cmd)
    
    
    try:
        # Create posix IPC message queue
        os.umask(000) # Set umask to allow write access to all users to the message queue
        mq = posix_ipc.MessageQueue(MSG_QUEUE_NAME, posix_ipc.O_CREAT, 777)
        #mq = posix_ipc.MessageQueue(MSG_QUEUE_NAME)
        mq.block=False
    except Exception as e:
        # Some other error (eg. cmd not valid)
        print ("Unable to create message queue " + str(e))
        exit(0)
        pass
    
    print ("Message queue "+MSG_QUEUE_NAME)
    
    print ("Waiting...")
    
    while cmd.getCommand() != "STOP":
        try:
            msg, priority = mq.receive()
            msgstr = msg.decode('UTF-8')
            print ("Received msg "+msgstr)
            qcmd, qvalue = msgstr.split(',')
            print ("New cmd "+qcmd+" value "+qvalue)
            # split the queue string into method and parameter
            # Security note there is no checking of cmd and value at this stage
            # Anything that is not valid will raise an exception, but
            # will not stop the server - these can only be sent by
            # other processes with the same permission anyway and it is
            # the web server code that is validating the user input
            updcmd = getattr (cmd, qcmd)
            updcmd(qvalue)
            
        except posix_ipc.BusyError:
            # Nothing waiting
            #print ("Busy error")
            pass
        
        except Exception as e:
            # Some other error (eg. cmd not valid)
            print ("Other error " + str(e))
            pass
        
        
        # run appropriate script
        #method = getattr (LEDs, cmd.getCommand())
        #method()
        # sleep to allow other threads to run
        time.sleep(0.01)
        
    mq.close()
    mq.unlink()
    #posix_ipc.unlink_message_queue(MSG_QUEUE_NAME)



    
if __name__ == "__main__":

    main()

