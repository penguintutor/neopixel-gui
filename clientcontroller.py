# Moves the client communication away from the GUI.
# Instead of using direct communication call to this, which 
# converts into a network request
## Note that there is now a greater risk of commands failing, so
## error messages are more likely


import json
import urllib.request
from urllib.error import *


class ClientController():
    
    def __init__(self, hostname, port):
        self.urlpost = 'http://'+hostname+":"+str(port)+'/neopixel'  
    

    def setSequence(self, sequence):
        parmsdict = {"request":"command", "sequence":sequence}
        response = self.fetchPage(parmsdict)
        return response
        
    def getConfig(self):
        parmsdict = {"request":"query", "type":"config"}
        response = self.fetchPage(parmsdict)
        return response
        
    def fetchPage(self, parmsdict):
        params = json.dumps(parmsdict).encode('utf8')
        try:
            req = urllib.request.Request(self.urlpost, data=params, headers={'content-type': 'application/json'})
            response = urllib.request.urlopen(req)
            reply = response.read().decode('utf8')
            replydata = json.loads(reply)
        except (HTTPError, URLError) as error:
            return "Error communicating with server"
        if (replydata['reply'] == 'success'):
            return 'success'
        return replydata['error']
       
    #Todo
    def setColours(self, colours):
        pass
    
    def setDelay(self, delay):
        pass
    
    
    