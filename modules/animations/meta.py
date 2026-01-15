#!/usr/bin/env python3
"""
Meta-Animation Definitions
"""

import datetime
from typing import Iterable, Literal

from rpi_ws2805 import RGBCCT

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


def blend(*animations: Animation | RGBCCT) -> Animation:
    def animation(
        time: float,
        _ctx: SceneContext,
        led: LED,
        objects: Iterable[Point],
        *_args,
        **_kwargs,
    ) -> RGBCCT:
        colors = (
            animation
            if isinstance(animation, RGBCCT)
            else animation(time, _ctx, led, objects)
            for animation in animations
        )

        tuples = ((color.r, color.g, color.b, color.cw, color.ww) for color in colors)
        average = tuple(int(sum(values) / len(animations)) for values in zip(*tuples))

        return RGBCCT(
            r=average[0], g=average[1], b=average[2], cw=average[3], ww=average[4]
        )

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
