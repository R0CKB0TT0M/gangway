"""
This module defines the API endpoints for animations.
"""

import typing
from typing import Literal

import rpi_ws2805
from fastapi import APIRouter, HTTPException
from pydantic import create_model

from ..animations.utils import get_animations_from_module

router = APIRouter()

ANIMATIONS = get_animations_from_module("idle") + get_animations_from_module("object")


@router.get("/")
def get_animations():
    return ANIMATIONS


@router.get("/{animation_name}/schema")
def get_animation_schema(animation_name: str):
    animation = next((a for a in ANIMATIONS if a["name"] == animation_name), None)
    if not animation:
        raise HTTPException(status_code=404, detail="Animation not found")

    fields = {}
    for param in animation["params"]:
        param_type = param["type"]
        # This is a simplification, a more robust solution would handle
        # the complex types like IdleAnimation and ObjectAnimation
        if "IdleAnimation" in param_type or "ObjectAnimation" in param_type:
            param_type = str
        else:
            param_type = eval(
                param_type,
                {
                    "typing": typing,
                    "rpi_ws2805": rpi_ws2805,
                    "Literal": Literal,
                    "List": typing.List,
                },
            )
        fields[param["name"]] = (param_type, param["default"])

    AnimationConfig = create_model(f"{animation_name}Config", **fields)
    return AnimationConfig.model_json_schema()
