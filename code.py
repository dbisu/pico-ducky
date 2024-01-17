# License : GPLv2.0
# copyright (c) 2023  Dave Bailey
# Author: Dave Bailey (dbisu, @daveisu)
# Pico and Pico W board support
# Beta Trinkey QT2040 support

import supervisor
import time
import digitalio
import board
from duckyinpython import *
if(board.board_id == 'raspberry_pi_pico_w'):
    import wifi
    from webapp import *

# Wait half a second to allow the device to be recognized by the host computer 
wait_time = time.monotonic() + .5

# turn off automatically reloading when files are written to the pico
#supervisor.disable_autoreload()
supervisor.runtime.autoreload = False

payload = None
progStatus = False
progStatus = getProgrammingStatus()
print("progStatus", progStatus)
if(progStatus == False):
    print("Finding payload")
    # not in setup mode, inject the payload
    payload = selectPayload()
else:
    print("Update your payload")

# Wait for the half second timeout to expire before running the payload
while time.monotonic() < wait_time:
    pass

# If we are not in setup mode, run the payload
if progStatus == False:
    print("Running ", payload)
    runScript(payload)
    print("Done")

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

async def main_loop():
    tasks = []
    button_task = asyncio.create_task(monitor_buttons())
    tasks.append(button_task)
    led_task = asyncio.create_task(blink_led())
    tasks.append(led_task)
    if(board.board_id == 'raspberry_pi_pico_w'):
        print("Starting Wifi")
        startWiFi()
        print("Starting Web Service")
        webservice_task = asyncio.create_task(startWebService())
        tasks.append(webservice_task)
    # Pass the task list as *args to wait for them all to complete
    await asyncio.gather(*tasks)

asyncio.run(main_loop())
