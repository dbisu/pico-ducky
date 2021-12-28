<h1 align="center">Rubber-Nugget</h1>

<div align="center">
  <strong>Deploy up to 4 different Duckyscript payloads with an S2 Wi-Fi Nugget</strong>
  
</div>
<br />
<p align="center">
  <img src="https://cdn.shopify.com/s/files/1/2779/8142/products/S2-Nugget_1024x1024.png" alt="S2 Nugget" title="S2 Nugget" width="500"/>
</p>
<div align="center">
  <img alt="GitHub code size in bytes" src="https://img.shields.io/github/languages/code-size/dbisu/pico-ducky">
  <img alt="GitHub license" src="https://img.shields.io/github/license/dbisu/pico-ducky">
  <a href="https://github.com/dbisu/pico-ducky/graphs/contributors"><img alt="GitHub contributors" src="https://img.shields.io/github/contributors/dbisu/pico-ducky"></a>
  <img alt="GitHub commit activity" src="https://img.shields.io/github/commit-activity/m/dbisu/pico-ducky">
  <img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/dbisu/pico-ducky">
</div>

<br />

This is a port of the Pico-Ducky project by Dave Bailey (dbisu, @daveisu), converted to run on the S2 Wi-Fi Nugget

You can buy one here: (https://retia.io/products/wi-fi-nugget-s2-nugget-esp32s2).


## Major changes:

To hide the USB drive, hold the DOWN button when plugging in the S2 Nugget and release when the menu face appears.

To auto-inject payload 1, hold the RIGHT button when plugging in the S2 Nugget.

Once the menu face appears, you can run any one of 4 duckyscript payloads: 
*  press the UP button to run payload1.dd
*  press the DOWN button to run payload2.dd 
*  press the LEFT button to run payload3.dd
*  press and the RIGHT button to run payload4.dd

To add new payloads, replace the payload.dd files on the CircuitPython drive.

## Install

Install and have your USB Rubber Ducky working in less than 5 minutes.

1. Download [CircuitPython for the S2 Mini](https://circuitpython.org/board/lolin_s2_mini/). *Updated to 7.0.0

2. Plug the device into a USB port while holding the RESET button, click the 0 button, then release the RESET button. It will show up as a removable media device named `S2MINIBOOT`.

3. Copy the downloaded `.uf2` file to the root of the S2 Mini (`S2MINIBOOT`). The device will reboot and after a second or so, it will reconnect as `CIRCUITPY`.

4. Download and extract the .ZIP file for this project on your computer.

5. Copy the following files and folders to your Nugget: `code.py`, `boot.py`, `lib`, `faces`, `payload1.dd`, `payload2.dd`, `payload3.dd`, `payload4.dd` 

6. Find a script [here](https://github.com/hak5darren/USB-Rubber-Ducky/wiki/Payloads) or [create your own one using Ducky Script](https://github.com/hak5darren/USB-Rubber-Ducky/wiki/Duckyscript) and save it as `payload1.dd` in the S2 Nugget. You can add to 4 payloads the same way, adding a number to each payload file name.

7. If you want device to load in stealth mode, hold the down button when plugging in your Nugget to prevent the USB drive from appearing.

### Attack mode

To edit a payload, setup mode is entered automatically when inserted. You can deploy a payload at any time by pressing one of the 4 payload buttons.

If you want to inject a script with maximum speed, hold the RIGHT button down when inserting your S2 Nugget into the target computer. 

This will cause payload1.dd to be automatically injected as soon as the S2 Nugget is powered up.

### USB enable/disable mode

If you need the S2 Nugget to not show up as a USB mass storage device for stealth, follow these instructions:

Hold the DOWN button when plugging in your S2 Nugget. It should load the menu and inject payloads, but not appear as a USB device.

Reset the board without holding down the button to make the device appear as a USB drive again.

### Changing Keyboard Layouts

Copied from [Neradoc/Circuitpython_Keyboard_Layouts](https://github.com/Neradoc/Circuitpython_Keyboard_Layouts/blob/main/PICODUCKY.md)  

#### How to use one of these layouts with the RubberNugget repository.

**Go to the [latest release page](https://github.com/Neradoc/Circuitpython_Keyboard_Layouts/releases/latest), look if your language is in the list.**

#### If your language/layout is in the bundle

Download the `py` zip, named `circuitpython-keyboard-layouts-py-XXXXXXXX.zip`

**NOTE: You can use the mpy version targetting the version of Circuitpython that is on the device, but on the S2 Nugget you don't need it - they only reduce file size and memory use on load, which the S2 Nugget has plenty of.**

#### If your language/layout is not in the bundle

Try the online generator, it should get you a zip file with the bundles for yout language

https://www.neradoc.me/layouts/

#### Now you have a zip file

#### Find your language/layout in the lib directory

For a language `LANG`, copy the following files from the zip's `lib` folder to the `lib` directory of the board.  
**DO NOT** modify the adafruit_hid directory. Your files go directly in `lib`.  
**DO NOT** change the names or extensions of the files. Just pick the right ones.  
Replace `LANG` with the letters for your language of choice.

- `keyboard_layout.py`
- `keyboard_layout_win_LANG.py`
- `keycode_win_LANG.py`

Don't forget to get [the adafruit_hid library](https://github.com/adafruit/Adafruit_CircuitPython_HID/releases/latest).

This is what it should look like **if your language is French for example**.

![CIRCUITPY drive screenshot](https://github.com/Neradoc/Circuitpython_Keyboard_Layouts/raw/main/docs/drive_pico_ducky.png)

#### Modify the RubberNugget code to use your language file:

At the start of the file comment out these lines:

```py
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS as KeyboardLayout
from adafruit_hid.keycode import Keycode
```

Uncomment these lines:  
*Replace `LANG` with the letters for your language of choice. The name must match the file (without the py or mpy extension).*
```py
from keyboard_layout_win_LANG import KeyboardLayout
from keycode_win_LANG import Keycode
```

## Useful links and resources

### Docs

[CircuitPython](https://circuitpython.readthedocs.io/en/6.3.x/README.html)

[CircuitPython HID](https://learn.adafruit.com/circuitpython-essentials/circuitpython-hid-keyboard-and-mouse)

[Ducky Script](https://github.com/hak5darren/USB-Rubber-Ducky/wiki/Duckyscript)

### Video tutorials

[pico-ducky tutorial by **NetworkChuck**](https://www.youtube.com/watch?v=e_f9p-_JWZw)

[USB Rubber Ducky playlist by **Hak5**](https://www.youtube.com/playlist?list=PLW5y1tjAOzI0YaJslcjcI4zKI366tMBYk)

[CircuitPython tutorial on the Raspberry Pi Pico by **DroneBot Workshop**](https://www.youtube.com/watch?v=07vG-_CcDG0)
