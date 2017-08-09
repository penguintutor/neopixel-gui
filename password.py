from passlib.hash import pbkdf2_sha256
import configparser
import random
import string
import re

class Password():
        
    def __init__ (self, passwordfile):
        self.passwordfile = passwordfile
        self.pwconfig = configparser.ConfigParser()

        # Try to open password file - if not then create a new one with random password
        try :
            self.pwconfig.read(passwordfile)
            # check loaded successfully by looking for 'admin' user
            adminpw = self.pwconfig['admin']['password']
            newconfig = False
            #print ("Password check enabled " + adminpw)
            print ("Username and password required")
        except Exception as e:
            print ("Warning: No password file found\nCreating password file")
            newconfig = True
            
        # Save on first creation to save config being lost
        # newconfig used to determine if we need to save or not
        if (newconfig == True):
            # Create random password
            adminpw = randomPassword()
            self.addUser('admin', adminpw)
            print ("User admin created with password: "+adminpw)
            
            self.savePasswords()
            
        
    def savePasswords(self):
        try:
            with open(self.passwordfile, 'w') as pwcfgfile:
                self.pwconfig.write (pwcfgfile)
        except Exception as e:
            print ("Error saving password config")
            
    
    # Dynamically adds password, but doesn't save
    # Will clobber over existing user
    def addUser(self, username, password):
        hash = pbkdf2_sha256.encrypt(password, rounds=200000, salt_size=16)
        self.pwconfig.add_section(username)
        self.pwconfig.set(username, 'password', hash)
        
        
    # Checks password against saved hash
    def chkPassword(self, username, password):
        # First check for any characters not permitted (ie. not letter / digit)
        # + char means it won't match an empty string
        if (not re.match(r'^\w+$', username)) or (not re.match(r'^\w+$', password)):
            print ("Invalid characters in username / password")
            return False
        # Next check it's a valid username (it has an entry in the pwconfig)
        if (not self.pwconfig.has_section(username)):
            print ("Username "+username+" does not exist")
            return False
        #print ("Checking password for "+username)
        return pbkdf2_sha256.verify(password, self.pwconfig[username]['password'])
        
        
# Returns random string (lowercase, uppercase and digits) - 15 chars long
def randomPassword() :
    char_set = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(random.sample(char_set*15, 15))