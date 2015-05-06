from tkinter import *
from tkinter import messagebox
import ledsettings

class ConfigWindow():
    
    # Track whether config window open to stop duplicate windows
    configWindowOpen = False

    def __init__ (self, config, configfile, defaults, settings, ledseq):
        self.config = config
        self.configfile = configfile
        self.defaults = defaults
        self.settings = settings
        # ledseq is the instance of the NeoPixelSeq class provide here to allow  updates without restarting
        self.ledseq = ledseq


    # called from window manager handler or from Cancel button
    def closeConfig(self):
        self.configWindowOpen = False
        self.configTop.destroy()
        
    def restoreDefaults(self):
        # Todo 
        self.numLEDString.set(self.defaults['ledcount'])
        self.numGPIOString.set(self.defaults['gpiopin'])
        self.maxBrightnessString.set(self.defaults['ledmaxbrightness'])
        if (bool(self.defaults['ledinvert'])):
            self.invertVar.set(1)
        else :
            self.invertVar.set(0)



    def saveConfig(self):
        # Todo - add validation
        self.config['LEDs']['ledcount'] = self.numLEDString.get()
        self.config['LEDs']['gpiopin'] = self.numGPIOString.get()
        self.config['LEDs']['ledmaxbrightness'] = self.maxBrightnessString.get()
        if (self.invertVar.get() == 1):
            self.config['LEDs']['ledinvert'] = "True"
        else:
            self.config['LEDs']['ledinvert'] = "False"
            
        
        # pass updated config to the NeoPixelSeq class
        self.ledseq.updSettings(self.settings.allSettings())
        
        # save config
        try:
            with open(self.configfile, 'w') as cfgfile:
                self.config.write(cfgfile)
                self.closeConfig()
                messagebox.showinfo("Info", "Configuration saved")
        except : 
            self.closeConfig()
            messagebox.showinfo("Error", "Error saving configuration file "+configfile)
            
            
        
    def windowClient (self):
        if (self.configWindowOpen) :
            return
        self.configWindowOpen = True
        self.configTop = Toplevel()
        self.configTop.wm_title("RpNpGp - Configuration")
        self.configTop.wm_geometry("400x300")
        # set handler for close window using WM X
        self.configTop.wm_protocol('WM_DELETE_WINDOW',  self.closeConfig)
        
        self.numLEDString = StringVar()
        self.numLEDString.set(int(self.config['LEDs']['ledcount']))
        self.numGPIOString = StringVar()
        self.numGPIOString.set(int(self.config['LEDs']['gpiopin']))
        self.maxBrightnessString = StringVar()
        self.maxBrightnessString.set(int(self.config['LEDs']['ledmaxbrightness']))
        self.invertVar = IntVar()
        if (self.config['LEDs']['ledinvert'] == "True"):
            self.invertVar.set(1)
        else:
            self.invertVar.set(0)
        
        configTitleLabel = Label(self.configTop,
                text="RpNpGp - Configuration",
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
        

