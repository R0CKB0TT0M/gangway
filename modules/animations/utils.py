"""
This module provides utility functions for inspecting animation modules.
"""

import importlib
import inspect
from typing import Any, Dict, List


def get_animations_from_module(module_name: str) -> List[Dict[str, Any]]:
    """
    Extracts animation functions from a given module.
    """
    animations = []
    module = importlib.import_module(f".{module_name}", "modules.animations")
    for name, func in inspect.getmembers(module, inspect.isfunction):
        if name.startswith("_") or name == "interpolate_rgbcct":
            continue
        sig = inspect.signature(func)
        animations.append(
            {
                "name": name,
                "module": module_name,
                "params": [
                    {
                        "name": param.name,
                        "type": param.annotation.__name__
                        if hasattr(param.annotation, "__name__")
                        else str(param.annotation),
                        "default": param.default
                        if param.default != inspect.Parameter.empty
                        else None,
                    }
                    for param in sig.parameters.values()
                ],
            }
        )
    return animations
