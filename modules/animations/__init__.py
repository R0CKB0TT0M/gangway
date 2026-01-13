#!/usr/bin/env python3
"""
Animations module
"""

from rpi_ws2805 import RGBCCT


def interpolate_rgbcct(color_a: RGBCCT, color_b: RGBCCT, weight_a: float) -> RGBCCT:
    return RGBCCT(
        r=int(color_a.r * weight_a + color_b.r * (1 - weight_a)),
        g=int(color_a.g * weight_a + color_b.g * (1 - weight_a)),
        b=int(color_a.b * weight_a + color_b.b * (1 - weight_a)),
        ww=int(color_a.ww * weight_a + color_b.ww * (1 - weight_a)),
        cw=int(color_a.cw * weight_a + color_b.cw * (1 - weight_a)),
    )
