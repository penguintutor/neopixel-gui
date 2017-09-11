from tkinter import *
from tkinter import messagebox
import localsettings
import sys
import re

# This pop-up window is used for the client server configuration of the client

class ConfigLocal():
    
    # Track whether config window open to stop duplicate windows
    configWindowOpen = False

    def __init__ (self, config, configfile, settings, defaults, command):
        self.config = config
        self.configfile = configfile
        self.settings = settings
        self.defaults = defaults
        self.command = command              # Used to update current ClientController


    # called from window manager handler or from Cancel button
    def closeConfig(self):
        self.configWindowOpen = False
        self.configTop.destroy()
        
    def restoreDefaults(self): 
        
        if (bool(self.defaults['remoteserver'])):
            self.remoteVar.set(1)
        else :
            self.remoteVar.set(0)
        self.hostnameString.set(self.defaults['hostname'])
        self.portString.set(self.defaults['port'])
        if (bool(self.defaults['ssl'])):
            self.sslVar.set(1)
        else :
            self.sslVar.set(0)
        if (bool(self.defaults['allowunverified'])):
            self.unverifiedVar.set(1)
        else :
            self.unverifiedVar.set(0)
        self.usernameString.set(self.defaults['username'])
        self.passwordString.set(self.defaults['password'])
        

    def saveConfig(self):
        # Check for valid entries - if not restore previous value and give error message
        if (self.remoteVar.get() == 1):
            self.config['Server']['remoteserver'] = "True"
        else:
            self.config['Server']['remoteserver'] = "False"
        if (self._validateHostname(self.hostnameString.get(), "Hostname ")):
            self.config['Server']['hostname'] = self.hostnameString.get()
        else :
            # Restore previous value
            self.hostnameString.set(self.config['Server']['hostname'])
            return        
        if (self._validateNumber(self.portString.get(), 0, 65535, "Port number ")):
            self.config['Server']['port'] = self.portString.get()
        else :
            # Restore previous value
            self.portString.set(self.config['Server']['port'])
            return  
        if (self.sslVar.get() == 1):
            self.config['Server']['ssl'] = "True"
        else:
            self.config['Server']['ssl'] = "False"
        if (self.unverifiedVar.get() == 1):
            self.config['Server']['allowunverified'] = "True"
        else:
            self.config['Server']['allowunverified'] = "False"
        # username and password
        if (self._validateUsernamePassword(self.usernameString.get(), "Username ")):
            self.config['Server']['username'] = self.usernameString.get()
        else :
            # Restore previous value
            self.usernameString.set(self.config['Server']['username'])
            return  
        if (self._validateUsernamePassword(self.passwordString.get(), "Password ")):
            self.config['Server']['password'] = self.passwordString.get()
        else :
            # Restore previous value
            self.passwordString.set(self.config['Server']['password'])
            return  

        # Save config
        try:
            with open(self.configfile, 'w') as cfgfile:
                self.config.write(cfgfile)
                self.closeConfig()
                # Change server info dynamically
                self.config['Server'].getboolean('remoteserver'),
                self.command.chgServer (self.config['Server']['hostname'], self.config['Server']['port'], self.config['Server'].getboolean('ssl'), self.config['Server']['username'], self.config['Server']['password'], self.config['Server'].getboolean('allowunverified')) 
                messagebox.showinfo("Info", "Configuration saved.")
        except : 
            self.closeConfig()
            messagebox.showinfo("Error", "Error saving configuration file "+configfile)
            
        
    def windowClient (self):
        if (self.configWindowOpen) :
            return
                   
        self.configWindowOpen = True
        self.configTop = Toplevel()
        self.configTop.wm_title("Local Configuration")
        self.configTop.wm_geometry("450x300")
        # set handler for close window using WM X
        self.configTop.wm_protocol('WM_DELETE_WINDOW',  self.closeConfig)

        self.remoteVar = IntVar()
        if (self.config['Server']['remoteserver'] == 'True'):
            self.remoteVar.set(1)
        else:
            self.remoteVar.set(0)
        self.hostnameString = StringVar()
        self.hostnameString.set(self.config['Server']['hostname'])
        self.portString = StringVar()
        self.portString.set(int(self.config['Server']['port']))
        self.sslVar = IntVar()
        if (self.config['Server']['ssl'] == 'True'):
            self.sslVar.set(1)
        else:
            self.sslVar.set(0)
        self.unverifiedVar = IntVar()
        if (self.config['Server']['allowunverified'] == 'True'):
            self.unverifiedVar.set(1)
        else:
            self.unverifiedVar.set(0)
        self.usernameString = StringVar()
        self.usernameString.set(self.config['Server']['username'])
        self.passwordString = StringVar()
        self.passwordString.set(self.config['Server']['password'])


        configTitleLabel = Label(self.configTop,
                text="NeoPixel - Local Configuration",
                foreground="blue", font="Verdana 16 bold").grid(columnspan=4, sticky=W, pady=(4, 15), padx=5)
                
        remoteLabel = Label(self.configTop,
                    font="Verdana 14",
                    text="Remote server").grid(row=1, column=1, columnspan=1, sticky=W, padx=(15,2))


        remoteCheckBox = Checkbutton(self.configTop,
                    font="Verdana 14",
                    variable=self.remoteVar).grid(row=1, column=2, sticky=W)

        hostnameLabel = Label(self.configTop,
                    font="Verdana 14",
                    text="Hostname").grid(row=2, column=1, columnspan=1, sticky=W, padx=(15,2))


        hostnameEntry = Entry(self.configTop,
                    font="Verdana 14",
                    width=15,
                    textvariable=self.hostnameString).grid(row=2, column=2, columnspan=2, sticky=W)
                    
        portLabel = Label(self.configTop,
                    font="Verdana 14",
                    text="Port").grid(row=3, column=1, columnspan=1, sticky=W, padx=(15,2))
                    
        portEntry = Entry(self.configTop,
                    font="Verdana 14",
                    width=5,
                    textvariable=self.portString).grid(row=3, column=2, sticky=W)
                    
        sslLabel = Label(self.configTop,
                    font="Verdana 14",
                    text="SSL enable").grid(row=4, column=1, columnspan=1, sticky=W, padx=(15,2))


        sslCheckBox = Checkbutton(self.configTop,
                    font="Verdana 14",
                    variable=self.sslVar).grid(row=4, column=2, sticky=W)
                    
        unverifiedLabel = Label(self.configTop,
                    font="Verdana 14",
                    text="Allow unverified").grid(row=5, column=1, columnspan=1, sticky=W, padx=(15,2))

        unverifiedCheckBox = Checkbutton(self.configTop,
                    font="Verdana 14",
                    variable=self.unverifiedVar).grid(row=5, column=2, sticky=W)
                    
        usernameLabel = Label(self.configTop,
                    font="Verdana 14",
                    text="Username").grid(row=6, column=1, columnspan=1, sticky=W, padx=(15,2))
                    
        usernameEntry = Entry(self.configTop,
                    font="Verdana 14",
                    width=15,
                    textvariable=self.usernameString).grid(row=6, column=2, columnspan=2, sticky=W)
                    
        passwordLabel = Label(self.configTop,
                    font="Verdana 14",
                    text="Password").grid(row=7, column=1, columnspan=1, sticky=W, padx=(15,2))
                    
        passwordEntry = Entry(self.configTop,
                    font="Verdana 14",
                    width=15,
                    textvariable=self.passwordString).grid(row=7, column=2, columnspan=2, sticky=W)

        buttonRow = 8

        restoreButton = Button(self.configTop, 
                    text="Restore\ndefaults",
                    font="Verdana 9",
                    width = 8,
                    height = 2,
                    command=self.restoreDefaults)
        restoreButton.grid(row=buttonRow, column=1, pady=(40, 10), padx=5)


        cancelButton = Button(self.configTop, 
                    text="Cancel",
                    font="Verdana 14",
                    width = 8,
                    height = 1,
                    command=self.closeConfig)
        cancelButton.grid(row=buttonRow, column=2, pady=(40, 10), padx=5)
    
    
        saveButton = Button(self.configTop, 
                    text="Save",
                    font="Verdana 14",
                    width = 8,
                    height = 1,
                    command=self.saveConfig)
        saveButton.grid(row=buttonRow, column=3, pady=(40, 10), padx=5)
        
    
    # return true if a valid integer - otherwise false
    # error message is issued based on errormsg and whether it's greater than min / max
    # if no min / max required then set to suitably huge values
    # eg 1000000 is a huge number of LEDs to try and control using a single PWM channel
    def _validateNumber (self, string, min, max, errormsg):
        try:
            testval = int(string)
        except (TypeError, ValueError):
            messagebox.showinfo("Warning", errormsg + "is not a number.\nSee User Guide for more details.", parent=self.configTop)
            return False
        if (testval < min):
            messagebox.showinfo("Warning", errormsg + "is below the minimum value.\nSee User Guide for more details.", parent=self.configTop)
            return False
        if (testval > max):
            messagebox.showinfo("Warning", errormsg + "is above the maximum value.\nSee User Guide for more details.", parent=self.configTop)
            return False
        return True
        
    # username and password can only have \w (ie. letters, digits and _)
    def _validateUsernamePassword (self, string, errormsg):
        # uses * instead of + so allows empty string
        if (not re.match(r'^\w*$', string)):
            messagebox.showinfo("Warning", errormsg + "contains invalid characters.", parent=self.configTop)
            return False
        return True
        
        
    # Warning this is for user of a local hostname and has no checking
    # at the moment, provided as a stub if further checking required in 
    # future (eg. to pass hostname to server)
    def _validateHostname (self, string, errormsg):
        return True