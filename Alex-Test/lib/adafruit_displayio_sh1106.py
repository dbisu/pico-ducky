# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2021 ladyada for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_displayio_sh1106`
================================================================================

DisplayIO compatible library for SH1106 OLED displays


* Author(s): ladyada

Implementation Notes
--------------------

**Hardware:**

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

# imports
import displayio

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_DisplayIO_SH1106.git"


# Sequence from sh1106 framebuf driver formatted for displayio init
_INIT_SEQUENCE = (
    b"\xae\x00"  # display off, sleep mode
    b"\xd5\x01\x80"  # divide ratio/oscillator: divide by 2, fOsc (POR)
    b"\xa8\x01\x3f"  # multiplex ratio = 64 (POR)
    b"\xd3\x01\x00"  # set display offset mode = 0x0
    b"\x40\x00"  # set start line
    b"\xad\x01\x8b"  # turn on DC/DC
    b"\xa1\x00"  # segment remap = 1 (POR=0, down rotation)
    b"\xc8\x00"  # scan decrement
    b"\xda\x01\x12"  # set com pins
    b"\x81\x01\xff"  # contrast setting = 0xff
    b"\xd9\x01\x1f"  # pre-charge/dis-charge period mode: 2 DCLKs/2 DCLKs (POR)
    b"\xdb\x01\x40"  # VCOM deselect level = 0.770 (POR)
    b"\x20\x01\x20"  #
    b"\x33\x00"  # turn on VPP to 9V
    b"\xa6\x00"  # normal (not reversed) display
    b"\xa4\x00"  # entire display off, retain RAM, normal status (POR)
    b"\xaf\x00"  # DISPLAY_ON
)


class SH1106(displayio.Display):
    """
    SH1106 driver for use with DisplayIO

    :param bus: The bus that the display is connected to.
    :param int width: The width of the display. Maximum of 132
    :param int height: The height of the display. Maximum of 64
    :param int rotation: The rotation of the display. 0, 90, 180 or 270.
    """

    def __init__(self, bus, **kwargs):
        init_sequence = bytearray(_INIT_SEQUENCE)
        super().__init__(
            bus,
            init_sequence,
            **kwargs,
            color_depth=1,
            grayscale=True,
            pixels_in_byte_share_row=False,  # in vertical (column) mode
            data_as_commands=True,  # every byte will have a command byte preceeding
            brightness_command=0x81,
            single_byte_bounds=True,
            # for sh1107 use column and page addressing.
            #                lower column command = 0x00 - 0x0F
            #                upper column command = 0x10 - 0x17
            #                set page address     = 0xB0 - 0xBF (16 pages)
            SH1107_addressing=True,
        )
        self._is_awake = True  # Display starts in active state (_INIT_SEQUENCE)

    @property
    def is_awake(self):
        """
        The power state of the display. (read-only)

        `True` if the display is active, `False` if in sleep mode.
        """
        return self._is_awake

    def sleep(self):
        """
        Put display into sleep mode. The display uses < 5uA in sleep mode.

        Sleep mode does the following:

            1) Stops the oscillator and DC-DC circuits
            2) Stops the OLED drive
            3) Remembers display data and operation mode active prior to sleeping
            4) The MP can access (update) the built-in display RAM
        """
        if self._is_awake:
            self.bus.send(int(0xAE), "")  # 0xAE = display off, sleep mode
            self._is_awake = False

    def wake(self):
        """
        Wake display from sleep mode
        """
        if not self._is_awake:
            self.bus.send(int(0xAF), "")  # 0xAF = display on
            self._is_awake = True
