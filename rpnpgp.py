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
from helpwindow import *
import webbrowser

# File containing sequences and colour options
# Must exist and have valid entries
sequencefile = 'sequences.cfg'

# File containing user config
# If not exist then use defaults
configfile = 'rpnpgp.cfg'

helpfile = 'help.html'

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
        # The button is hidden if only one screen so always change when clicked
        self.seqScreen += 1
        if (self.seqScreen > numpages(len(self.sequenceOptions), numsequenceButtons)):
                self.seqScreen = 1
        # Update the page button
        self.pageButton.config(text = "Page " + str(self.seqScreen) + " of " + str(numpages(len(self.sequenceOptions), numsequenceButtons)))
        # Update the sequence radiobuttons
        for i in range(0, numsequenceButtons):
            seqNumber = ((self.seqScreen-1)*numsequenceButtons)+i
            if (len(self.sequenceOptions) > seqNumber):
                cmd, txt = self.sequenceOptions[seqNumber]
                self.seqButtons[i].config(text=txt, value=seqNumber)
                # add it back to grid
                self.seqButtons[i].grid()
            else:
                self.seqButtons[i].grid_remove()
            
        

    def __del__(self):
        global cmdMessage
        # When close window notify thread to terminate and then give 
        # time for it to close properly before cleanup
        self.command.setCommand("STOP")
        self.command.setCmdStatus(True)
        #time.wait(5)
    
    def __init__(self, parent, command, sequenceOptions, colourChoice, config, cfgwindow, helpwindow):
        Frame.__init__(self, parent)
        self.seqScreen = 1                  # which screen of sequences we are displaying - starts at 1
        self.command = command
        self.sequenceOptions = sequenceOptions
        self.colourChoice = colourChoice
        self.config = config
        self.parent = parent
        self.cfgwindow = cfgwindow
        self.helpwindow = helpwindow
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
        
        self.rowconfigure(2, minsize=85)
        self.rowconfigure(3, minsize=85)
        self.rowconfigure(4, minsize=85)
        self.rowconfigure(5, minsize=85)

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



        logo = PhotoImage(file="logo.gif")
        image1 = Label(self, image=logo, justify=RIGHT)
        # next line is required to stop the image from being garbage collected
        image1.image = logo
        image1.grid(row=1, column=0, pady=10, columnspan=1)

        description = """Control NeoPixels (RGB LEDs)\nusing a Raspberry Pi"""
        text1 = Label(self, 
                justify=LEFT,
                font="Verdana 14",
                text=description).grid(row=1, column=1, sticky=W, columnspan=4, ipadx=10)
                
        helpButton = Button(self, 
                    text="Help",
                    font="Verdana 14",
                    width = 10,
                    height = 2,
                    command=viewHelp)
#                    command=self.helpwindow.windowClient)
        helpButton.grid(row=1, column=5, pady=10)



        currentRow = 2
        currentColumn = 0
        numColumns = 6
        
        self.seqButtons = []

        for i in range(0, numsequenceButtons):
            cmd, txt = self.sequenceOptions[i]
            self.seqButtons.append(Radiobutton(self,
                    text=txt,
                    font="Verdana 14",
                    variable=self.sequence,
                    height=3,
                    width=25,
                    indicatoron=0,
                    value=i))
            self.seqButtons[i].grid(row=currentRow, column=currentColumn, columnspan=2, padx=10, pady=10)
            currentColumn += 2
            if currentColumn >= numColumns :
                currentColumn = 0
                currentRow += 1

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
            self.pageButton = Button(self, 
                        text="Page 1 of " + str(numpages(len(self.sequenceOptions), numsequenceButtons)),
                        font="Verdana 14",
                        width = 10,
                        height = 3,
                        command=self.moreSequences)
            self.pageButton.grid(row=currentRow, column=5, pady=20)
        
        
        # Finished setting up GUI - now issue any message
        if (message[0] != ""):
            messagebox.showinfo(message[0], message[1])
            
        #### Testing
        #self.seqButtons[11].grid_remove()
        #self.seqButtons[10].grid_remove()
        #self.seqButtons[9].grid_remove()



def viewHelp():
    webbrowser.open_new(helpfile)

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
    
    # Create config & help Windows
    helpwindow = HelpWindow()
    cfgwindow = ConfigWindow(config, configfile)
    
    thread=threading.Thread(target=runPixels, args=(LEDs, command))
    thread.start()
    
    root = Tk()
    root.geometry("800x600+100+100")
    app = App(root, command, sequenceOptions, colourChoice, config, cfgwindow, helpwindow)
    root.mainloop()
    
    
if __name__ == "__main__":

    main()

