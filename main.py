#!/usr/bin/env python3
import time

from ws2805_controller import RGBCCT, WS2805Controller

LED_COUNT: int = 30

if __name__ == "__main__":
    device = WS2805Controller(count=LED_COUNT)
    colors = [
        RGBCCT(r=255),
        RGBCCT(g=255),
        RGBCCT(b=255),
        RGBCCT(cw=255),
        RGBCCT(ww=255),
    ]

    try:
        while True:
            for color in colors:
                device.clear()
                device.fill(color)
                device.show()
                time.sleep(1)
    except KeyboardInterrupt:
        device.clear()
