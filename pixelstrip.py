#!/usr/bin/env python3

import sys
import math
import random
import threading
from neopixelcmds import *
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from neopixelseq import *
import configparser
import time
from configwindow import *
import webbrowser
import ledsettings
from collections import OrderedDict


VERSION = '0.1 beta'

# File containing sequences and colour options
# Must exist and have valid entries
sequencefile = 'sequences.cfg'

# File containing user config
# If not exist then use defaults
configfile = 'rpnpgp.cfg'

readmefile = 'docs/readme.html'
userfile = 'docs/userguide.html'
customfile = 'docs/customguide.html'

# Use to send a message to GUI - created during startup
# eg. message = ("Warning", "Insert warning here")
message = ("","")

# Settings for neopixels
# load from config file - these are defaults if no config file found

defaultLEDSettings = {
    'ledcount': 16,
    'gpiopin': 18,
    'ledfreq': 800000,
    'leddma' : 5,
    'ledmaxbrightness': 255,
    'ledinvert': False
    }

# Grid for sequence buttons
sequenceGridX = 3
sequenceGridY = 4
numsequenceButtons = sequenceGridX * sequenceGridY


DEFAULTSPEED = 50
MAXCOLOURS = 10
MINDELAY = 10.0
MAXDELAY = 100.0


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
            self.coloursChosenBox.itemconfigure(i, background=hexColourToString(self.colourChoice[self.chosenColours[i]]), foreground=colourContrast(self.colourChoice[self.chosenColours[i]]))

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
            self.coloursChosenBox.itemconfigure(i, background=hexColourToString(self.colourChoice[self.chosenColours[i]]), foreground=colourContrast(self.colourChoice[self.chosenColours[i]]))
    
    def rstColour(self):
        self.chosenColours = tuple()
        self.chosenColoursVar = StringVar(value=self.chosenColours)
        self.coloursChosenBox.configure (listvariable=self.chosenColoursVar)


    def ApplyChange(self):
        # update command object to be passed to the 
        cmd, text = self.sequenceOptions[self.sequence.get()]
        self.command.setCommand(cmd)
        coloursTicked = []
        for i in range (len(self.chosenColours)):
            text = self.chosenColours[i]
            value = self.colourChoice[text]
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
        # Set status to updated so light sequence can stop during method execution
        self.command.setCmdStatus(True)

        
    # Moved from def __del__(self): to closeApp with WindowManager binding 
    # as more reliable than needing to wait for __del__
    def closeApp(self):
        # When close window notify thread to terminate 
        self.command.setCommand("STOP")
        self.command.setCmdStatus(True)
        self.parent.destroy()


    def __init__(self, parent, command, sequenceOptions, colourChoice, config, cfgwindow):
        Frame.__init__(self, parent)
        self.seqScreen = 1                  # which screen of sequences we are displaying - starts at 1
        self.command = command
        self.sequenceOptions = sequenceOptions
        self.colourChoice = colourChoice
        self.config = config
        self.parent = parent
        self.cfgwindow = cfgwindow
        self.initUI()

    def initUI(self):

        self.parent.title("RpNpGp - Raspberry Pi Neopixel Gui Package");
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
        menu_file.add_separator()
        menubar.add_cascade(menu=menu_help, label='Help')
        
        menu_file.add_command(label='Quit', command=self.closeApp)
        menu_edit.add_command(label='Settings', command=self.cfgwindow.windowClient)
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
        
        self.rowconfigure(1, minsize=20)    # Spacer at top
        self.rowconfigure(2, minsize=85)    # Tab frame
        self.rowconfigure(3, minsize=40)    # Speed slider
        self.rowconfigure(4, minsize=60)    # Colours (also rowspan to 5)
        self.rowconfigure(5, minsize=60)    # Apply button       
        self.rowconfigure(6, minsize=40)    # Bottom padding / messages

        self.sequence = IntVar()
        self.sequence.set(0)

        # The image is a massively oversized image of a strip of LEDs
        # I like the effect of being zoomed in, but this will also help with large screens not having horrible borders 
        backgroundImage = PhotoImage(file="neopixel2.gif")
        backgroundImageLabel = Label(self, image=backgroundImage)
        # next line is required to stop the image from being garbage collected
        backgroundImage.image = backgroundImage
        backgroundImageLabel.place(x=0, y=0, relwidth=1, relheight=1)

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
        currentButton = 0;
        
        for numframe in range (numtabs):
            self.frames.append(ttk.Frame(self.tabFrame))
            self.frames[numframe]['style'] = 'TabFrame.TFrame';
            self.tabFrame.add(self.frames[numframe], text="Sequences "+str(numframe+1))
            for i in range(0, numsequenceButtons):
                cmd, txt = self.sequenceOptions[currentButton]
                self.seqButtons.append(Radiobutton(self.frames[numframe],
                        text=txt,
                        font="Verdana 14",
                        variable=self.sequence,
                        height=3,
                        width=20,
                        indicatoron=0,
                        value=currentButton))
                self.seqButtons[currentButton].grid(row=currentRow, column=currentColumn, columnspan=2, padx=10, pady=10)
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
        
        speedLabel = Label(self,
                    font="Verdana 14",
                    text="Speed")
        speedLabel.grid (row=currentRow, column=1, sticky='ew', padx=10)
        
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
        colourLabel = Label(colourSelectFrame,
                    font="Verdana 14",
                    text="Colours Available")
        colourLabel.grid (row=0, column=0, columnspan=2, sticky='ews')
        
        colourLabel2 = Label(colourSelectFrame,
                    font="Verdana 14",
                    text="Colours Chosen")
        colourLabel2.grid (row=0, column=3, sticky='ews')
        
        
        self.tuple_colours = ()
        # temp to get from list of tuples to dict
        for key in self.colourChoice:
            self.tuple_colours += (key,)
        
        
        self.colourList = StringVar(value=self.tuple_colours)
                
        self.coloursAvailBox = Listbox(colourSelectFrame, listvariable=self.colourList, height=10)
        self.coloursAvailBox.grid(column=0, row=1, rowspan=6, sticky=(N,S,E,W))

        # Colour code the list
        for i in range(len(self.colourChoice)):
            self.coloursAvailBox.itemconfigure(i, background=hexColourToString(self.colourChoice[self.tuple_colours[i]]), foreground=colourContrast(self.colourChoice[self.tuple_colours[i]]))


        # Set event bindings for when the selection in the listbox changes,
        # when the user double clicks the list, and when they hit the Return key
        self.coloursAvailBox.bind('<Double-1>', self.addColourEvent)


        self.chosenColours = ()        
        self.chosenColoursVar = StringVar(value=self.chosenColours)

        self.coloursChosenBox = Listbox(colourSelectFrame, listvariable=self.chosenColoursVar, height=10)
        self.coloursChosenBox.grid(column=3, row=1, rowspan=6, sticky=(N,S,E,W))
        
        
        addColourButton = ttk.Button(colourSelectFrame, 
                    text=">>",
                    width = 5,
                    style="ColButtons.TButton",
                    command=self.addColour)
        addColourButton.grid(row=1, column=2)
        
        
        delColourButton = ttk.Button(colourSelectFrame, 
                    text="<<",
                    width = 5,
                    style="ColButtons.TButton",
                    command=self.delColour)
        delColourButton.grid(row=4, column=2)
        
        
        rstColourButton = ttk.Button(colourSelectFrame, 
                    text="Clr",
                    width = 5,
                    style="ColButtons.TButton",
                    command=self.rstColour)
        rstColourButton.grid(row=6, column=2)
        
        

        applyButton = ttk.Button(self, 
                    text="Apply",
                    width = 20,
                    command=self.ApplyChange,)
        applyButton.grid(row=currentRow+1, column=4, columnspan=2, pady=20, padx=40, sticky='nesw')


        
        
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
    
    # Create config window
    cfgwindow = ConfigWindow(config, configfile, defaultLEDSettings, settings, LEDs)
    
    thread=threading.Thread(target=runPixels, args=(LEDs, command))
    thread.start()
    
    root = Tk()
    
    root .option_add('*tearOff', FALSE)
    
    ttk.Style().configure("TButton", font='Helvetica 16 bold')
    ttk.Style().configure("TNotebook", background='#999999')
    ttk.Style().configure('TabFrame.TFrame', background='#999999')
    ttk.Style().configure('TNotebook.Tab', font='Helvetica 16 bold')
    ttk.Style().configure('ColButtons.TButton', font='Helvetica 10 bold')
                                                                          
    root.geometry("800x600+100+100")
    app = App(root, command, sequenceOptions, colourChoice, config, cfgwindow)
    root.mainloop()
    
if __name__ == "__main__":

    main()

