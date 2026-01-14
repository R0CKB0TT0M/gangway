from typing import Any, Dict, List, Optional, Set

import yaml
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator

from ..animations.utils import get_animations_from_module
from ..config import CONFIG
from ..state import STATE
from .animations import ANIMATIONS, get_model_for_animation

router = APIRouter()

# Fetch available animations for validation
try:
    IDLE_ANIMATIONS_META = get_animations_from_module("idle")
    OBJECT_ANIMATIONS_META = get_animations_from_module("object")
    IDLE_ANIMATION_NAMES = {a["name"] for a in IDLE_ANIMATIONS_META}
    OBJECT_ANIMATION_NAMES = {a["name"] for a in OBJECT_ANIMATIONS_META}
except Exception as e:
    print(f"Warning: Could not load animation metadata: {e}")
    IDLE_ANIMATION_NAMES = set()
    OBJECT_ANIMATION_NAMES = set()


def validate_recursive(config: Any, allowed_names: Set[str]):
    if not isinstance(config, dict):
        raise ValueError("Animation config must be a dictionary")

    if "ref" in config:
        return

    keys = list(config.keys())
    if len(keys) != 1:
        raise ValueError("Animation config must define exactly one root animation")

    anim_name = keys[0]
    if anim_name not in allowed_names:
        # Fallback: if we are validating object animation, maybe this is an idle animation nested inside?
        # It's safer to just check if it is a valid animation name at all.
        if anim_name not in (IDLE_ANIMATION_NAMES | OBJECT_ANIMATION_NAMES):
            raise ValueError(f"Unknown animation: {anim_name}")

    params = config[anim_name] or {}

    if not isinstance(params, dict):
        raise ValueError(f"Parameters for {anim_name} must be a dictionary")

    Model = get_model_for_animation(anim_name, validation_mode=True)
    if not Model:
        raise ValueError(f"Model not found for {anim_name}")

    try:
        Model(**params)
    except Exception as e:
        raise ValueError(f"Invalid parameters for {anim_name}: {e}")

    # Check for nested animations
    anim_def = next((a for a in ANIMATIONS if a["name"] == anim_name), None)
    if anim_def:
        for param in anim_def["params"]:
            if param["type"] == "Callable":
                p_name = param["name"]
                if p_name in params:
                    val = params[p_name]
                    # Allowed names for nested animations: could be anything valid
                    all_names = IDLE_ANIMATION_NAMES | OBJECT_ANIMATION_NAMES
                    if isinstance(val, list):
                        for item in val:
                            validate_recursive(item, all_names)
                    elif isinstance(val, dict):
                        validate_recursive(val, all_names)


# --- Pydantic Models ---


class ProjectionModel(BaseModel):
    src_points: List[List[float]]
    dst_points: List[List[float]]
    floor: List[float]


class LedsModel(BaseModel):
    target_weight: float
    offset_x: float
    offset_y: float


class StripModel(BaseModel):
    index: int
    len: int
    start: List[float]
    end: List[float]


class AnimationsConfigModel(BaseModel):
    idle: Optional[Dict[str, Any]] = None
    object: Optional[Dict[str, Any]] = None

    @validator("idle")
    def validate_idle_animation(cls, v):
        if v is None:
            return v
        validate_recursive(v, IDLE_ANIMATION_NAMES)
        return v

    @validator("object")
    def validate_object_animation(cls, v):
        if v is None:
            return v
        validate_recursive(v, OBJECT_ANIMATION_NAMES)
        return v


class ConfigModel(BaseModel):
    projection: ProjectionModel
    leds: LedsModel
    strips: List[StripModel]
    animations: AnimationsConfigModel


# --- Endpoints ---


@router.get("/", response_model=ConfigModel)
def get_config():
    """
    Returns the current configuration loaded from the YAML file.
    """
    try:
        with open(CONFIG.path, "r") as f:
            raw_config = yaml.safe_load(f)
        return raw_config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load config: {e}")


@router.put("/")
def update_config(new_config: ConfigModel):
    """
    Updates the configuration, saves it to disk, and reloads the system.
    """
    try:
        # Convert model to dict
        config_dict = new_config.model_dump()

        # Save to file
        with open(CONFIG.path, "w") as f:
            yaml.dump(config_dict, f, sort_keys=False)

        # Reload global config object
        CONFIG.load()

        # Reload LED Controller if active
        if STATE.led_controller:
            STATE.led_controller.reload_config()

        return {"message": "Config updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update config: {e}")
