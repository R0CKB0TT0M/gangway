#!/usr/bin/env python3
import time
from threading import Thread
from typing import Callable, Dict, List, Tuple

from modules.animations import interpolate_rgbcct
from modules.animations.idle_animations import (
    IdleAnimation,
    fire,
    rainbow,
    strobo,
    theater_chase,
    wave,
)
from modules.animations.object_animations import ObjectAnimation, exponential
from modules.strips_conf import LED, LEDS, Point
from modules.ws2805_controller import RGBCCT, WS2805Controller
from modules.xovis.server import XOVISServer

LED_COUNT: int = 30
TARGET_WEIGHT: float = 10 / 255


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


IdleColor = Dict[int, RGBCCT] | RGBCCT | IdleAnimation


class LEDController(Thread):
    leds: List[LED]
    running: bool = True
    device: WS2805Controller

    floor: Tuple[float, float, float, float]

    target_colors: Dict[int, RGBCCT]
    current_colors: Dict[int, RGBCCT]

    init_time: float
    update_time: float

    idle: bool = True
    idle_instant_update: bool
    idle_color: IdleColor

    last_objects: List[Point]
    object_timeout: float
    object_animation: ObjectAnimation
    object_instant_update: bool

    def __init__(
        self,
        leds: List[LED] = LEDS,
        idle_color: IdleColor = RGBCCT(cw=255),
        object_animation: ObjectAnimation = exponential(),
        floor: Tuple[float, float, float, float] = (0, 0, 115, 490),
        object_timeout: float = 5,
        object_instant_update: bool = False,
        idle_instant_update: bool = False,
    ) -> None:
        super().__init__()
        self.leds = leds

        self.device = WS2805Controller(count=len(self.leds))

        self.idle_color = idle_color
        self.idle_instant_update = idle_instant_update

        self.floor = floor
        self.object_animation = object_animation
        self.object_timeout = object_timeout
        self.object_instant_update = object_instant_update

        self.init_time = time.time()
        self.update_time = time.time()

        if isinstance(self.idle_color, dict):
            self.target_colors = self.idle_color
        elif isinstance(self.idle_color, RGBCCT):
            self.target_colors = {led.index: self.idle_color for led in self.leds}
        else:
            self.target_colors = {led.index: RGBCCT(cw=255) for led in self.leds}

    @property
    def time(self):
        return time.time() - self.init_time

    def stop(self) -> None:
        self.running = False

    def update_objects(self, objects: List[Point]):
        self.update_time = time.time()

        if len(objects) == 0:
            self.idle = True

            if isinstance(self.idle_color, dict):
                self.target_colors = self.idle_color
            elif isinstance(self.idle_color, RGBCCT):
                self.target_colors = {led.index: self.idle_color for led in self.leds}
            return

        self.idle = False
        self.last_objects = objects

        self.target_colors = {
            led.index: self.object_animation(
                self.time, self.floor, led.p.tuple, led.index, objects
            )
            for led in self.leds
        }

        if self.object_instant_update:
            self.current_colors = self.target_colors.copy()

    def color_of(self, led: LED) -> RGBCCT:
        return self.current_colors[led.index]

    def target_of(self, led: LED) -> RGBCCT:
        return self.target_colors[led.index]

    def run(self):
        self.init_time = time.time()
        self.current_colors = self.target_colors

        loop_time = time.time()

        while self.running:
            if time.time() - self.update_time > self.object_timeout:
                self.update_objects([])

            if self.idle and isinstance(self.idle_color, Callable):
                current_time = self.time

                self.target_colors = {
                    led.index: self.idle_color(
                        current_time, self.floor, led.p.tuple, led.index
                    )
                    for led in self.leds
                }

                if self.idle_instant_update:
                    self.current_colors = self.target_colors.copy()
            else:
                current_time = self.time

                self.target_colors = {
                    led.index: self.object_animation(
                        current_time,
                        self.floor,
                        led.p.tuple,
                        led.index,
                        self.last_objects,
                    )
                    for led in self.leds
                }

                if self.object_instant_update:
                    self.current_colors = self.target_colors.copy()

            self.current_colors = {
                led.index: interpolate_rgbcct(
                    self.target_of(led),
                    self.color_of(led),
                    weight_a=(1 - (2 ** (loop_time - time.time()))) * TARGET_WEIGHT,
                )
                for led in self.leds
            }

            _ = [
                self.device.set_color(led.index, self.color_of(led))
                for led in self.leds
            ]

            self.device.show()
            loop_time = time.time()


if __name__ == "__main__":
    colors_a = [RGBCCT(r=255), RGBCCT(g=255)]
    colors_b = [RGBCCT(g=255), RGBCCT(r=255)]

    strobo_colors = [
        RGBCCT(r=255, g=255, b=255, cw=255, ww=255),
        RGBCCT(),
        RGBCCT(r=255),
        RGBCCT(),
        RGBCCT(b=255),
    ]

    led_controller = LEDController(
        idle_color=wave(colors_a),
        object_animation=exponential(
            primary=strobo(strobo_colors),
            secondary=strobo(strobo_colors),
            radius=100,
        ),
        idle_instant_update=True,
        object_instant_update=True,
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
