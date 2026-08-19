"""
Shared HTTP session for Hive API requests.

Every request this package makes targets the single, fixed Hive API
endpoint. Opening a fresh TCP connection per call (bare ``requests.post``)
leaves a socket in TIME_WAIT for 60 seconds after close, and because
ephemeral-port exhaustion is per destination tuple, all of that churn
piles onto the one ``(host, port)`` the Hive API listens on. At high
simulator throughput (e.g. ``consume-enginex`` at >100 tests/s with three
API calls per test) the client-side ephemeral port range toward that
endpoint fills up and ``connect()`` intermittently fails with
``EADDRNOTAVAIL`` (``OSError: [Errno 99]``), losing test results.

Routing all Hive API calls through one process-wide keep-alive session
collapses the per-call connections into a handful of persistent sockets,
removing the mechanism entirely. The mounted ``Retry`` additionally
retries connection-establishment failures with exponential backoff as a
safety net. Only *connect* errors are retried: they are raised before the
request has been sent, so retrying is safe even for non-idempotent POSTs
(a retried ``start_test`` cannot create a duplicate test case).

Note: pooling only helps if the server honors keep-alive. Hive's Go
backend serves the simulation API with a default ``net/http`` server,
which keeps connections alive and sets no idle timeout.
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Retry connection-establishment failures only. Read errors and HTTP error
# statuses are not retried (the request may already have been processed by
# the server, so a retry could duplicate a non-idempotent call).
CONNECT_RETRIES = 5
BACKOFF_FACTOR = 0.5  # sleeps 0.5, 1, 2, 4 seconds between attempts

_session: requests.Session | None = None


def get_session() -> requests.Session:
    """
    Return the process-wide session used for all Hive API requests.

    The session is created lazily on first use, one per process (with
    pytest-xdist, one per worker). ``requests.Session`` connection pooling
    is thread-safe via the underlying ``urllib3`` pool.
    """
    global _session
    if _session is None:
        retries = Retry(
            total=None,
            connect=CONNECT_RETRIES,
            read=0,
            status=0,
            other=0,
            backoff_factor=BACKOFF_FACTOR,
        )
        adapter = HTTPAdapter(max_retries=retries)
        session = requests.Session()
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        _session = session
    return _session


def close_session() -> None:
    """
    Close the shared session and discard it.

    The next call to `get_session` creates a fresh session. Mainly useful
    for tests and for long-lived processes that want to release the pooled
    connections explicitly.
    """
    global _session
    if _session is not None:
        _session.close()
        _session = None
