# Class to provide settings from configwriter config

class LEDSettings():
    
    def __init__(self, config):
        self.config = config
        
    def allSettings(self):
        settings = {
        'ledcount': int(self.config['LEDs']['ledcount']),
        'gpiopin': int(self.config['LEDs']['gpiopin']),
        'ledfreq': int(self.config['LEDs']['ledfreq']),
        'leddma' : int(self.config['LEDs']['leddma']),
        'ledmaxbrightness': int(self.config['LEDs']['ledmaxbrightness']),
        'ledinvert': self.config['LEDs'].getboolean('ledinvert'),
        'rgb': self.config['LEDs'].getboolean('rgb')
        }
        return settings
