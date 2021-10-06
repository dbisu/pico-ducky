<h1 align="center">pico-ducky</h1>

<div align="center">
  <strong>Make a cheap but powerful USB Rubber Ducky with a Raspberry Pi Pico</strong>
</div>

<br />

<div align="center">
  <img alt="GitHub code size in bytes" src="https://img.shields.io/github/languages/code-size/dbisu/pico-ducky">
  <img alt="GitHub license" src="https://img.shields.io/github/license/dbisu/pico-ducky">
  <a href="https://github.com/dbisu/pico-ducky/graphs/contributors"><img alt="GitHub contributors" src="https://img.shields.io/github/contributors/dbisu/pico-ducky"></a>
  <img alt="GitHub commit activity" src="https://img.shields.io/github/commit-activity/m/dbisu/pico-ducky">
  <img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/dbisu/pico-ducky">
</div>

<br />

## Usage

Install and have your USB Rubber Ducky working in less than 5 minutes.

1. Download the [latest release](https://github.com/cycool29/pico-ducky/releases/download/v1.0/pico-ducky-v1.0.zip) and extract it.

2. Plug your Raspberry Pi Pico into a USB port. It should show up as a mass storage device named `RPI-RP2`.

3. Copy the `adafruit-circuitpython-raspberry_pi_pico-en_US-7.0.0.uf2` file from the folder you extracted the zip to the root of the Pico (`RPI-RP2`). The device will reboot and after a second or so, and reconnect as `CIRCUITPY`, with a `lib` folder, `boot_out.txt` and `code.py` .

5. Navigate to the folder you extracted the zip and copy the `adafruit_hid` folder to the `lib` folder in your Raspberry Pi Pico.

6. Delete the `code.py` in your Raspberry Pi Pico, copy `code.py` from the folder you extracted the zip to your Raspberry Pi Pico.

7. Find a script [here](https://github.com/hak5darren/USB-Rubber-Ducky/wiki/Payloads) or [create your own one using Ducky Script](https://github.com/hak5darren/USB-Rubber-Ducky/wiki/Duckyscript) and save it as `payload.dd` in your Raspberry Pi Pico root.

8. Finally, make sure you have a `lib` folder with `adafruit-hid` folder in it, a `boot_out.txt`, `code.py` and `payload.dd`. Now your Raspberry Pi Pico is a **USB Rubber Ducky**. 

9. Be careful, if your device isn't in [setup mode](#setup-mode), the device will reboot and after half a second, the script will run.

## Setup mode

To edit the payload, enter setup mode by connecting the pin 1 (`GP0`) to pin 3 (`GND`), this will stop the pico-ducky from injecting the payload in your own machine.
The easiest way to so is by using a jumper wire between those pins as seen bellow.

![Setup mode with a jumper](images/setup-mode.png)

## Reset 

If you don't have a jumper wire or you want a more convenient way to edit your payload, resetting it will be a great choice.

1. Hold the `BOOTSEL` button while plugging your Raspberry Pi Pico to a USB port.
2. Download the [flash_nuke.uf2](https://datasheets.raspberrypi.org/soft/flash_nuke.uf2) file.
3. Copy the `flash_nuke.uf2` file to your Raspberry Pi Pico.
4. Your Raspberry Pi Pico will reboot after half a second and your Raspberry Pi Pico is resetted.

Now you can just repeat steps in [usage](#usage) to setup your pico-ducky.

![BOOTSEL](images/bootsel.png)

## USB enable/disable mode

If you need the pico-ducky to not show up as a USB mass storage device for stealth, follow these instructions.  
1. Enter [setup mode](#setup-mode).  
2. Download [boot.py](https://github.com/dbisu/pico-ducky/raw/main/boot.py).
3. Copy `boot.py` to the root of the pico-ducky.  
4. Copy your payload script to the pico-ducky.  
5. Disconnect the pico from your host PC.
6. Connect a jumper wire between pin 18 and pin 20. This will prevent the pico-ducky from showing up as a USB drive when plugged into the target device.  
7. Remove the jumper wire and reconnect to your PC to reprogram.

The default mode is USB mass storage enabled.   

![USB enable/disable mode](images/usb-boot-mode.png)


## Troubleshoot

Read here for some known troubleshooting guides. If the issue still persists, please [open a new issue](https://github.com/dbisu/pico-ducky/issues/new/choose).

- After copy `adafruit-circuitpython-raspberry_pi_pico-en_US-7.0.0.uf2` file to my Raspberry Pi Pico, it reboots but only shows `boot_out.txt`

  - Try [reset](#reset) you Raspberry Pi Pico and download the `adafruit-circuitpython-raspberry_pi_pico-en_US-7.0.0.uf2` file again and repeat the steps.
  If it still not showing up, you may manually create the `lib` and `code.py`, that won't affect the effect of your pico-ducky.
  
- When saving `code.py` or `payload.dd`, system prompt not enough space

  - [Reset](#reset) you Raspberry Pi Pico and repeat the steps again. There may have some hidden files on your Raspberry Pi Pico.


- Raspberry Pi Pico won't boot up

  - Try different USB cable. You need a power + data micro-USB cable when using the Raspberry Pi Pico, as this lets the computer and Raspberry Pi Pico 'talk' to each other for programming.



## Useful links and resources

### Docs

[CircuitPython](https://circuitpython.readthedocs.io/en/6.3.x/README.html)

[CircuitPython HID](https://learn.adafruit.com/circuitpython-essentials/circuitpython-hid-keyboard-and-mouse)

[Ducky Script](https://github.com/hak5darren/USB-Rubber-Ducky/wiki/Duckyscript)

### Video tutorials

[pico-ducky tutorial by **NetworkChuck**](https://www.youtube.com/watch?v=e_f9p-_JWZw)

[USB Rubber Ducky playlist by **Hak5**](https://www.youtube.com/playlist?list=PLW5y1tjAOzI0YaJslcjcI4zKI366tMBYk)

[CircuitPython tutorial on the Raspberry Pi Pico by **DroneBot Workshop**](https://www.youtube.com/watch?v=07vG-_CcDG0)
