# SPDX-FileCopyrightText: 2019 Limor Fried for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`triangle`
================================================================================

Various common shapes for use with displayio - Triangle shape!


* Author(s): Melissa LeBlanc-Williams

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

from adafruit_display_shapes.polygon import Polygon

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Display_Shapes.git"


class Triangle(Polygon):
    # pylint: disable=too-many-arguments,invalid-name
    """A triangle.

    :param x0: The x-position of the first vertex.
    :param y0: The y-position of the first vertex.
    :param x1: The x-position of the second vertex.
    :param y1: The y-position of the second vertex.
    :param x2: The x-position of the third vertex.
    :param y2: The y-position of the third vertex.
    :param fill: The color to fill the triangle. Can be a hex value for a color or
                 ``None`` for transparent.
    :param outline: The outline of the triangle. Can be a hex value for a color or
                    ``None`` for no outline.
    """
    # pylint: disable=too-many-locals
    def __init__(self, x0, y0, x1, y1, x2, y2, *, fill=None, outline=None):
        # Sort coordinates by Y order (y2 >= y1 >= y0)
        if y0 > y1:
            y0, y1 = y1, y0
            x0, x1 = x1, x0

        if y1 > y2:
            y1, y2 = y2, y1
            x1, x2 = x2, x1

        if y0 > y1:
            y0, y1 = y1, y0
            x0, x1 = x1, x0

        # Find the largest and smallest X values to figure out width for bitmap
        xs = [x0, x1, x2]
        points = [(x0, y0), (x1, y1), (x2, y2)]

        # Initialize the bitmap and palette
        super().__init__(points)

        if fill is not None:
            self._draw_filled(
                x0 - min(xs), 0, x1 - min(xs), y1 - y0, x2 - min(xs), y2 - y0
            )
            self.fill = fill
        else:
            self.fill = None

        if outline is not None:
            self.outline = outline
            for index, _ in enumerate(points):
                point_a = points[index]
                if index == len(points) - 1:
                    point_b = points[0]
                else:
                    point_b = points[index + 1]
                self._line(
                    point_a[0] - min(xs),
                    point_a[1] - y0,
                    point_b[0] - min(xs),
                    point_b[1] - y0,
                    1,
                )

    # pylint: disable=invalid-name, too-many-branches
    def _draw_filled(self, x0, y0, x1, y1, x2, y2):
        if y0 == y2:  # Handle awkward all-on-same-line case as its own thing
            a = x0
            b = x0
            if x1 < a:
                a = x1
            elif x1 > b:
                b = x1

            if x2 < a:
                a = x2
            elif x2 > b:
                b = x2
            self._line(a, y0, b, y0, 2)
            return

        if y1 == y2:
            last = y1  # Include y1 scanline
        else:
            last = y1 - 1  # Skip it

        # Upper Triangle
        for y in range(y0, last + 1):
            a = round(x0 + (x1 - x0) * (y - y0) / (y1 - y0))
            b = round(x0 + (x2 - x0) * (y - y0) / (y2 - y0))
            if a > b:
                a, b = b, a
            self._line(a, y, b, y, 2)
        # Lower Triangle
        for y in range(last + 1, y2 + 1):
            a = round(x1 + (x2 - x1) * (y - y1) / (y2 - y1))
            b = round(x0 + (x2 - x0) * (y - y0) / (y2 - y0))

            if a > b:
                a, b = b, a
            self._line(a, y, b, y, 2)

    # pylint: enable=invalid-name, too-many-locals, too-many-branches

    @property
    def fill(self):
        """The fill of the triangle. Can be a hex value for a color or
        ``None`` for transparent."""
        return self._palette[2]

    @fill.setter
    def fill(self, color):
        if color is None:
            self._palette[2] = 0
            self._palette.make_transparent(2)
        else:
            self._palette[2] = color
            self._palette.make_opaque(2)
