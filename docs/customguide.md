# neopixel-gui customisation guide

## About the neopixel GUI

The Neopixel GUI application is a simple graphical interface for controlling neopixel RGB LEDs on a Raspberry Pi. 

![NeoPixel GUI screenshot](screenshot-v0-1.png "Screenshot of NeoPixel GUI Version 0.1")

The software includes a number of pre-programmed sequences that provide a variety of different effects. This guide provides details of how additional sequences can be added to the application.


## Installing neopixel GUI

For information on installing and initial configuration of the application see the README.md and INSTALL.md files. There is also a user guide explaining how to use the GUI.

## WARNING

The customisations listed in this guide include changes to the program code files. This means that:

*Any errors can stop the application from running.
*Files will be overwritten in future versions.

To provide protection against breaking a working application I suggest that you backup all files before making any changes. This includes the neopixelseq.py and the sequences.cfg file.

The two files mentioned above are considered part of the main application so will be overwritten by any upgrades. *Before upgrading* make sure that you have created a backup of any changes that you have made to the file.

If you have created a new sequence that you think would be useful for other users then please consider adding it to the main code through a github fork (details later), or by contacting me with the details through the contact form on my website.


## Changing the colours

The colour options are listed in sequences.cfg in the [Colours] section.
Each colour must have a name (on the left) followed by a colour number on the right. The colour is normally provided as a hexadecimal sequence (prefixed with 0x). The first two digits are for the Red value, the next two digits for the Green and the final two digits for the Blue value. All three set to full will be 0xffffff which is white. All off is 0x000000 which is black (no illumination from the LED).

There must be no spaces in the colour word.

Different colours can be found using you favourite photo / drawing application (eg. The GIMP) or online using a website such as the [w3schools color picker](http://www.w3schools.com/tags/ref_colorpicker.asp)

You will normally need to change the # to 0x to match the required configuration file format. 

You may find the actual colour is different from that shown on the website which is due to a difference between the colours generated from a computer screen and those created by the RGB LEDs.

The maximum number of colours that can be included is ten.


## Changing the order and disabling sequences

The sequences are listed in the [Sequences] section of the sequences.cfg.
The order of these can be changed by changing the order in the file. 

To disable any entries prefix with a '#' character to turn them into a comment. 

The text on the right can be changed to provide a more meaningful explanation, but the word on the left must not be changed without also updating the corresponding entry in the neopixelseq.py file (see next section).

There must be **at least 12 sequences** for the code to run. Any more than 12 will be split into tabs with up to 12 sequences per tab.

## Adding new custom sequences

Custom sequences can be added by updating the neopixelseq.py file. This is a python file and **any syntax or programming errors may result in the program not running or crashing**.

Note if you add your own sequences and the program fails to run then you will need to terminate the existing processes using the Kill command before trying again. Alternatively running the program from within IDLE will ensure the previous run is properly cleaned up first `gksudo idle3`

### Copying existing sequences

You can copy an existing sequence by copying the entire method. The sequence will need to be renamed to prevent any duplicates. Alternatively you can create a new method from scratch.

### Setting the LED colour

Each LED is set using self.strip.setPixelColor - using the number of the RGB counting from the start of the strip, follwed by the colour as a hexadecimal value. The LED colours will not change at once. Once all the LEDs have been updated then self.strip.show() updates all the LEDs. 

The self.strip.numPixels() method will provide the number of LEDs on the strip.


### Adding the delay

After each sequence update a delay should be called using the following method.

```Python
time.sleep(self.command.getOptions()['delay']/1000.0)
```

### Magic number = 4

Where a sequence is repeats over a set number of LEDs other than the number of colours selected by the user then the preferred value is 4. The magic number of 4 is used as it is a factor of all the neopixels rings (12, 16, 24) and it is an easy number to integrate within sequences.

### Long running sequences

Each sequence should return from the method as soon as possible after including the delay method mentioned above.

If the method needs to run for more than a few loops then the self.command.getCmdStatus method should be checked regularly and if that changes from False to True then the method should return immediately.

The value should be set to False using self.command.setCmdStatus before entering the loop.


### Resuming mid sequence

If a sequence is running when the method returns then it can keep track of it's current status using the self.chaserStartPos variable. 


### Adding the custom sequence to the list of sequences

After adding a new sequence you then need to add it to sequences.cfg in the format of 
```                         
methodName = User friendly name
```

## Adding new sequences to the project

If you have created your own sequences then please consider adding them to the official source code. This is best achieved by creating a fork from the [NeoPixel-GUI GitHub](https://github.com/penguintutor/neopixel-gui) repository and sending a pull request.

Alternatively you can send the details through the submit form on the website.

Any code submitted must be your own work or based upon source code compatible with GPL version 3 license. Submitting code to this project may result in your code being included in any software compatible with GPL version 3. If you do not agree with your source code being used in this manner then please do not submit any code to the project.

## Further information

See the user guide for more information on using the application.

More information will also be provided on [www.penguintutor.com](http://www.penguintutor.com)
