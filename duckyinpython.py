import usb_hid
from adafruit_hid.keyboard import Keyboard
import time
import digitalio
from board import *

from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS as KeyboardLayout
from adafruit_hid.keycode import Keycode
# from keyboard_layout_win_fr import KeyboardLayout
# from keycode_win_fr import Keycode

duckyConvert = {
    "APP": "APPLICATION",
    "MENU": "APPLICATION",
    "CTRL": "CONTROL",
    "DOWNARROW": "DOWN_ARROW",
    "DOWN": "DOWN_ARROW",
    "LEFTARROW": "LEFT_ARROW",
    "LEFT": "LEFT_ARROW",
    "RIGHTARROW": "RIGHT_ARROW",
    "RIGHT": "RIGHT_ARROW",
    "UPARROW": "UP_ARROW",
    "UP": "UP_ARROW",
    "BREAK": "PAUSE",
    "CAPSLOCK": "CAPS_LOCK",
    "ESC": "ESCAPE",
    "NUMLOCK": "KEYPAD_NUMLOCK",
    "PAGEUP": "PAGE_UP",
    "PAGEDOWN": "PAGE_DOWN",
    "PRINTSCREEN": "PRINT_SCREEN",
    "SCROLLLOCK": "SCROLL_LOCK",
}

def convertLine(line):
    newline = []
    print(line)
    for word in line.split(" "):
        type_word = word.upper()
        if type_word in duckyConvert:
            type_word = duckyConvert[type_word]
        if hasattr(Keycode, type_word):
            newline.append(getattr(Keycode, type_word))
        else:
            print(f"Unknown key: <{type_word}>")
    print(newline)
    return newline

def runScriptLine(line):
    for k in line:
        kbd.press(k)
    kbd.release_all()

def sendString(line):
    layout.write(line)

def parseLine(line):
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

kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayout(kbd)

# sleep at the start to allow the device to be recognized by the host computer
time.sleep(.5)

# check GP0 for setup mode
# see setup mode for instructions
progStatus = False
progStatusPin = digitalio.DigitalInOut(GP0)
progStatusPin.switch_to_input(pull=digitalio.Pull.UP)
progStatus = not progStatusPin.value
defaultDelay = 0
if(progStatus == False):
    # not in setup mode, inject the payload
    duckyScriptPath = "payload.dd"
    f = open(duckyScriptPath,"r",encoding='utf-8')
    print("Running payload.dd")
    previousLine = ""
    duckyScript = f.readlines()
    for line in duckyScript:
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

    print("Done")
else:
    print("Update your payload")
