#!/usr/bin/env python3
"""
Web Server to show the current state of the LEDs and objects
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import List

from .config import STRIPS, Point
from .helpers import to_hex
from .led_controller import LEDController


def create_request_handler(server_instance: "VisualizationServer"):
    class RequestHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/objects":
                self.send_response(200)

                self.send_header("Content-type", "image/svg+xml")

                self.end_headers()

                self.wfile.write(self._generate_objects_svg().encode("utf-8"))

            elif self.path == "/strips":
                self.send_response(200)

                self.send_header("Content-type", "image/svg+xml")

                self.end_headers()

                self.wfile.write(self._generate_strips_svg().encode("utf-8"))

            elif self.path == "/state":
                self.send_response(200)

                self.send_header("Content-type", "image/svg+xml")

                self.end_headers()

                self.wfile.write(self._generate_state_svg().encode("utf-8"))

            else:
                self.send_response(404)

                self.end_headers()

        def _generate_objects_svg(self) -> str:
            svg_elements = [
                f'<circle cx="{p.x}" cy="{p.y}" r="5" fill="red" />'
                for p in server_instance._objects
            ]

            return f'<svg width="{server_instance._led_controller.floor[2]}" height="{server_instance._led_controller.floor[3]}" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="transparent" stroke="black"/>{"".join(svg_elements)}</svg>'

        def _generate_strips_svg(self) -> str:
            svg_elements = [
                f'<line x1="{s.start.x}" y1="{s.start.y}" x2="{s.end.x}" y2="{s.end.y}" stroke="black" stroke-width="5" />'
                for s in STRIPS
            ]

            return f'<svg width="{server_instance._led_controller.floor[2]}" height="{server_instance._led_controller.floor[3]}" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="transparent" stroke="black"/>{"".join(svg_elements)}</svg>'

        def _generate_state_svg(self) -> str:
            defs = []
            svg_elements = []

            for i, strip in enumerate(STRIPS):
                gradient_id = f"gradient{i}"
                stops = []
                for j in range(strip.len):
                    led_index = strip.index + j
                    led = next(
                        (
                            led
                            for led in server_instance._led_controller.leds
                            if led.index == led_index
                        ),
                        None,
                    )
                    if led:
                        color = server_instance._led_controller.color_of(led)
                        hex_color = to_hex(color)
                        offset = j / (strip.len - 1)
                        stops.append(
                            f'<stop offset="{offset}" stop-color="{hex_color}" />'
                        )
                defs.append(
                    f'<linearGradient id="{gradient_id}" x1="{strip.start.x}" y1="{strip.start.y}" x2="{strip.end.x}" y2="{strip.end.y}" gradientUnits="userSpaceOnUse">{"".join(stops)}</linearGradient>'
                )
                svg_elements.append(
                    f'<line x1="{strip.start.x}" y1="{strip.start.y}" x2="{strip.end.x}" y2="{strip.end.y}" stroke="black" stroke-width="7" />'
                )
                svg_elements.append(
                    f'<line x1="{strip.start.x}" y1="{strip.start.y}" x2="{strip.end.x}" y2="{strip.end.y}" stroke="url(#{gradient_id})" stroke-width="5" />'
                )

            return f'<svg width="{server_instance._led_controller.floor[2]}" height="{server_instance._led_controller.floor[3]}" xmlns="http://www.w3.org/2000/svg"><defs>{"".join(defs)}</defs><rect width="100%" height="100%" fill="transparent" stroke="black"/>{"".join(svg_elements)}</svg>'

    return RequestHandler


class VisualizationServer:
    _host: str
    _port: int
    _led_controller: LEDController
    _objects: List[Point]

    def __init__(
        self, led_controller: LEDController, host: str = "0.0.0.0", port: int = 8082
    ) -> None:
        self._host = host
        self._port = port
        self._led_controller = led_controller
        self._objects = []

    def update_objects(self, objects: List[Point]) -> None:
        self._objects = objects

    def start_server(self) -> HTTPServer:
        handler = create_request_handler(self)
        http_server = HTTPServer((self._host, self._port), handler)
        thread = Thread(target=http_server.serve_forever)
        thread.daemon = True
        thread.start()
        print(f"Visualization server started on {self._host}:{self._port}")
        return http_server
