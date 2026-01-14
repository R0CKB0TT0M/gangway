from fastapi import APIRouter
from fastapi.responses import Response

from .. import config
from ..helpers import to_hex
from ..led_controller import LEDController
from ..types import Point

router = APIRouter()

# TODO: Find a better way to access the led_controller
led_controller = LEDController()
objects: list[Point] = []


@router.get("/objects", response_class=Response)
def get_objects():
    svg_elements = [
        f'<circle cx="{p.x}" cy="{p.y}" r="5" fill="red" />' for p in objects
    ]

    content = f'<svg width="{led_controller.floor[2]}" height="{led_controller.floor[3]}" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="transparent" stroke="black"/>{"".join(svg_elements)}</svg>'
    return Response(content=content, media_type="image/svg+xml")


@router.get("/strips", response_class=Response)
def get_strips():
    svg_elements = [
        f'<line x1="{s.start.x}" y1="{s.start.y}" x2="{s.end.x}" y2="{s.end.y}" stroke="black" stroke-width="5" />'
        for s in config.CONFIG.STRIPS
    ]

    content = f'<svg width="{led_controller.floor[2]}" height="{led_controller.floor[3]}" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="transparent" stroke="black"/>{"".join(svg_elements)}</svg>'
    return Response(content=content, media_type="image/svg+xml")


@router.get("/state", response_class=Response)
def get_state():
    defs = []
    svg_elements = []

    for i, strip in enumerate(config.CONFIG.STRIPS):
        gradient_id = f"gradient{i}"
        stops = []
        for j in range(strip.len):
            led_index = strip.index + j
            led = next(
                (led for led in led_controller.leds if led.index == led_index),
                None,
            )
            if led:
                color = led_controller.color_of(led)
                hex_color = to_hex(color)
                offset = j / (strip.len - 1)
                stops.append(f'<stop offset="{offset}" stop-color="{hex_color}" />')
        defs.append(
            f'<linearGradient id="{gradient_id}" x1="{strip.start.x}" y1="{strip.start.y}" x2="{strip.end.x}" y2="{strip.end.y}" gradientUnits="userSpaceOnUse">{"".join(stops)}</linearGradient>'
        )
        svg_elements.append(
            f'<line x1="{strip.start.x}" y1="{strip.start.y}" x2="{strip.end.x}" y2="{strip.end.y}" stroke="black" stroke-width="7" />'
        )
        svg_elements.append(
            f'<line x1="{strip.start.x}" y1="{strip.start.y}" x2="{strip.end.x}" y2="{strip.end.y}" stroke="url(#{gradient_id})" stroke-width="5" />'
        )

    content = f'<svg width="{led_controller.floor[2]}" height="{led_controller.floor[3]}" xmlns="http://www.w3.org/2000/svg"><defs>{"".join(defs)}</defs><rect width="100%" height="100%" fill="transparent" stroke="black"/>{"".join(svg_elements)}</svg>'
    return Response(content=content, media_type="image/svg+xml")
