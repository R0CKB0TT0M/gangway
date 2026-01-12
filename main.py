#!/usr/bin/env python3
import time
from threading import Thread
from typing import Tuple

from ws2805_controller import RGBCCT, WS2805Controller
from xovis.model import ZoneEntry, ZoneExit
from xovis.server import XOVISServer

LED_COUNT: int = 30


def run_led_cycle(device: WS2805Controller):
    colors = [
        RGBCCT(r=255),
        RGBCCT(g=255),
        RGBCCT(b=255),
        RGBCCT(cw=255),
        RGBCCT(ww=255),
    ]

    while True:
        for color in colors:
            device.clear()
            device.fill(color)
            device.show()
            time.sleep(1)


def handle_event(position: Tuple[int, int]):
    print(position)


if __name__ == "__main__":
    device = WS2805Controller(count=LED_COUNT)

    xovis_server = XOVISServer()
    xovis_server.subscribe_position(handle_event)
    http_server = xovis_server.start_server()

    led_thread = Thread(target=run_led_cycle, args=(device,))
    led_thread.daemon = True
    led_thread.start()

    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down.")
        http_server.shutdown()
        device.clear()
