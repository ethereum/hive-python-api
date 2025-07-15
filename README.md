# Ethereum Hive Simulators Python Library

[![PyPI version](https://badge.fury.io/py/ethereum-hive.svg)](https://badge.fury.io/py/ethereum-hive)
[![Python versions](https://img.shields.io/pypi/pyversions/ethereum-hive.svg)](https://pypi.org/project/ethereum-hive/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

Write [ethereum/hive](https://github.com/ethereum/hive) simulators using Python.

This library provides a Python API for creating and running Ethereum Hive simulation tests, allowing you to test Ethereum clients against various scenarios and network conditions.

## Installation

```bash
pip install ethereum-hive
```

## Features

- **Client Management**: Start, stop, and manage Ethereum clients.
- **Network Configuration**: Configure custom networks and genesis configuration.
- **Test Simulation**: Run comprehensive test suites against Ethereum clients.

## Quick Start

### Start a Hive Development Server

```console
./hive --dev --client go-ethereum
```

### Basic Example

Here's a basic example of how to use the Hive Python API with Hive running in developer mode. It requires a [genesis file](https://github.com/ethereum/hive-python-api/blob/e4a1108f3a8feab4c0d638f1393a94319733ae89/src/hive/tests/genesis.json); please modify the path as required.

```python
from pathlib import Path

from hive.simulation import Simulation
from hive.testing import HiveTestResult

# Create a simulation on a development hive server
simulator = Simulation(url="http://127.0.0.1:3000")

# Get information about the hive instance cli args and clients
hive_info = simulator.hive_instance()

# Start a test suite
suite = simulator.start_suite("my_test_suite", "my test suite description")

# Start a test
test = suite.start_test("my_test", "my test description")

# Start a client for the test
all_clients = simulator.client_types()
print(all_clients[0].version)

# Specify the genesis file; here we use the genesis from the unit test
files = {"genesis.json": Path("src/hive/tests/genesis.json").as_posix()}
env = {"HIVE_CHAIN_ID": "1"}
client = test.start_client(client_type=all_clients[0], environment=env, files=files)

# Run your test logic
# ...

# Stop the test and the suite (will clean-up clients)
test.end(result=HiveTestResult(test_pass=True, details="test details"))
suite.end()
```

For more detailed examples, check out the [unit tests](https://github.com/ethereum/hive-python-api/blob/e4a1108f3a8feab4c0d638f1393a94319733ae89/src/hive/tests/test_sanity.py) or explore the simulators in the [execution-spec-tests](https://github.com/ethereum/execution-spec-tests) repository.

## Development

### Setup

1. Install `uv`:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Clone and setup the project:

   ```bash
   git clone https://github.com/marioevz/hive.py.git
   cd hive.py
   uv sync --all-extras
   ```

### Running Tests

#### Prerequisites

1. Fetch and build hive:

   ```bash
   git clone https://github.com/ethereum/hive.git
   cd hive
   go build -v .
   ```

2. Run hive in dev mode:

   ```bash
   ./hive --dev --client go-ethereum,lighthouse-bn,lighthouse-vc
   ```

3. Run the test suite:

   ```bash
   uv run pytest
   ```

### Code Quality

- **Linting**: `uv run black src/`
- **Type checking**: `uv run mypy src/`
- **Import sorting**: `uv run isort src/`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Related Projects

- [ethereum/hive](https://github.com/ethereum/hive) - The main Hive testing framework.
- [ethereum/execution-spec-tests](https://github.com/ethereum/execution-spec-tests) - Contains implementations of several Hive simulators.
