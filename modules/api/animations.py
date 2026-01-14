"""
This module defines the API endpoints for animations.
"""

import typing
from inspect import Parameter
from typing import Callable, List, Literal

import rpi_ws2805
from fastapi import APIRouter, HTTPException
from pydantic import create_model

from ..animations.utils import get_animations_from_module

router = APIRouter()

ANIMATIONS = get_animations_from_module("idle") + get_animations_from_module("object")


@router.get("/")
def get_animations():
    return ANIMATIONS


def get_model_for_animation(animation_name: str, validation_mode: bool = False):
    animation = next((a for a in ANIMATIONS if a["name"] == animation_name), None)
    if not animation:
        return None

    fields = {}
    for param in animation["params"]:
        param_type = param["type"]
        # This is a simplification, a more robust solution would handle
        # the complex types like IdleAnimation and ObjectAnimation
        if param_type == "Callable":
            if validation_mode:
                param_type = (
                    List[typing.Dict[str, typing.Any]]
                    if param["kind"] == Parameter.VAR_POSITIONAL
                    else typing.Dict[str, typing.Any]
                )
            else:
                param_type = (
                    List[Literal["Animation"]]
                    if param["kind"] == Parameter.VAR_POSITIONAL
                    else Literal["Animation"]
                )
        else:
            param_type = eval(
                param_type,
                {
                    "typing": typing,
                    "rpi_ws2805": rpi_ws2805,
                    "Literal": Literal,
                    "List": typing.List,
                    "Callable": Callable,
                    "RGBCCT": rpi_ws2805.RGBCCT,
                },
            )

            if validation_mode:
                origin = getattr(param_type, "__origin__", None)
                if param_type == rpi_ws2805.RGBCCT:
                    param_type = typing.Dict[str, int]
                elif (origin is list or origin is typing.List) and getattr(
                    param_type, "__args__", []
                )[0] == rpi_ws2805.RGBCCT:
                    param_type = typing.List[typing.Dict[str, int]]

        fields[param["name"]] = (param_type, param["default"])

    return create_model(f"{animation_name}Config", **fields)


@router.get("/{animation_name}/schema")
def get_animation_schema(animation_name: str):
    AnimationConfig = get_model_for_animation(animation_name)
    if not AnimationConfig:
        raise HTTPException(status_code=404, detail="Animation not found")
    return AnimationConfig.model_json_schema()
