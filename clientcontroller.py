# Moves the client communication away from the GUI.
# Instead of using direct communication call to this, which 
# converts into a network request
## Note that there is now a greater risk of commands failing, so
## error messages are more likely


import json
import urllib.request


class ClientController():
    
    def __init__(self, hostname, port):
        self.urlpost = 'http://'+hostname+":"+str(port)+'/neopixel'  
    

    def setSequence(self, sequence):
        parmsdict = {"request":"command", "sequence":sequence}
        data = self.fetchPage(parmsdict)
        
    def getConfig(self):
        parmsdict = {"request":"query", "type":"config"}
        data = self.fetchPage(parmsdict)
        
        
    def fetchPage(self, parmsdict):
        params = json.dumps(parmsdict).encode('utf8')
        req = urllib.request.Request(self.urlpost, data=params, headers={'content-type': 'application/json'})
        response = urllib.request.urlopen(req)
        replydata = response.read().decode('utf8')
        return replydata
       
    #Todo
    def setColours(self, colours):
        pass
    
    def setDelay(self, delay):
        pass
    
    
    