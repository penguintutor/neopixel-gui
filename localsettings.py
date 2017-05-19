# Class to provide settings from configwriter config

class LocalSettings():
    
    def __init__(self, config):
        self.config = config
        
    def allSettings(self):
        settings = {
        'hostname': self.config['Server']['hostname'],
        'port': int(self.config['Server']['port']),
        }
        return settings
