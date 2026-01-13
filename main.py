#!/usr/bin/env python3
import time

from modules.animations.idle_animations import (
    alternate,
    fire,
    rainbow,
    strobo,
    swing,
    theater_chase,
    wave,
)
from modules.animations.object_animations import dot, exponential
from modules.led_controller import LEDController
from modules.ws2805_controller import RGBCCT
from modules.xovis.server import XOVISServer

if __name__ == "__main__":
    colors_a = [
        RGBCCT(r=255),
        RGBCCT(g=255),
        RGBCCT(b=255),
        RGBCCT(cw=255),
    ]

    led_controller = LEDController(
        idle_color=alternate(
            swing(),
            wave(colors_a),
            fire(),
            rainbow(),
            theater_chase(),
            strobo(),
            length=5,
        ),
        object_animation=dot(
            primary=strobo(),
            secondary=RGBCCT(r=255),  # swing(RGBCCT(cw=255, r=255, g=255, b=255)),
            radius=50,
        ),
    )

    led_controller.device.fill(RGBCCT(cw=255))
    led_controller.device.show()
    led_controller.start()

    xovis_server = XOVISServer()
    xovis_server.subscribe_position(led_controller.update_objects)
    http_server = xovis_server.start_server()

    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down.")
        http_server.shutdown()
        led_controller.stop()
