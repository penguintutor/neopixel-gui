#!/usr/bin/env python3

import sys
import random
import threading
from neopixelcmds import *
from tkinter import *
from neopixelseq import *
import configparser
import time


# File containing config
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

sequenceOptions = [
    ("allOff", "All off"),                    
    ("allOn", "All on"),
    ("allOnSingleColour", "All on\nSingle Colour"),
    ("chaser", "Chaser"),
    ("chaserSingleColour", "Chaser\nSingle Colour"),
    ("chaserBackground", "Chaser\nSolid background"),
    ("colourWipe", "Colour Wipe"),
    ("inOut", "In Out"),
    ("outIn", "Out In"),    
    ("rainbow", "Rainbow"),
    ("rainbowCycle", "Rainbow Cycle\nFast"),
    ("theatreChaseRainbow", "Rainbow Theatre Chase")
    ]

colourChoice = [
    ('White', 0xffffff), ('Red', 0xff0000), ('Green', 0x00ff00), ('Blue', 0x0000ff)
    ]


DEFAULTSPEED = 50;


class App(Frame):

    # Track whether config window open to stop duplicate windows
    configWindowOpen = False

    # called from window manager handler or from Cancel button
    def CloseConfig(self):
        self.configWindowOpen = False
        self.configTop.destroy()


    def SaveConfig(self):
        self.config['LEDs']['ledcount'] = self.numLEDString.get()
        self.config['LEDs']['gpiopin'] = self.numGPIOString.get()
        # save config - and inform user to restart
        try:
            with open(configfile, 'w') as cfgfile:
                self.config.write(cfgfile)
                self.CloseConfig()
                messagebox.showinfo("Info", "Configuration saved\nRestart application to reload config")
        except : 
            self.CloseConfig()
            messagebox.showinfo("Error", "Error saving configuration file "+configfile)
        


    def Config(self):
        if (self.configWindowOpen) :
            return
        self.configWindowOpen = True
        self.configTop = tk.Toplevel(self)
        self.configTop.wm_title("RpNpGp - Configuration")
        self.configTop.wm_geometry("400x300")
        # set handler for close window using WM X
        self.configTop.wm_protocol('WM_DELETE_WINDOW',  self.CloseConfig)
        
        self.numLEDString = StringVar()
        self.numLEDString.set(int(self.config['LEDs']['ledcount']))
        self.numGPIOString = StringVar()
        self.numGPIOString.set(int(self.config['LEDs']['gpiopin']))
        
        configTitleLabel = Label(self.configTop,
                text="RpNpGp - Configuration",
                foreground="blue", font="Verdana 16 bold").grid(columnspan=3, sticky=W, pady=(4, 15), padx=5)
                
        numLEDLabel = Label(self.configTop,
                    font="Verdana 14",
                    text="Number LEDs").grid(row=1, column=1)
                    
        numLEDEntry = Entry(self.configTop,
                    font="Verdana 14",
                    width=5,
                    textvariable=self.numLEDString).grid(row=1, column=2)
                    
        numGPIOLabel = Label(self.configTop,
                    font="Verdana 14",
                    text="GPIO pin number").grid(row=2, column=1)
                    
        numGPIOEntry = Entry(self.configTop,
                    font="Verdana 14",
                    width=5,
                    textvariable=self.numGPIOString).grid(row=2, column=2)
                    
        cancelButton = Button(self.configTop, 
                    text="Cancel",
                    font="Verdana 14",
                    width = 8,
                    height = 1,
                    command=self.CloseConfig)
        cancelButton.grid(row=4, column=2, pady=(40, 10), padx=10)
    
    
        saveButton = Button(self.configTop, 
                    text="Save",
                    font="Verdana 14",
                    width = 8,
                    height = 1,
                    command=self.SaveConfig)
        saveButton.grid(row=4, column=3, pady=(40, 10), padx=10)
        

    def ApplyChange(self):
        # update command object to be passed to the 
        cmd, text = sequenceOptions[self.sequence.get()]
        self.command.setCommand(cmd)
        coloursTicked = []
        for i in range (len(self.colourSelected)):
            if (self.colourSelected[i].get() == 1) :
                text, value = colourChoice[i]
                coloursTicked.append(value)
        # Handle speed - convert from String to int
        try:
            delay = int(self.speedLEDString.get())
        except ValueError:
            delay = DEFAULTSPEED
        self.speedLEDString.set(delay)
        self.command.setDelay(delay)
        self.command.setColours(coloursTicked)
        # Set status to updated so light sequence can stop during method execution
        self.command.setCmdStatus(True)

            
        

    def __del__(self):
        global cmdMessage
        # When close window notify thread to terminate and then give 
        # time for it to close properly before cleanup
        self.command.setCommand("STOP")
        self.command.setCmdStatus(True)
        #time.wait(5)
    
    def __init__(self, parent, command, config):
        Frame.__init__(self, parent)
        self.command = command
        self.config = config
        self.parent = parent
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
        self.colourSelected = [0 for x in range(len(colourChoice))]

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

        for i in range(0, len(sequenceOptions)):
            cmd, txt = sequenceOptions[i]
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
        

        for i in range(len(colourChoice)):
            self.colourSelected[i] = IntVar()
            colourWord, colourCode = colourChoice[i]
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
                    command=self.Config)
        configButton.grid(row=currentRow, column=0, pady=20)
        
        
        # Finished setting up GUI - now issue any message
        if (message[0] != ""):
            messagebox.showinfo(message[0], message[1])



#Thread for communicating with neopixels
#Simple one-way communication with thread using globals
#checks variables or updates (cmdMessage, cmdColours)
def runPixels(LEDs, command):
    while command.getCommand() != "STOP":
        # run appropriate script
        method = getattr (LEDs, command.getCommand())
        method() 
        



def main():


    # load settings during startup    
    config = configparser.ConfigParser()
    # load from configfile
    try :
        config.read(configfile)
        # Test that config entries loaded by looking at first entry
        numLEDs = int(config['LEDs']['ledcount'])
    except (configparser.Error, KeyError) :
        # Can't display warning at this stage so save message for when gui loaded
        global message
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
    
    thread=threading.Thread(target=runPixels, args=(LEDs, command))
    thread.start()
    
    root = Tk()
    root.geometry("800x600+100+100")
    app = App(root, command, config)
    root.mainloop()
    
    
if __name__ == "__main__":

    main()

