#!/usr/bin/env python3
"""Serve the hub without a directory listing.

Folders that contain index.html still open that page. Any other folder
address returns a short not-found page and does not name the files inside.
"""

import argparse
import io
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "hub"

NOT_FOUND = b"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Not found</title>
</head>
<body>
  <p>This address is not a page.</p>
  <p><a href="/">Home</a></p>
</body>
</html>
"""


class HubHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def list_directory(self, path):
        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(NOT_FOUND)))
        self.end_headers()
        return io.BytesIO(NOT_FOUND)


def main():
    parser = argparse.ArgumentParser(description="Serve the hub without directory listings.")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    handler = partial(HubHandler, directory=str(ROOT))
    server = ThreadingHTTPServer(("", args.port), handler)
    print(f"Serving {ROOT} at http://127.0.0.1:{args.port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
