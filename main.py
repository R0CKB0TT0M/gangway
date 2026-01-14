#!/usr/bin/env python3
import argparse
import time
from pathlib import Path
from threading import Thread

import uvicorn

from modules import config
from modules.api import app
from modules.api.visualization import objects
from modules.led_controller import LEDController
from modules.xovis.server import XOVISServer


class UvicornServer(Thread):
    def __init__(self, app, host, port):
        super().__init__()
        self.daemon = True
        self.app = app
        self.host = host
        self.port = port
        self.server = None

    def run(self):
        self.server = uvicorn.Server(
            uvicorn.Config(self.app, host=self.host, port=self.port)
        )
        self.server.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to the config.yaml file",
    )
    args = parser.parse_args()

    if args.config:
        config.CONFIG.path = args.config
        config.CONFIG.load()

    led_controller = LEDController(
        idle_color=config.CONFIG.IDLE_ANIMATION,
        object_animation=config.CONFIG.OBJECT_ANIMATION,
    )
    led_controller.start()

    xovis_server = XOVISServer()
    xovis_server.subscribe_position(led_controller.update_objects)
    xovis_http_server = xovis_server.start_server()

    def update_api_objects(new_objects):
        objects.clear()
        objects.extend(new_objects)

    xovis_server.subscribe_position(update_api_objects)

    api_server = UvicornServer(app, host="0.0.0.0", port=8082)
    api_server.start()
    print("API server started on 0.0.0.0:8082")

    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down.")
        xovis_http_server.shutdown()
        led_controller.stop()
