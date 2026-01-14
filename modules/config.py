#!/usr/bin/env python3
"""
Definitions for LED positions
"""

import inspect
import threading
from pathlib import Path
from typing import List, Tuple

import yaml
from rpi_ws2805 import RGBCCT

from .animations import idle, object
from .helpers import interpolate_points
from .types import LED, IdleAnimation, ObjectAnimation, Point, Strip


def _get_animation_functions():
    """Dynamically collects all animation functions from imported modules."""
    functions = {}
    # Inspect idle and object animation modules
    for module in [idle, object]:
        for name, func in inspect.getmembers(module, inspect.isfunction):
            # Add function to registry if it's not a private helper
            if not name.startswith("_") and name != "interpolate_rgbcct":
                functions[name] = func
    # Add the color class for type checking
    functions["RGBCCT"] = RGBCCT
    return functions


ANIMATION_FUNCTIONS = _get_animation_functions()


class GANGWAYConfig:
    SRC_POINTS: List[Tuple[int, int]]
    DST_POINTS: List[Tuple[int, int]]
    FLOOR: Tuple[int, int, int, int]
    TARGET_WEIGHT: float
    STRIPS: List[Strip]
    OFFSET_X: int
    OFFSET_Y: int
    LEDS: List[LED]
    IDLE_ANIMATION: IdleAnimation
    OBJECT_ANIMATION: ObjectAnimation

    def __init__(self, path: Path):
        self._lock = threading.Lock()
        self.path = path
        self.load()

    def load(self):
        with self._lock:
            with open(self.path, "r") as f:
                config = yaml.safe_load(f)

            self.data = config
            projection = config.get("projection", {})
            self.SRC_POINTS = [tuple(p) for p in projection.get("src_points", [])]
            self.DST_POINTS = [tuple(p) for p in projection.get("dst_points", [])]
            self.FLOOR = tuple(projection.get("floor", (0, 0, 0, 0)))

            leds_config = config.get("leds", {})
            self.TARGET_WEIGHT = leds_config.get("target_weight", 0.1)
            self.OFFSET_X = leds_config.get("offset_x", 0)
            self.OFFSET_Y = leds_config.get("offset_y", 0)

            self.STRIPS = [
                Strip(
                    index=s.get("index"),
                    len=s.get("len"),
                    start=Point(*s.get("start")),
                    end=Point(*s.get("end")),
                )
                for s in config.get("strips", [])
            ]

            self.LEDS = [
                LED(
                    i + strip.index,
                    interpolate_points(strip.start, strip.end, strip.len, i)
                    + Point(x=self.OFFSET_X, y=self.OFFSET_Y),
                )
                for strip in self.STRIPS
                for i in range(strip.len)
            ]

            anim_config = config.get("animations", {})

            all_animations = {}
            idle_animation_config = anim_config.get("idle")
            if idle_animation_config:
                all_animations["idle"] = self._parse_animation(
                    idle_animation_config, all_animations
                )

            object_animation_config = anim_config.get("object")
            if object_animation_config:
                all_animations["object"] = self._parse_animation(
                    object_animation_config, all_animations
                )

            self.IDLE_ANIMATION = all_animations.get("idle")
            self.OBJECT_ANIMATION = all_animations.get("object")

    def save(self):
        with self._lock:
            # This is a bit tricky as we have complex objects.
            # We'll just save the raw dictionary for now.
            # A more robust solution would be to serialize the objects back to the YAML structure.
            with open(self.path, "r") as f:
                config = yaml.safe_load(f)

            # We are not modifying the config at runtime in this application, so we can just
            # save the file as is. If we were to modify the config, we would need to
            # reconstruct the dictionary from the class attributes.
            with open(self.path, "w") as f:
                yaml.dump(config, f)

    def _parse_animation(self, anim_config, all_animations):
        if not isinstance(anim_config, dict):
            return anim_config

        if "r" in anim_config and "g" in anim_config and "b" in anim_config:
            return RGBCCT(**anim_config)

        if "ref" in anim_config:
            return all_animations[anim_config["ref"]]

        anim_name = list(anim_config.keys())[0]
        anim_args = list(anim_config.values())[0]

        anim_func = ANIMATION_FUNCTIONS.get(anim_name)
        if not anim_func:
            raise ValueError(f"Unknown animation function: {anim_name}")

        sig = inspect.signature(anim_func)

        # Check for unexpected arguments
        valid_param_names = {p.name for p in sig.parameters.values()}
        for arg_name in anim_args.keys():
            if arg_name not in valid_param_names:
                raise ValueError(
                    f"Unknown parameter '{arg_name}' for animation '{anim_name}'"
                )

        parsed_args = {}
        var_args = []

        for param in sig.parameters.values():
            if param.kind == inspect.Parameter.VAR_POSITIONAL:
                if param.name in anim_args:
                    for arg in anim_args[param.name]:
                        var_args.append(self._parse_animation(arg, all_animations))
                continue

            if param.name in anim_args:
                arg_value = anim_args[param.name]
                if isinstance(arg_value, dict):
                    parsed_args[param.name] = self._parse_animation(
                        arg_value, all_animations
                    )
                elif isinstance(arg_value, list):
                    parsed_args[param.name] = [
                        self._parse_animation(v, all_animations) for v in arg_value
                    ]
                else:
                    parsed_args[param.name] = arg_value
            elif param.default is not inspect.Parameter.empty:
                parsed_args[param.name] = param.default

        return anim_func(*var_args, **parsed_args)


# Global config instance
CONFIG = GANGWAYConfig(Path(__file__).parent.parent / "config.yaml")
