#!/usr/bin/env python3

import sys
import random
import threading
from neopixelcmds import *
from tkinter import *
from neopixelseq import *
import configparser
import time
from configwindow import *

# File containing sequences and colour options
# Must exist and have valid entries
sequencefile = 'sequences.cfg'

# File containing user config
# If not exist then use defaults
configfile = 'rpnpgp.cfg'

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


# sequenceOptions = [
    # ("allOff", "All off"),                    
    # ("allOn", "All on"),
    # ("allOnSingleColour", "All on\nSingle Colour"),
    # ("chaser", "Chaser"),
    # ("chaserSingleColour", "Chaser\nSingle Colour"),
    # ("chaserBackground", "Chaser\nSolid background"),
    # ("colourWipe", "Colour Wipe"),
    # ("inOut", "In Out"),
    # ("outIn", "Out In"),    
    # ("rainbow", "Rainbow"),
    # ("rainbowCycle", "Rainbow Cycle\nFast"),
    # ("theatreChaseRainbow", "Rainbow Theatre Chase")
    # ]

#colourChoice = [
#    ('White', 0xffffff), ('Red', 0xff0000), ('Green', 0x00ff00), ('Blue', 0x0000ff)
#    ]

# Grid for sequence buttons
sequenceGridX = 3
sequenceGridY = 4
numsequenceButtons = sequenceGridX * sequenceGridY


DEFAULTSPEED = 50;


class App(Frame):



    def ApplyChange(self):
        # update command object to be passed to the 
        cmd, text = self.sequenceOptions[self.sequence.get()]
        self.command.setCommand(cmd)
        coloursTicked = []
        for i in range (len(self.colourSelected)):
            if (self.colourSelected[i].get() == 1) :
                text, value = self.colourChoice[i]
                # value is from config which is string - so convert to int
                coloursTicked.append(int(value, 16))
        # Handle speed - convert from String to int
        try:
            delay = int(self.speedLEDString.get())
        except ValueError:
            delay = DEFAULTSPEED, 
        self.speedLEDString.set(delay), 
        self.command.setDelay(delay)
        self.command.setColours(coloursTicked)
        # Set status to updated so light sequence can stop during method execution
        self.command.setCmdStatus(True)

    
    def moreSequences(self):
        # Change the sequence buttons
        # Todo
        pass
    
        

    def __del__(self):
        global cmdMessage
        # When close window notify thread to terminate and then give 
        # time for it to close properly before cleanup
        self.command.setCommand("STOP")
        self.command.setCmdStatus(True)
        #time.wait(5)
    
    def __init__(self, parent, command, sequenceOptions, colourChoice, config, cfgwindow):
        Frame.__init__(self, parent)
        self.command = command
        self.sequenceOptions = sequenceOptions
        self.colourChoice = colourChoice
        self.config = config
        self.parent = parent
        self.cfgwindow = cfgwindow
        self.initUI()

    def initUI(self):

        self.parent.title("RpNpGp - Raspberry Pi Neopixel Gui Package");

        self.pack(fill=BOTH, expand=1)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=1)
        self.columnconfigure(5, weight=1)
        self.columnconfigure(6, weight=1)                                                           
        

        self.sequence = IntVar()
        self.sequence.set(0)



        # Use to set the selected colour
        self.colourSelected = [0 for x in range(len(self.colourChoice))]

        # Store number of LEDs (as a string)
        self.speedLEDString = StringVar()
        # Set a default value
        self.speedLEDString.set("50")
        
        titleLabel = Label(self,
                text="RpNpGp - Raspberry Pi Neopixel Gui Package",
                foreground="blue", font="Verdana 16 bold").grid(columnspan=6, sticky=W, pady=4, padx=5)
        
        description = """Control NeoPixels (RGB LEDs)\nfrom the Raspberry Pi"""
        text1 = Label(self, 
                justify=LEFT,
                font="Verdana 14",
                text=description).grid(sticky=W, columnspan=4, ipadx=10)


        logo = PhotoImage(file="logo.gif")
        image1 = Label(self, image=logo, justify=RIGHT)
        # next line is required to stop the image from being garbage collected
        image1.image = logo
        image1.grid(row=1, column=4, pady=10, columnspan=2)

        currentRow = 2
        currentColumn = 0
        numColumns = 6

        for i in range(0, numsequenceButtons):
            cmd, txt = self.sequenceOptions[i]
            Radiobutton(self,
                    text=txt,
                    font="Verdana 14",
                    variable=self.sequence,
                    height=3,
                    width=25,
                    indicatoron=0,
                    value=i).grid(row=currentRow, column=currentColumn, columnspan=2, padx=10, pady=10)
            currentColumn += 2
            if currentColumn >= numColumns :
                currentColumn = 0
                currentRow += 2

        # If currentColumn is 0 then aready incremented since last button added
        # otherwise add new row
        if currentColumn != 0:
            currentRow += 1

        # Create a frame within the frame for checkbuttons
        optionFrame = Frame(self)
        optionFrame.grid(row=currentRow, column=0, columnspan=6)

        currentRow += 1
        

        for i in range(len(self.colourChoice)):
            self.colourSelected[i] = IntVar()
            colourWord, colourCode = self.colourChoice[i]
            colourCheckBox = Checkbutton(optionFrame,
                    text=colourWord,
                    font="Verdana 14",
                    variable=self.colourSelected[i])
            colourCheckBox.pack(side=LEFT)

        spacer1 = LabelFrame(optionFrame, width=100).pack(side=LEFT)

        numSpeedLabel = Label(optionFrame,
                    font="Verdana 14",
                    text="Wait ms").pack(side=LEFT)

        numSpeedEntry = Entry(optionFrame,
                    font="Verdana 14",
                    width=5,
                    textvariable=self.speedLEDString).pack(side=LEFT, padx=10)


        applyButton = Button(self, 
                    text="Apply",
                    font="Verdana 14",
                    width = 20,
                    height = 3,
                    command=self.ApplyChange)
        applyButton.grid(row=currentRow, column=2, columnspan=2, pady=20)



        configButton = Button(self, 
                    text="Config",
                    font="Verdana 14",
                    width = 10,
                    height = 3,
                    command=self.cfgwindow.windowClient)
        configButton.grid(row=currentRow, column=0, pady=20)
        
        # Only display page button if we have more than 1 page of sequences
        if (len(self.sequenceOptions) > numsequenceButtons) :
            pageButton = Button(self, 
                        text="Page 1 of " + str(numpages(len(self.sequenceOptions), numsequenceButtons)),
                        font="Verdana 14",
                        width = 10,
                        height = 3,
                        command=self.moreSequences)
            pageButton.grid(row=currentRow, column=5, pady=20)
        
        
        # Finished setting up GUI - now issue any message
        if (message[0] != ""):
            messagebox.showinfo(message[0], message[1])


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
    # configwriter keys are normally case insensitive - override as need case for method names
    seqconfig.optionxform = str
    # Load the sequences
    try :
        seqconfig.read(sequencefile)
    except (configparser.Error, KeyError) :
        # Can't display warning at this stage so save message for when gui loaded
        message = ("Error", "Sequence.cfg does not exist\n or is missing important values")
        
    # iterate over sequences which allows handling of "\n" text to '\n' character
    sequenceOptions = []
    for key, value in seqconfig.items('Sequences') :
        sequenceOptions.append ([key, value.replace('\\n', '\n')]) 
    colourChoice = seqconfig.items('Colours')
               
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
    
    LEDSettings = {
    'ledcount': int(config['LEDs']['ledcount']),
    'gpiopin': int(config['LEDs']['gpiopin']),
    'ledfreq': int(config['LEDs']['ledfreq']),
    'leddma' : int(config['LEDs']['leddma']),
    'ledmaxbrightness': int(config['LEDs']['ledmaxbrightness']),
    'ledinvert': config['LEDs'].getboolean('ledinvert')
    }
    
    command = NeoPixelCmds()
    LEDs = NeoPixelSeq(LEDSettings, command)
    
    # Create config Window
    cfgwindow = ConfigWindow(config, configfile)
    
    thread=threading.Thread(target=runPixels, args=(LEDs, command))
    thread.start()
    
    root = Tk()
    root.geometry("800x600+100+100")
    app = App(root, command, sequenceOptions, colourChoice, config, cfgwindow)
    root.mainloop()
    
    
if __name__ == "__main__":

    main()

