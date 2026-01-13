#!/usr/bin/env python3
"""
Object Animation Definitions
"""

from typing import Callable, Iterable, Tuple

from rpi_ws2805 import RGBCCT

from ..strips_conf import Point
from . import interpolate_rgbcct
from .idle_animations import IdleAnimation

ObjectAnimation = Callable[
    [
        float,
        Tuple[float, float, float, float],
        Tuple[float, float],
        int,
        Iterable[Point],
        Callable[[], None],  # Set smooth update
        Callable[[], None],  # Set instant update
    ],
    RGBCCT,
]


def exponential(
    primary: RGBCCT | IdleAnimation = RGBCCT(r=255),
    secondary: RGBCCT | IdleAnimation = RGBCCT(g=255),
    radius: float = 150,
):
    def animation(
        time: float,
        floor: Tuple[float, float, float, float],
        led_pos: Tuple[float, float],
        index: int,
        objects: Iterable[Point],
        smooth: Callable[[], None],
        instant: Callable[[], None],
    ) -> RGBCCT:
        intensity = max(
            2 ** (-(Point.from_tuple(led_pos) - object).length / radius)
            for object in objects
        )

        primary_rgbcct: RGBCCT

        if isinstance(primary, RGBCCT):
            primary_rgbcct = primary
        else:
            primary_rgbcct = primary(time, floor, led_pos, index, smooth, instant)

        if isinstance(secondary, RGBCCT):
            secondary_rgbcct = secondary
        else:
            secondary_rgbcct = secondary(time, floor, led_pos, index, smooth, instant)

        return interpolate_rgbcct(
            primary_rgbcct, secondary_rgbcct, intensity, use_sign=False
        )

    return animation


def dot(
    primary: RGBCCT | IdleAnimation = RGBCCT(r=255),
    secondary: RGBCCT | IdleAnimation = RGBCCT(g=255),
    radius: float = 150,
):
    def animation(
        time: float,
        floor: Tuple[float, float, float, float],
        led_pos: Tuple[float, float],
        index: int,
        objects: Iterable[Point],
        smooth: Callable[[], None],
        instant: Callable[[], None],
    ) -> RGBCCT:
        instant()

        primary_rgbcct: RGBCCT

        if isinstance(primary, RGBCCT):
            primary_rgbcct = primary
        else:
            primary_rgbcct = primary(time, floor, led_pos, index, smooth, instant)

        if isinstance(secondary, RGBCCT):
            secondary_rgbcct = secondary
        else:
            secondary_rgbcct = secondary(time, floor, led_pos, index, smooth, instant)

        return (
            primary_rgbcct
            if any(
                (Point.from_tuple(led_pos) - object).length < radius
                for object in objects
            )
            else secondary_rgbcct
        )

    return animation
