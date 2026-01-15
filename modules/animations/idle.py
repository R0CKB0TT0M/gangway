#!/usr/bin/env python3
"""
Idle Animation Definitions
"""

import math
import random
from typing import Callable, List, Literal, Tuple

from rpi_ws2805 import RGBCCT

from ..helpers import interpolate_rgbcct
from ..types import IdleAnimation


def wave(
    colors: List[RGBCCT],
    n_waves: int = 3,
    speed: float = 50.0,
    wavelength: float = 200.0,
) -> IdleAnimation:
    waves = []
    for i in range(n_waves):
        angle = random.uniform(0, 2 * math.pi)
        direction = (math.cos(angle), math.sin(angle))
        color = random.choice(colors)
        waves.append(
            {
                "direction": direction,
                "color": color,
                "phase": (i / n_waves) * 2 * math.pi,
            }
        )

    k = 2 * math.pi / wavelength

    def animation(
        time: float,
        floor: Tuple[float, float, float, float],
        led_pos: Tuple[float, float],
        index: int,
        _: Callable[[], None],
        instant: Callable[[], None],
    ) -> RGBCCT:
        instant()

        r, g, b, cw, ww = 0, 0, 0, 0, 0

        for wave_params in waves:
            direction = wave_params["direction"]
            color = wave_params["color"]
            phase = wave_params["phase"]

            proj = led_pos[0] * direction[0] + led_pos[1] * direction[1]
            intensity = (1 + math.sin(k * proj - (k * speed * time) + phase)) / 2

            r += color.r * intensity
            g += color.g * intensity
            b += color.b * intensity
            cw += color.cw * intensity
            ww += color.ww * intensity

        return RGBCCT(
            r=min(255, int(r)),
            g=min(255, int(g)),
            b=min(255, int(b)),
            cw=min(255, int(cw)),
            ww=min(255, int(ww)),
        )

    return animation


def _hsv_to_rgb(h, s, v):
    if s == 0.0:
        return int(v * 255), int(v * 255), int(v * 255)
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i %= 6
    if i == 0:
        r, g, b = v, t, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, t
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = t, p, v
    else:
        r, g, b = v, p, q
    return int(r * 255), int(g * 255), int(b * 255)


def rainbow(speed: float = 0.1, spread: float = 3.0) -> IdleAnimation:
    def animation(
        time: float,
        floor: Tuple[float, float, float, float],
        led_pos: Tuple[float, float],
        index: int,
        smooth: Callable[[], None],
        _: Callable[[], None],
    ) -> RGBCCT:
        smooth()

        x_norm = (led_pos[0] - floor[0]) / (floor[2] - floor[0])
        hue = (x_norm * spread + time * speed) % 1.0
        r, g, b = _hsv_to_rgb(hue, 1.0, 1.0)
        return RGBCCT(r=r, g=g, b=b)

    return animation


def fire(
    base_color: RGBCCT = RGBCCT(r=255, g=140, b=0),
    flicker_speed: float = 0.1,
    flicker_intensity: float = 0.5,
) -> IdleAnimation:
    def animation(
        time: float,
        floor: Tuple[float, float, float, float],
        led_pos: Tuple[float, float],
        index: int,
        smooth: Callable[[], None],
        _: Callable[[], None],
    ) -> RGBCCT:
        smooth()

        time_bucket = int(time / flicker_speed)
        seed = hash((led_pos, time_bucket))
        rand_gen = random.Random(seed)
        brightness_factor = 1.0 - flicker_intensity * rand_gen.random()

        return RGBCCT(
            r=int(base_color.r * brightness_factor),
            g=int(base_color.g * brightness_factor),
            b=int(base_color.b * brightness_factor),
            cw=int(base_color.cw * brightness_factor),
            ww=int(base_color.ww * brightness_factor),
        )

    return animation


def theater_chase(
    color: RGBCCT = RGBCCT(r=255, g=255, b=255),
    speed: float = 1.0,
    spacing: int = 4,
) -> IdleAnimation:
    def animation(
        time: float,
        floor: Tuple[float, float, float, float],
        led_pos: Tuple[float, float],
        index: int,
        _: Callable[[], None],
        instant: Callable[[], None],
    ) -> RGBCCT:
        instant()

        time_offset = int(time * speed * 10)
        if (index - time_offset) % spacing == 0:
            return color
        return RGBCCT()

    return animation


def strobo(
    colors: List[RGBCCT] = [
        RGBCCT(r=255, g=255, b=255, cw=255, ww=255),
        RGBCCT(),
        RGBCCT(r=255),
        RGBCCT(),
        RGBCCT(b=255),
    ],
    frequency: int = 100,
) -> IdleAnimation:
    def animation(
        time: float,
        floor: Tuple[float, float, float, float],
        led_pos: Tuple[float, float],
        index: int,
        _: Callable[[], None],
        instant: Callable[[], None],
    ) -> RGBCCT:
        instant()

        return colors[int(time * frequency) % len(colors)]

    return animation


def alternate(
    *animations: IdleAnimation,
    length: float = 10,
) -> IdleAnimation:
    def animation(
        time: float,
        floor: Tuple[float, float, float, float],
        led_pos: Tuple[float, float],
        index: int,
        smooth: Callable[[], None],
        instant: Callable[[], None],
    ) -> RGBCCT:
        return animations[int(time / length) % len(animations)](
            time, floor, led_pos, index, smooth, instant
        )

    return animation


def swing(
    color: RGBCCT = RGBCCT(r=255, g=255, b=255, cw=255),
    direction: Literal["x"] | Literal["y"] = "y",
    wavelength: int = 50,
    speed: float = 10,
) -> IdleAnimation:
    def animation(
        time: float,
        floor: Tuple[float, float, float, float],
        led_pos: Tuple[float, float],
        index: int,
        _: Callable[[], None],
        instant: Callable[[], None],
    ) -> RGBCCT:
        instant()
        coordinate: float = led_pos[0] if direction == "x" else led_pos[1]
        floor_len: float = floor[2] if direction == "x" else floor[3]

        target_coordinate: float = (
            math.sin(time * speed) * floor_len / 2 + floor_len / 2
        )

        intensity = 2 ** (-abs(coordinate - target_coordinate) / wavelength)

        if intensity < 0.2:
            intensity = 0

        return interpolate_rgbcct(color, RGBCCT(), intensity, use_sign=False)

    return animation


def static(color: RGBCCT = RGBCCT(r=255, g=255, b=255)) -> IdleAnimation:
    """
    A simple animation that returns a static color.
    """

    def animation(
        time: float,
        floor: Tuple[float, float, float, float],
        led_pos: Tuple[float, float],
        index: int,
        _: Callable[[], None],
        instant: Callable[[], None],
    ) -> RGBCCT:
        instant()
        return color

    return animation
