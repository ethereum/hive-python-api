"""
Tests for the shared Hive API HTTP session.

These tests run against a local in-process HTTP server; unlike
`test_sanity.py` they do not require a running hive instance.
"""

import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Generator, List, Tuple

import pytest

from hive.session import CONNECT_RETRIES, close_session, get_session
from hive.testing import HiveTestResult, HiveTestSuite


class KeepAliveHandler(BaseHTTPRequestHandler):
    """Minimal keep-alive HTTP/1.1 handler mimicking the hive API."""

    protocol_version = "HTTP/1.1"

    def _respond(self, body: bytes = b"1") -> None:
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", 0))
        if length:
            self.rfile.read(length)
        self._respond()

    def do_DELETE(self) -> None:  # noqa: N802
        self._respond()

    def log_message(self, format: str, *args) -> None:
        pass


class ConnectionCountingServer(ThreadingHTTPServer):
    """HTTP server recording each new TCP connection's client address."""

    daemon_threads = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connections: List[Tuple[str, int]] = []
        self._connections_lock = threading.Lock()

    def get_request(self):
        request, client_address = super().get_request()
        with self._connections_lock:
            self.connections.append(client_address)
        return request, client_address


@pytest.fixture(autouse=True)
def fresh_session() -> Generator[None, None, None]:
    """Give each test its own shared session instance."""
    close_session()
    yield
    close_session()


@pytest.fixture
def server() -> Generator[ConnectionCountingServer, None, None]:
    server = ConnectionCountingServer(("127.0.0.1", 0), KeepAliveHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server
    server.shutdown()
    server.server_close()


def test_get_session_returns_singleton():
    assert get_session() is get_session()


def test_session_mounts_connect_retries():
    adapter = get_session().get_adapter("http://127.0.0.1:3000")
    assert adapter.max_retries.connect == CONNECT_RETRIES
    # Read errors and HTTP error statuses must not be retried: the request
    # may already have been processed, and e.g. a duplicated `start_test`
    # would create a duplicate test case.
    assert adapter.max_retries.read == 0
    assert adapter.max_retries.status == 0


def test_hive_api_calls_reuse_one_connection(server: ConnectionCountingServer):
    """
    The whole point of the shared session: many suite/test API calls must
    be multiplexed over a small set of persistent keep-alive connections
    instead of opening (and TIME_WAIT-ing) one connection per call.
    """
    url = f"http://127.0.0.1:{server.server_address[1]}/testsuite"
    suite = HiveTestSuite.start(url=url, name="suite", description="desc")
    for _ in range(20):
        test = suite.start_test(name="test", description="desc")
        test.end(result=HiveTestResult(test_pass=True, details=""))
    suite.end()

    # 42 API calls; without pooling the server would see 42 connections.
    assert len(server.connections) == 1


def test_connect_errors_are_retried_with_backoff():
    """
    A connect() failure (e.g. EADDRNOTAVAIL under ephemeral-port
    exhaustion, or ECONNREFUSED here) must be retried until the endpoint
    becomes reachable.
    """
    # Reserve a port that is initially not listening.
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    probe.bind(("127.0.0.1", 0))
    port = probe.getsockname()[1]
    probe.close()

    server_holder: List[ConnectionCountingServer] = []

    def start_server_late() -> None:
        time.sleep(1.0)
        server = ConnectionCountingServer(("127.0.0.1", port), KeepAliveHandler)
        server_holder.append(server)
        server.serve_forever()

    thread = threading.Thread(target=start_server_late, daemon=True)
    thread.start()
    try:
        # First attempts hit ECONNREFUSED; a backoff retry succeeds once
        # the server is up (retries span ~15s in total, well past 1s).
        suite = HiveTestSuite.start(
            url=f"http://127.0.0.1:{port}/testsuite", name="suite", description="desc"
        )
        assert suite.id == 1
    finally:
        if server_holder:
            server_holder[0].shutdown()
            server_holder[0].server_close()
