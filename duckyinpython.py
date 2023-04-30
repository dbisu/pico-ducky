# License : GPLv2.0
# copyright (c) 2023  Dave Bailey
# Author: Dave Bailey (dbisu, @daveisu)


import time
import digitalio
from digitalio import DigitalInOut, Pull
from adafruit_debouncer import Debouncer
import board
from board import *
import pwmio
import asyncio
import usb_hid
from adafruit_hid.keyboard import Keyboard

# comment out these lines for non_US keyboards
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS as KeyboardLayout
from adafruit_hid.keycode import Keycode

# uncomment these lines for non_US keyboards or use LANG command
# replace LANG with appropriate language
#from keyboard_layout_win_LANG import KeyboardLayout
#from keycode_win_LANG import Keycode

def define_ducky_commands():
    return {
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
        'BACKSPACE': Keycode.BACKSPACE,
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
duckyCommands = define_ducky_commands()

def convertLine(line):
    newline = []
    # print(line)
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
    # print(newline)
    return newline

def parseCondition(condition):
    return True
    #return eval(condition) FIXME: Needs to be replaced with a more adequate condition checker

def detectOS():
    inital_state = kbd.led_on(Keyboard.LED_CAPS_LOCK)
    
    # Check if windows
    runScriptLine(convertLine('GUI r'))
    time.sleep(0.5)
    sendString('''powershell -Command "(New-Object -com WScript.Shell).SendKeys('{CAPSLOCK}')"''')
    runScriptLine(convertLine('ENTER'))
    time.sleep(1)

    if inital_state != kbd.led_on(Keyboard.LED_CAPS_LOCK):
        return "windows"

    return "other"


def changeLang(lang):
    if lang == 'us':
        from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS as new_KeyboardLayout
        from adafruit_hid.keycode import Keycode as new_Keycode
    else:
        layout_name = f'keyboard_layout_win_{lang}'
        new_KeyboardLayout = getattr(__import__(layout_name), 'KeyboardLayout')

        keycode_name = f'keycode_win_{lang}'
        new_Keycode = getattr(__import__(keycode_name), 'Keycode')

    return new_KeyboardLayout, new_Keycode

def runScriptLine(line):
    for k in line:
        kbd.press(k)
    kbd.release_all()

def sendString(line):
    layout.write(line)

def parseLine(line):
    global defaultDelay
    global duckyCommands
    global layout
    if(line.startswith("REM")):
        # ignore ducky script comments
        pass
    elif(line.startswith("DELAY")):
        time.sleep(float(line[6:])/1000)
    elif(line.startswith("STRING")):
        sendString(line[7:])
    elif(line.startswith("PRINT")):
        print("[SCRIPT]: " + line[6:])
    elif(line.startswith("IMPORT")):
        runScript(line[7:])
    elif(line.startswith("DEFAULT_DELAY")):
        defaultDelay = int(line[14:]) * 10
    elif(line.startswith("DEFAULTDELAY")):
        defaultDelay = int(line[13:]) * 10
    elif(line.startswith("LED")):
        if(led.value == True):
            led.value = False
        else:
            led.value = True
    elif(line.startswith("LANG")):
        KeyboardLayout, Keycode = changeLang(line[5:])
        duckyCommands = define_ducky_commands()
        layout = KeyboardLayout(kbd)
    elif(line.startswith("DETECT_OS")):
        os = detectOS()
        sendString(os)
    elif(line.startswith("IF")):
        return parseCondition(line[3:-5])
    elif(line.startswith("END_IF")):
        return True
    else:
        newScriptLine = convertLine(line)
        runScriptLine(newScriptLine)
    return False

kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayout(kbd)




#init button
button1_pin = DigitalInOut(GP22) # defaults to input
button1_pin.pull = Pull.UP      # turn on internal pull-up resistor
button1 =  Debouncer(button1_pin)

#init payload selection switch
payload1Pin = digitalio.DigitalInOut(GP4)
payload1Pin.switch_to_input(pull=digitalio.Pull.UP)
payload2Pin = digitalio.DigitalInOut(GP5)
payload2Pin.switch_to_input(pull=digitalio.Pull.UP)
payload3Pin = digitalio.DigitalInOut(GP10)
payload3Pin.switch_to_input(pull=digitalio.Pull.UP)
payload4Pin = digitalio.DigitalInOut(GP11)
payload4Pin.switch_to_input(pull=digitalio.Pull.UP)

def getProgrammingStatus():
    # check GP0 for setup mode
    # see setup mode for instructions
    progStatusPin = digitalio.DigitalInOut(GP0)
    progStatusPin.switch_to_input(pull=digitalio.Pull.UP)
    progStatus = not progStatusPin.value
    return(progStatus)


defaultDelay = 0

def conditionCheck(condition: str) -> bool: # FIXME: missing variable check
    if condition.contains('&'):
        conditions = condition.split('&')
        for con in conditions:
            if not conditionCheck(con):
                return False
        return True
    elif condition.contains('|'):
        conditions = condition.split('|')
        for con in conditions:
            if conditionCheck(con):
                return True
        return False
    elif condition.contains('=='):
        con_split = condition.split('==')
        return True if con_split[0] == con_split[1] else False
    elif condition.contains('>='):
        con_split = condition.split('>=')
        return True if con_split[0] >= con_split[1] else False
    elif condition.contains('<='):
        con_split = condition.split('<=')
        return True if con_split[0] <= con_split[1] else False
    elif condition.contains('<'):
        con_split = condition.split('<')
        return True if con_split[0] < con_split[1] else False
    elif condition.contains('>'):
        con_split = condition.split('>')
        return True if con_split[0] > con_split[1] else False

def runScript(file):
    global defaultDelay

    if_false = False

    duckyScriptPath = file
    try:
        f = open(duckyScriptPath,"r",encoding='utf-8')
        previousLine = ""
        lines = f.lines()
        i=0
        while i < len(lines):
            line = lines[i].rstrip()

            if line.startswith('IF') or line.startswith('ELSE IF'):
                condition = line.split('(')[1].split(')')[0]
                condition_result = conditionCheck(condition)
                i += 1
                while not lines[i].startswith('END_IF') and not lines[i].startswith('ELSE'):
                    if condition_result:
                        parseLine(lines[i])
                    i += 1
                    
                if lines[i].startswith('ELSE IF') and not condition_result:
                    continue
                    
                if lines[i].startswith('ELSE'):
                    while not lines[i].startswith('END_IF'):
                        if not condition_result:
                            parseLine(lines[i])
                        i += 1
                    continue
                else:
                    i += 1
                    continue

            if(line[0:6] == "REPEAT"):
                for i in range(int(line[7:])):
                    #repeat the last command
                    parseLine(previousLine)
                    time.sleep(float(defaultDelay)/1000)
            else:
                if parseLine(line) == True:
                    if_false = not if_false
                previousLine = line
            time.sleep(float(defaultDelay)/1000)
    except OSError as e:
        print("Unable to open file ", file)

def selectPayload():
    global payload1Pin, payload2Pin, payload3Pin, payload4Pin
    payload = "payload.dd"
    # check switch status
    # payload1 = GPIO4 to GND
    # payload2 = GPIO5 to GND
    # payload3 = GPIO10 to GND
    # payload4 = GPIO11 to GND
    payload1State = not payload1Pin.value
    payload2State = not payload2Pin.value
    payload3State = not payload3Pin.value
    payload4State = not payload4Pin.value

    if(payload1State == True):
        payload = "payload.dd"

    elif(payload2State == True):
        payload = "payload2.dd"

    elif(payload3State == True):
        payload = "payload3.dd"

    elif(payload4State == True):
        payload = "payload4.dd"

    else:
        # if all pins are high, then no switch is present
        # default to payload1
        payload = "payload.dd"

    return payload

async def blink_led(led):
    print("Blink")
    if(board.board_id == 'raspberry_pi_pico'):
        blink_pico_led(led)
    elif(board.board_id == 'raspberry_pi_pico_w'):
        blink_pico_w_led(led)

async def blink_pico_led(led):
    print("starting blink_pico_led")
    led_state = False
    while True:
        if led_state:
            #led_pwm_up(led)
            #print("led up")
            for i in range(100):
                # PWM LED up and down
                if i < 50:
                    led.duty_cycle = int(i * 2 * 65535 / 100)  # Up
                await asyncio.sleep(0.01)
            led_state = False
        else:
            #led_pwm_down(led)
            #print("led down")
            for i in range(100):
                # PWM LED up and down
                if i >= 50:
                    led.duty_cycle = 65535 - int((i - 50) * 2 * 65535 / 100)  # Down
                await asyncio.sleep(0.01)
            led_state = True
        await asyncio.sleep(0)

async def blink_pico_w_led(led):
    print("starting blink_pico_w_led")
    led_state = False
    while True:
        if led_state:
            #print("led on")
            led.value = 1
            await asyncio.sleep(0.5)
            led_state = False
        else:
            #print("led off")
            led.value = 0
            await asyncio.sleep(0.5)
            led_state = True
        await asyncio.sleep(0.5)

async def monitor_buttons(button1):
    global inBlinkeyMode, inMenu, enableRandomBeep, enableSirenMode,pixel
    print("starting monitor_buttons")
    button1Down = False
    while True:
        button1.update()

        button1Pushed = button1.fell
        button1Released = button1.rose
        button1Held = not button1.value

        if(button1Pushed):
            print("Button 1 pushed")
            button1Down = True
        if(button1Released):
            print("Button 1 released")
            if(button1Down):
                print("push and released")

        if(button1Released):
            if(button1Down):
                # Run selected payload
                payload = selectPayload()
                print("Running ", payload)
                runScript(payload)
                print("Done")
            button1Down = False

        await asyncio.sleep(0)
