#!/usr/bin/env python3
"""
Controller Thread for Animations
"""

import time
from threading import Thread
from typing import Callable, Dict, List, Optional, Tuple

from rpi_ws2805 import RGBCCT, PixelStrip

from . import config
from .animations.object import ObjectAnimation
from .defaults import (
    LED_BRIGHTNESS,
    LED_CHANNEL,
    LED_DMA,
    LED_FREQ_HZ,
    LED_INVERT,
    LED_PIN,
    WS2805_STRIP,
)
from .helpers import interpolate_rgbcct
from .types import LED, IdleColor, Point


class LEDController(Thread):
    """
    Controller Thread for LED-Strips. Can be updated with object positions to use in animations.

    Attributes:
        leds (List[LED]):
            List of LEDs with their respective indices and positions to handle
            Uses .strips_conf.LEDS by default.

        idle_color (IdleColor):
            Animation to play while no objects are within the handled zone.
            May either be a solid RGBCCT, a List of RGBCCTs or a function of signature IdleAnimation.
            Solid white by default.

        object_animation (ObjectAnimation):
            Animation to play while at least one object is within the handled zone.
            Must be a function of signature ObjectAnimation.
            exponential() by default.

        floor (Tuple[float, float, float, float]):
            Size of the handled area in cm.
            Uses .strips_conf.FLOOR by default.
    """

    leds: List[LED]
    running: bool = True
    strip: PixelStrip

    floor: Tuple[float, float, float, float]

    target_colors: Dict[int, RGBCCT]
    current_colors: Dict[int, RGBCCT]

    # Time counters
    init_time: float

    # An object is equivalent to a detected person
    last_objects: List[Point]
    object_animation: ObjectAnimation
    object_instant_update: bool = False

    # When no objects are detected the sensor switches to idle
    idle: bool = True
    idle_instant_update: bool = False
    idle_color: IdleColor

    def __init__(
        self,
        leds: Optional[List[LED]] = None,
        idle_color: Optional[IdleColor] = None,
        object_animation: Optional[ObjectAnimation] = None,
        floor: Optional[Tuple[float, float, float, float]] = None,
        gpio_pin: int = LED_PIN,
    ) -> None:
        super().__init__()
        self.leds = leds or config.CONFIG.LEDS
        self.idle_color = idle_color or config.CONFIG.IDLE_ANIMATION
        self.object_animation = object_animation or config.CONFIG.OBJECT_ANIMATION
        self.floor = floor or config.CONFIG.FLOOR

        self.strip = PixelStrip(
            len(self.leds),
            gpio_pin,
            LED_FREQ_HZ,
            LED_DMA,
            LED_INVERT,
            LED_BRIGHTNESS,
            LED_CHANNEL,
            strip_type=WS2805_STRIP,
        )
        self.strip.begin()

        self.init_time = time.time()

        if isinstance(self.idle_color, dict):
            self.target_colors = self.idle_color
        elif isinstance(self.idle_color, RGBCCT):
            self.target_colors = {led.index: self.idle_color for led in self.leds}
        else:
            self.target_colors = {led.index: RGBCCT(cw=255) for led in self.leds}

    def reload_config(self) -> None:
        self.leds = config.CONFIG.LEDS
        self.idle_color = config.CONFIG.IDLE_ANIMATION
        self.object_animation = config.CONFIG.OBJECT_ANIMATION
        self.floor = config.CONFIG.FLOOR

        if isinstance(self.idle_color, dict):
            self.target_colors = self.idle_color
        elif isinstance(self.idle_color, RGBCCT):
            self.target_colors = {led.index: self.idle_color for led in self.leds}
        else:
            self.target_colors = {led.index: RGBCCT(cw=255) for led in self.leds}

    def set_object_smooth(self) -> None:
        self.object_instant_update = False

    def set_object_instant(self) -> None:
        self.object_instant_update = True

    def set_idle_smooth(self) -> None:
        self.idle_instant_update = False

    def set_idle_instant(self) -> None:
        self.idle_instant_update = True

    @property
    def time(self):
        return time.time() - self.init_time

    def stop(self) -> None:
        self.running = False
        self.join()

    def update_objects(self, objects: List[Point] = []):
        """
        Inform the Thread of new objects to render.
        Will switch the thread to idle animation if called without parameters or empty list.
        """

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
                self.time,
                self.floor,
                led.p.tuple,
                led.index,
                objects,
                self.set_object_smooth,
                self.set_object_instant,
            )
            for led in self.leds
        }

        if self.object_instant_update:
            self.current_colors = self.target_colors.copy()

    def color_of(self, led: LED) -> RGBCCT:
        """
        Get the current color of an LED
        """

        return RGBCCT(
            value=self.current_colors[led.index] & 0xFFFFFFFFFF,
        )

    def target_of(self, led: LED) -> RGBCCT:
        """
        Get the target color of an LED (to be morphed to by interpolation in loop)
        """

        return self.target_colors[led.index]

    def apply_color(self) -> List[RGBCCT]:
        return [
            self.strip.setPixelColor(led.index, (c := self.color_of(led))) or c
            for led in self.leds
        ]

    def run(self):
        """
        Main animation loop
        """

        self.init_time = time.time()
        self.current_colors = self.target_colors

        loop_time = time.time()

        while self.running:
            if self.idle and isinstance(self.idle_color, Callable):
                self.target_colors = {
                    led.index: self.idle_color(
                        self.time,
                        self.floor,
                        led.p.tuple,
                        led.index,
                        self.set_idle_smooth,
                        self.set_idle_instant,
                    )
                    for led in self.leds
                }

                if self.idle_instant_update:
                    self.current_colors = self.target_colors.copy()
            else:
                self.target_colors = {
                    led.index: self.object_animation(
                        self.time,
                        self.floor,
                        led.p.tuple,
                        led.index,
                        self.last_objects,
                        self.set_object_smooth,
                        self.set_object_instant,
                    )
                    for led in self.leds
                }

                if self.object_instant_update:
                    self.current_colors = self.target_colors.copy()

            self.current_colors = {
                led.index: interpolate_rgbcct(
                    self.target_of(led),
                    self.color_of(led),
                    weight_a=(1 - (2 ** (loop_time - time.time())))
                    * config.CONFIG.TARGET_WEIGHT,
                )
                for led in self.leds
            }

            self.apply_color()

            self.strip.show()
            loop_time = time.time()
