#!/usr/bin/env python3
"""
Meta-Animation Definitions
"""

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
