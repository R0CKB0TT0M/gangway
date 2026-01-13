#!/usr/bin/env python3
"""
Animations module
"""

from rpi_ws2805 import RGBCCT


def sign(x: float, use_sign: bool) -> int:
    if not use_sign:
        return 0

    return 0 if x == 0 else (-1 if x < 0 else 1)


def interpolate_rgbcct(
    color_a: RGBCCT, color_b: RGBCCT, weight_a: float, use_sign: bool = True
) -> RGBCCT:
    return RGBCCT(
        r=int(color_a.r * weight_a + color_b.r * (1 - weight_a))
        - sign(color_b.r - color_a.r, use_sign),
        g=int(color_a.g * weight_a + color_b.g * (1 - weight_a))
        - sign(color_b.g - color_a.g, use_sign),
        b=int(color_a.b * weight_a + color_b.b * (1 - weight_a))
        - sign(color_b.b - color_a.b, use_sign),
        ww=int(color_a.ww * weight_a + color_b.ww * (1 - weight_a))
        - sign(color_b.ww - color_a.ww, use_sign),
        cw=int(color_a.cw * weight_a + color_b.cw * (1 - weight_a))
        - sign(color_b.cw - color_a.cw, use_sign),
    )
