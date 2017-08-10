#!/usr/bin/env python3

# Client for the NeoPixel GUI - Disco Mode
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
import threading
from tkinter import *
from tkinter import ttk
from tkinter import messagebox  
from tkinter.colorchooser import *
import configparser
import time
from configneopixel import *
from configlocal import *
import webbrowser
import ledsettings
from collections import OrderedDict
from clientcontroller import *



### This is work in progress migrating to client server technology
# Initially this still uses the sequence file etc (so must be installed on
# the same machine as the server (or at least have the same configuration
# files copied over - in future this will be completely separated so
# can be run on a different server
###



VERSION = '0.3'

# File containing sequences and colour options
# Must exist and have valid entries
sequencefile = 'sequences.cfg'

# default hostnames and ports
defaultLocalSettings = {
    'hostname': '127.0.0.1',
    'port' : 80,
    'ssl' : False,
    'username' : '',
    'password' : '',
    # allow unverified will not check authentication of server
    # This could allow for server spoofing
    'allowunverified': False
    }


# File containing user config
# If it does not exist then use defaults
configfile = 'neopixel-disco.cfg'

readmefile = 'docs/readme.html'
userfile = 'docs/userguide.html'
customfile = 'docs/customguide.html'

# Use to send a message to GUI - created during startup
# eg. message = ("Warning", "Insert warning here")
message = ("","")

# Grid for sequence buttons
sequenceGridX = 3
sequenceGridY = 4
numsequenceButtons = sequenceGridX * sequenceGridY


DEFAULTSPEED = 50
MAXCOLOURS = 10
MINDELAY = 10.0
MAXDELAY = 100.0

DEFAULTWIDTH = 800
DEFAULTHEIGHT = 400
MINWIDTH = 800
MINHEIGHT = 400


global app


class App(Frame):

    # Adds colour from left (colours avail) to right (colours chosen)
    def addColour(self):
        colours = self.coloursAvailBox.curselection()
        if (len(colours)) < 1: return
        #Add all colours to the tuple (need to replace tuple in the process)
        for colourNum in colours:
            if (len(self.chosenColours)>=MAXCOLOURS):
                break
            self.chosenColours += (self.tuple_colours[int(colourNum)],)
        self.chosenColoursVar = StringVar(value=self.chosenColours)
        self.coloursChosenBox.configure (listvariable=self.chosenColoursVar)

        # Colour code the list
        for i in range(len(self.chosenColours)):
            self.coloursChosenBox.itemconfigure(i, background=hexColourToString(colourLookup(self.colourChoice, self.chosenColours[i])), foreground=colourContrast(colourLookup(self.colourChoice, self.chosenColours[i])))

    # Handle resize of screen. Does not change the root size, just resize internal components
    # Fairly basic - font resizing and button sizes based on frame size
    def resizeLayout(self, width, height):
        # Resize the font on the buttons etc - just basic thresholds where we change
        # min = default font
        newfont = "Verdana 10"
        newcolourfont = "Verdana 8"
        paddingsize = 5
        seqheight = 2
        seqwidth = 20
        if (width < 900 or height < 550):
            ttk.Style().configure("TButton", font='Helvetica 10')
            ttk.Style().configure('TNotebook.Tab', font='Helvetica 9')
            ttk.Style().configure('ColButton.TButton', font='Helvetica 10 bold')
        elif (width < 1000 or height < 750):
            newfont = "Verdana 12"
            newcolourfont = "Verdana 10"
            paddingsize = 15
            seqheight = 3
            seqwidth = 25
            ttk.Style().configure("TButton", font='Helvetica 13')
            ttk.Style().configure('TNotebook.Tab', font='Helvetica 12 bold')
            ttk.Style().configure('ColButton.TButton', font='Helvetica 13 bold')
        else :
            newfont = "Verdana 15"
            newcolourfont = "Verdana 13"
            paddingsize = 30
            seqheight = 4
            seqwidth = 30
            ttk.Style().configure("TButton", font='Helvetica 15')
            ttk.Style().configure('TNotebook.Tab', font='Helvetica 15 bold')
            ttk.Style().configure('ColButton.TButton', font='Helvetica 14 bold')
            
        for thisSeqButton in self.seqButtons:
            thisSeqButton.configure(font=newfont, height=seqheight, width=seqwidth)
            
        self.speedLabel.configure(font=newfont)
        self.colourLabel.configure(font=newcolourfont)
        self.colourLabel2.configure(font=newcolourfont)
        self.coloursAvailBox.configure(font=newcolourfont)
        self.coloursChosenBox.configure(font=newcolourfont)
        self.rowconfigure(1, minsize=paddingsize)
        self.rowconfigure(6, minsize=paddingsize)


    # Adds custom colour using colorchooser
    # todo - modify to match required colour selection
    def customColour(self):
        thiscolour = askcolor()
        if (thiscolour[0] == None) :
            return
        self.chosenColours += ((thiscolour[1]),)

        self.chosenColoursVar = StringVar(value=self.chosenColours)
        self.coloursChosenBox.configure (listvariable=self.chosenColoursVar)

        # Colour code the list
        for i in range(len(self.chosenColours)):
            self.coloursChosenBox.itemconfigure(i, background=hexColourToString(colourLookup(self.colourChoice, self.chosenColours[i])), foreground=colourContrast(colourLookup(self.colourChoice, self.chosenColours[i])))


    def getStatus(self):
        print ("Running")


    def addColourEvent(self, event):
        self.addColour()

    def delColour(self):
        colours = self.coloursChosenBox.curselection()
        if (len(colours)) < 1: return
        # Create a new tuple excluding colourNum
        removeColours = []
        for colourNum in colours:
            # copy the position as int into a remove this colour list
            removeColours.append(int(colourNum))
        # now go over existing tuple
        tuple_colours = tuple()
        for i in range(len(self.chosenColours)):
            # as long as not in list then add
            if (i not in removeColours):
                tuple_colours += (self.chosenColours[i],)
        self.chosenColours = tuple_colours
        self.chosenColoursVar = StringVar(value=self.chosenColours)
        self.coloursChosenBox.configure (listvariable=self.chosenColoursVar)
        # Reapply colour coding
        # Colour code the list
        for i in range(len(self.chosenColours)):
            self.coloursChosenBox.itemconfigure(i, background=hexColourToString(colourLookup(self.colourChoice, self.chosenColours[i])), foreground=colourContrast(colourLookup(self.colourChoice, self.chosenColours[i])))
    
    def rstColour(self):
        self.chosenColours = tuple()
        self.chosenColoursVar = StringVar(value=self.chosenColours)
        self.coloursChosenBox.configure (listvariable=self.chosenColoursVar)


    def ApplyChange(self):
        # update command object to be passed to the 
        cmd, text = self.sequenceOptions[self.sequence.get()]
        response = self.command.setSequence(cmd)
        #print ("Response received "+str(response))
        if (response['reply'] == "auth"):
            messagebox.showinfo("Error", "Authentication required\nUpdate settings with username and password\n")
            return
        elif (response['reply'] == "fail"):
            messagebox.showinfo("Error", "Unable to connect to server.\nCheck server is started and address matches\n")
            return
        coloursTicked = []
        for i in range (len(self.chosenColours)):
            text = self.chosenColours[i]
            value = colourLookup (self.colourChoice, text)
            # value is from config which is string - so convert to int
            coloursTicked.append(int(value, 16))
        # Handle speed - convert from String to int
        try:
            delay = int(self.speedLEDVar.get())
        except ValueError:
            delay = DEFAULTSPEED, 
        self.speedLEDVar.set(delay), 
        self.command.setDelay(delay)
        self.command.setColours(coloursTicked)

        
    # Moved from def __del__(self): to closeApp with WindowManager binding 
    # as more reliable than needing to wait for __del__
    def closeApp(self):
        # When close window notify thread to terminate 
        self.parent.destroy()


    def __init__(self, parent, command, sequenceOptions, colourChoice, config, cfglocal, cfgneopixel):
        Frame.__init__(self, parent)
        self.seqScreen = 1                  # which screen of sequences we are displaying - starts at 1
        self.command = command
        self.sequenceOptions = sequenceOptions
        self.colourChoice = colourChoice
        self.config = config
        self.parent = parent
        self.cfglocal = cfglocal
        self.cfgneopixel = cfgneopixel
        self.initUI()

    def initUI(self):

        self.parent.title("Disco Pixels - Raspberry Pi Neopixel Disco Lighting");
        self.parent.wm_protocol('WM_DELETE_WINDOW',  self.closeApp)

                
        menubar = Menu(self.parent)
        self.parent['menu'] = menubar
        menu_file = Menu(menubar)
        menu_edit = Menu(menubar)
        menu_hardware = Menu(menubar)
        menu_help = Menu(menubar, name='help')
        menubar.add_cascade(menu=menu_file, label='File')
        menubar.add_cascade(menu=menu_edit, label='Edit')
        menubar.add_cascade(menu=menu_hardware, label='Hardware')
        #menu_file.add_separator()
        menubar.add_cascade(menu=menu_help, label='Help')
        
        menu_file.add_command(label='Quit', command=self.closeApp)
        menu_edit.add_command(label='Settings', command=self.cfglocal.windowClient)
        menu_hardware.add_command(label='NeoPixels', command=self.cfgneopixel.windowClient)
        menu_help.add_command(label='Readme', command=viewReadme)
        menu_help.add_command(label='User Guide', command=viewUserGuide)
        menu_help.add_command(label='Customisation Guide', command=viewCustom)
        menu_help.add_command(label='About', command=aboutBox)
        
        
        self.pack(fill=BOTH, expand=1)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=1)
        self.columnconfigure(5, weight=1)
        self.columnconfigure(6, weight=1)                                                           
        
        self.rowconfigure(1, minsize=5)     # Spacer at top
        self.rowconfigure(2, minsize=65)    # Tab frame
        self.rowconfigure(3, minsize=25)    # Speed slider
        self.rowconfigure(4, minsize=60)    # Colours (also rowspan to 5)
        self.rowconfigure(5, minsize=25)    # Apply button       
        self.rowconfigure(6, minsize=5)     # Bottom padding / messages

        self.sequence = IntVar()
        self.sequence.set(0)


        # The image is a massively oversized image of a strip of LEDs
        # I like the effect of being zoomed in, but this will also help with large screens not having horrible borders 
        # These are created as self. to prevent them being garbage collected
        self.backgroundImage = PhotoImage(file="neopixel2.gif")
        self.backgroundImageLabel = Label(self, image=self.backgroundImage)
        # next line is required to stop the image from being garbage collected
        self.backgroundImage.image = self.backgroundImage
        self.backgroundImageLabel.place(x=0, y=0, relwidth=1, relheight=1)

        # Use to set the selected colour
        self.colourSelected = [0 for x in range(len(self.colourChoice))]

        # Store delay time for LEDs (as a string)
        self.speedLEDVar = DoubleVar()
        # Set a default value
        self.speedLEDVar.set("50")
 
        currentRow = 1
        currentColumn = 0
        numColumns = 6

        self.tabFrame = ttk.Notebook(self)
        # Allow CTRL-Tab between frames
        self.tabFrame.enable_traversal()
        self.frames = []
        self.seqButtons = []
        numtabs = int(math.ceil(len(self.sequenceOptions)/numsequenceButtons));
        currentButton = 0
        
        
        for numframe in range (numtabs):
            self.frames.append(ttk.Frame(self.tabFrame))
            self.frames[numframe]['style'] = 'TabFrame.TFrame';
            self.tabFrame.add(self.frames[numframe], text="Sequences "+str(numframe+1))
            for i in range(0, numsequenceButtons):
                cmd, txt = self.sequenceOptions[currentButton]
                self.seqButtons.append(Radiobutton(self.frames[numframe],
                        text=txt,
                        font="Verdana 11",
                        variable=self.sequence,
                        height=2,
                        width=20,
                        indicatoron=0,
                        value=currentButton))
                self.seqButtons[currentButton].grid(row=currentRow, column=currentColumn, columnspan=2, padx=5, pady=1)
                currentColumn += 2
                if currentColumn >= numColumns :
                    currentColumn = 0
                    currentRow += 1
                currentButton += 1
                if (currentButton >= len(self.sequenceOptions)):
                    break;
        self.tabFrame.grid(row=2, column=0, columnspan=6)
       
        currentRow = 3
       
        # Set to allow between 10 and 500 
        
        self.speedLabel = Label(self,
                    font="Verdana 11",
                    text="Speed")
        self.speedLabel.grid (row=currentRow, column=1, sticky='ew', padx=10, pady=5)
        
        # default is 50mS
        speedBar = ttk.Scale(self, orient=HORIZONTAL, from_=MAXDELAY, to=MINDELAY, variable=self.speedLEDVar)
        speedBar.grid(row=currentRow, column=2, columnspan=3, sticky='ew')


        currentRow = 4
        currentColumn = 0
        
        # Frame to hold the colour selection options
        colourSelectFrame = ttk.Frame(self)
        colourSelectFrame.grid (column=1, row=currentRow, columnspan=3, rowspan=2, sticky='nsew')
        
        colourSelectFrame.columnconfigure(2, weight=10)
        
        #Title for frame
        self.colourLabel = Label(colourSelectFrame,
                    font="Verdana 8",
                    text="Colours Available")
        self.colourLabel.grid (row=0, column=0, columnspan=2, sticky='ews')
        
        self.colourLabel2 = Label(colourSelectFrame,
                    font="Verdana 8",
                    text="Colours Chosen")
        self.colourLabel2.grid (row=0, column=3, sticky='ews')
        
        
        self.tuple_colours = ()
        # temp to get from list of tuples to dict
        # This stores the pre-stored colours as tuples eg. ('white', 0xffffff)
        # Note that it should not be used directly (as that would fail with custom colours - instead use colourLookup passing this as first argument and colour string (or # code) as second argument
        for key in self.colourChoice:
            self.tuple_colours += (key,)
        
        
        self.colourList = StringVar(value=self.tuple_colours)
                
        self.coloursAvailBox = Listbox(colourSelectFrame, listvariable=self.colourList, height=10, font="Verdana 8")
        self.coloursAvailBox.grid(column=0, row=1, rowspan=6, sticky=(N,S,E,W))

        # Colour code the list
        for i in range(len(self.colourChoice)):
            self.coloursAvailBox.itemconfigure(i, background=hexColourToString(self.colourChoice[self.tuple_colours[i]]), foreground=colourContrast(self.colourChoice[self.tuple_colours[i]]))


        # Set event bindings for when the selection in the listbox changes,
        # when the user double clicks the list, and when they hit the Return key
        self.coloursAvailBox.bind('<Double-1>', self.addColourEvent)


        self.chosenColours = ()        
        self.chosenColoursVar = StringVar(value=self.chosenColours)

        self.coloursChosenBox = Listbox(colourSelectFrame, listvariable=self.chosenColoursVar, height=10, font="Verdana 8")
        self.coloursChosenBox.grid(column=3, row=1, rowspan=6, sticky=(N,S,E,W))
        
        
        self.addColourButton = ttk.Button(colourSelectFrame, 
                    text=">>",
                    width = 5,
                    style="ColButton.TButton",
                    command=self.addColour)
        self.addColourButton.grid(row=1, column=2)
        
        
        self.delColourButton = ttk.Button(colourSelectFrame, 
                    text="<<",
                    width = 5,
                    style="ColButton.TButton",
                    command=self.delColour)
        self.delColourButton.grid(row=4, column=2)
        
        
        self.rstColourButton = ttk.Button(colourSelectFrame, 
                    text="Clr",
                    width = 5,
                    style="ColButton.TButton",
                    command=self.rstColour)
        self.rstColourButton.grid(row=6, column=2)
        
        # todo - enable custom colour button
        self.customColourButton = ttk.Button(self, text="Custom colour", command=self.customColour)
        self.customColourButton.grid(row=currentRow, column=4, columnspan=2, pady=10,padx=10)
        
                        
        self.applyButton = ttk.Button(self, 
                    text="Apply",
                    width = 10,
                    command=self.ApplyChange,)
        self.applyButton.grid(row=currentRow+1, column=4, columnspan=2, pady=20, padx=40, sticky='nesw')

       
        # Finished setting up GUI - now issue any message
        if (message[0] != ""):
            messagebox.showinfo(message[0], message[1])

# Designed for tkinter so handles strings
# returns string #ffffff for white writing or #000000 for black 
def colourContrast(colour):
    blueValue = int(colour, 16) & 0xFF
    greenValue = (int(colour, 16) >> 8) & 0xFF
    redValue = (int(colour, 16) >> 16) & 0xFF
    # Perceptive luminance based on human eye relativity 
    lumValue = 1 - (( 0.299 * redValue) + (0.587 * greenValue) + (0.114 * blueValue))/255;

    if (lumValue < 0.5):
       return "#000000"
    else:
       return "#FFFFFF"
    
# Takes colour rgb tuple and returns as int
# todo Notused ??
def colourToInt (colour):
    red = colour[0] << 16
    green = colour [1] << 8
    blue = colour[2]
    
    return int(reg+green+blue)
    
def htmlColourToHexString (htmlcolour):
    # replace # with 0x
    return ('0x'+htmlcolour[2:])
    
# Looks up colour from colourChoice - or returns 0x string if starts with #
# if doesn't begin with # then lookup value from colourChoice dict
# eg. '#ffffff' - would return '0xffffff', 'white' would return colourChoice['white'] which should have been pre-configured as '0xffffff'
def colourLookup(colourChoice, thisColour):
    if (thisColour[:1] == '#'):
        return '0x'+thisColour[1:]
        #return thisColour
    return colourChoice[thisColour]
    
def hexColourToString(colour):
    blueValue = int(colour, 16) & 0xFF
    greenValue = (int(colour, 16) >> 8) & 0xFF
    redValue = (int(colour, 16) >> 16) & 0xFF
    return "#%02x%02x%02x" % (redValue, greenValue, blueValue)


def viewReadme():
    webbrowser.open_new(readmefile)

def viewUserGuide():
    webbrowser.open_new(userfile)

def viewCustom():
    webbrowser.open_new(customfile)


def aboutBox(): 
    messagebox.showinfo(
            "About",
            "Neopixel GUI\nVersion %s\nBy Stewart Watkiss @penguintutor" % VERSION
        )


def numpages (numsequences, numbuttons) :
    return int((numsequences-1) / numbuttons) + 1


def configure (event):
    # Only interested in changes to the top level window (.)
    if (str(event.widget) != '.'): return
    width, height = event.width, event.height
    app.resizeLayout(width,height)


def main():

    global message, app

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
    
    command = ClientController(settings.hostname(), settings.port(), settings.ssl(), settings.username(), settings.password(), settings.allowunverified())
    
    # Create config windows
    cfglocal = ConfigLocal(config, configfile, settings, defaultLocalSettings, command)
    cfgneopixel = ConfigNeopixel(config, settings, command)
    
    root = Tk()
    
    root.iconbitmap('@disco-pixels.xbm')
    
    root.option_add('*tearOff', FALSE)
    
    # New styles use <newname>.<existing> - where newname derives rest of properties from existing
    ttk.Style().configure("TButton", font='Helvetica 11')
    ttk.Style().configure('TabFrame.TFrame', background='#999999')
    ttk.Style().configure("TNotebook", background='#999999')
    ttk.Style().configure('TNotebook.Tab', font='Helvetica 11 bold')
    ttk.Style().configure('ColButton.TButton', font='Helvetica 10 bold')

                                                                          
    root.geometry("%dx%d+100+100" % (DEFAULTWIDTH, DEFAULTHEIGHT))
    root.minsize(MINWIDTH,MINHEIGHT)
    app = App(root, command, sequenceOptions, colourChoice, config, cfglocal, cfgneopixel)
    root.bind("<Configure>", configure)
    root.mainloop()
    
if __name__ == "__main__":

    main()

