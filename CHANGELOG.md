# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- All Hive API calls in `hive/testing.py` (`HiveTestSuite.start`/`end`,
  `HiveTest.start`/`end`, `HiveTest.register_multi_test_client`) now share a
  single process-wide keep-alive `requests.Session` with connect-error retries
  (`HTTPAdapter` + `urllib3.Retry`) instead of opening a fresh TCP connection
  per call. At high simulator throughput (e.g. `consume-enginex` at >100
  tests/s), per-call connections exhausted the client-side ephemeral port range
  toward the Hive API endpoint (`OSError: [Errno 99]`, `EADDRNOTAVAIL`),
  causing sporadic test failures and silently lost test results.

## [v0.1.0] - 2025-07-09

Initial release of the Python Hive Simulator API with:

- Network configuration support.
- Client management functionality.
- Test suite management functionality.
