from neopixel import *

# Class used to hold commands to share with thread

class NeoPixelCmds():
    
    cmdMessage="allOff"
    cmdColours=[Color(255,255,255)]
    backColour=0x000000   # Used by some methods as colour for not set pixels
    
    cmdOptions={
        "delay":60,         # delay in ms (short delay eg. per each led move
        "wait": 120,        # longer delay eg colour changes
        "intensity":100     # intensity as % of colour
    }

    # Change to True when there is a new command allows to breakout during a slow command.
    newCmdStatus = False;

    def setCommand(self, command):
        self.cmdMessage = command
        
    def getCommand(self):
        return self.cmdMessage
        
    def setColours(self, colours):
        self.cmdColours = colours;
    
    # Returns array of selected colours - or white if none selected
    def getColours(self):
        if (len(self.cmdColours)<1):
            return [0xffffff]
        else:
            return self.cmdColours
            
    # return first selected colour - or white if none selected
    def getSingleColour(self):
        if (len(self.cmdColours)<1):
            return 0xffffff
        else:
            return self.cmdColours[0]
        
    def getOptions(self):
        return self.cmdOptions
        
        
    def getBackColour(self):
        return self.backColour
        
    def getCmdStatus(self):
        return self.newCmdStatus
    
    def setCmdStatus(self, status):
        self.newCmdStatus = status
        
    def setDelay (self, delay):
        self.cmdOptions['delay'] = delay
        self.cmdOptions['wait'] = delay * 2



if __name__ == "__main__":
    print ("This file is not executable - please run rpnpgp.py\nOr import this into your own code")


