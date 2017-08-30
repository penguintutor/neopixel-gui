from neopixelutils import *

# Class used to hold commands to share with thread




class WebSrvCmds():

    def __init__(self, queue):
        self.queue = queue
        self.cmdMessage="allOff"
        self.cmdColours=[Color(255,255,255)]
        self.backColour=0x000000   # Used by some methods as colour for not set pixels
    
        self.cmdOptions={
            "delay":60,         # delay in ms (short delay eg. per each led move
            "wait": 120,        # longer delay eg colour changes
            "intensity":100     # intensity as % of colour
        }

        # Change to True when there is a new command issued
        # This allows the program to breakout during a slow command, otherwise waits until the end of the cycle
        newCmdStatus = False;
    


    def setCommand(self, command):
        self.cmdMessage = command
        self.queue.put("setCommand,"+command)
        
    def getCommand(self):
        return self.cmdMessage
        
    def setColours(self, colours):
        self.cmdColours = colours;
        self.queue.put("cmdColours,"+colours)
    
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
        self.queue.put("newCmdStatus,"+str(status))
        
    def setDelay (self, delay):
        self.cmdOptions['delay'] = delay
        self.cmdOptions['wait'] = delay * 2
        self.queue.put("setDelay,"+delay)



if __name__ == "__main__":
    print ("This file is not executable - please run neopixel-server.py and appropriate client")


