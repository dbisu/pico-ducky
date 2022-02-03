# License : GPLv2.0
# copyright (c) 2021  Dave Bailey
# Author: Dave Bailey (dbisu, @daveisu)

import time
from ast import match_case
from typing import List

import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard

# comment out these lines for non_US keyboards
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS as KeyboardLayout
from adafruit_hid.keycode import Keycode
from board import *

# uncomment these lines for non_US keyboards
# replace LANG with appropriate language
#from keyboard_layout_win_LANG import KeyboardLayout
#from keycode_win_LANG import Keycode

led = digitalio.DigitalInOut(LED)
led.direction = digitalio.Direction.OUTPUT


kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayout(kbd)


duckyCommands = {
    'WINDOWS': Keycode.WINDOWS,
    'GUI': Keycode.GUI,
    'APP': Keycode.APPLICATION,
    'MENU': Keycode.APPLICATION,
    'SHIFT': Keycode.SHIFT,
    'ALT': Keycode.ALT,
    'CONTROL': Keycode.CONTROL,
    'CTRL': Keycode.CONTROL,
    'DOWNARROW': Keycode.DOWN_ARROW,
    'DOWN': Keycode.DOWN_ARROW,
    'LEFTARROW': Keycode.LEFT_ARROW,
    'LEFT': Keycode.LEFT_ARROW,
    'RIGHTARROW': Keycode.RIGHT_ARROW,
    'RIGHT': Keycode.RIGHT_ARROW,
    'UPARROW': Keycode.UP_ARROW,
    'UP': Keycode.UP_ARROW,
    'BREAK': Keycode.PAUSE,
    'PAUSE': Keycode.PAUSE,
    'CAPSLOCK': Keycode.CAPS_LOCK,
    'DELETE': Keycode.DELETE,
    'END': Keycode.END,
    'ESC': Keycode.ESCAPE,
    'ESCAPE': Keycode.ESCAPE,
    'HOME': Keycode.HOME,
    'INSERT': Keycode.INSERT,
    'NUMLOCK': Keycode.KEYPAD_NUMLOCK,
    'PAGEUP': Keycode.PAGE_UP,
    'PAGEDOWN': Keycode.PAGE_DOWN,
    'PRINTSCREEN': Keycode.PRINT_SCREEN,
    'ENTER': Keycode.ENTER,
    'SCROLLLOCK': Keycode.SCROLL_LOCK,
    'SPACE': Keycode.SPACE,
    'TAB': Keycode.TAB,
    'BACKSPACE': Keycode.BACKSPACE,
    'A': Keycode.A,
    'B': Keycode.B,
    'C': Keycode.C,
    'D': Keycode.D,
    'E': Keycode.E,
    'F': Keycode.F,
    'G': Keycode.G,
    'H': Keycode.H,
    'I': Keycode.I,
    'J': Keycode.J,
    'K': Keycode.K,
    'L': Keycode.L,
    'M': Keycode.M,
    'N': Keycode.N,
    'O': Keycode.O,
    'P': Keycode.P,
    'Q': Keycode.Q,
    'R': Keycode.R,
    'S': Keycode.S,
    'T': Keycode.T,
    'U': Keycode.U,
    'V': Keycode.V,
    'W': Keycode.W,
    'X': Keycode.X,
    'Y': Keycode.Y,
    'Z': Keycode.Z,
    'F1': Keycode.F1,
    'F2': Keycode.F2,
    'F3': Keycode.F3,
    'F4': Keycode.F4,
    'F5': Keycode.F5,
    'F6': Keycode.F6,
    'F7': Keycode.F7,
    'F8': Keycode.F8,
    'F9': Keycode.F9,
    'F10': Keycode.F10,
    'F11': Keycode.F11,
    'F12': Keycode.F12,
}


def convertLine(line: str)-> List:
    newline = []
    # print(line)
    # loop on each key - the filter removes empty values
    for key in filter(None, line.split(" ")):
        key = key.upper()
        # find the keycode for the command in the list
        if key in duckyCommands:
            # if it exists in the list, use it
            newline.append(duckyCommands[key])
        elif hasattr(Keycode, key):
            # if it's in the Keycode module, use it (allows any valid keycode)
            newline.append(getattr(Keycode, key))
        else:
            # if it's not a known key name, show the error for diagnosis
            print(f"Unknown key: <{key}>")
    # print(newline)
    return newline


def runScriptLine(line: str) -> None:
    for k in line:
        kbd.press(k)
    kbd.release_all()


def sendString(line: str) -> None:
    layout.write(line)


def splitIntoCommandAndArg(line: str) -> List[str]:
    return line.strip().split(" ", 1)


def parseLine(line: str) -> None:
    global defaultDelay
    cmd, arg = splitIntoCommandAndArg(line)
    if(cmd == "REM"):
        # ignore ducky script comments
        pass
    elif(cmd == "DELAY"):
        time.sleep(float(arg/1000))
    elif(cmd == "STRING"):
        sendString(arg)
    elif(cmd == "PRINT"):
        print("[SCRIPT]: " + arg)
    elif(cmd == "IMPORT"):
        runScript(arg)
    elif(cmd == "DEFAULT_DELAY" or cmd == "DEFAULTDELAY"):
        defaultDelay = int(arg) * 10
    elif(cmd == "LED"):
        led.value = not led.value
    else:
        newScriptLine = convertLine(line)
        runScriptLine(newScriptLine)


def runScript(file: str) -> None:
    global defaultDelay

    with open(file, "r", encoding='utf-8') as f:
        duckyScript = f.readlines()
        for previousLine, currentLine in zip(duckyScript, duckyScript[1:]):
            currentCmd, currentArg = splitIntoCommandAndArg(currentLine)
            if(currentCmd == "REPEAT"):
                for _ in range(int(currentArg)):
                    # repeat the last command
                    parseLine(previousLine)
                    time.sleep(float(defaultDelay)/1000)
            else:
                parseLine(currentLine)
            time.sleep(float(defaultDelay)/1000)


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
    print("Running payload.dd")
    runScript("payload.dd")

    print("Done")
else:
    print("Update your payload")
