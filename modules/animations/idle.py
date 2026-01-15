#!/usr/bin/env python3
"""
Idle Animation Definitions
"""

import math
import random
from typing import Iterable, List, Literal, Tuple

from rpi_ws2805 import RGBCCT

from ..helpers import interpolate_rgbcct
from ..types import LED, Animation, Point, SceneContext


def wave(
    colors: List[RGBCCT],
    n_waves: int = 3,
    speed: float = 50.0,
    wavelength: float = 200.0,
) -> Animation:
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
        _ctx: SceneContext,
        led: LED,
        *_args,
        **_kwargs,
    ) -> RGBCCT:
        r, g, b, cw, ww = 0, 0, 0, 0, 0

        for wave_params in waves:
            direction = wave_params["direction"]
            color = wave_params["color"]
            phase = wave_params["phase"]

            proj = led.p.x * direction[0] + led.p.y * direction[1]
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


def rainbow(speed: float = 0.1, spread: float = 3.0) -> Animation:
    def animation(
        time: float,
        ctx: SceneContext,
        led: LED,
        *_args,
        **_kwargs,
    ) -> RGBCCT:
        x_norm = (led.p.x - ctx.floor.p1.x) / (ctx.floor.p2.x - ctx.floor.p1.x)
        hue = (x_norm * spread + time * speed) % 1.0
        r, g, b = _hsv_to_rgb(hue, 1.0, 1.0)
        return RGBCCT(r=r, g=g, b=b)

    return animation


def fire(
    base_color: RGBCCT = RGBCCT(r=255, g=140, b=0),
    flicker_speed: float = 0.1,
    flicker_intensity: float = 0.5,
) -> Animation:
    def animation(
        time: float,
        _ctx: SceneContext,
        led: LED,
        *_args,
        **_kwargs,
    ) -> RGBCCT:
        time_bucket = int(time / flicker_speed)
        seed = hash((led.p.x, time_bucket))
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
) -> Animation:
    def animation(
        time: float,
        _ctx: SceneContext,
        led: LED,
        *_args,
        **_kwargs,
    ) -> RGBCCT:
        time_offset = int(time * speed * 10)
        if (led.index - time_offset) % spacing == 0:
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
) -> Animation:
    def animation(
        time: float,
        *_args,
        **_kwargs,
    ) -> RGBCCT:
        return colors[int(time * frequency) % len(colors)]

    return animation


def alternate(
    *animations: Animation,
    length: float = 10,
) -> Animation:
    def animation(
        time: float,
        _ctx: SceneContext,
        led: LED,
        objects: Iterable[Point],
        *_args,
        **_kwargs,
    ) -> RGBCCT:
        return animations[int(time / length) % len(animations)](
            time, _ctx, led, objects
        )

    return animation


def swing(
    color: RGBCCT = RGBCCT(r=255, g=255, b=255, cw=255),
    direction: Literal["x"] | Literal["y"] = "y",
    wavelength: int = 50,
    speed: float = 10,
) -> Animation:
    def animation(
        time: float,
        ctx: SceneContext,
        led: LED,
        *_args,
        **_kwargs,
    ) -> RGBCCT:
        coordinate: float = led.p.x if direction == "x" else led.p.y
        floor_len: float = (
            ctx.floor.p2.x - ctx.floor.p1.x
            if direction == "x"
            else ctx.floor.p2.y - ctx.floor.p1.y
        )

        target_coordinate: float = (
            math.sin(time * speed) * floor_len / 2 + floor_len / 2
        )

        intensity = 2 ** (-abs(coordinate - target_coordinate) / wavelength)

        if intensity < 0.2:
            intensity = 0

        return interpolate_rgbcct(color, RGBCCT(), intensity, use_sign=False)

    return animation


def static(color: RGBCCT = RGBCCT(r=255, g=255, b=255)) -> Animation:
    """
    A simple animation that returns a static color.
    """

    def animation(
        *_args,
        **_kwargs,
    ) -> RGBCCT:
        return color

    return animation


def idle(idle_animation: Animation, active_animation: Animation) -> Animation:
    """
    A simple animation that returns a static color.
    """

    def animation(
        time: float,
        ctx: SceneContext,
        led: LED,
        objects: Iterable[Point],
        *_args,
        **_kwargs,
    ) -> RGBCCT:
        objects = [object for object in objects]

        if len(objects) == 0:
            return idle_animation(
                time,
                ctx,
                led,
                objects,
                *_args,
                **_kwargs,
            )
        else:
            return active_animation(
                time,
                ctx,
                led,
                objects,
                *_args,
                **_kwargs,
            )

    return animation
