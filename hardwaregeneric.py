# Generic hardware abstraction for lightseq to convert to neopixel / other hardware
# This is a dummy version that doesn't actually update any hardware
# Useful for testing on a computer that does not support the neopixel library

class HardwareGeneric():
    
    def __init__(self, settings):
        self.settings = settings
        
    # Change settings
    def updSettings(self,settings):
        pass
    
    
    def setPixel (self, i, colour):
        #print ("Pixel "+str(i)+"set to : "+str(colour))
        pass
    
    
    # Update sequence - if required
    def show(self):
        pass
    
    
    def begin(self):
        pass
    
    
    def setPixelColor (self, i, colour):
        #print ("Pixel "+str(i)+"set to colour :"+str(colour))
        pass
    
    def numPixels (self):
        return self.settings['ledcount']