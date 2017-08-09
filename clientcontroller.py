# Moves the client communication away from the GUI.
# Instead of using direct communication call to this, which 
# converts into a network request
## Note there is a greater risk of commands failing if over a network
## or server is down, so error messages are more likely


import json
import urllib.request
import ssl
from urllib.error import *


class ClientController():
    
    def __init__(self, hostname, port, sslenabled, username, password, allowunverified=False):
        if (sslenabled == False):
            self.urlpost = 'http://'+hostname+":"+str(port)+'/neopixel'
        else:
            self.urlpost = 'https://'+hostname+":"+str(port)+'/neopixel'
        self.config = {}
        self.sslenabled = sslenabled
        self.username = username
        self.password = password
        self.allowunverified = allowunverified
        # if unverified allowed then create context
        if (self.allowunverified == True):
            self.ctx = ssl.create_default_context()
            self.ctx.check_hostname = False
            self.ctx.verify_mode = ssl.CERT_NONE
        
    def chgServer (self, hostname, port, sslenabled, username, password):
        if (self.sslenabled == False):
            self.urlpost = 'http://'+hostname+":"+str(port)+'/neopixel'
        else:
            self.urlpost = 'https://'+hostname+":"+str(port)+'/neopixel'
        self.username = username
        self.password = password

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
        # If username and/or password then add to parmsdict
        if (self.username != '') :
            parmsdict['username'] = self.username
        if (self.password != '') :
            parmsdict ['password'] = self.password
        params = json.dumps(parmsdict).encode('utf8')
#        print ("Post: "+self.urlpost)
#        print ("Trying: "+str(params))
        try:
            req = urllib.request.Request(self.urlpost, data=params, headers={'content-type': 'application/json'})
            if (self.sslenabled == True and self.allowunverified == True):
                response = urllib.request.urlopen(req, context=self.ctx)
            else:
                response = urllib.request.urlopen(req)
            reply = response.read().decode('utf8')
            replydata = json.loads(reply)
        except (OSError, HTTPError) as e:
            print ("Error "+str(e))
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
    
    
    