# Hardware abstraction class for lightseq to control neopixels

class Hardware_NeoPixel():

    def __init__(self, settings):
        self.settings = settings
        
        self.strip = Dynamic_NeoPixel(self.settings['ledcount'], self.settings['gpiopin'], self.settings['ledfreq'], self.settings['leddma'], self.settings['ledinvert'], self.settings['ledmaxbrightness'])
        