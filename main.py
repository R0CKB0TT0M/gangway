#!/usr/bin/env python3
import argparse
import time
from pathlib import Path

from modules import config
from modules.led_controller import LEDController
from modules.visualization_server import VisualizationServer
from modules.xovis.server import XOVISServer

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).parent / "config.yaml",
        help="Path to the config.yaml file",
    )
    args = parser.parse_args()

    config.load_config(args.config)

    led_controller = LEDController(
        idle_color=config.IDLE_ANIMATION,
        object_animation=config.OBJECT_ANIMATION,
    )
    led_controller.start()

    xovis_server = XOVISServer()
    xovis_server.subscribe_position(led_controller.update_objects)
    xovis_http_server = xovis_server.start_server()

    visualization_server = VisualizationServer(led_controller)
    xovis_server.subscribe_position(visualization_server.update_objects)
    visualization_http_server = visualization_server.start_server()

    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down.")
        xovis_http_server.shutdown()
        visualization_http_server.shutdown()
        led_controller.stop()
