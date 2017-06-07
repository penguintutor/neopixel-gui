# Moves the client communication away from the GUI.
# Instead of using direct communication call to this, which 
# converts into a network request
## Note that there is now a greater risk of commands failing, so
## error messages are more likely


import json
import urllib.request
from urllib.error import *


class ClientController():
    
    def __init__(self, hostname, port, ssl):
        if (ssl == False):
            self.urlpost = 'http://'+hostname+":"+str(port)+'/neopixel'
        else:
            self.urlpost = 'https://'+hostname+":"+str(port)+'/neopixel'
        self.config = {}

    def chgServer (self, hostname, port):
        self.urlpost = 'http://'+hostname+":"+str(port)+'/neopixel'

    def setConfigNeopixels(self, config):
        config['request']='update'
        config['type']='config'
        config['value']='neopixels'
        response = self.fetchPage(config)
        return response

    def setSequence(self, sequence):
        parmsdict = {"request":"command", "sequence":sequence}
        response = self.fetchPage(parmsdict)
        return response
        
    def getConfigNeopixels(self):
        parmsdict = {"request":"query", "type":"config", "value":"neopixels"}
        response = self.fetchPage(parmsdict)
        return response
        
    #Todo
    def getConfigServer(self):
        pass
        
    def fetchPage(self, parmsdict):
        params = json.dumps(parmsdict).encode('utf8')
        try:
            req = urllib.request.Request(self.urlpost, data=params, headers={'content-type': 'application/json'})
            response = urllib.request.urlopen(req)
            reply = response.read().decode('utf8')
            replydata = json.loads(reply)
        except (OSError, HTTPError) as e:
            replydata = {"reply":"fail","error":"Error communicating with server"}
        return replydata
       
    def setColours(self, colours):
        parmsdict = {'request':'command','colours':colours}
        response = self.fetchPage(parmsdict)
        return response
    
    def setDelay(self, delay):
        parmsdict = {'request':'command','delay':delay}
        response = self.fetchPage(parmsdict)
        return response
    
    
    