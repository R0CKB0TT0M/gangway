#!/usr/bin/env python3
"""
Definitions for LED positions
"""

from .helpers import interpolate_points
from .types import LED, Point, Strip

OFFSET_Y = 10
OFFSET_X = 0

SRC_POINTS = [
    (252, 357),
    (366, 358),
    (351, 101),
    (312, 102),
]

DST_POINTS = [
    (0, 490),
    (115, 490),
    (115, 0),
    (0, 0),
]

FLOOR = (0, 0, 115, 490)

TARGET_WEIGHT: float = 10 / 255

STRIPS = [
    Strip(index=1, len=24, start=Point(10, 0), end=Point(63, 197)),
    Strip(index=25, len=24, start=Point(105, 243), end=Point(105, 43)),
    Strip(index=49, len=24, start=Point(98, 14), end=Point(25, 197)),
    Strip(index=73, len=24, start=Point(66, 25), end=Point(66, 225)),
    Strip(index=97, len=24, start=Point(88, 210), end=Point(14, 400)),
    Strip(index=121, len=24, start=Point(45, 490), end=Point(45, 290)),
]

LEDS = [
    LED(
        i + strip.index,
        interpolate_points(strip.start, strip.end, strip.len, i)
        + Point(x=OFFSET_X, y=OFFSET_Y),
    )
    for strip in STRIPS
    for i in range(strip.len)
]

MAX_INDEX = max(strip.index + strip.len for strip in STRIPS)
