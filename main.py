#!/usr/bin/env python3
import time

from rpi_ws2805 import RGBCCT

from modules.animations.idle import (
    alternate,
    fire,
    rainbow,
    strobo,
    swing,
    theater_chase,
    wave,
)
from modules.animations.object import dot, exponential
from modules.led_controller import LEDController
from modules.xovis.server import XOVISServer

if __name__ == "__main__":
    colors_a = [
        RGBCCT(r=255),
        RGBCCT(g=255),
        RGBCCT(b=255),
        RGBCCT(cw=255),
    ]

    anim = alternate(
        swing(),
        strobo(),
        swing(RGBCCT(r=255), speed=20, direction="x", wavelength=10),
        strobo(),
        strobo(),
        swing(RGBCCT(b=255), speed=20),
        strobo(),
        strobo(),
        swing(RGBCCT(b=255), direction="x", wavelength=10),
        strobo(),
        strobo(),
        length=3,
    )

    led_controller = LEDController(
        idle_color=anim,
        object_animation=dot(
            primary=strobo(),
            secondary=anim,  # swing(RGBCCT(cw=255, r=255, g=255, b=255)),
            radius=50,
            force_instant=True,
        ),
    )
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
