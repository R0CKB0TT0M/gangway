"""
This module defines the API endpoint for discovering available animations.

It works by introspecting the Pydantic models defined in `modules.api.models`
to serve as a single source of truth for the animation structures, which the
frontend can then use to dynamically build its UI.
"""

<<<<<<< HEAD
import typing
from inspect import Parameter
from typing import Callable, List, Literal
=======
import inspect
from typing import Any, Dict, ForwardRef, List, Union, get_args, get_origin
>>>>>>> dca5af6 (simplified transfer models)

from fastapi import APIRouter
from pydantic import BaseModel
from pydantic_core import PydanticUndefined

from .models import IdleAnimationModel, ObjectAnimationModel, RGBCCTModel

router = APIRouter()


def _get_type_info(annotation: Any) -> Dict[str, Any]:
    """
    Recursively inspects a Python type annotation and converts it into a
    JSON-serializable dictionary that describes the type for the frontend.
    """
    if isinstance(annotation, ForwardRef):
        # This handles nested animations, like "AnyAnimationModel"
        return {"name": "Animation", "module": "any"}

    # Base cases for simple types
    if annotation is int:
        return {"name": "int"}
    if annotation is float:
        return {"name": "float"}
    if annotation is bool:
        return {"name": "bool"}
    if annotation is str:
        return {"name": "str"}
    if annotation is RGBCCTModel:
        return {"name": "RGBCCT"}

    origin = get_origin(annotation)
    args = get_args(annotation)

    # Handle generic types like List[T] and Union[T, U]
    if origin:
        origin_name = getattr(origin, "__name__", str(origin))
        # Filter out NoneType for Optional[T] which is Union[T, None]
        processed_args = [_get_type_info(arg) for arg in args if arg is not type(None)]
        return {"name": origin_name, "args": processed_args}

    # Fallback for unknown/any types
    return {"name": "any"}


def _parse_animation_union(union_model: Any, module_name: str) -> List[Dict[str, Any]]:
    """
    Parses a Pydantic Union model (e.g., IdleAnimationModel) and extracts the
    details of each animation within it.
    """
    animations = []
    # A model like `Union[StroboAnimation, FireAnimation]` is unpacked with get_args
    wrapper_models = get_args(union_model)

    for wrapper_model in wrapper_models:
        if not issubclass(wrapper_model, BaseModel) or not wrapper_model.model_fields:
            continue

        # Each wrapper model (e.g., StroboAnimation) has exactly one field
        # whose name is the animation name ('strobo') and whose type is the
        # parameter model (StroboParams).
        anim_name, params_field = list(wrapper_model.model_fields.items())[0]
        params_model = params_field.annotation

        params_list = []
        if issubclass(params_model, BaseModel):
            for param_name, param_field in params_model.model_fields.items():
                default_val = param_field.get_default()

                # Process the default value to make it JSON serializable
                if default_val is PydanticUndefined:
                    serializable_default = None
                elif isinstance(default_val, BaseModel):
                    serializable_default = default_val.model_dump()
                else:
                    serializable_default = default_val

                # Use a dummy kind, since the frontend doesn't need the full detail
                # of POSITIONAL_OR_KEYWORD vs VAR_POSITIONAL. The type info is enough.
                kind = inspect.Parameter.POSITIONAL_OR_KEYWORD

                param_info = {
                    "name": param_name,
                    "type": _get_type_info(param_field.annotation),
                    "default": serializable_default,
                    "kind": kind,
                }
                params_list.append(param_info)

        animations.append(
            {"name": anim_name, "module": module_name, "params": params_list}
        )

    # Sort animations alphabetically by name
    animations.sort(key=lambda x: x["name"])
    return animations


@router.get("/")
<<<<<<< HEAD
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
=======
def get_animations() -> List[Dict[str, Any]]:
    """
    Returns a list of all available idle and object animations, introspected
    from the API's own Pydantic models.
    """
    idle_anims = _parse_animation_union(IdleAnimationModel, "idle")
    object_anims = _parse_animation_union(ObjectAnimationModel, "object")
    return idle_anims + object_anims
>>>>>>> dca5af6 (simplified transfer models)
