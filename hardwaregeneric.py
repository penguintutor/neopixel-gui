# Generic hardware abstraction for lightseq to convert to neopixel / other hardware
# This is a dummy version that doesn't actually update any hardware

class HardwareGeneric():
    
    def __init__(self, settings):
        self.settings = settings
        
    # Change settings
    def updSettings(self,settings):
        pass
    
    
    def setPixel (self, i, colour):
        pass
    
    
    # Update sequence - if required
    def show(self):
        pass
    
    
    def begin(self):
        pass
    
    
    def setPixelColor (self, i, colour):
        pass