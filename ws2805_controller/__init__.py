#!/usr/bin/env python3
from dataclasses import dataclass

from rpi_ws2805 import RGBW, PixelStrip

# Configuration
LED_COUNT = 30  # Number of WS2805 ICs
LED_PIN = 18  # GPIO 18 (PWM0)
LED_FREQ_HZ = 800000  # 800khz
LED_DMA = 10
LED_BRIGHTNESS = 255
LED_INVERT = False
LED_CHANNEL = 0

# Strip type mask must match your C-patch (0x1F000000)
# This triggers the 'array_size = 5' logic in your patched ws2811.c
WS2805_STRIP = 0x1F000000


class RGBCCT(int):
    def __new__(cls, r=0, g=0, b=0, cw=0, ww=0):
        return int.__new__(cls, (cw << 32) | (ww << 24) | (b << 16) | (g << 8) | r)

    @property
    def r(self):
        return self & 0xFF

    @property
    def g(self):
        return (self >> 8) & 0xFF

    @property
    def b(self):
        return (self >> 16) & 0xFF

    @property
    def ww(self):
        return (self >> 24) & 0xFF

    @property
    def cw(self):
        return (self >> 32) & 0xFF


class WS2805Controller:
    def __init__(self, count: int = LED_COUNT, gpio_pin: int = LED_PIN):
        self.strip = PixelStrip(
            count,
            gpio_pin,
            LED_FREQ_HZ,
            LED_DMA,
            LED_INVERT,
            LED_BRIGHTNESS,
            LED_CHANNEL,
            strip_type=WS2805_STRIP,
        )
        self.strip.begin()

    def set_rgbcct(self, index, r, g, b, cw, ww):
        """
        Packs 5 channels into the 64-bit ws2811_led_t.
        Mapping matches your C-patch:
        Byte 0: R | Byte 1: G | Byte 2: B | Byte 3: CW | Byte 4: WW (bit 32+)
        """
        # Ensure values are within 8-bit bounds
        r, g, b, cw, ww = [val & 0xFF for val in (r, g, b, cw, ww)]

        # Packing into 64-bit integer
        color_64 = (cw << 32) | (ww << 24) | (b << 16) | (g << 8) | r
        self.strip.setPixelColor(index, color_64)

    def set_color(self, index, color: RGBW | RGBCCT):
        self.strip.setPixelColor(index, color)

    def fill(self, color):
        for i in range(self.strip.size):
            self.strip.setPixelColor(i, color)

    def show(self):
        self.strip.show()

    def clear(self):
        for i in range(LED_COUNT):
            self.strip.setPixelColor(i, 0)
        self.strip.show()
