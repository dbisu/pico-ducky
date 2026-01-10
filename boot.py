# License : GPLv2.0
# copyright (c) 2023  Dave Bailey
# Author: Dave Bailey (dbisu, @daveisu)
# Pico and Pico W board support

from board import *
import board
import digitalio
import storage
import os

def is_exfil_enabled(payload_path="payload.dd"):
    try:
        with open(payload_path, "r") as f:
            for line in f:
                if "$_EXFIL_MODE_ENABLED" in line and "TRUE" in line.upper():
                    return True
    except OSError:
        pass
    return False

exfil_enabled = is_exfil_enabled()
loot_exists = "loot.bin" in os.listdir("/")
noStorage = False
noStoragePin = digitalio.DigitalInOut(GP15)
noStoragePin.switch_to_input(pull=digitalio.Pull.UP)
noStorageStatus = noStoragePin.value

# If GP15 is not connected, it will default to being pulled high (True)
# If GP is connected to GND, it will be low (False)

# Pico:
#   GP15 not connected == USB visible
#   GP15 connected to GND == USB not visible

# Pico W:
#   GP15 not connected == USB NOT visible
#   GP15 connected to GND == USB visible
if exfil_enabled:
    if not loot_exists:
        storage.disable_usb_drive()
if(board.board_id == 'raspberry_pi_pico' or board.board_id == 'raspberry_pi_pico2'):
    # On Pi Pico, default to USB visible
    noStorage = not noStorageStatus
elif(board.board_id == 'raspberry_pi_pico_w' or board.board_id == 'raspberry_pi_pico2_w'):
    # on Pi Pico W, default to USB hidden by default
    # so webapp can access storage
    noStorage = noStorageStatus

if(noStorage == True):
    # don't show USB drive to host PC
    storage.disable_usb_drive()
    print("Disabling USB drive")
else:
    # normal boot
    print("USB drive enabled")


