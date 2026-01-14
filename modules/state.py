from typing import List, Optional

from .led_controller import LEDController
from .types import Point


class State:
    led_controller: Optional[LEDController] = None
    objects: List[Point] = []


STATE = State()
