# License : GPLv2.0
# copyright (c) 2023  Dave Bailey
# Author: Dave Bailey (dbisu, @daveisu)
# Pico and Pico W board support
# Beta Trinkey QT2040 support

import board
import digitalio
import storage

noStorage = False

# If GP15 is not connected, it will default to being pulled high (True)
# If GP is connected to GND, it will be low (False)

# Pico:
#   GP15 not connected == USB visible
#   GP15 connected to GND == USB not visible

# Pico W:
#   GP15 not connected == USB NOT visible
#   GP15 connected to GND == USB visible

# Trinkey QT2040:
#   Boot button pressed during timeout == USB visible
#   Boot button not pressed == USB not visible 

if(board.board_id == 'raspberry_pi_pico'):
    noStoragePin = digitalio.DigitalInOut(board.GP15)
    noStoragePin.switch_to_input(pull=digitalio.Pull.UP)
    noStorageStatus = noStoragePin.value
    # On Pi Pico, default to USB visible
    noStorage = not noStorageStatus
    noStoragePin.deinit()
elif(board.board_id == 'raspberry_pi_pico_w'):
    noStoragePin = digitalio.DigitalInOut(board.GP15)
    noStoragePin.switch_to_input(pull=digitalio.Pull.UP)
    noStorageStatus = noStoragePin.value
    # on Pi Pico W, default to USB hidden by default
    # so webapp can access storage
    noStorage = noStorageStatus
    noStoragePin.deinit()
elif (board.board_id == 'adafruit_qt2040_trinkey'):
    # Import os to read the environment file
    import os
    # Import supervisor to wait for the timeout
    import supervisor
    # Listen for the BOOT button being pressed
    button = digitalio.DigitalInOut(board.BUTTON)
    # There is a hardware pullup on this pin, so no need to set it high
    button.switch_to_input()
    # Read the timeout from the environment file settings.toml. default to 500ms
    wait_timeout = os.getenv('trinkey_storage_timeout', 500)
    # Add the timeout to the current time to final timeout time
    wait_timeout = supervisor.ticks_ms() + int(wait_timeout)
    # Loop for the timeout seeing if the button is pressed
    while supervisor.ticks_ms() < wait_timeout:
        # By default the BOOT button is pulled high in hardware
        # so button.value will be True unless the button is pressed
        if not button.value:
            print('Not disabling USB drive on Trinkey QT2040')
            break
    # If the loop completes that means the button was not pressed
    else:
        # And storage should be disabled
        noStorage = True
    # Deinit the BOOT button for later use
    button.deinit()
        

if(noStorage == True):
    # don't show USB drive to host PC
    storage.disable_usb_drive()
    print("Disabling USB drive")
else:
    # normal boot
    print("USB drive enabled")
