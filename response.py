#Utility class for server response

# reply holds overall status
# if all aspects that are set are successful then set successful
# if partial then set to warning
# if all fail (or no instruction) then set to error

# Each individual section then gives a status of "success" or an error message

class Response():
    response = dict()
    
    def __init__(self, debug):
        self.debug = debug
        self.response['reply'] = "none"
        
    def addStatus (self, status, field, message):
        if (status == "success"):
            if (self.response['reply']=="none") :
                self.response['reply'] = 'success'
            elif (self.response['reply']=="error") :
                self.response['reply'] = 'warning'
            # Otherwise we already have either warning or success so no need to change
            if (self.debug >= 5):
                print ("Info: success for "+ field +" "+message)
        elif (status == "error"):
            if (self.response['reply'] == 'success'):
                self.response['reply'] = 'warning'
            # warning we leave unchanged (so anything that's not warning is error)
            elif (self.response['reply'] != 'warning'):
                self.response['reply'] = 'error'
            if (self.debug >= 3):
                print ("Error: error for "+ field +" "+message)
        # if status is warning then set to warning regardless
        elif (status == "warning"):
            self.response['reply']= 'warning'
            if (self.debug >= 5):
                print ("Warning: warning for "+ field +" "+message)
                
            
            
    # getStatus if none then returns "error" (ie. no valid command issued)
    def getStatus (self):
        if (self.response['reply'] == 'none'):
            # make copy so we don't change from none (in case call again)
            newresponse = self.response
            newresponse['reply'] = 'error'
            return newresponse
        return self.response