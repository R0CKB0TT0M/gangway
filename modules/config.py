#!/usr/bin/env python3
"""
Definitions for LED positions
"""

from pathlib import Path
from typing import List, Tuple

import toml

from .animations.library import animations
from .helpers import interpolate_points
from .types import LED, Point, Strip

SRC_POINTS: List[Tuple[int, int]]
DST_POINTS: List[Tuple[int, int]]
FLOOR: Tuple[int, int, int, int]
TARGET_WEIGHT: float
STRIPS: List[Strip]
OFFSET_X: int
OFFSET_Y: int
LEDS: List[LED]


def load_config(config_path: str):
    global \
        SRC_POINTS, \
        DST_POINTS, \
        FLOOR, \
        TARGET_WEIGHT, \
        STRIPS, \
        LEDS, \
        IDLE_ANIMATION, \
        OBJECT_ANIMATION, \
        OFFSET_X, \
        OFFSET_Y

    config = toml.load(config_path)

    projection = config.get("projection", {})
    SRC_POINTS = [tuple(p) for p in projection.get("src_points", [])]
    DST_POINTS = [tuple(p) for p in projection.get("dst_points", [])]
    FLOOR = tuple(projection.get("floor", (0, 0, 0, 0)))

    leds_config = config.get("leds", {})
    TARGET_WEIGHT = leds_config.get("target_weight", 0.1)
    OFFSET_X = leds_config.get("offset_x", 0)
    OFFSET_Y = leds_config.get("offset_y", 0)

    STRIPS = [
        Strip(
            index=s.get("index"),
            len=s.get("len"),
            start=Point(*s.get("start")),
            end=Point(*s.get("end")),
        )
        for s in config.get("strips", [])
    ]

    LEDS = [
        LED(
            i + strip.index,
            interpolate_points(strip.start, strip.end, strip.len, i)
            + Point(x=OFFSET_X, y=OFFSET_Y),
        )
        for strip in STRIPS
        for i in range(strip.len)
    ]

    anim_config = config.get("animations", {})
    IDLE_ANIMATION = animations.get(anim_config.get("idle"))
    OBJECT_ANIMATION = animations.get(anim_config.get("object"))


# Default config path
default_config_path = Path(__file__).parent.parent / "config.toml"
load_config(str(default_config_path))
