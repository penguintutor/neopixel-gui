#!/usr/bin/env python3
	
import random
import tkinter
import threading
import queue
from neopixelcmds import *
from tkinter import *
from neopixelseq import *



# Settings for neopixels
# load from config file in future

settings = {
    'ledcount': 150,
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


class App(Frame):


    def ApplyChange(self):
        # update command object to be passed to the 
        cmd, text = sequenceOptions[self.sequence.get()]
        self.command.setCommand(cmd)
        coloursTicked = []
        for i in range (len(self.colourSelected)):
            if (self.colourSelected[i].get() == 1) :
                text, value = colourChoice[i]
                coloursTicked.append(value)
        self.command.setColours(coloursTicked)
        # Set status to updated so they can exit during command
        self.command.setCmdStatus(True)
            
        

    def __del__(self):
        global cmdMessage
        self.command.setCommand("STOP")
    
    def __init__(self, parent, command):
        Frame.__init__(self, parent)
        self.command = command
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

        numLEDLabel = Label(optionFrame,
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




#Thread for communicating with neopixels
#Simple one-way communication with thread using globals
#checks variables or updates (cmdMessage, cmdColours)
def runPixels(LEDs, command):
    while command.getCommand() != "STOP":
        # run appropriate script
        method = getattr (LEDs, command.getCommand())
        method() 
        



def main():

    # TODO
    # load settings during startup

    command = NeoPixelCmds()
    LEDs = NeoPixelSeq(settings, command)
    
    
    thread=threading.Thread(target=runPixels, args=(LEDs, command))
    thread.start()
    
    root = Tk()
    root.geometry("800x600+100+100")
    app = App(root, command)
    root.mainloop()
    
    
if __name__ == "__main__":

    main()

