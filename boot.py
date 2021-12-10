from board import *
import digitalio
import storage
import usb_midi
import time
led = digitalio.DigitalInOut(LED)
led.direction = digitalio.Direction.OUTPUT
storage.remount("/", True)

noStorageStatus = False
noStoragePin = digitalio.DigitalInOut(GP15)
noStoragePin.switch_to_input(pull=digitalio.Pull.UP)

if(noStoragePin.value == True):
    # boot as stealth mode
    storage.disable_usb_drive()
    usb_cdc.disable()
    usb_midi.disable()
    usb_cdc.enable(console=False, data=False)
    print("Disabling USB drive")
else:
    # normal boot
    storage.unmount()
    print("Enabling USB drive")
