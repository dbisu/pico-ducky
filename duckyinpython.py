# License : GPLv2.0
# copyright (c) 2026  Dave Bailey
# Author: Dave Bailey (dbisu, @daveisu)
#
#  TODO: ADD support for the following:
# Add jitter
# Add LED functionality
import re
import time
import random
import pwmio
import digitalio
from digitalio import DigitalInOut, Pull
from adafruit_debouncer import Debouncer
import board
from board import *
import asyncio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.mouse import Mouse
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
import microcontroller

# comment out these lines for non_US keyboards
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS as KeyboardLayout
from adafruit_hid.keycode import Keycode

# uncomment these lines for non_US keyboards
# replace LANG with appropriate language
#from keyboard_layout_win_LANG import KeyboardLayout as KeyboardLayout
#from keycode_win_LANG import Keycode

# Global variables dict - must be defined in this module so all functions here can access it
variables = {}

def _capsOn():
    return kbd.led_on(Keyboard.LED_CAPS_LOCK)

def _numOn():
    return kbd.led_on(Keyboard.LED_NUM_LOCK)

def _scrollOn():
    return kbd.led_on(Keyboard.LED_SCROLL_LOCK)

def pressLock(key):
    kbd.press(key)
    kbd.release(key)

def SaveKeyboardLedState():
    variables["$_INITIAL_SCROLLLOCK"] = _scrollOn()
    variables["$_INITIAL_NUMLOCK"] = _numOn()
    variables["$_INITIAL_CAPSLOCK"] = _capsOn()


def RestoreKeyboardLedState():
    if(variables["$_INITIAL_CAPSLOCK"] != _capsOn()):
        pressLock(Keycode.CAPS_LOCK)
    if(variables["$_INITIAL_NUMLOCK"] != _numOn()):
        pressLock(Keycode.NUM_LOCK)
    if(variables["$_INITIAL_SCROLLLOCK"] != _scrollOn()):
        pressLock(Keycode.SCROLL_LOCK)

duckyKeys = {
    'WINDOWS': Keycode.GUI, 'RWINDOWS': Keycode.RIGHT_GUI, 'GUI': Keycode.GUI, 'RGUI': Keycode.RIGHT_GUI, 'COMMAND': Keycode.GUI, 'RCOMMAND': Keycode.RIGHT_GUI,
    'APP': Keycode.APPLICATION, 'MENU': Keycode.APPLICATION, 'SHIFT': Keycode.SHIFT, 'RSHIFT': Keycode.RIGHT_SHIFT,
    'ALT': Keycode.ALT, 'RALT': Keycode.RIGHT_ALT, 'OPTION': Keycode.ALT, 'ROPTION': Keycode.RIGHT_ALT, 'CONTROL': Keycode.CONTROL, 'CTRL': Keycode.CONTROL, 'RCTRL': Keycode.RIGHT_CONTROL,
    'DOWNARROW': Keycode.DOWN_ARROW, 'DOWN': Keycode.DOWN_ARROW, 'LEFTARROW': Keycode.LEFT_ARROW,
    'LEFT': Keycode.LEFT_ARROW, 'RIGHTARROW': Keycode.RIGHT_ARROW, 'RIGHT': Keycode.RIGHT_ARROW,
    'UPARROW': Keycode.UP_ARROW, 'UP': Keycode.UP_ARROW, 'BREAK': Keycode.PAUSE,
    'PAUSE': Keycode.PAUSE, 'CAPSLOCK': Keycode.CAPS_LOCK, 'DELETE': Keycode.DELETE,
    'END': Keycode.END, 'ESC': Keycode.ESCAPE, 'ESCAPE': Keycode.ESCAPE, 'HOME': Keycode.HOME,
    'INSERT': Keycode.INSERT, 'NUMLOCK': Keycode.KEYPAD_NUMLOCK, 'PAGEUP': Keycode.PAGE_UP,
    'PAGEDOWN': Keycode.PAGE_DOWN, 'PRINTSCREEN': Keycode.PRINT_SCREEN, 'ENTER': Keycode.ENTER,
    'SCROLLLOCK': Keycode.SCROLL_LOCK, 'SPACE': Keycode.SPACE, 'TAB': Keycode.TAB,
    'BACKSPACE': Keycode.BACKSPACE,
    'A': Keycode.A, 'B': Keycode.B, 'C': Keycode.C, 'D': Keycode.D, 'E': Keycode.E,
    'F': Keycode.F, 'G': Keycode.G, 'H': Keycode.H, 'I': Keycode.I, 'J': Keycode.J,
    'K': Keycode.K, 'L': Keycode.L, 'M': Keycode.M, 'N': Keycode.N, 'O': Keycode.O,
    'P': Keycode.P, 'Q': Keycode.Q, 'R': Keycode.R, 'S': Keycode.S, 'T': Keycode.T,
    'U': Keycode.U, 'V': Keycode.V, 'W': Keycode.W, 'X': Keycode.X, 'Y': Keycode.Y,
    'Z': Keycode.Z, 'F1': Keycode.F1, 'F2': Keycode.F2, 'F3': Keycode.F3,
    'F4': Keycode.F4, 'F5': Keycode.F5, 'F6': Keycode.F6, 'F7': Keycode.F7,
    'F8': Keycode.F8, 'F9': Keycode.F9, 'F10': Keycode.F10, 'F11': Keycode.F11,
    'F12': Keycode.F12, 'F13': Keycode.F13, 'F14': Keycode.F14, 'F15': Keycode.F15,
    'F16': Keycode.F16, 'F17': Keycode.F17, 'F18': Keycode.F18, 'F19': Keycode.F19,
    'F20': Keycode.F20, 'F21': Keycode.F21, 'F22': Keycode.F22, 'F23': Keycode.F23,
    'F24': Keycode.F24
}

# Consumer control keys (media keys etc)
duckyConsumerKeys = {}

kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayout(kbd)

mouse = Mouse(usb_hid.devices)
cc = ConsumerControl(usb_hid.devices)

#init button
try:
    button1_pin = DigitalInOut(GP22)
except ValueError:
    microcontroller.reset()
button1_pin.pull = Pull.UP      # turn on internal pull-up resistor
button1 = Debouncer(button1_pin)

#init payload selection switch
payload1Pin = digitalio.DigitalInOut(GP4)
payload1Pin.switch_to_input(pull=digitalio.Pull.UP)
payload2Pin = digitalio.DigitalInOut(GP5)
payload2Pin.switch_to_input(pull=digitalio.Pull.UP)
payload3Pin = digitalio.DigitalInOut(GP10)
payload3Pin.switch_to_input(pull=digitalio.Pull.UP)
payload4Pin = digitalio.DigitalInOut(GP11)
payload4Pin.switch_to_input(pull=digitalio.Pull.UP)
progStatusPin = digitalio.DigitalInOut(GP0)
progStatusPin.switch_to_input(pull=digitalio.Pull.UP)

defaultDelay = 0

if(board.board_id == 'raspberry_pi_pico'):
    led = pwmio.PWMOut(board.LED, frequency=5000, duty_cycle=0)
elif(board.board_id == 'raspberry_pi_pico_w'):
    led = digitalio.DigitalInOut(board.LED)
    led.switch_to_output()

def convertLine(line):
    commands = []
    for key in filter(None, line.split(" ")):
        key = key.upper()
        command_keycode = duckyKeys.get(key, None)
        command_consumer_keycode = duckyConsumerKeys.get(key, None)
        if command_keycode is not None:
            commands.append(command_keycode)
        elif command_consumer_keycode is not None:
            commands.append(1000+command_consumer_keycode)
        elif hasattr(Keycode, key):
            commands.append(getattr(Keycode, key))
        else:
            print(f"Unknown key: <{key}>")
    return commands

def runScriptLine(line):
    keys = convertLine(line)
    for k in keys:
        if k > 1000:
            cc.send(int(k-1000))
        else:
            kbd.press(k)
    for k in reversed(keys):
        if k > 1000:
            pass  # consumer control releases automatically
        else:
            kbd.release(k)

def sendString(line):
    for char in line:
        layout.write(char)
        if char.isupper() or char in '!@#$%^&*()_+-"7|':
            time.sleep(0.08)
        else:
            time.sleep(0.03)

def parseMouseCommand(line):
    if line.startswith('CLICK'):
        if line[6:] == 'LEFT':
            mouse.click(Mouse.LEFT_BUTTON)
        elif line[6:] == 'RIGHT':
            mouse.click(Mouse.RIGHT_BUTTON)
        elif hasattr(Mouse, line[6:]):
            mouse.click(getattr(Mouse, line[6:]))

    elif line.startswith('MOVE'):
        x, y = line[5:].split(',')
        x, y = int(x), int(y)
        mouse.move(x, y)

    elif line.startswith('WHEEL'):
        wheel = int(line[6:])
        mouse.move(wheel=wheel)

    elif line.startswith('PRESS'):
        if line[6:] == 'LEFT':
            mouse.press(Mouse.LEFT_BUTTON)
        elif line[6:] == 'RIGHT':
            mouse.press(Mouse.RIGHT_BUTTON)
        elif hasattr(Mouse, line[6:]):
            mouse.press(getattr(Mouse, line[6:]))

    elif line.startswith('RELEASE'):
        if line[8:] == 'LEFT':
            mouse.release(Mouse.LEFT_BUTTON)
        elif line[8:] == 'RIGHT':
            mouse.release(Mouse.RIGHT_BUTTON)
        elif hasattr(Mouse, line[8:]):
            mouse.release(getattr(Mouse, line[8:]))

def parseLine(line):
    global defaultDelay

    line = line.rstrip('\n\r')

    if line.startswith("REM"):
        pass  # ignore comment

    elif line.startswith("DELAY"):
        time.sleep(float(line[6:])/1000)

    elif line.startswith("STRING"):
        sendString(line[7:])

    elif line.startswith("MOUSE"):
        parseMouseCommand(line[6:])

    elif line.startswith("CC"):
        CC_KEY = line[3:]
        if hasattr(ConsumerControlCode, CC_KEY):
            cc.send(getattr(ConsumerControlCode, CC_KEY))

    elif line.startswith("PRINT"):
        print("[SCRIPT]: " + line[6:])

    elif line.startswith("IMPORT"):
        runScript(line[7:])

    elif line.startswith("DEFAULT_DELAY"):
        defaultDelay = int(line[14:])

    elif line.startswith("DEFAULTDELAY"):
        defaultDelay = int(line[13:])

    elif line.startswith("LED"):
        if board.board_id == 'raspberry_pi_pico':
            led.duty_cycle = 0 if led.duty_cycle else 65535
        else:
            led.value = not led.value

    elif line.strip() == "":
        pass  # skip blank lines

    else:
        runScriptLine(line)

def getProgrammingStatus():
    progStatus = not progStatusPin.value
    return(progStatus)

def runScript(file):
    global defaultDelay

    duckyScriptPath = file
    restart = True
    try:
        while restart:
            restart = False
            with open(duckyScriptPath, "r", encoding='utf-8') as f:
                script_lines = f.readlines()
            previousLine = ""
            i = 0
            while i < len(script_lines):
                line = script_lines[i]
                line = line.rstrip('\n\r')
                print(f"runScript: {line}")
                if line.startswith("REPEAT"):
                    count = int(line[7:])
                    for _ in range(count):
                        parseLine(previousLine)
                        time.sleep(float(defaultDelay) / 1000)
                elif line.startswith("RESTART_PAYLOAD"):
                    restart = True
                    break
                elif line.startswith("STOP_PAYLOAD"):
                    restart = False
                    break
                else:
                    parseLine(line)
                    previousLine = line
                time.sleep(float(defaultDelay) / 1000)
                i += 1
    except OSError as e:
        print("Unable to open file", file)

def selectPayload():
    payload = "payload.dd"
    payload1State = not payload1Pin.value
    payload2State = not payload2Pin.value
    payload3State = not payload3Pin.value
    payload4State = not payload4Pin.value

    if payload1State:
        payload = "payload.dd"
    elif payload2State:
        payload = "payload2.dd"
    elif payload3State:
        payload = "payload3.dd"
    elif payload4State:
        payload = "payload4.dd"
    else:
        payload = "payload.dd"

    return payload

async def blink_pico_led():
    print("starting blink_pico_led")
    led_state = False
    while True:
        if variables.get("$_EXFIL_LEDS_ENABLED"):
            led.duty_cycle = 65535
        else:
            if led_state:
                for i in range(100):
                    if i < 50:
                        led.duty_cycle = int(i * 2 * 65535 / 100)
                    await asyncio.sleep(0.01)
                led_state = False
            else:
                for i in range(100):
                    if i >= 50:
                        led.duty_cycle = 65535 - int((i - 50) * 2 * 65535 / 100)
                    await asyncio.sleep(0.01)
                led_state = True
        await asyncio.sleep(0)

async def blink_pico_w_led():
    print("starting blink_pico_w_led")
    led_state = False
    while True:
        if variables.get("$_EXFIL_LEDS_ENABLED"):
            led.value = 1
        else:
            if led_state:
                led.value = 1
                await asyncio.sleep(0.5)
                led_state = False
            else:
                led.value = 0
                await asyncio.sleep(0.5)
                led_state = True
            await asyncio.sleep(0.5)

async def monitor_buttons(button1):
    print("starting monitor_buttons")
    button1Down = False
    while True:
        button1.update()

        button1Pushed = button1.fell
        button1Released = button1.rose

        if button1Pushed:
            print("Button 1 pushed")
            button1Down = True
        if button1Released:
            print("Button 1 released")
            if button1Down:
                print("push and released")

        if button1Released:
            if button1Down:
                payload = selectPayload()
                print("Running ", payload)
                runScript(payload)
                print("Done")
            button1Down = False

        await asyncio.sleep(0)

async def monitor_led_changes():
    print("starting monitor_led_changes")

    while True:
        if variables.get("$_EXFIL_MODE_ENABLED"):
            try:
                bit_list = []
                last_caps_state = _capsOn()
                last_num_state = _numOn()
                last_scroll_state = _scrollOn()

                with open("loot.bin", "ab") as file:
                    while variables.get("$_EXFIL_MODE_ENABLED"):
                        caps_state = _capsOn()
                        num_state = _numOn()
                        scroll_state = _scrollOn()

                        if caps_state != last_caps_state:
                            bit_list.append(0)
                            last_caps_state = caps_state

                        elif num_state != last_num_state:
                            bit_list.append(1)
                            last_num_state = num_state

                        if len(bit_list) == 8:
                            byte = 0
                            for b in bit_list:
                                byte = (byte << 1) | b
                            file.write(bytes([byte]))
                            bit_list = []

                        if scroll_state != last_scroll_state:
                            variables["$_EXFIL_LEDS_ENABLED"] = False
                            break

                        await asyncio.sleep(0.001)
            except Exception as e:
                print(f"Error occurred: {e}")

        await asyncio.sleep(0.0)
