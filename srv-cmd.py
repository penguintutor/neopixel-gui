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


# Receive instruction from webserver and send to led-server via posix msg queue

import sys
import math
import random
from websrvcmds import *
#from lightseq import *
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


# cgi module - perform error handling
import cgi
import cgitb
cgitb.enable()
# to avoid showing errors to user change to 
# cgitb.enable(display=0, logdir="/path/to/logdir")

# to load non standard libraries use 
#sys.path.insert(0, "/usr/home/joe/lib/python")

SOCKET_ADDRESS = "/tmp/led-server-socket"


# Version number added for client server architecture
# Config file can have different version number as long as it includes same features
version = '0.3'

# Level of debugging shown on the console 
# 1 = normal - errors only
# 3 = detailed debugging (any malformed requests show)
# 5 = very detailed debugging includes allowed operations

DEBUG = 5

## Command is defined globally as it provides the main interface to the 
# NeoPixels which needs to be accessible from the webserver code as well as 
# being passed as a parameter to the thread for handling the update of the 
# NeoPixels
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
configfile = 'neopixel-server.cfg'

# File containing passwords (will be generated if doesn't exist)
# Only used if LOGINREQ = True
passwordfile = 'users.cfg'


DEFAULTSPEED = 50
MINDELAY = 10.0
MAXDELAY = 100.0

# Recommended to enable SSL for security - if enabled you will need to create 
# an SSL certificate
# openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
# by default server file is in "/etc/letsencrypt/live/<servername>/combined.pem"



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


def server_public (filename):
    return static_file (filename, root=DOCUMENT_ROOT+"/public")
    
    
## Can accept two types of request
# preferred /neopixel which is used by the client applications 
# this uses json to exchange messages between client and server

# The alternative are some "user friendly" url links that can be used for calling
# basic functions without needing to worry about converting to json
# Can have multiple commands, but not query and command at same time
# and not multiple queries

def server_json ():
    global command, settings, LEDs, passwords
    data = request.json
    # response is our reply - stored by utility class
    response = Response(DEBUG)
    
    # First check if this is a login (which we can handle directly)
    if (data['request'] == 'login'):
        # Todo - handle login requests
        return "Login not supported"
    
    
    # If it's not a login then check we have got an active session
    if (config.getboolean('Server','loginreq') == True):
        # check session identifier
        if ((not 'username' in data) or (not 'password' in data)):
            showLogin("Login required")
            # Field (2nd argument) set to login - could be missing username or password
            response.addStatus ("auth", "login", "Login required")
            return response.getStatus()
            #return ("Login required")
        if (not passwords.chkPassword(data['username'], data['password'])):
            showLogin("Login failed - invalid username or password")
            response.addStatus ("auth", "login", "Login failed")
            return response.getStatus()
        # otherwise login successful
    
    
    
    
    #### If we reach here then we must be logged in (or login not required)
    
    ### Command
    if (data['request'] == 'command'):
        if 'sequence' in data:
            # check it's a valid sequence
            if not data['sequence'] in sequenceOptions.keys():
                response.addStatus ("error", "sequence", "Sequence not valid")
            else:
                command.setCommand(data['sequence'])
                command.setCmdStatus(True)
                response.addStatus ("success", "sequence", "Sequence updated")
        if 'colours' in data:
            selectedColours = data['colours']
            intcolours = []
            for i in range(len(selectedColours)):
                try:
                    if (securitychecks.validateIntegerResponse(selectedColours[i], "colour", 0, 16777215, response)) :
                            intcolours.append(selectedColours[i])
                            response.addStatus("success", "colours", "success")
                    else:
                        response.addStatus("error", "colours", "Fail security check")
                        return response.getStatus()
                except ValueError as err:
                    response.addStatus ("error", "colours", "Colour not valid")
                    return response.getStatus()       
                except Exception as e:
                    response.addStatus ("error", "colours", "Unknown error in setting colour" + str(e))
                    return response.getStatus()
            command.setColours(intcolours)
            response.addStatus ("success", "colours", "Colour updated")
        if 'delay' in data:
            if (securitychecks.validateIntegerResponse(data['delay'], "delay", MINDELAY, MAXDELAY, response)) :
                command.setDelay(data['delay'])
                response.addStatus("success", "delay", "Delay updated")
            else :
                return response.getStatus()
                
    ### Queries
    elif (data['request'] == 'query'):
        ## Config - current saved configs (eg. neopixel / server)
        if (data['type'] == 'config'):
            if (data['value'] == "neopixels"):
                returnvalue = settings.allSettings()
                returnvalue['reply'] = "success"
                return returnvalue
    
    ### Updates
    ### Need to doubly make sure that all values are valid
    elif (data['request'] == 'update'):
        if (data['type']=='config'):
            if (data['value'] == 'neopixels'):
                # update the neopixel settings individually - checking for valid settings
                # I don't know how many NeoPixels could be supported, but clearly 1M is going to be too large
                if ('ledcount' in data):
                    try:
                        thisvalue = int(data['ledcount'])
                    except (TypeError, ValueError):
                        # This is a serious error - not even sending correct
                        # value type so don't even try the other values
                        response = {'reply':'error', 'error':'Invalid type in ledcount'}
                        return response.getStatus()
                    validate = securitychecks.validateIntegerResponse(thisvalue, "ledcount", 0, 1000000, response)
                    if validate:
                        config['LEDs']['ledcount'] = data['ledcount']
                # Don't check it's a valid pwm pin (that should be checked first), just that it's a sensible number ie between 0 and 128 
                if ('gpiopin' in data):
                    try:
                        thisvalue = int(data['gpiopin'])
                    except (TypeError, ValueError):
                        # This is a serious error - not even sending correct
                        # value type so don't even try the other values
                        response = {'reply':'error', 'error':'Invalid type in gpiopin'}
                        return response.getStatus()
                    validate = securitychecks.validateIntegerResponse(thisvalue, "gpiopin", 0, 128, response)
                    if validate:
                        config['LEDs']['gpiopin'] = data['gpiopin']
                if ('ledmaxbrightness' in data):
                    try:
                        thisvalue = int(data['ledmaxbrightness'])
                    except (TypeError, ValueError):
                        # This is a serious error - not even sending correct
                        # value type so don't even try the other values
                        response = {'reply':'error', 'error':'Invalid type in ledmaxbrightness'}
                        return response.getStatus()
                    validate = securitychecks.validateIntegerResponse(thisvalue, "ledmaxbrightness", 0, 255, response)
                    if validate:
                        config['LEDs']['ledmaxbrightness'] = data['ledmaxbrightness']
                if ('ledinvert' in data):
                    if (data['ledinvert'] == 'True'):
                        response.addStatus ("success", "ledinvert", "success")
                        config['LEDs']['ledinvert'] = "True"
                    elif (data['ledinvert'] == 'False'):
                        response.addStatus ("success", "ledinvert", "success")
                        config['LEDs']['ledinvert'] = "False"
                    # if not true or false then serious error
                    else:
                        response = {'reply':'error', 'error':'Invalid type in ledinvert'}
                        return response.getStatus()
                if ('rgb' in data):
                    if (data['rgb'] == 'True'):
                        response.addStatus ("success", "rgb", "success")
                        config['LEDs']['rgb'] = "True"
                    elif (data['rgb'] == 'False'):
                        response.addStatus ("success", "rgb", "success")
                        config['LEDs']['rgb'] = "False"
                    # if not true or false then serious error
                    else:
                        response = {'reply':'error', 'error':'Invalid type in rgb'}
                        return response.getStatus()
                ## Now save the config
                # save config
                try:
                    with open(configfile, 'w') as cfgfile:
                        config.write(cfgfile)
                        response.addStatus ("success", "saveconfig", "success")
                        if (DEBUG >= 3) : print ("Info: Updated configuration saved "+configfile)
                except Exception as e:
                        response = {'reply':'error', 'error':'Error saving configuration'}
                        if (DEBUG >= 1) : print ("Error: saving configuration file "+configfile+"::"+str(e))
                        return response.getStatus()
                # Reread in settings (always use the saved config - if can't update then settings don't get updated
                settings = ledsettings.LEDSettings(config)
                LEDs.updSettings(settings.allSettings())
                
                

    # Reach here then unknown request
    return response.getStatus()
    
    

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
    elif (colour != ""):
        debugMsg (5, "Warning: Invalid colour provided for allon")
    command.setCommand("allOn")
    command.setCmdStatus(True)
      

def chg_sequence():
    seq = request.query.seq
    # For security reasons check that it is a valid sequence
    if not seq in sequenceOptions.keys(): 
        debugMsg (3, "Warning: Invalid sequence requested")
        return
    command.setCommand(seq)
    command.setCmdStatus(True)
    

def alloff():
    command.setCommand("allOff")
    command.setCmdStatus(True)

## Todo


def setcolours():
    colours = request.query.colours
    colourlist = colours.split(",")
    intcolours = []
    
    # Check that all colours are valid and convert them into Colors 
    # If any are not valid then quit without changing any colours
    
    #for (thiscolour: colourlist):
    for i in range(colourlist.size()):
        try:
            intcolours.append(int(colourlist[i], 16))
        except ValueError as err:
            debugMsg (3, "Warning: Invalid colour provided in setcolour")
            return
        except Exception as e:
            debugMsg (1, "Warning: Unknown exception has occurred setting colours")
            return

    # Now have an array of int values 
    command.setColours(intcolours)


def server_home ():
    #return static_file ('index.html', root=DOCUMENT_ROOT)
    return indexPage(sequenceOptions)


#Thread for communicating with neopixels
#Simple one-way communication with thread using globals
#checks variables or updates (cmdMessage, cmdColours)
def runPixels(q):
    
    cmd = LEDCmds()
    LEDs = LightSeq(config['Server']['hardware'], settings.allSettings(), cmd)
    
    while cmd.getCommand() != "STOP":
        # check for new command on the queue
        if (not q.empty()):
            qcmd, qvalue = q.get()
            # split the queue string into method and parameter
            updcmd = getattr (cmd, qcmd)
            updcmd(qvalue)
        # run appropriate script
        method = getattr (LEDs, cmd.getCommand())
        method()
        # sleep to allow other threads to run
        time.sleep(0.01)
        


def debugMsg(priority, message) :
    if (DEBUG >= priority):
        print (message)


def showLogin(message):
    print ("Login required "+message)
    
    
def loadConfig():
    
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




def main():

    global command, settings, LEDs, passwords


    print ("Content-Type: text/html")     # HTML is following
    print ("")                              # blank line, end of headers

    arguments = cgi.FieldStorage()
    for i in arguments.keys():
        print (arguments[i].value)


    settings = ledsettings.LEDSettings(config)
    command = WebSrvCmds(SOCKET_ADDRESS)
    
    command.setCommand("allOn")
    
    # memory queue now moved to WebSrvCmds
    
    # Setup shared memory queue - only if already exists
    #try:
    #    mq = posix_ipc.MessageQueue(MSG_QUEUE_NAME, posix_ipc.O_CREAT)
    #    print ("Message queue connected")
        # Send message to queue
    #    mq.send("status,1")
    #except Exception as e: 
    #    print ("Error connecting to server "+str(e))
        
    # Send message to queue
    #mq.send("status, ", block=False)

                                                                          
    
if __name__ == "__main__":
  

    main()

