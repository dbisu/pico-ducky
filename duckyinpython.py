# License : GPLv2.0
# copyright (c) 2023  Dave Bailey
# Author: Dave Bailey (dbisu, @daveisu)

import time
import digitalio
from digitalio import DigitalInOut, Pull
from adafruit_debouncer import Debouncer
import board
import os
import pwmio
import asyncio
import usb_hid
from adafruit_hid.keyboard import Keyboard

if board.board_id == 'adafruit_qt2040_trinkey':
    import neopixel_write
    NEOPIXEL_MAX = 64

# comment out these lines for non_US keyboards
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS as KeyboardLayout
from adafruit_hid.keycode import Keycode

# uncomment these lines for non_US keyboards
# replace LANG with appropriate language
#from keyboard_layout_win_LANG import KeyboardLayout
#from keycode_win_LANG import Keycode

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

if(board.board_id == 'raspberry_pi_pico'):
    led = pwmio.PWMOut(board.LED, frequency=5000, duty_cycle=0)
elif(board.board_id == 'raspberry_pi_pico_w'):
    led = digitalio.DigitalInOut(board.LED)
    led.switch_to_output()
elif(board.board_id == 'adafruit_qt2040_trinkey'):
    led = digitalio.DigitalInOut(board.NEOPIXEL)

def led_on():
    global led
    # If the LED is a PWMOut, set the duty cycle to 65535
    # This is for the generic Pico
    if isinstance(led, pwmio.PWMOut):
        led.duty_cycle = 65535
    # If the LED is a DigitalInOut
    elif isinstance(led, digitalio.DigitalInOut):
        # If the board has a NEOPIXEL use that as the LED (trinkey)
        if hasattr(board, 'NEOPIXEL'):
            neopixel_write.neopixel_write(led, bytearray([NEOPIXEL_MAX, NEOPIXEL_MAX, NEOPIXEL_MAX]))
        # Otherwise, use the normal LED (pico w)
        else:
            led.value = True
    
def led_off():
    global led
    # If the LED is a PWMOut, set the duty cycle to 0
    if isinstance(led, pwmio.PWMOut):
        led.duty_cycle = 0
    # If the LED is a DigitalInOut
    elif isinstance(led, digitalio.DigitalInOut):
        # If the board has a NEOPIXEL use that as the LED (trinkey)
        if hasattr(board, 'NEOPIXEL'):
           neopixel_write.neopixel_write(led, bytearray([0, 0, 0]))
        # Otherwise, use the normal LED (pico w)
        else:
            led.value = False 

LED_STATE = False

def toggleLED():
    global LED_STATE
    # LED_STATE = True == led on
    if LED_STATE:
        led_off()
        LED_STATE = False
    else:
        led_on()
        LED_STATE = True

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

def runScriptLine(line):
    for k in line:
        kbd.press(k)
    kbd.release_all()

def sendString(line):
    layout.write(line)

DEFAULT_DELAY = 0

def parseLine(line):
    global DEFAULT_DELAY
    if(line[0:3] == "REM"):
        # ignore ducky script comments
        pass
    elif(line[0:5] == "DELAY"):
        time.sleep(float(line[6:])/1000)
    elif(line[0:6] == "STRING"):
        sendString(line[7:])
    elif(line[0:5] == "PRINT"):
        print("[SCRIPT]: " + line[6:])
    elif(line[0:6] == "IMPORT"):
        runScript(line[7:])
    elif(line[0:13] == "DEFAULT_DELAY"):
        DEFAULT_DELAY = int(line[14:]) * 10
    elif(line[0:12] == "DEFAULTDELAY"):
        DEFAULT_DELAY = int(line[13:]) * 10
    elif(line[0:3] == "LED"):
        toggleLED()
    else:
        newScriptLine = convertLine(line)
        runScriptLine(newScriptLine)

kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayout(kbd)

def getProgrammingStatus():
    # check GP0 for setup mode
    # see setup mode for instructions
    # If using the Trinkey, the BOOT button is used instead of GP0
    progStatus = False
    if (board.board_id == 'adafruit_qt2040_trinkey'):
        # Get the setup timeout from the environment file settings.toml. default to no setup time
        # Since this will run rapidly after boot, it could trigger off the storage button press
        timeout = os.getenv('one_button_setup_timeout', 500)
        if timeout is not None:
            print('Waiting for button press to decide if script should run')
            import supervisor
            button = digitalio.DigitalInOut(board.BUTTON)
            button.switch_to_input()
            timeout = supervisor.ticks_ms() + int(timeout)
            # Loop for the timeout, setting progStatus to True if the button is pressed
            while supervisor.ticks_ms() < timeout:
                if not button.value:
                    progStatus = True
                    break
            # After the timeout
            else:
                progStatus = False
            # Deinit the button for later use
            button.deinit()
    # Non-Trinkey boards
    else:
        progStatusPin = digitalio.DigitalInOut(board.GP0)
        progStatusPin.switch_to_input(pull=digitalio.Pull.UP)
        progStatus = not progStatusPin.value
    return(progStatus)

def runScript(file):
    global DEFAULT_DELAY
    duckyScriptPath = file
    try:
        f = open(duckyScriptPath,"r",encoding='utf-8')
        previousLine = ""
        for line in f:
            line = line.rstrip()
            if(line[0:6] == "REPEAT"):
                for i in range(int(line[7:])):
                    #repeat the last command
                    parseLine(previousLine)
                    time.sleep(float(DEFAULT_DELAY)/1000)
            else:
                parseLine(line)
                previousLine = line
            time.sleep(float(DEFAULT_DELAY)/1000)
    except OSError as e:
        print("Unable to open file ", file)

# Global list of payloads, and the pin to check for each payload
# Will apply in the order they are added to the list
payloads = []

if (board.board_id == 'adafruit_qt2040_trinkey'):
    # With only a single button, alternate payloads are not easy
    pass
else:
    # Other boards need a switch to select the payload
    payload1Pin = digitalio.DigitalInOut(board.GP4)
    payload1Pin.switch_to_input(pull=digitalio.Pull.UP)
    payloads.append(("payload1.dd", payload1Pin))

    payload2Pin = digitalio.DigitalInOut(board.GP5)
    payload2Pin.switch_to_input(pull=digitalio.Pull.UP)
    payloads.append(("payload2.dd", payload2Pin))
    
    payload3Pin = digitalio.DigitalInOut(board.GP10)
    payload3Pin.switch_to_input(pull=digitalio.Pull.UP)
    payloads.append(("payload3.dd", payload3Pin))

    payload4Pin = digitalio.DigitalInOut(board.GP11)
    payload4Pin.switch_to_input(pull=digitalio.Pull.UP)
    payloads.append(("payload4.dd", payload4Pin))

def selectPayload():
    global payloads
    # Go over all the loaded payload
    for payload_name, check_pin in payloads:
        # These are all pull-up, so False means the switch is pressed
        if not check_pin.value:
            # If the switch is pressed, set the payload to the key
            payload = payload_name
            break
    else:
        # If we made it through the loop without a break, no switch is pressed
        # So try to get the default payload from the environment file
        # If it's not there, default to payload.dd
        payload = os.getenv('default_payload', "payload.dd")

    return payload

async def blink_neopixel_led():
    global led
    print("starting blink_neopixel_led")
    # led_state = True == led off
    # led_state = False == led on
    led_state = False
    while True:
        if led_state:
            for i in range(100):
                # While the LED is off, fade it up
                if i < NEOPIXEL_MAX:
                    neopixel_write.neopixel_write(led, bytearray([i, i, i]))
                await asyncio.sleep(0.01)
            led_state = False
        else:
            for i in range(100):
                # While the LED is on, fade it down
                if i <= NEOPIXEL_MAX:
                    neopixel_write.neopixel_write(led, bytearray([NEOPIXEL_MAX - i, NEOPIXEL_MAX - i, NEOPIXEL_MAX - i]))
                await asyncio.sleep(0.01)
            led_state = True
        await asyncio.sleep(0.1)

async def blink_pwm_led():
    global led
    print("starting blink_pwm_led")
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

async def blink_binary_led():
    global led
    print("starting blink_binary_led")
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

async def blink_led():
    global led
    # If the LED is a PWMOut, blink it
    if isinstance(led, pwmio.PWMOut):
        await blink_pwm_led()
    # Otherwise decide if it's a neopixel or binary LED
    elif isinstance(led, digitalio.DigitalInOut):
        if hasattr(board, 'NEOPIXEL'):
            await blink_neopixel_led()
        else:
            await blink_binary_led()

async def monitor_buttons():
    # Button to re-run the payload
    if (board.board_id == 'adafruit_qt2040_trinkey'):
        re_run_pin = digitalio.DigitalInOut(board.BUTTON)
        re_run_pin.switch_to_input(pull=digitalio.Pull.UP)
    else:
        re_run_pin = digitalio.DigitalInOut(board.GP22)
        re_run_pin.switch_to_input(pull=digitalio.Pull.UP)
    re_run_button = Debouncer(re_run_pin)

    print("Starting monitoring of buttons")
    re_run_down = False
    while True:
        re_run_button.update()

        re_run_pushed = re_run_button.fell
        re_run_released = re_run_button.rose
        re_run_held = not re_run_button.value

        if(re_run_pushed):
            print("Re-run button pushed")
            re_run_down = True
        if(re_run_released):
            print("Re-run button released")
            if(re_run_down):
                print("push and released")

        if(re_run_released):
            if(re_run_down):
                # Run selected payload
                payload = selectPayload()
                print("Running ", payload)
                runScript(payload)
                print("Done")
            re_run_down = False

        await asyncio.sleep(0)
