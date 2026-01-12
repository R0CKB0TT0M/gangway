#!/usr/bin/env python3
import csv
import time
from typing import Iterable

from xovis.model import EventObject
from xovis.server import XOVISServer

OUTPUT_FILE = "positions.csv"


def handle_event(objects: Iterable[EventObject]) -> None:
    with open(OUTPUT_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        for obj in objects:
            writer.writerow([obj.x, obj.y, obj.height])


if __name__ == "__main__":
    # Set up CSV file with header
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["x", "y", "z"])

    xovis_server = XOVISServer()
    xovis_server.subscribe_position(handle_event)
    http_server = xovis_server.start_server()

    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down.")
        http_server.shutdown()
