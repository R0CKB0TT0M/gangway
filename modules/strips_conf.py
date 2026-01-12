import time
from dataclasses import dataclass
from typing import Union

from .ws2805_controller import RGBCCT, WS2805_STRIP, WS2805Controller


@dataclass
class Point:
    x: Union[float, int]
    y: Union[float, int]

    def __sub__(self, other: "Point") -> "Point":
        return Point(x=other.x - self.x, y=other.y - self.y)

    def __add__(self, other: "Point") -> "Point":
        return Point(x=self.x + other.x, y=self.y + other.y)

    def __mul__(self, other: Union[float, int]) -> "Point":
        return Point(x=self.x * other, y=self.y * other)

    def __truediv__(self, other: Union[float, int]) -> "Point":
        return Point(x=self.x / other, y=self.y / other)

    @property
    def length(self) -> float:
        return (self.x**2 + self.y**2) ** 0.5


@dataclass
class Strip:
    index: int
    len: int
    start: Point
    end: Point


@dataclass
class LED:
    index: int
    p: Point


STRIPS = [
    Strip(index=1, len=24, start=Point(10, 0), end=Point(63, 197)),
    Strip(index=25, len=24, start=Point(105, 215), end=Point(105, 43)),
    Strip(index=49, len=24, start=Point(98, 14), end=Point(25, 197)),
    Strip(index=73, len=24, start=Point(66, 25), end=Point(66, 225)),
    Strip(index=97, len=24, start=Point(88, 210), end=Point(14, 400)),
    Strip(index=121, len=24, start=Point(45, 490), end=Point(45, 290)),
]


def interpolate(p1: Point, p2: Point, num, index):
    return (p1 - p2) / num * (index + 0.5) + p1


LEDS = [
    LED(i + strip.index, interpolate(strip.start, strip.end, strip.len, i))
    for strip in STRIPS
    for i in range(strip.len)
]

MAX_INDEX = max(strip.index + strip.len for strip in STRIPS)
