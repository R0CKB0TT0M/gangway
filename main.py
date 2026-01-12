#!/usr/bin/env python3
import time
from threading import Thread
from typing import Iterable, List

from strips_conf import LED, LEDS, MAX_INDEX, Point
from ws2805_controller import RGBCCT, WS2805Controller
from xovis.model import EventObject
from xovis.server import XOVISServer

LED_COUNT: int = 30


def run_led_cycle(device: WS2805Controller) -> None:
    colors = [
        RGBCCT(r=255),
        RGBCCT(b=255),
    ]

    while True:
        for color in colors:
            device.clear()
            device.fill(color)
            device.show()
            time.sleep(0.01)


def handle_event(objects: Iterable[EventObject]) -> None:
    print(list(objects))


class LEDController(Thread):
    objects: Iterable[EventObject]
    leds: List[LED]
    running: bool = True
    device: WS2805Controller

    def __init__(self, leds: List[LED] = LEDS) -> None:
        # Wichtig: Basisklasse initialisieren
        super().__init__()
        self.objects = []
        self.leds = leds

        self.device = WS2805Controller(count=len(self.leds))

    def stop(self) -> None:
        self.running = False

    def notify(self, objects: Iterable[EventObject]) -> None:
        self.objects = objects

    @staticmethod
    def __object_to_point(object: EventObject) -> Point:
        return Point(object.x, object.y)

    def update_direct(self, objects: Iterable[EventObject]):
        print(f"updating... – {len(self.leds)} leds – objects")

        for object in objects:
            print(f"updating {object}")
            for led in self.leds:
                p_object = self.__object_to_point(object)
                if (led.p - p_object).length < 50:
                    self.device.set_color(led.index, RGBCCT(r=255))
                else:
                    self.device.set_color(led.index, RGBCCT(cw=255))
        self.device.show()

    def update_leds(self):
        for led in self.leds:
            for object in self.objects:
                p_object = self.__object_to_point(object)
                if (led.p - p_object).length < 30:
                    self.device.set_color(led.index, RGBCCT(cw=255))
                else:
                    self.device.set_color(led.index, RGBCCT())
        self.device.show()

    def run(self) -> None:
        print(f"Handling {len(self.leds)} leds")

        while self.running:
            self.update_leds()


if __name__ == "__main__":
    led_thread = LEDController()
    led_thread.start()

    led_thread.device.fill(RGBCCT(cw=255))
    led_thread.device.show()

    xovis_server = XOVISServer()
    xovis_server.subscribe_position(led_thread.update_direct)
    http_server = xovis_server.start_server()

    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down.")
        http_server.shutdown()
        device.clear()
