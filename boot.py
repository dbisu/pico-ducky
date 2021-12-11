from board import *
import digitalio
import storage
import board
import time

time.sleep(3)

noStorageStatus = False
noStoragePin = digitalio.DigitalInOut(board.IO18) ## If the down button is pressed on the S2 Nugget
noStoragePin.switch_to_input(pull=digitalio.Pull.UP)
noStorageStatus = not noStoragePin.value

if(noStorageStatus == True):
    # don't show USB drive to host PC
    storage.disable_usb_drive()
    print("Disabling USB drive")
else:
    # normal boot
    print("USB drive enabled")
# Write your code here :-)
