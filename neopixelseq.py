import time
import tkinter as tk
from neopixel import *
from dynneopixel import *

# Sequence method should change some LEDs and then return
# If that sequence is still running then the method should resume
# from where it left off. In the case of short sequences then the entire 
# sequence can be run in a single run of the method.

# All sequences must include a sleep delay, normally this is
# time.sleep(self.command.getOptions()['delay']/1000)

# Any sequences that are long lasting need to check self.command.getCmdStatus()
# preiodically and if true return 
# this is not critical, but will cause updates to be unresponsive
# If used set it to False at the start of the method

# The chaserStartPos variable can be used by sequences to provide a means
# to return to the same point after checking if a configuration change has 
# has been made

# Where a sequence is repeated over a set number of LEDs other than the number
# of colours selected by the user then the preferred value is 4
# The magic number of 4 is used as it is a factor of all the neopixels rings 
# (12, 16, 24) and it is an easy number to integrate within sequences.


class NeoPixelSeq():

    def __init__(self, settings, command):
        
        # class variables to maintain between function calls
        self.chaserStartPos = 0  # can use across all chasers as only required when we don't restart chaser

        self.settings = settings
        self.command = command
        self.numPixels = settings['ledcount']
        self.rgb = settings['rgb']
        self.strip = Dynamic_NeoPixel(self.settings['ledcount'], self.settings['gpiopin'], self.settings['ledfreq'], self.settings['leddma'], self.settings['ledinvert'], self.settings['ledmaxbrightness'])
        
        # Intialize the library (must be called once before other functions).
        self.strip.begin()


    # Wrapper around strip.setPixelColor
    # This will check self.rgb to determine if the colour needs to be changed first
    def setPixel (self, i, colour):
        # if not then need to change colour from RGB to GRB
        if (self.rgb == False) :
            blueValue = (colour & 0xFF)
            greenValue = (colour >> 8) & 0xFF
            redValue = (colour >> 16) & 0xFF
            colour = Color(greenValue, redValue, blueValue)
        self.strip.setPixelColor(i, colour)
        

    # Update settings by replacing existing led strip
    def updSettings (self, settings):
        self.settings = settings
        self.rgb = settings['rgb']
        self.numPixels = settings['ledcount']
        self.strip.updSettings(self.settings)


    # All on with a single colour (first colour is used)
    # Full intensity
    def allOnSingleColour(self):
        colours = self.command.getColours()
        colour = colours[0]
        for i in range(self.numPixels):
            self.setPixel(i, colour)
        self.strip.show()
        time.sleep(self.command.getOptions()['delay']/1000)


    # All on with multiple colours (each colour used in cycle)
    # Full intensity
    def allOn(self):
        colours = self.command.getColours()
        currentColour = 0
        for i in range(self.numPixels):
            self.setPixel(i, colours[currentColour])
            currentColour += 1
            if (currentColour >= len(colours)):
                currentColour = 0
        self.strip.show()
        time.sleep(self.command.getOptions()['delay']/1000)

    def allOff(self):
        for i in range(self.numPixels):
            self.setPixel(i, Color(0,0,0))
        self.strip.show()
        time.sleep(self.command.getOptions()['delay']/1000)
    
    # chase colours across a background
    # uses getBackColour - normally black
    def chaserBackground(self):
        options = self.command.getOptions()
        colours = self.command.getColours()
        backColour = self.command.getBackColour()

        # number of times of the num colours the group occupies
        groupsize = 4
        colourPixelRange = len(colours) * groupsize

        # Check we are within range (ie. number of leds selected reduced)
        if (self.chaserStartPos >= colourPixelRange):
                self.chaserStartPos = 0
        iterations = 4

        for iter in range(iterations):
            #colourNum = colourNumStart
            
            # Set all pixels to the background - then we update those not
            for resetPixel in range(self.strip.numPixels()):
                self.setPixel (resetPixel, backColour)
            
            for i in range(0, self.strip.numPixels()+1, colourPixelRange):
                for j in range(0, len(colours)):
                    if (i + j + self.chaserStartPos < self.strip.numPixels()) :
                        self.setPixel (i + j + self.chaserStartPos, colours[j])
            
            self.strip.show()
            time.sleep(options['delay']/1000.0)
            
            self.chaserStartPos += 1
            if (self.chaserStartPos >= colourPixelRange):
                self.chaserStartPos = 0
   
   
    # colors is an array of colors to display
    # simple sequencer / shift
    def chaser(self):
        options = self.command.getOptions()
        colours = self.command.getColours()
        # colourNum tracks which colour in array we are showing
        colourNum = 0
        # If less than two colours then add a second for off to create a chase
        if (len(colours)<2):
            colours.append(0x000000)
        # which colour to start on defined in constructor so we maintain across calls to this method
        #self.chaserStartPos = 0
        # check that chaser number is not too large (ie if we reduce number of colours)
        if (self.chaserStartPos >= len(colours)) :
            self.chaserStartPos = 0
        iterations = 5
        for j in range(iterations):
            colourNum = self.chaserStartPos
            
            for i in range(self.strip.numPixels()):
                self.setPixel (i, colours[colourNum])
                colourNum = colourNum +1
                if (colourNum >= len(colours)):
                    colourNum = 0
            self.strip.show()
            time.sleep(options['wait']/1000.0)
            
            self.chaserStartPos = self.chaserStartPos + 1
            if (self.chaserStartPos >= len(colours)):
                self.chaserStartPos = 0



    # Chaser that turns pixels on and off 4 at a time
    def chaserSingleColour(self):
        options = self.command.getOptions()
        colours = self.command.getColours()
        colour = colours[0]
        
        for q in range(4):
            for i in range(0, self.strip.numPixels(), 4):
               self.setPixel(i+q, colour)
            self.strip.show()
            time.sleep(options['delay']/1000.0)
            for i in range(0, self.strip.numPixels(), 4):
                self.setPixel(i+q, 0)



    # Define functions which animate LEDs in various ways.
    def colourWipe(self):
        self.command.setCmdStatus(False)
        options = self.command.getOptions()
        colours = self.command.getColours()
        colourNum = 0
        for i in range(self.strip.numPixels()):
            self.setPixel(i, colours[colourNum])
            self.strip.show()
            colourNum += 1
            if (colourNum >= len(colours)) :
                colourNum = 0
            # Exit if new command
            if (self.command.getCmdStatus()):
                return
            time.sleep(self.command.getOptions()['delay']/1000.0)



    def wheel(self, pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos < 85:
            return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Color(0, pos * 3, 255 - pos * 3)



    def rainbow(self):
        """Draw rainbow that fades across all pixels at once."""
        self.command.setCmdStatus(False)
        for j in range(256):
            for i in range(self.strip.numPixels()):
                self.setPixel(i, self.wheel((i+j) & 255))
            self.strip.show()
            # Exit if new command
            if (self.command.getCmdStatus()):
                return
            time.sleep(self.command.getOptions()['delay']/1000.0)



    def rainbowCycle(self):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        for j in range(256):
            for i in range(self.strip.numPixels()):
                    self.setPixel(i, self.wheel((int)((i * 256 / self.strip.numPixels())+ j) & 255))
            self.strip.show()
            time.sleep(self.command.getOptions()['delay']/10000.0)



    def theatreChaseRainbow(self):
        self.command.setCmdStatus(False)
        """Rainbow movie theater light style chaser animation."""
        for j in range(256):
            for q in range(3):
                for i in range(0, self.strip.numPixels(), 3):
                    self.setPixel(i+q, self.wheel((i+j) % 255))
                self.strip.show()
                time.sleep(self.command.getOptions()['delay']/1000.0)
                for i in range(0, self.strip.numPixels(), 3):
                    self.setPixel(i+q, 0)
            # Exit if new command
            if (self.command.getCmdStatus()):
                return


    def inOut(self):
        self.outToIn()
        if (self.command.getCmdStatus()):
            return
        self.inToOutOff()
        if (self.command.getCmdStatus()):
            return

    def outIn(self):
        self.inToOut()
        if (self.command.getCmdStatus()):
            return
        self.outToInOff()
        if (self.command.getCmdStatus()):
            return
        
        
        
    # outToIn -
    def outToIn(self):
        self.command.setCmdStatus(False)
        colour = self.command.getSingleColour()
        """Wipe color across starting at both ends"""
        for i in range((int)(self.strip.numPixels()/2)):
            self.setPixel(i, colour)
            self.setPixel(self.strip.numPixels() - i, colour);
            self.strip.show()
            if (self.command.getCmdStatus()):
                return
            time.sleep(self.command.getOptions()['delay']/1000.0)



    # inToOut -
    def inToOut(self):
        """Wipe color across starting at both ends"""
        self.command.setCmdStatus(False)
        colour = self.command.getSingleColour()
        for i in range((int)(self.strip.numPixels()/2)):
            self.setPixel((int)(self.strip.numPixels()/2) - i, colour)
            self.setPixel((int)(self.strip.numPixels()/2) + i, colour);
            self.strip.show()
            if (self.command.getCmdStatus()):
                return
            time.sleep(self.command.getOptions()['delay']/1000.0)


    def outToInOff(self):
        colour = 0x000000
        self.command.setCmdStatus(False)
        """Wipe color across starting at both ends"""
        for i in range((int)(self.strip.numPixels()/2)):
            self.setPixel(i, colour)
            self.setPixel(self.strip.numPixels() - i, colour);
            self.strip.show()
            if (self.command.getCmdStatus()):
                return
            time.sleep(self.command.getOptions()['delay']/1000.0)



    def inToOutOff(self):
        """Turn off starting at both ends"""
        colour = 0x000000
        self.command.setCmdStatus(False)
        for i in range((int)(self.strip.numPixels()/2)):
            self.setPixel((int)(self.strip.numPixels()/2) - i, colour)
            self.setPixel((int)(self.strip.numPixels()/2) + i, colour);
            self.strip.show()
            if (self.command.getCmdStatus()):
                return
            time.sleep(self.command.getOptions()['delay']/1000.0)


    def twinkleChase(self):
        options = self.command.getOptions()
        colours = self.command.getColours()
        colour = colours[0]
        
        for q in range(4):
            for i in range(0, self.strip.numPixels(), 4):
               self.setPixel(i+q, 0)
            self.strip.show()
            time.sleep(options['delay']/1000.0)
            for i in range(0, self.strip.numPixels(), 4):
                self.setPixel(i+q, colour)


    # Follow me
    # uses two colours (or use white)
    # uses getBackColour - normally black
    def chaseMe(self):
        options = self.command.getOptions()
        colours = self.command.getColours()
        backColour = self.command.getBackColour()
        
        # If we only have one colour then add white
        if (len(colours) < 2) :
            colours.append(0xffffff)

        # number of times of the num colours the group occupies
        groupsize = 8
        colourPixelRange = 16

        # Check we are within range (ie. number of leds selected reduced)
        if (self.chaserStartPos >= colourPixelRange):
                self.chaserStartPos = 0
        iterations = 4

        for iter in range(iterations):
            # Set all pixels to the background - then we update those not
            for resetPixel in range(self.strip.numPixels()):
                self.setPixel (resetPixel, backColour)
            
            for i in range(0, self.strip.numPixels(), colourPixelRange):
                if (self.chaserStartPos + i < self.strip.numPixels()) :
                    self.setPixel (self.chaserStartPos + i, colours[0])
                    if (self.chaserStartPos + i + 4 < self.strip.numPixels()) :
                        self.setPixel (self.chaserStartPos + i + 4, colours[1])
            self.strip.show()
            time.sleep(options['delay']/1000.0)
            
            self.chaserStartPos += 1
            if (self.chaserStartPos >= colourPixelRange):
                self.chaserStartPos = 0


		

if __name__ == "__main__":
    print ("This file is not executable - please run the appropriate code\nOr import this into your own code")


