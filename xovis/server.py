#!/usr/bin/env python3
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Callable, List, Optional

from .model import Event, create_events_from_json


class XOVISServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 8081):
        self._host = host
        self._port = port
        self._subscribers = []
        self._subscribers_position = []

    def subscribe(self, callback: Callable, filter: Optional[List[Event]] = None):
        self._subscribers.append((callback, filter))

    def subscribe_position(self, callback: Callable):
        self._subscribers_position.append(callback)

    def _notify(self, data):
        self._notify_event(data)
        self._notify_position(data)

    def _notify_event(self, data):
        events = create_events_from_json(data)
        for event in events:
            for callback, event_filter in self._subscribers:
                if event_filter is None or type(event) in event_filter:
                    callback(event)

    def _notify_position(self, data):
        events = create_events_from_json(data)
        events.sort(key=lambda event: event.timestamp)

        latest_event = events[0] if len(events) > 0 else None

        if latest_event is None:
            return

        for callback in self._subscribers_position:
            callback((latest_event.object.x, latest_event.object.y))

    def start_server(self):
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
