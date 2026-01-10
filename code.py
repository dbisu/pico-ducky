# License : GPLv2.0
# copyright (c) 2023  Dave Bailey
# Author: Dave Bailey (dbisu, @daveisu)
# Pico and Pico W board support


import supervisor
import os
import pwmio
import time
import digitalio
from board import *
import board
from duckyinpython import *
if(board.board_id == 'raspberry_pi_pico_w' or board.board_id == 'raspberry_pi_pico2_w'):
    import wifi
    from webapp import *


# sleep at the start to allow the device to be recognized by the host computer
time.sleep(.5)

def startWiFi():
    import ipaddress
    # Get wifi details and more from a secrets.py file
    try:
        from secrets import secrets
    except ImportError:
        print("WiFi secrets are kept in secrets.py, please add them there!")
        raise

    print("Connect wifi")
    #wifi.radio.connect(secrets['ssid'],secrets['password'])
    wifi.radio.start_ap(secrets['ssid'],secrets['password'])

    HOST = repr(wifi.radio.ipv4_address_ap)
    PORT = 80        # Port to listen on
    print(HOST,PORT)

# turn off automatically reloading when files are written to the pico
#supervisor.disable_autoreload()
supervisor.runtime.autoreload = False

if(board.board_id == 'raspberry_pi_pico' or board.board_id == 'raspberry_pi_pico2'):
    led = pwmio.PWMOut(board.LED, frequency=5000, duty_cycle=0)
elif(board.board_id == 'raspberry_pi_pico_w' or board.board_id == 'raspberry_pi_pico2_w'):
    led = digitalio.DigitalInOut(board.LED)
    led.switch_to_output()

async def run_payload_on_startup():
    progStatus = False
    progStatus = getProgrammingStatus()
    print("progStatus", progStatus)
    if(progStatus == False):
        print("Finding payload")
        if "loot.bin" in os.listdir("/"):
            print("loot.bin exists, skipping payload execution.")
        else:
            payload = selectPayload()
            await asyncio.sleep(0.1)
            print("Running")
            await runScript(payload)
    else:
        print("Done")


led_state = False



async def main_loop():
    global led,button1

    button_task = asyncio.create_task(monitor_buttons(button1))
    payload_task = asyncio.create_task(run_payload_on_startup())
    led_task = asyncio.create_task(monitor_led_changes())
    if(board.board_id == 'raspberry_pi_pico_w' or board.board_id == 'raspberry_pi_pico2_w'):
        pico_led_task = asyncio.create_task(blink_pico_w_led(led))
        print("Starting Wifi")
        startWiFi()
        print("Starting Web Service")
        webservice_task = asyncio.create_task(startWebService())
        await asyncio.gather(pico_led_task, button_task, webservice_task, payload_task, led_task)
    else:
        pico_led_task = asyncio.create_task(blink_pico_led(led))
        await asyncio.gather(pico_led_task, button_task, payload_task, led_task )

asyncio.run(main_loop())
