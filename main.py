#!/usr/bin/env python3
import math
import random
import time
from threading import Thread
from typing import Callable, Dict, Iterable, List, Tuple

from modules.strips_conf import LED, LEDS, Point
from modules.ws2805_controller import RGBCCT, WS2805Controller
from modules.xovis.server import XOVISServer

LED_COUNT: int = 30
TARGET_WEIGHT: float = 0.05


def interpolate_rgbcct(
    color_a: RGBCCT, color_b: RGBCCT, weight_a=TARGET_WEIGHT
) -> RGBCCT:
    return RGBCCT(
        r=int(color_a.r * TARGET_WEIGHT + color_b.r * (1 - TARGET_WEIGHT)),
        g=int(color_a.g * TARGET_WEIGHT + color_b.b * (1 - TARGET_WEIGHT)),
        b=int(color_a.b * TARGET_WEIGHT + color_b.b * (1 - TARGET_WEIGHT)),
        ww=int(color_a.ww * TARGET_WEIGHT + color_b.ww * (1 - TARGET_WEIGHT)),
        cw=int(color_a.cw * TARGET_WEIGHT + color_b.cw * (1 - TARGET_WEIGHT)),
    )


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


IdleColor = (
    Dict[int, RGBCCT]
    | RGBCCT
    | Callable[[float, Tuple[float, float, float, float], Tuple[float, float]], RGBCCT]
)


class LEDController(Thread):
    leds: List[LED]
    running: bool = True
    device: WS2805Controller

    target_colors: Dict[int, RGBCCT]
    current_colors: Dict[int, RGBCCT]
    idle_color: IdleColor
    init_time: float
    idle: bool = True

    def __init__(
        self,
        leds: List[LED] = LEDS,
        idle_color: IdleColor = RGBCCT(cw=255),
    ) -> None:
        super().__init__()
        self.leds = leds

        self.device = WS2805Controller(count=len(self.leds))
        self.idle_color = idle_color
        self.init_time = time.time()

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

    def update_objects(self, objects: Iterable[Point]):
        no_objects: bool = True

        for object in objects:
            for led in self.leds:
                intensity = int(2 ** (-(led.p - object).length / 150) * 255)
                self.target_colors[led.index] = RGBCCT(r=intensity, g=255 - intensity)
            no_objects = False
            self.idle = False

        if no_objects:
            self.idle = True

            if isinstance(self.idle_color, dict):
                self.target_colors = self.idle_color
            elif isinstance(self.idle_color, RGBCCT):
                self.target_colors = {led.index: self.idle_color for led in self.leds}

    def run(self):
        self.init_time = time.time()
        self.current_colors = self.target_colors

        while self.running:
            if self.idle and isinstance(self.idle_color, Callable):
                self.current_colors = {
                    i: self.idle_color(
                        self.time, (0, 0, 115, 490), self.leds[i - 1].p.tuple
                    )
                    for (i, _) in self.current_colors.items()
                }
            else:
                self.current_colors = {
                    i: interpolate_rgbcct(self.target_colors[i], cc)
                    for (i, cc) in self.current_colors.items()
                }

            _ = [
                self.device.set_color(i, color)
                for i, color in self.current_colors.items()
            ]

            self.device.show()
            time.sleep(0.01)


def wave(
    colors: List[RGBCCT],
    n_waves: int = 3,
    speed: float = 50.0,
    wavelength: float = 200.0,
):
    waves = []
    for i in range(n_waves):
        angle = random.uniform(0, 2 * math.pi)
        direction = (math.cos(angle), math.sin(angle))
        color = random.choice(colors)
        waves.append(
            {
                "direction": direction,
                "color": color,
                "phase": (i / n_waves) * 2 * math.pi,
            }
        )

    k = 2 * math.pi / wavelength

    def animation(
        time: float,
        floor: Tuple[float, float, float, float],
        led_pos: Tuple[float, float],
    ) -> RGBCCT:
        final_color = RGBCCT()

        for wave_params in waves:
            direction = wave_params["direction"]
            color = wave_params["color"]
            phase = wave_params["phase"]

            proj = led_pos[0] * direction[0] + led_pos[1] * direction[1]
            intensity = (1 + math.sin(k * proj - (k * speed * time) + phase)) / 2

            final_color.r = min(255, final_color.r + int(color.r * intensity))
            final_color.g = min(255, final_color.g + int(color.g * intensity))
            final_color.b = min(255, final_color.b + int(color.b * intensity))
            final_color.cw = min(255, final_color.cw + int(color.cw * intensity))
            final_color.ww = min(255, final_color.ww + int(color.ww * intensity))

        return final_color

    return animation


if __name__ == "__main__":
    wavy_colors = [RGBCCT(r=255), RGBCCT(g=255), RGBCCT(b=255)]
    led_controller = LEDController(idle_color=wave(wavy_colors))

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
