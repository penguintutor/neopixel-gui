from tkinter import *
from tkinter import messagebox

class ConfigWindow():
    
    # Track whether config window open to stop duplicate windows
    configWindowOpen = False

    def __init__ (self, config, configfile):
        self.config = config
        self.configfile = configfile


    # called from window manager handler or from Cancel button
    def CloseConfig(self):
        self.configWindowOpen = False
        self.configTop.destroy()


    def SaveConfig(self):
        self.config['LEDs']['ledcount'] = self.numLEDString.get()
        self.config['LEDs']['gpiopin'] = self.numGPIOString.get()
        # save config - and inform user to restart
        try:
            with open(self.configfile, 'w') as cfgfile:
                self.config.write(cfgfile)
                self.CloseConfig()
                messagebox.showinfo("Info", "Configuration saved\nRestart application to reload config")
        except : 
            self.CloseConfig()
            messagebox.showinfo("Error", "Error saving configuration file "+configfile)
            
            
        
    def windowClient (self):
        if (self.configWindowOpen) :
            return
        self.configWindowOpen = True
        self.configTop = Toplevel()
        self.configTop.wm_title("RpNpGp - Configuration")
        self.configTop.wm_geometry("400x300")
        # set handler for close window using WM X
        self.configTop.wm_protocol('WM_DELETE_WINDOW',  self.CloseConfig)
        
        self.numLEDString = StringVar()
        self.numLEDString.set(int(self.config['LEDs']['ledcount']))
        self.numGPIOString = StringVar()
        self.numGPIOString.set(int(self.config['LEDs']['gpiopin']))
        
        configTitleLabel = Label(self.configTop,
                text="RpNpGp - Configuration",
                foreground="blue", font="Verdana 16 bold").grid(columnspan=3, sticky=W, pady=(4, 15), padx=5)
                
        numLEDLabel = Label(self.configTop,
                    font="Verdana 14",
                    text="Number LEDs").grid(row=1, column=1)
                    
        numLEDEntry = Entry(self.configTop,
                    font="Verdana 14",
                    width=5,
                    textvariable=self.numLEDString).grid(row=1, column=2)
                    
        numGPIOLabel = Label(self.configTop,
                    font="Verdana 14",
                    text="GPIO pin number").grid(row=2, column=1)
                    
        numGPIOEntry = Entry(self.configTop,
                    font="Verdana 14",
                    width=5,
                    textvariable=self.numGPIOString).grid(row=2, column=2)
                    
        cancelButton = Button(self.configTop, 
                    text="Cancel",
                    font="Verdana 14",
                    width = 8,
                    height = 1,
                    command=self.CloseConfig)
        cancelButton.grid(row=4, column=2, pady=(40, 10), padx=10)
    
    
        saveButton = Button(self.configTop, 
                    text="Save",
                    font="Verdana 14",
                    width = 8,
                    height = 1,
                    command=self.SaveConfig)
        saveButton.grid(row=4, column=3, pady=(40, 10), padx=10)
        

