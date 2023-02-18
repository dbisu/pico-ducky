# License : GPLv2.0
# copyright (c) 2023  Dave Bailey
# Author: Dave Bailey (dbisu, @daveisu)
# Pico and Pico W board support

from board import *
import board
import digitalio
import storage

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

if(board.board_id == 'raspberry_pi_pico'):
    # On Pi Pico, default to USB visible
    noStorage = not noStorageStatus
elif(board.board_id == 'raspberry_pi_pico_w'):
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
