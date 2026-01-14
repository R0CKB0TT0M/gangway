#!/usr/bin/env python3
"""
Definitions for LED positions
"""

import inspect
from pathlib import Path

import yaml
from rpi_ws2805 import RGBCCT

from .animations import idle, object
from .helpers import interpolate_points
from .types import LED, Point, Strip

ANIMATION_FUNCTIONS = {
    "alternate": idle.alternate,
    "fire": idle.fire,
    "rainbow": idle.rainbow,
    "strobo": idle.strobo,
    "swing": idle.swing,
    "theater_chase": idle.theater_chase,
    "wave": idle.wave,
    "dot": object.dot,
    "exponential": object.exponential,
}


def _parse_animation(anim_config, all_animations):
    if not isinstance(anim_config, dict):
        return anim_config

    if "ref" in anim_config:
        return all_animations[anim_config["ref"]]

    anim_name = list(anim_config.keys())[0]
    anim_args = list(anim_config.values())[0]

    anim_func = ANIMATION_FUNCTIONS.get(anim_name)
    if not anim_func:
        raise ValueError(f"Unknown animation function: {anim_name}")

    sig = inspect.signature(anim_func)
    parsed_args = {}
    var_args = []

    for param in sig.parameters.values():
        if param.kind == inspect.Parameter.VAR_POSITIONAL:
            # Handle varargs like *animations in alternate
            if param.name in anim_args:
                for arg in anim_args[param.name]:
                    var_args.append(_parse_animation(arg, all_animations))
            continue

        if param.name in anim_args:
            if param.annotation == RGBCCT:
                parsed_args[param.name] = RGBCCT(**anim_args[param.name])
            elif isinstance(anim_args[param.name], dict):
                parsed_args[param.name] = _parse_animation(
                    anim_args[param.name], all_animations
                )
            elif isinstance(anim_args[param.name], list):
                parsed_args[param.name] = [
                    _parse_animation(v, all_animations) for v in anim_args[param.name]
                ]
            else:
                parsed_args[param.name] = anim_args[param.name]
        elif param.default is not inspect.Parameter.empty:
            parsed_args[param.name] = param.default

    return anim_func(*var_args, **parsed_args)


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

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

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

    all_animations = {}
    idle_animation_config = anim_config.get("idle")
    if idle_animation_config:
        all_animations["idle"] = _parse_animation(idle_animation_config, all_animations)

    object_animation_config = anim_config.get("object")
    if object_animation_config:
        all_animations["object"] = _parse_animation(
            object_animation_config, all_animations
        )

    IDLE_ANIMATION = all_animations.get("idle")
    OBJECT_ANIMATION = all_animations.get("object")


# Default config path
default_config_path = Path(__file__).parent.parent / "config.yaml"
load_config(str(default_config_path))
