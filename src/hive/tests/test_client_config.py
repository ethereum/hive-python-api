"""
Tests for `ClientConfig.post_with_files`.

These tests run against a local in-process HTTP server; unlike
`test_sanity.py` they do not require a running hive instance.
"""

import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import BufferedReader, BytesIO
from typing import Generator, List

import pytest

from hive.client import ClientConfig, ClientType

GENESIS = b'{"config": {"chainId": 1}}'


class CaptureHandler(BaseHTTPRequestHandler):
    """Record each request body and reply like the hive client endpoint."""

    bodies: List[bytes] = []

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", 0))
        self.bodies.append(self.rfile.read(length))
        body = b'{"id": "abc", "ip": "10.0.0.2"}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args) -> None:  # noqa: A002
        pass


@pytest.fixture
def server() -> Generator[ThreadingHTTPServer, None, None]:
    CaptureHandler.bodies = []
    srv = ThreadingHTTPServer(("127.0.0.1", 0), CaptureHandler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    yield srv
    srv.shutdown()
    srv.server_close()


@pytest.mark.parametrize(
    "file_input",
    [
        pytest.param(GENESIS, id="bytes"),
        pytest.param(BufferedReader(BytesIO(GENESIS)), id="buffered_reader"),
    ],
)
def test_post_with_files_uploads_file(server: ThreadingHTTPServer, file_input) -> None:
    config = ClientConfig(
        client_type=ClientType(name="go-ethereum", version="", meta={}),
        files={"/genesis.json": file_input},
    )
    url = f"http://127.0.0.1:{server.server_address[1]}/node"

    status, resp = config.post_with_files(url)

    assert status == 200
    assert resp == {"id": "abc", "ip": "10.0.0.2"}
    (body,) = CaptureHandler.bodies
    assert b'name="/genesis.json"' in body
    assert GENESIS in body
