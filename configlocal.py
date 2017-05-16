from tkinter import *
from tkinter import messagebox
import ledsettings
import sys

# This pop-up window is used for the hardware configuration of the NeoPixels

# All pwm GPIO ports on Raspberry Pi (used as additional check, but not enforced)
# Note these are strings as that's how the are edited / stored
GPIOpwm = ['12', '13', '18', '19', '40', '41', '45']


class ConfigLocal():
    
    # Track whether config window open to stop duplicate windows
    configWindowOpen = False

    def __init__ (self, config, configfile, defaults, settings, command):
        #self.config = config
        self.configfile = configfile
        self.defaults = defaults
        self.settings = settings
        # ledseq is the instance of the NeoPixelSeq class provide here to allow  updates without restarting
        self.command = command
        self.config={}


    # called from window manager handler or from Cancel button
    def closeConfig(self):
        self.configWindowOpen = False
        self.configTop.destroy()
        
    def restoreDefaults(self): 
        self.numLEDString.set(self.defaults['ledcount'])
        self.numGPIOString.set(self.defaults['gpiopin'])
        self.maxBrightnessString.set(self.defaults['ledmaxbrightness'])
        if (bool(self.defaults['ledinvert'])):
            self.invertVar.set(1)
        else :
            self.invertVar.set(0)



    def saveConfig(self):
        # Check for valid entries - if not restore previous value and give error message
        if (self._validateNumber(self.numLEDString.get(), 1, 1000000, "Number of LEDs ")):
            self.config['LEDs']['ledcount'] = self.numLEDString.get()
        else :
            # Restore previous value
            self.numLEDString.set(self.config['LEDs']['ledcount'])
            return        
        # Could limit to the actual PWM pins on the current Raspberry Pi, but this allows for future versions with other pins (up to GPIO 128)
        if (self._validateNumber(self.numGPIOString.get(), 0, 128, "GPIO pin number ")):
            # Here's the additional "Info" check
            # If a valid pwm pin in the BCM2835 is chosen we assume user knows what they are doing - if not we suggest they may not be using a valid port
            pinvalue = self.numGPIOString.get()
            if (pinvalue not in GPIOpwm):
                if (messagebox.askyesno("Info", "Info:\nGPIO pin is not known to be a valid pwm port.\nIf unsure use port 18.\nSee User Guide for more details.\nWould you still like to use port "+pinvalue+"?", parent=self.configTop)):
                    self.config['LEDs']['gpiopin'] = pinvalue
                else:
                    self.numGPIOString.set(self.config['LEDs']['gpiopin'])
                    return
            else:
                self.config['LEDs']['gpiopin'] = pinvalue
        else :
            # Restore previous value
            self.numGPIOString.set(self.config['LEDs']['gpiopin'])
            return  
        
        if (self._validateNumber(self.maxBrightnessString.get(), 0, 255, "Brightness ")):
            self.config['LEDs']['ledmaxbrightness'] = self.maxBrightnessString.get()
        else :
            # Restore previous value
            self.maxBrightnessString.set(self.config['LEDs']['ledmaxbrightness'])
            return    
        
        if (self.invertVar.get() == 1):
            self.config['LEDs']['ledinvert'] = "True"
        else:
            self.config['LEDs']['ledinvert'] = "False"
            
        
        # save config
        response = self.command.setConfigNeopixels(self.config['LEDs'])
        if (response['reply'] == 'success'):
            self.closeConfig()
            messagebox.showinfo("Info", "Configuration updated")
        else : 
            self.closeConfig()
            # It's not enough to just add response['error'] as need to iterate
            # through all the values to check individually 
            # if there is an 'error' then display it (comms error), but the 
            # individual errors should have been caught by checking within
            # this prior to attempting to send to the server
            if ('error' in response) :
                messagebox.showinfo("Error", "Error updating configuration" + response['error'])
            else :
                messagebox.showinfo("Error", "Error updating configuration")
            
        
    def windowClient (self):
        if (self.configWindowOpen) :
            return
            
        # load config from server
        self.config['LEDs'] = self.command.getConfigNeopixels()
        #print (self.config)
        # Check we have a valid response
        if (self.config['LEDs']['reply'] != "success") :
            messagebox.showinfo("Error", "Unable to retrieve config from server\nPlease check network configuration");
            return
            
        self.configWindowOpen = True
        self.configTop = Toplevel()
        self.configTop.wm_title("Local Configuration")
        self.configTop.wm_geometry("450x300")
        # set handler for close window using WM X
        self.configTop.wm_protocol('WM_DELETE_WINDOW',  self.closeConfig)

        
        self.numLEDString = StringVar()
        self.numLEDString.set(int(self.config['LEDs']['ledcount']))
        self.numGPIOString = StringVar()
        self.numGPIOString.set(int(self.config['LEDs']['gpiopin']))
        self.maxBrightnessString = StringVar()
        self.maxBrightnessString.set(int(self.config['LEDs']['ledmaxbrightness']))
        self.invertVar = IntVar()
        if (self.config['LEDs']['ledinvert'] == True):
            self.invertVar.set(1)
        else:
            self.invertVar.set(0)
        
        configTitleLabel = Label(self.configTop,
                text="NeoPixel - Configuration",
                foreground="blue", font="Verdana 16 bold").grid(columnspan=3, sticky=W, pady=(4, 15), padx=5)
                
        numLEDLabel = Label(self.configTop,
                    font="Verdana 14",
                    text="Number LEDs").grid(row=1, column=1, columnspan=2, sticky=W, padx=(15,2))
                    
        numLEDEntry = Entry(self.configTop,
                    font="Verdana 14",
                    width=5,
                    textvariable=self.numLEDString).grid(row=1, column=3, sticky=W)
                    
        numGPIOLabel = Label(self.configTop,
                    font="Verdana 14",
                    text="GPIO pin number").grid(row=2, column=1, columnspan=2, sticky=W, padx=(15,2))
                    
        numGPIOEntry = Entry(self.configTop,
                    font="Verdana 14",
                    width=5,
                    textvariable=self.numGPIOString).grid(row=2, column=3, sticky=W)

        maxBrightnessLabel = Label(self.configTop,
                    font="Verdana 14",
                    text="LED brightness").grid(row=3, column=1, columnspan=2, sticky=W, padx=(15,2))
                    
        maxBrightnessEntry = Entry(self.configTop,
                    font="Verdana 14",
                    width=5,
                    textvariable=self.maxBrightnessString).grid(row=3, column=3, sticky=W)

        invertLabel = Label(self.configTop,
                    font="Verdana 14",
                    text="Invert Output").grid(row=4, column=1, columnspan=2, sticky=W, padx=(15,2))


        invertCheckBox = Checkbutton(self.configTop,
                    font="Verdana 14",
                    variable=self.invertVar).grid(row=4, column=3, sticky=W)



        buttonRow = 6

        restoreButton = Button(self.configTop, 
                    text="Restore\ndefaults",
                    font="Verdana 9",
                    width = 8,
                    height = 2,
                    command=self.restoreDefaults)
        restoreButton.grid(row=buttonRow, column=1, pady=(40, 10), padx=10)


        cancelButton = Button(self.configTop, 
                    text="Cancel",
                    font="Verdana 14",
                    width = 8,
                    height = 1,
                    command=self.closeConfig)
        cancelButton.grid(row=buttonRow, column=2, pady=(40, 10), padx=10)
    
    
        saveButton = Button(self.configTop, 
                    text="Save",
                    font="Verdana 14",
                    width = 8,
                    height = 1,
                    command=self.saveConfig)
        saveButton.grid(row=buttonRow, column=3, pady=(40, 10), padx=10)
        
    
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
        
        

