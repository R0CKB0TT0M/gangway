#!/usr/bin/env python3
"""
Animation Definitions
"""

import math
import random
from typing import Callable, List, Tuple

from rpi_ws2805 import RGBCCT

Animation = Callable[
    [float, Tuple[float, float, float, float], Tuple[float, float]], RGBCCT
]


def wave(
    colors: List[RGBCCT],
    n_waves: int = 3,
    speed: float = 50.0,
    wavelength: float = 200.0,
):
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
    ) -> RGBCCT:
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
