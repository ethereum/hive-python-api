"""
Ethereum Hive Simulators Python Library

This library provides a Python API for creating and running Ethereum Hive simulation tests,
allowing you to test Ethereum clients against various scenarios and network conditions.
"""

from importlib.metadata import version

from .client import Client, ClientRole, ClientType
from .network import Network
from .simulation import Simulation
from .testing import HiveTestSuite

try:
    __version__ = version("ethereum-hive")
except Exception:
    __version__ = "unknown"

__all__ = [
    "__version__",
    "Client",
    "ClientRole",
    "ClientType",
    "Network",
    "Simulation",
    "HiveTestSuite",
]
