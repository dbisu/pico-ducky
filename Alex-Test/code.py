# RubberNugget HID Attack Tool
# By Kody Kinzie & Alex Lynd
# Optimized by Areza
# Forked from https://github.com/dbisu/pico-ducky

# import libraries
import usb_hid, neopixel, board, busio, adafruit_displayio_sh1106, displayio, adafruit_framebuf, time, ssl, wifi, socketpool, ipaddress
import adafruit_requests, adafruit_requests as requests, ampule, adafruit_binascii as binascii, terminalio, base64, os
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS as KeyboardLayout
from adafruit_hid.keycode import Keycode
from digitalio import DigitalInOut, Pull
from adafruit_debouncer import Debouncer
from board import *
from adafruit_display_text import label
from adafruit_display_shapes.line import Line


# display config for SH1106
displayio.release_displays()
WIDTH = 130 
HEIGHT = 64
BORDER = 1
i2c = busio.I2C(SCL, SDA)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)
display = adafruit_displayio_sh1106.SH1106(display_bus, width=WIDTH, height=HEIGHT)

# use default font & white for font
font = terminalio.FONT
color = 0xFFFFFF


# configure button input
pins = (board.IO9, board.IO18, board.IO11, board.IO7)
buttons = []       # will hold list of Debouncer objects
for pin in pins:   # set up each pin
    tmp_pin = DigitalInOut(pin) # defaults to input
    tmp_pin.pull = Pull.UP      # turn on internal pull-up resistor
    buttons.append( Debouncer(tmp_pin) )

# keyboard config
kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayout(kbd)

# payload config & root dir
payloadstatus  = ""
defaultDelay = 0
path = "payloads"


# get pressed button
def getButtonPressed():
    for i in range(len(buttons)):
        buttons[i].update()
        if buttons[i].fell:
            return i
    return -1


###### draw key map function ######

def drawNavMap(map_vals):
    global path
    map = ["UP   ", "DOWN ", "LEFT ", "RIGHT"]
    
    #insert "back" as down value or blank values
    if len(map_vals) <4:
        for i in range (len(map_vals),4):
            map_vals.insert(i,"")
        map_vals.insert(1, "Back")
    counter = 0
    navScreen = displayio.Group()
    
    # iterate text values and add to screen
    for i in map_vals[:4]:
        text_area = label.Label(font, text=map[counter]+": "+i, color=color)
        text_area.x = 2
        text_area.y =3+(10*counter)
        counter+=1
        navScreen.append(text_area)

    # draw stuff
    navScreen.append(Line(0, 50, 127, 50, 0xFFFFFF))
    navScreen.append(Line(0, 51, 127, 51, 0xFFFFFF))
    text_area = label.Label(font, text="Dir: "+ path[path.rfind("/")+1:], color=color)
    text_area.x = 2
    text_area.y =57
    navScreen.append(text_area)
    display.show(navScreen)
    
    # update path until text file reached
    currButton = -1
    while (currButton== -1):
        currButton = getButtonPressed()
    if("Back" in map_vals and currButton==1):
        path=path[0:path.rfind("/")]
    elif (map_vals[currButton]==""):
        pass
    else :
        path+="/"+map_vals[currButton]
    if (".txt" in path):
        runPayload(path)
        path=path[0:path.rfind("/")]
        path=path[0:path.rfind("/")]
        

##### draw and execute payload ######

def drawPayload(status, payloadName):

    # draw Nugget to indicate status!
    
    if (status=="START"):
        statusText = "executing"
        bitmap = displayio.OnDiskBitmap("/faces/payload-running.bmp")
    else:
        statusText = "finished"
        bitmap = displayio.OnDiskBitmap("/faces/payload-finished.bmp")
     # Setup the file as the bitmap data source
    tile_grid = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)
    
    group = displayio.Group() # Create a Group to hold the TileGrid
    group.append(tile_grid)
    group.append(Line(0, 50, 129, 50, 0xFFFFFF))
    group.append(Line(0, 51, 129, 51, 0xFFFFFF))
    group.append(Line(0, 11, 129, 11, 0xFFFFFF))
    group.append(Line(0, 12, 129, 12, 0xFFFFFF))
    
    text = ("STATUS: "+statusText)
    text_area = label.Label(font, text=text, color=color)
    text_area.x = 2
    text_area.y =57
    group.append(text_area)
    text = (payloadName[path.rfind("/")+1:])
    if(len(text)>21):
        text = text[:18]+"..."

    text_area = label.Label(font, text=text, color=color)
    text_area.x = 2
    text_area.y =3
    group.append(text_area)
    display.show(group)
    time.sleep(3)

# duckyscript command map

duckyCommands = {
    'WINDOWS': Keycode.WINDOWS, 'GUI': Keycode.GUI,
    'APP': Keycode.APPLICATION, 'MENU': Keycode.APPLICATION, 'SHIFT': Keycode.SHIFT,
    'ALT': Keycode.ALT, 'CONTROL': Keycode.CONTROL, 'CTRL': Keycode.CONTROL,
    'DOWNARROW': Keycode.DOWN_ARROW, 'DOWN': Keycode.DOWN_ARROW, 'LEFTARROW': Keycode.LEFT_ARROW,
    'LEFT': Keycode.LEFT_ARROW, 'RIGHTARROW': Keycode.RIGHT_ARROW, 'RIGHT': Keycode.RIGHT_ARROW,
    'UPARROW': Keycode.UP_ARROW, 'UP': Keycode.UP_ARROW, 'BREAK': Keycode.PAUSE,
    'PAUSE': Keycode.PAUSE, 'CAPSLOCK': Keycode.CAPS_LOCK, 'DELETE': Keycode.DELETE,
    'END': Keycode.END, 'ESC': Keycode.ESCAPE, 'ESCAPE': Keycode.ESCAPE, 'HOME': Keycode.HOME,
    'INSERT': Keycode.INSERT, 'NUMLOCK': Keycode.KEYPAD_NUMLOCK, 'PAGEUP': Keycode.PAGE_UP,
    'PAGEDOWN': Keycode.PAGE_DOWN, 'PRINTSCREEN': Keycode.PRINT_SCREEN, 'ENTER': Keycode.ENTER,
    'SCROLLLOCK': Keycode.SCROLL_LOCK, 'SPACE': Keycode.SPACE, 'TAB': Keycode.TAB,
    'A': Keycode.A, 'B': Keycode.B, 'C': Keycode.C, 'D': Keycode.D, 'E': Keycode.E,
    'F': Keycode.F, 'G': Keycode.G, 'H': Keycode.H, 'I': Keycode.I, 'J': Keycode.J,
    'K': Keycode.K, 'L': Keycode.L, 'M': Keycode.M, 'N': Keycode.N, 'O': Keycode.O,
    'P': Keycode.P, 'Q': Keycode.Q, 'R': Keycode.R, 'S': Keycode.S, 'T': Keycode.T,
    'U': Keycode.U, 'V': Keycode.V, 'W': Keycode.W, 'X': Keycode.X, 'Y': Keycode.Y,
    'Z': Keycode.Z, 'F1': Keycode.F1, 'F2': Keycode.F2, 'F3': Keycode.F3,
    'F4': Keycode.F4, 'F5': Keycode.F5, 'F6': Keycode.F6, 'F7': Keycode.F7,
    'F8': Keycode.F8, 'F9': Keycode.F9, 'F10': Keycode.F10, 'F11': Keycode.F11,
    'F12': Keycode.F12,
}

###### ducky parser by @dbisu ######

def convertLine(line):
    newline = []
    print(line)
    # loop on each key - the filter removes empty values
    for key in filter(None, line.split(" ")):
        key = key.upper()
        # find the keycode for the command in the list
        command_keycode = duckyCommands.get(key, None)
        if command_keycode is not None:
            # if it exists in the list, use it
            newline.append(command_keycode)
        elif hasattr(Keycode, key):
            # if it's in the Keycode module, use it (allows any valid keycode)
            newline.append(getattr(Keycode, key))
        else:
            # if it's not a known key name, show the error for diagnosis
            print(f"Unknown key: <{key}>")
    print(newline)
    return newline

def runScriptLine(line):
    for k in line:
        kbd.press(k)
    kbd.release_all()

def sendString(line):
    layout.write(line)

def parseLine(line):
    global defaultDelay
    if(line[0:3] == "REM"):
        # ignore ducky script comments
        pass
    elif(line[0:5] == "DELAY"):
        time.sleep(float(line[6:])/1000)
    elif(line[0:6] == "STRING"):
        sendString(line[7:])
    elif(line[0:13] == "DEFAULT_DELAY"):
        defaultDelay = int(line[14:]) * 10
    elif(line[0:12] == "DEFAULTDELAY"):
        defaultDelay = int(line[13:]) * 10
    else:
        newScriptLine = convertLine(line)
        runScriptLine(newScriptLine)

###### payload run function ######

def runPayload(payloadPath):
    ##startup indicator
    drawPayload("START",payloadPath)
    f = open(payloadPath,"r",encoding='utf-8')
    previousLine = ""
    duckyScript = f.readlines()
    for line in duckyScript:
        print(line)
        line = line.rstrip()
        if(line[0:6] == "REPEAT"):
            for i in range(int(line[7:])):
                #repeat the last command
                parseLine(previousLine)
                time.sleep(float(defaultDelay)/1000)
        else:
            parseLine(line)
            previousLine = line
        time.sleep(float(defaultDelay)/1000)

    ##finish indicator
    drawPayload("STOP",payloadPath)
    time.sleep(.5)

while True:
    # check for root payload directory
    if (path!="payloads"):
        drawNavMap(os.listdir(path)[:3]) # take first 3 items from list
    else:
        drawNavMap(os.listdir(path))
