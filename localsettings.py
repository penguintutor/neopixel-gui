# Class to provide settings from configwriter config

class LocalSettings():
    
    def __init__(self, config):
        self.config = config
        
    def allSettings(self):
        settings = {
        'hostname': self.config['Server']['hostname'],
        'port': int(self.config['Server']['port']),
        'ssl' : self.config['Server'].getboolean('ssl'),
        'username': int(self.config['Server']['username']),
        'password': int(self.config['Server']['password'])
        }
        return settings
        
    def hostname(self):
        return self.config['Server']['hostname']

    def port(self):
        return self.config['Server']['port']
        
    def ssl(self):
        return self.config['Server'].getboolean('ssl')
        
    def username(self):
        return self.config['Server']['username']
        
    def password(self):
        return self.config['Server']['password']