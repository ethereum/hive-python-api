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

Here's a basic example of how to use the Hive Python API:

```python
from hive import Hive
from hive.client import Client

# Initialize Hive simulator
hive = Hive()

# Start a client
client = hive.start_client("go-ethereum")

# Run your test logic
# ...

# Stop the client
hive.stop_client(client)
```

For more detailed examples, check out the [unit tests](src/hive/tests/test_sanity.py) or explore the simulators in the [execution-spec-tests](https://github.com/ethereum/execution-spec-tests) repository.

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
