#!/usr/bin/env python3
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Callable, Iterable, List, Optional, Tuple

from .homographic_projection import apply_transform
from .model import Event, EventObject, create_events_from_json


class XOVISServer:
    _subscribers: List[Tuple[Callable[[Event], None], Optional[List[Event]]]]
    _subscribers_position: List[Callable[[Iterable[EventObject]], None]]
    _host: str
    _port: int

    def __init__(self, host: str = "0.0.0.0", port: int = 8081) -> None:
        self._host = host
        self._port = port
        self._subscribers = []
        self._subscribers_position = []

    def subscribe(
        self, callback: Callable[[Event], None], filter: Optional[List[Event]] = None
    ) -> None:
        self._subscribers.append((callback, filter))

    def subscribe_position(
        self, callback: Callable[[Iterable[EventObject]], None]
    ) -> None:
        self._subscribers_position.append(callback)

    def _notify(self, data) -> None:
        self._notify_event(data)
        self._notify_position(data)

    def _notify_event(self, data) -> None:
        events = create_events_from_json(data)
        for event in events:
            for callback, event_filter in self._subscribers:
                if event_filter is None or type(event) in event_filter:
                    callback(event)

    def _notify_position(self, data) -> None:
        events = create_events_from_json(data)

        object_ids = [event.object.id for event in events]
        latest_objects: Iterable[EventObject] = [
            sorted(
                (event for event in events if event.object.id == object_id),
                key=lambda event: event.timestamp,
            )[-1].object
            for object_id in object_ids
        ]

        points = [(object.x, object.y) for object in latest_objects]
        mapped_points = apply_transform(points)
        mapped_objects = (
            EventObject(id=object.id, x=p[0], y=p[1], height=object.height)
            for object, p in zip(latest_objects, mapped_points)
        )

        for callback in self._subscribers_position:
            callback(mapped_objects)

    def start_server(self) -> HTTPServer:
        server = self

        class RequestHandler(BaseHTTPRequestHandler):
            def do_POST(self):
                content_length = int(self.headers["Content-Length"])
                post_data = self.rfile.read(content_length)

                try:
                    data = json.loads(post_data)
                    server._notify(data)
                    self.send_response(200)
                    self.end_headers()
                except json.JSONDecodeError:
                    self.send_response(400)
                    self.end_headers()

            def log_message(self, format, *args):
                # Suppress logging
                return

        http_server = HTTPServer((self._host, self._port), RequestHandler)
        thread = Thread(target=http_server.serve_forever)
        thread.daemon = True
        thread.start()
        print(f"HTTP server started on {self._host}:{self._port}")
        return http_server
