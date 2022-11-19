# License : GPLv2.0
# copyright (c) 2021  Dave Bailey
# Author: Dave Bailey (dbisu, @daveisu)
# FeatherS2 board support


import usb_hid
from adafruit_hid.keyboard import Keyboard

# comment out these lines for non_US keyboards
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS as KeyboardLayout
from adafruit_hid.keycode import Keycode

# uncomment these lines for non_US keyboards
# replace LANG with appropriate language
#from keyboard_layout_win_LANG import KeyboardLayout
#from keycode_win_LANG import Keycode

import supervisor


import time
import digitalio
from board import *
import board
from duckyinpython import *
if(board.board_id == 'raspberry_pi_pico_w'):
    import wifi
    from webapp import *


# sleep at the start to allow the device to be recognized by the host computer
time.sleep(.5)

def startWiFi():
    # Get wifi details and more from a secrets.py file
    try:
        from secrets import secrets
    except ImportError:
        print("WiFi secrets are kept in secrets.py, please add them there!")
        raise

    print("Connect wifi")
    #wifi.radio.connect(secrets['ssid'],secrets['password'])
    #wifi.radio.start_ap(secrets['ssid'],secrets['password']) # currently not working

    HOST = repr(wifi.radio.ipv4_address_ap)
    PORT = 80        # Port to listen on
    print(HOST,PORT)

# turn off automatically reloading when files are written to the pico
#supervisor.disable_autoreload()
supervisor.runtime.autoreload = False

led = pwmio.PWMOut(board.LED, frequency=5000, duty_cycle=0)


progStatus = False
progStatus = getProgrammingStatus()

if(progStatus == False):
    # not in setup mode, inject the payload
    payload = selectPayload()
    print("Running ", payload)
    runScript(payload)

    print("Done")
else:
    print("Update your payload")

led_state = False

async def main_loop():
    global led,button1
    pico_led_task = asyncio.create_task(blink_pico_led(led))
    button_task = asyncio.create_task(monitor_buttons(button1))
    task_list = [pico_led_task, button_task]
    if(board.board_id == 'raspberry_pi_pico_w'):
        print("Starting Wifi")
        startWiFi()
        print("Starting Web Service")
        webservice_task = asyncio.create_task(startWebService())
        task_list.append(webservice_task)
    await asyncio.gather(*task_list)

asyncio.run(main_loop())
