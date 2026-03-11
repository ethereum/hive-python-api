"""Smoke test: verify the package is importable and exports its public API."""

import hive

assert hive.__version__
for name in ("Client", "ClientRole", "ClientType", "Network", "Simulation", "HiveTestSuite"):
    assert hasattr(hive, name), f"missing export: {name}"

print(f"hive {hive.__version__} OK")
