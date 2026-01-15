#!/usr/bin/env python3
"""
Object Animation Definitions
"""

from typing import Iterable, List, Tuple

from rpi_ws2805 import RGBCCT

from ..helpers import interpolate_rgbcct
from ..types import LED, Animation, Point, SceneContext
from .idle import wave


def exponential(
    primary: RGBCCT | Animation = RGBCCT(r=255),
    secondary: RGBCCT | Animation = RGBCCT(g=255),
    radius: float = 150,
) -> Animation:
    def animation(
        time: float,
        ctx: SceneContext,
        led: LED,
        objects: Iterable[Point],
    ) -> RGBCCT:
        intensity = max(2 ** (-(led.p - object).length / radius) for object in objects)

        primary_rgbcct: RGBCCT

        if isinstance(primary, RGBCCT):
            primary_rgbcct = primary
        else:
            primary_rgbcct = primary(time, ctx, led, objects)

        if isinstance(secondary, RGBCCT):
            secondary_rgbcct = secondary
        else:
            secondary_rgbcct = secondary(time, ctx, led, objects)

        return interpolate_rgbcct(
            primary_rgbcct, secondary_rgbcct, intensity, use_sign=False
        )

    return animation


def dot(
    primary: RGBCCT | Animation = wave([RGBCCT(r=255)]),
    secondary: RGBCCT | Animation = wave([RGBCCT(g=255)]),
    radius: float = 150,
) -> Animation:
    def animation(
        time: float,
        ctx: SceneContext,
        led: LED,
        objects: Iterable[Point],
    ) -> RGBCCT:
        primary_rgbcct: RGBCCT

        if isinstance(primary, RGBCCT):
            primary_rgbcct = primary
        else:
            primary_rgbcct = primary(time, ctx, led, objects)

        if isinstance(secondary, RGBCCT):
            secondary_rgbcct = secondary
        else:
            secondary_rgbcct = secondary(time, ctx, led, objects)

        return (
            primary_rgbcct
            if any((led.p - object).length < radius for object in objects)
            else secondary_rgbcct
        )

    return animation


def paint(
    primary: RGBCCT | Animation = RGBCCT(r=255, g=0, b=0),
    secondary: RGBCCT | Animation = RGBCCT(r=0, g=0, b=0),
    radius: float = 150,
    persistence: float = 2.0,
) -> Animation:
    """
    Like dot() but persists object-locations for n seconds.
    """
    history: List[Tuple[Point, float]] = []
    last_frame_time = -1.0

    def animation(
        time: float,
        ctx: SceneContext,
        led: LED,
        objects: Iterable[Point],
    ) -> RGBCCT:
        nonlocal history, last_frame_time

        # Update history once per frame
        # We assume 'time' is monotonic and strictly increasing per frame
        if time > last_frame_time:
            cutoff = time - persistence
            history = [(p, t) for p, t in history if t > cutoff]

            for obj in objects:
                history.append((obj, time))

            last_frame_time = time

        primary_rgbcct: RGBCCT
        if isinstance(primary, RGBCCT):
            primary_rgbcct = primary
        else:
            primary_rgbcct = primary(time, ctx, led, objects)

        if isinstance(secondary, RGBCCT):
            secondary_rgbcct = secondary
        else:
            secondary_rgbcct = secondary(time, ctx, led, objects)

        # Check against current objects AND history
        # (History includes current objects if we just added them)
        hit = any((led.p - p).length < radius for p, _ in history)

        return primary_rgbcct if hit else secondary_rgbcct

    return animation


def off() -> Animation:
    """
    A simple animation that turns LEDs off.
    """

    def animation(
        *_args,
        **_kwargs,
    ) -> RGBCCT:
        return RGBCCT()

    return animation
