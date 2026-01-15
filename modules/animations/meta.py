#!/usr/bin/env python3
"""
Meta-Animation Definitions
"""

import datetime
from typing import Dict, Iterable, Literal

from rpi_ws2805 import RGBCCT

from ..helpers import interpolate_rgbcct
from ..types import LED, Animation, Point, SceneContext


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


def blend(
    *animations: Animation | RGBCCT, mode: Literal["average", "max"] = "average"
) -> Animation:
    def animation(
        time: float,
        _ctx: SceneContext,
        led: LED,
        objects: Iterable[Point],
        *_args,
        **_kwargs,
    ) -> RGBCCT:
        colors_list = [
            anim if isinstance(anim, RGBCCT) else anim(time, _ctx, led, objects)
            for anim in animations
        ]

        if not colors_list:
            return RGBCCT()

        tuples = (
            (color.r, color.g, color.b, color.cw, color.ww) for color in colors_list
        )
        zipped = zip(*tuples)

        if mode == "max":
            result = tuple(max(values) for values in zipped)
        else:
            result = tuple(int(sum(values) / len(colors_list)) for values in zipped)

        return RGBCCT(r=result[0], g=result[1], b=result[2], cw=result[3], ww=result[4])

    return animation


def schedule(
    primary: Animation | RGBCCT,
    secondary: Animation | RGBCCT,
    start: str = "18:00",
    end: str = "06:00",
) -> Animation:
    """
    Activates the primary animation only between specific hours.
    Otherwise returns secondary animation.
    """

    def animation(
        time: float,
        ctx: SceneContext,
        led: LED,
        objects: Iterable[Point],
        *args,
        **kwargs,
    ) -> RGBCCT:
        now = datetime.datetime.now().time()
        try:
            start_t = datetime.time.fromisoformat(start)
            end_t = datetime.time.fromisoformat(end)
        except ValueError:
            # Fallback if time format is invalid
            start_t = datetime.time(18, 0)
            end_t = datetime.time(6, 0)

        is_active = False
        if start_t <= end_t:
            is_active = start_t <= now <= end_t
        else:  # crosses midnight
            is_active = now >= start_t or now <= end_t

        target = primary if is_active else secondary

        if isinstance(target, RGBCCT):
            return target

        return target(time, ctx, led, objects, *args, **kwargs)

    return animation


def smooth(
    animation: Animation | RGBCCT,
    smoothing: float = 0.5,
) -> Animation:
    """
    Smooths the input animation over time using an exponential moving average.
    smoothing: 0.0 = no smoothing (instant), 1.0 = infinite smoothing (no change).
    """
    last_colors: Dict[int, RGBCCT] = {}

    def func(
        time: float,
        ctx: SceneContext,
        led: LED,
        objects: Iterable[Point],
        *args,
        **kwargs,
    ) -> RGBCCT:
        nonlocal last_colors

        target: RGBCCT
        if isinstance(animation, RGBCCT):
            target = animation
        else:
            target = animation(time, ctx, led, objects, *args, **kwargs)

        current = last_colors.get(led.index)

        if current is None:
            # First frame, jump to target
            last_colors[led.index] = target
            return target

        # Interpolate
        # interpolate_rgbcct(current, target, smoothing) returns:
        # current * smoothing + target * (1 - smoothing)
        next_color = interpolate_rgbcct(current, target, smoothing, use_sign=False)
        last_colors[led.index] = next_color

        return next_color

    return func
