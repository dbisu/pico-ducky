# License : GPLv2.0
# copyright (c) 2023  Dave Bailey
# Author: Dave Bailey (dbisu, @daveisu)
#
#  TODO: ADD support for the following:
# Add jitter
# Add LED functionality

import re
import time
import random
import digitalio
from digitalio import DigitalInOut, Pull
from adafruit_debouncer import Debouncer
import board
from board import *
import pwmio
import asyncio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

# comment out these lines for non_US keyboards
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS as KeyboardLayout
from adafruit_hid.keycode import Keycode

# uncomment these lines for non_US keyboards
# replace LANG with appropriate language
#from keyboard_layout_win_LANG import KeyboardLayout as KeyboardLayout
#from keycode_win_LANG import Keycode

def _capsOn():
    return kbd.led_on(Keyboard.LED_CAPS_LOCK)

def _numOn():
    return kbd.led_on(Keyboard.LED_NUM_LOCK)

def _scrollOn():
    return kbd.led_on(Keyboard.LED_SCROLL_LOCK)

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
duckyConsumerKeys = {
    'MK_VOLUP': ConsumerControlCode.VOLUME_INCREMENT, 'MK_VOLDOWN': ConsumerControlCode.VOLUME_DECREMENT, 'MK_MUTE': ConsumerControlCode.MUTE,
    'MK_NEXT': ConsumerControlCode.SCAN_NEXT_TRACK, 'MK_PREV': ConsumerControlCode.SCAN_PREVIOUS_TRACK,
    'MK_PP': ConsumerControlCode.PLAY_PAUSE, 'MK_STOP': ConsumerControlCode.STOP
}

variables = {"$_RANDOM_MIN": 0, "$_RANDOM_MAX": 65535}
internalVariables = {"$_CAPSLOCK_ON": _capsOn, "$_NUMLOCK_ON": _numOn, "$_SCROLLLOCK_ON": _scrollOn}
defines = {}
functions = {}

letters = "abcdefghijklmnopqrstuvwxyz"
numbers = "0123456789"
specialChars = "!@#$%^&*()"

class IF:
    def __init__(self, condition, codeIter):
        self.condition = condition
        self.codeIter = list(codeIter)
        self.lastIfResult = None
    
    def _exitIf(self):
        _depth = 0
        for line in self.codeIter:
            line = self.codeIter.pop(0)
            line = line.strip()
            if line.upper().startswith("END_IF"):
                _depth -= 1
            elif line.upper().startswith("IF"):
                _depth += 1
            if _depth < 0:
                print("No else, exiting" + str(list(self.codeIter)))
                break
        return(self.codeIter)

    def runIf(self):
        if isinstance(self.condition, str):
            self.lastIfResult = evaluateExpression(self.condition)
        elif isinstance(self.condition, bool):
            self.lastIfResult = self.condition
        else:
            raise ValueError("Invalid condition type")

        # print(f"condition {self.condition} result is {self.lastIfResult} since \"$VAR\" is {variables["$VAR"]}, code is {self.codeIter}")
        depth = 0
        for line in self.codeIter:
            line = self.codeIter.pop(0)
            line = line.strip()
            if line == "":
                continue
            # print(line)

            if line.startswith("IF"):
                depth += 1
            elif line.startswith("END_IF"):
                if depth == 0:
                    return(self.codeIter, -1)
                depth -=1

            elif line.startswith("ELSE") and depth == 0:
                # print(f"ELSE LINE {line}, lastIfResult: {self.lastIfResult}")
                if self.lastIfResult is False:
                    line = line[4:].strip()  # Remove 'ELSE' and strip whitespace
                    if line.startswith("IF"):
                        nestedCondition = _getIfCondition(line)
                        # print(f"nested IF {nestedCondition}")
                        self.codeIter, self.lastIfResult = IF(nestedCondition, self.codeIter).runIf()
                        if self.lastIfResult == -1 or self.lastIfResult == True:
                            # print(f"self.lastIfResult {self.lastIfResult}")
                            return(self.codeIter, True)
                    else:
                        return IF(True, self.codeIter).runIf()                        #< Regular ELSE block
                else:
                    self._exitIf()
                    break

            # Process regular lines
            elif self.lastIfResult:
                # print(f"running line {line}")
                self.codeIter = list(parseLine(line, self.codeIter))
        # print("end of if")
        return(self.codeIter, self.lastIfResult)

def _getIfCondition(line):
    return str(line)[2:-4].strip()

def _isCodeBlock(line):
    line = line.upper().strip()
    if line.startswith("IF") or line.startswith("WHILE"):
        return True
    return False

def _getCodeBlock(linesIter):
    """Returns the code block starting at the given line."""
    code = []
    depth = 1
    for line in linesIter:
        line = line.strip()
        if line.upper().startswith("END_"):
            depth -= 1
        elif _isCodeBlock(line):
            depth += 1
        if depth <= 0:
            break
        code.append(line)
    return code

def evaluateExpression(expression):
    """Evaluates an expression with variables and returns the result."""
    # Replace variables (e.g., $FOO) in the expression with their values
    expression = re.sub(r"\$(\w+)", lambda m: str(variables.get(f"${m.group(1)}", 0)), expression)

    expression = expression.replace("^", "**")     #< Replace ^ with ** for exponentiation
    expression = expression.replace("&&", "and")
    expression = expression.replace("||", "or")

    return eval(expression, {}, variables)

def deepcopy(List):
    return(List[:])

def convertLine(line):
    commands = []
    # print(line)
    # loop on each key - the filter removes empty values
    for key in filter(None, line.split(" ")):
        key = key.upper()
        # find the keycode for the command in the list
        command_keycode = duckyKeys.get(key, None)
        command_consumer_keycode = duckyConsumerKeys.get(key, None)
        if command_keycode is not None:
            # if it exists in the list, use it
            commands.append(command_keycode)
        elif command_consumer_keycode is not None:
            # if it exists in the list, use it
            commands.append(1000+command_consumer_keycode)
        elif hasattr(Keycode, key):
            # if it's in the Keycode module, use it (allows any valid keycode)
            commands.append(getattr(Keycode, key))
        else:
            # if it's not a known key name, show the error for diagnosis
            print(f"Unknown key: <{key}>")
    # print(commands)
    return commands

def runScriptLine(line):
    keys = convertLine(line)
    for k in keys:
        if k > 1000:
            consumerControl.press(int(k-1000))
        else:
            kbd.press(k)
    for k in reversed(keys):
        if k > 1000:
            consumerControl.release()
        else:
            kbd.release(k)

def sendString(line):
    layout.write(line)

def replaceVariables(line):
    for var in variables:
        line = line.replace(var, str(variables[var]))
    for var in internalVariables:
        line = line.replace(var, str(internalVariables[var]()))
    return line

def replaceDefines(line):
    for define, value in defines.items():
        line = line.replace(define, value)
    return line

def parseLine(line, script_lines):
    global defaultDelay, variables, functions, defines
    line = line.strip()
    line = line.replace("$_RANDOM_INT", str(random.randint(int(variables.get("$_RANDOM_MIN", 0)), int(variables.get("$_RANDOM_MAX", 65535)))))
    line = replaceDefines(line)
    if line[:10] == "INJECT_MOD":
        line = line[11:]
    elif line.startswith("REM_BLOCK"):
        while line.startswith("END_REM") == False:
            line = next(script_lines).strip()
            # print(line)
    elif(line[0:3] == "REM"):
        pass
    elif line.startswith("HOLD"):
        # HOLD command to press and hold a key
        key = line[5:].strip().upper()
        commandKeycode = duckyKeys.get(key, None)
        if commandKeycode:
            kbd.press(commandKeycode)
        else:
            print(f"Unknown key to HOLD: <{key}>")
    elif line.startswith("RELEASE"):
        # RELEASE command to release a held key
        key = line[8:].strip().upper()
        commandKeycode = duckyKeys.get(key, None)
        if commandKeycode:
            kbd.release(commandKeycode)
        else:
            print(f"Unknown key to RELEASE: <{key}>")
    elif(line[0:5] == "DELAY"):
        line = replaceVariables(line)
        time.sleep(float(line[6:])/1000)
    elif line == "STRINGLN":               #< stringLN block
        line = next(script_lines).strip()
        line = replaceVariables(line)
        while line.startswith("END_STRINGLN") == False:
            sendString(line)
            kbd.press(Keycode.ENTER)
            kbd.release(Keycode.ENTER)
            line = next(script_lines).strip()
            line = replaceVariables(line)
            line = replaceDefines(line)
    elif(line[0:8] == "STRINGLN"):
        sendString(replaceVariables(line[9:]))
        kbd.press(Keycode.ENTER)
        kbd.release(Keycode.ENTER)
    elif line == "STRING":                 #< string block
        line = next(script_lines).strip()
        line = replaceVariables(line)
        while line.startswith("END_STRING") == False:
            sendString(line)
            line = next(script_lines).strip()
            line = replaceVariables(line)
            line = replaceDefines(line)
    elif(line[0:6] == "STRING"):
        sendString(replaceVariables(line[7:]))
    elif(line[0:5] == "PRINT"):
        line = replaceVariables(line[6:])
        print("[SCRIPT]: " + line)
    elif(line[0:6] == "IMPORT"):
        runScript(line[7:])
    elif(line[0:13] == "DEFAULT_DELAY"):
        defaultDelay = int(line[14:]) * 10
    elif(line[0:12] == "DEFAULTDELAY"):
        defaultDelay = int(line[13:]) * 10
    elif(line[0:3] == "LED"):
        if(led.value == True):
            led.value = False
        else:
            led.value = True
    elif(line[0:3] == "LED"):
        if(led.value == True):
            led.value = False
        else:
            led.value = True
    elif(line[:7] == "LED_OFF"):
        led.value = False
    elif(line[:5] == "LED_R"):
        led.value = True
    elif(line[:5] == "LED_G"):
        led.value = True
    elif(line[0:21] == "WAIT_FOR_BUTTON_PRESS"):
        button_pressed = False
        # NOTE: we don't use assincio in this case because we want to block code execution
        while not button_pressed:
            button1.update()

            button1Pushed = button1.fell
            button1Released = button1.rose
            button1Held = not button1.value

            if(button1Pushed):
                print("Button 1 pushed")
                button_pressed = True
    elif line.startswith("VAR"):
        match = re.match(r"VAR\s+\$(\w+)\s*=\s*(.+)", line)
        if match:
            varName = f"${match.group(1)}"
            value = evaluateExpression(match.group(2))
            variables[varName] = value
        else:
            raise SyntaxError(f"Invalid variable declaration: {line}")
    elif line.startswith("$"):
        match = re.match(r"\$(\w+)\s*=\s*(.+)", line)
        if match:
            varName = f"${match.group(1)}"
            expression = match.group(2)
            value = evaluateExpression(expression)
            variables[varName] = value
        else:
            raise SyntaxError(f"Invalid variable update, declare variable first: {line}")
    elif line.startswith("DEFINE"):
        defineLocation = line.find(" ")
        valueLocation = line.find(" ", defineLocation + 1)
        defineName = line[defineLocation+1:valueLocation]
        defineValue = line[valueLocation+1:]
        defines[defineName] = defineValue
    elif line.startswith("FUNCTION"):
        # print("ENTER FUNCTION")
        func_name = line.split()[1]
        functions[func_name] = []
        line = next(script_lines).strip()
        while line != "END_FUNCTION":
            functions[func_name].append(line)
            line = next(script_lines).strip()
    elif line.startswith("WHILE"):
        # print("ENTER WHILE LOOP")
        condition = line[5:].strip()
        loopCode = list(_getCodeBlock(script_lines))
        while evaluateExpression(condition) == True:
            currentIterCode = deepcopy(loopCode)
            print(loopCode)
            while currentIterCode:
                loopLine = currentIterCode.pop(0)
                currentIterCode = list(parseLine(loopLine, iter(currentIterCode)))      #< very inefficient, should be replaced later.

    elif line.upper().startswith("IF"):
        # print("ENTER IF")
        script_lines, ret = IF(_getIfCondition(line), script_lines).runIf()
        print(f"IF returned {ret} code")
    elif line.upper().startswith("END_IF"):
        pass
    elif line == "RANDOM_LOWERCASE_LETTER":
        sendString(random.choice(letters))
    elif line == "RANDOM_UPPERCASE_LETTER":
        sendString(random.choice(letters.upper()))
    elif line == "RANDOM_LETTER":
        sendString(random.choice(letters + letters.upper()))
    elif line == "RANDOM_NUMBER":
        sendString(random.choice(numbers))
    elif line == "RANDOM_SPECIAL":
        sendString(random.choice(specialChars))
    elif line == "RANDOM_CHAR":
        sendString(random.choice(letters + letters.upper() + numbers + specialChars))
    elif line == "VID_RANDOM" or line == "PID_RANDOM":
        for _ in range(4):
            sendString(random.choice("0123456789ABCDEF"))
    elif line == "MAN_RANDOM" or line == "PROD_RANDOM":
        for _ in range(12):
            sendString(random.choice(letters + letters.upper() + numbers))
    elif line == "SERIAL_RANDOM":
        for _ in range(12):
            sendString(random.choice(letters + letters.upper() + numbers + specialChars))
    elif line == "RESET":
        kbd.release_all()
    elif line in functions:
        updated_lines = []
        inside_while_block = False
        for func_line in functions[line]:
            if func_line.startswith("WHILE"):
                inside_while_block = True  # Start skipping lines
                updated_lines.append(func_line)
            elif func_line.startswith("END_WHILE"):
                inside_while_block = False  # Stop skipping lines
                updated_lines.append(func_line)
                parseLine(updated_lines[0], iter(updated_lines))
                updated_lines = []  # Clear updated_lines after parsing
            elif inside_while_block:
                updated_lines.append(func_line)
            elif not (func_line.startswith("END_WHILE") or func_line.startswith("WHILE")):
                parseLine(func_line, iter(functions[line]))
    else:
        runScriptLine(line)
    
    return(script_lines)

kbd = Keyboard(usb_hid.devices)
consumerControl = ConsumerControl(usb_hid.devices)
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

def runScript(file):
    global defaultDelay

    duckyScriptPath = file
    restart = True
    try:
        while restart:
            restart = False
            with open(duckyScriptPath, "r", encoding='utf-8') as f:
                script_lines = iter(f.readlines())
                previousLine = ""
                for line in script_lines:
                    print(f"runScript: {line}")
                    if(line[0:6] == "REPEAT"):
                        for i in range(int(line[7:])):
                            #repeat the last command
                            parseLine(previousLine, script_lines)
                            time.sleep(float(defaultDelay) / 1000)
                    elif line.startswith("RESTART_PAYLOAD"):
                        restart = True
                        break
                    elif line.startswith("STOP_PAYLOAD"):
                        restart = False
                        break
                    else:
                        parseLine(line, script_lines)
                        previousLine = line
                    time.sleep(float(defaultDelay) / 1000)
    except OSError as e:
        print("Unable to open file", file)

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
    if(board.board_id == 'raspberry_pi_pico' or board.board_id == 'raspberry_pi_pico2'):
        blink_pico_led(led)
    elif(board.board_id == 'raspberry_pi_pico_w' or board.board_id == 'raspberry_pi_pico2_w'):
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
