# Class to provide settings from configwriter config
# Used for the client

class LocalSettings():
    
    def __init__(self, config):
        self.config = config
        # If no username in the configfile (older version) set default
        if not "username" in self.config['Server']:
            self.config['Server']['username'] = ''
            self.config['Server']['password'] = ''
        # Same for allowunverified
        if not "allowunverified" in self.config['Server']:
            self.config['Server']['allowunverified'] = 'False'
        
    def allSettings(self):
        settings = {
        'hostname': self.config['Server']['hostname'],
        'port': int(self.config['Server']['port']),
        'ssl' : self.config['Server'].getboolean('ssl'),
        'username': int(self.config['Server']['username']),
        'password': int(self.config['Server']['password']),
        'allowunverified' : self.config['Server'].getboolean('allowunverified')
        }
        return settings
        
    def hostname(self):
        return self.config['Server']['hostname']

    def port(self):
        return self.config['Server']['port']
        
    def ssl(self):
        return self.config['Server'].getboolean('ssl')
        
    def allowunverified(self):
        return self.config['Server'].getboolean('allowunverified')
        
    def username(self):
        return self.config['Server']['username']
        
    def password(self):
        return self.config['Server']['password']