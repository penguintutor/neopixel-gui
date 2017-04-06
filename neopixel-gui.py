#!/usr/bin/pgzrun
from neopixel import *
import time

LEDCOUNT = 10
GPIOPIN = 18
FREQ = 800000
DMA = 5
INVERT = True       # Invert required when using inverting buffer
BRIGHTNESS = 255

WIDTH = 760
HEIGHT = 380

BUTTON_COLOR = 40,40,200
WHITE = 255, 255, 255

buttonText = (
    u"All On",
    u"All Off",
    u"Flash Alt",
    u"Chaser",
    u"Multi Chaser",
    u"Color Cycle"
)
buttonRect = (
    Rect(50, 100, 120, 40),
    Rect(300, 100, 120, 40),
    Rect(550, 100, 120, 40),
    Rect(50, 200, 120, 40),
    Rect(300, 200, 120, 40),
    Rect(550, 200, 120, 40)  
)

minusRect = Rect(150, 300, 40, 40)
plusRect = Rect(210, 300, 40, 40)

# Delay counts is number of updates before change in 60th of a second
delay_counts = 30 
seq_number = 0
sequence = "All On" # Start with all lights on
timer = 0


# Setup NeoPixel Strip
strip = Adafruit_NeoPixel(LEDCOUNT, GPIOPIN, FREQ, DMA, INVERT, BRIGHTNESS)
# Intialize the library (must be called once before other functions).
strip.begin()


def draw():
    screen.fill((80,80,80))

    screen.draw.text(
        "Neopixel Control",
        centerx = 360, top = 30,
        fontsize=40,
        color=WHITE
    )

    box = []
    for i in range(len(buttonRect)):
        box.append(buttonRect[i].inflate (-1, -1))
        screen.draw.filled_rect(box[i], BUTTON_COLOR)
        screen.draw.text(
            buttonText[i],
            centerx = box[i][0] + 60, centery = box[i][1] + 20,
            fontsize=28,
            color=WHITE
        )

    screen.draw.text(
        "Speed",
        (50, 310),
        fontsize=28,
        color=WHITE
        )

    boxMinus = minusRect.inflate(-1, -1)
    screen.draw.filled_rect(boxMinus, BUTTON_COLOR)
    screen.draw.text(
        "-",
        centerx = boxMinus[0] + 20, centery = boxMinus[1] + 20,
        fontsize=32,
        color=WHITE
    )

    boxPlus = plusRect.inflate(-1, -1)
    screen.draw.filled_rect(boxPlus, BUTTON_COLOR)
    screen.draw.text(
        "+",
        centerx = boxPlus[0] + 20, centery = boxPlus[1] + 20,
        fontsize=32,
        color=WHITE
    )


    

def on_mouse_down(button, pos):
    global seq_changed, sequence, delay_counts
    x, y = pos
    # Check position of main buttons
    for i in range(len(buttonRect)):
        if buttonRect[i].collidepoint(x,y) :
            sequence = buttonText[i]
    # Check position of speed buttons
    if minusRect.collidepoint(x,y) :
        delay_counts = delay_counts + 5
    if plusRect.collidepoint(x,y) :
        delay_counts = delay_counts - 5



def update():
    global timer
    global delay_counts 
    global seq_number
    timer = timer +1 
    if (timer > delay_counts) :
        seq_number += 1
        updseq ()
        timer = 0


def updseq () :
    global sequence
    if (sequence == "All On"):
        seq_all_on()
    if (sequence == "All Off"):
        seq_all_off()
    if (sequence == "Flash Alt"):
        seq_flash_alt ()
    if (sequence == "Chaser"):
        seq_chaser ()
    if (sequence == "Multi Chaser"):
        seq_multi_chaser ()
    if (sequence == "Color Cycle"):
        seq_color_cycle()
    



###### Sequences
def seq_all_on():
    for x in range (LEDCOUNT):
        strip.setPixelColor(x, Color(255,255,255))
    strip.show()        

def seq_all_off():
    for x in range (LEDCOUNT):
        strip.setPixelColor(x, Color(0,0,0))
    strip.show()
    
# Uses 2 seq numbers for odd and even
def seq_flash_alt ():
    global seq_number
    if (seq_number > 1):
        seq_number = 0
    colors = [Color(255, 255, 255), Color(0,0,0)]
    for x in range (LEDCOUNT):
        if (x %2 == 1):
            strip.setPixelColor(x, colors[seq_number])
        else:
            strip.setPixelColor(x, colors[1-seq_number])
    strip.show()
    
def seq_chaser ():
    global seq_number
    if (seq_number >= LEDCOUNT):
        seq_number = 0
    for x in range (LEDCOUNT):
        strip.setPixelColor(x, Color(0,0,0))
    strip.setPixelColor(seq_number, Color(255,255,255))
    strip.show()
    
def seq_chaser ():
    global seq_number
    if (seq_number >= LEDCOUNT):
        seq_number = 0
    for x in range (LEDCOUNT):
        strip.setPixelColor(x, Color(0,0,0))
    strip.setPixelColor(seq_number, Color(255,255,255))
    strip.show()
    
# Needs at least 6 pixels preferably more for this to look correct
def seq_multi_chaser ():
    global seq_number
    if (seq_number >= LEDCOUNT):
        seq_number = 0
    colors = [Color(255, 0, 0), Color(0,255,0), Color(0,0,255)]
    for x in range (LEDCOUNT):
        strip.setPixelColor(x, Color(0,0,0))
    # Set current, one before and one after
    # seq number is always valid
    strip.setPixelColor(seq_number, colors[1])
    # Ensure there is one before - if not put it at the end of the row
    if (seq_number > 0) :
        strip.setPixelColor(seq_number-1, colors[0])
    else:
        strip.setPixelColor(LEDCOUNT-1, colors[0])
    # Ensure there is one after - if not put it at the start of the row
    if (seq_number < LEDCOUNT-1) :
        strip.setPixelColor(seq_number+1, colors[2])
    else:
        strip.setPixelColor(0, colors[2])
        
    strip.show()
    
def seq_color_cycle():
    global seq_number
    colors = [Color(248,12,18), Color(255,51,17), Color(255,102,68), \
        Color(254,174,45), Color(208,195,16), Color(105,208,37), \
        Color(18,189,185), Color(68,68,221), Color(59,12,189)]
    if (seq_number >= len(colors)):
        seq_number = 0
        
    # seq number is used to define the first color then we increment through the colors
    this_color = seq_number
    for x in range(LEDCOUNT):
        strip.setPixelColor(x, colors[this_color])
        this_color = this_color + 1;
        if (this_color >= len(colors)):
            this_color = 0
    strip.show()
    
