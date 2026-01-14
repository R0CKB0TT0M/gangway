from fastapi import APIRouter

from ..state import STATE

router = APIRouter()


@router.get("/objects")
def get_objects():
    if not STATE.led_controller:
        return []

    return [{"x": p.x, "y": p.y} for p in STATE.objects]


@router.get("/leds")
def get_leds():
    if not STATE.led_controller:
        return {}

    leds_data = {}
    for led in STATE.led_controller.leds:
        color = STATE.led_controller.color_of(led)
        leds_data[led.index] = {
            "r": color.r,
            "g": color.g,
            "b": color.b,
            "cw": color.cw,
            "ww": color.ww,
        }
    return leds_data
