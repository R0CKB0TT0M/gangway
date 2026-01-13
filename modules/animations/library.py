#!/usr/bin/env python3
"""
Library of animations
"""

from rpi_ws2805 import RGBCCT

from .idle import alternate, strobo, swing
from .object import dot

main_animation = alternate(
    swing(),
    strobo(),
    swing(RGBCCT(r=255), speed=20, direction="x", wavelength=10),
    strobo(),
    strobo(),
    swing(RGBCCT(b=255), speed=20),
    strobo(),
    strobo(),
    swing(RGBCCT(b=255), direction="x", wavelength=10),
    strobo(),
    strobo(),
    length=3,
)

object_animation = dot(
    primary=strobo(),
    secondary=main_animation,
    radius=50,
    force_instant=True,
)

animations = {
    "main_animation": main_animation,
    "object_animation": object_animation,
}
