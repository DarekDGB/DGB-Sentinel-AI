# 🛡️ DGB Sentinel AI (Shield Contract v3)

[![CI](https://github.com/DarekDGB/DGB-Sentinel-AI/actions/workflows/tests.yml/badge.svg)](https://github.com/DarekDGB/DGB-Sentinel-AI/actions)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Contract](https://img.shields.io/badge/Shield%20Contract-v3-black.svg)](docs/CONTRACT.md)
[![Status](https://img.shields.io/badge/status-v3.1.0%20hardening-success.svg)](#)

### DigiByte Quantum Shield — External Telemetry Analysis & Threat Signal Generation
**Architecture by @DarekDGB — MIT Licensed**

---

## Overview

**Sentinel AI** is the **external, non-consensus telemetry analysis layer** of the **DigiByte Quantum Shield**.

It ingests **read-only signals** such as telemetry, observations, monitors, and external risk indicators. It evaluates those signals under **Shield Contract v3** and emits **deterministic threat signals** for higher layers to consume.

Sentinel AI is intentionally **non-authoritative**.

**Sentinel AI does NOT and MUST NOT:**

- change consensus
- sign transactions
- execute wallet actions
- gain authority over funds
- enforce mitigation or policy
- override Guardian Wallet, ADN, QWG, DQSN, Shield Orchestrator, or AdamantineOS decisions

> **Glass-box rule:** Sentinel can **observe and report**, never **execute or override**.

---

## Where Sentinel AI Sits (Architecture)

```text
┌──────────────────────────────────────────────┐
│        DigiByte Network / Environment         │
│                                              │
│  • Nodes                                     │
│  • Mempool                                   │
│  • Chain state                               │
│  • Telemetry / Metrics                       │
│  • External observations                     │
└───────────────────────┬──────────────────────┘
                        │   (read-only signals)
                        ▼
┌──────────────────────────────────────────────┐
│              Sentinel AI (v3)                 │
│  External Telemetry Analysis Layer            │
│                                              │
│  • Strict input validation (fail-closed)     │
│  • Deterministic evaluation                  │
│  • Stable reason codes                       │
│  • Canonical context_hash (SHA-256)          │
│  • Isolated Adaptive Core bridge tests       │
│                                              │
│  ❌ No signing                               │
│  ❌ No execution                             │
│  ❌ No authority                             │
└───────────────────────┬──────────────────────┘
                        │   (signals only)
                        ▼
┌──────────────────────────────────────────────┐
│      External Consumers / Higher Layers       │
│                                              │
│  • Guardian Wallet                            │
│  • Active Defense Network (ADN)              │
│  • Adaptive Core                              │
│  • Shield Orchestrator                        │
│  • Operators / Dashboards                    │
│                                              │
│  (Decision & enforcement happen here)        │
└──────────────────────────────────────────────┘
```

---

## Shield Contract v3 — What It Guarantees

Sentinel AI v3 is governed by Shield Contract v3.

The contract guarantees:

- deterministic evaluation
- versioned contract semantics
- strict input validation
- fail-closed behavior
- stable reason codes
- stable hashing anchors
- canonical `context_hash` generation
- no silent fallback
- no hidden authority

See `docs/CONTRACT.md` for the authoritative specification.

---

## Determinism Guarantees

Sentinel AI v3 is designed so that:

- same valid input produces the same output
- invalid input fails closed
- schema behavior is stable
- `context_hash` uses canonical SHA-256 hashing
- reason codes remain stable
- behavior is reproducible across Python 3.10, 3.11, and 3.12
- test outcomes do not depend on whether Adaptive Core is installed in the environment

---

## Adaptive Core Bridge Boundary

Sentinel AI may optionally report telemetry-derived signals into Adaptive Core through bridge logic.

This bridge is **not an authority path**.

The Adaptive Core bridge must remain:

- optional
- deterministic
- safe when unavailable
- isolated in tests
- non-executing
- non-consensus
- unable to convert Sentinel observations into direct enforcement

The v3.1.0 hardening track includes deterministic test isolation for the bridge availability path. Tests now cover the safe no-op behavior explicitly instead of depending on whether Adaptive Core happens to be installed in the environment.

---

## Quick Start (Integration)

```python
from sentinel_ai_v2.v3 import SentinelV3
from sentinel_ai_v2.config import CircuitBreakerThresholds

sentinel = SentinelV3(
    thresholds=CircuitBreakerThresholds(),
    model=None,
)

request = {
    "contract_version": 3,
    "component": "sentinel",
    "request_id": "sig_001",
    "telemetry": {"block_height": 12345},
    "constraints": {"max_latency_ms": 2500},
}

response = sentinel.evaluate(request)

if response["decision"] == "ERROR":
    raise RuntimeError(response["reason_codes"])
```

---

## Reason Codes

Sentinel returns stable identifiers such as:

- `SNTL_OK`
- `SNTL_ERROR_SCHEMA_VERSION`
- `SNTL_ERROR_UNKNOWN_TOP_LEVEL_KEY`
- `SNTL_ERROR_BAD_NUMBER`
- `SNTL_ERROR_TELEMETRY_TOO_LARGE`

See `src/sentinel_ai_v2/contracts/v3_reason_codes.py`.

---

## Backwards Compatibility

Legacy v2 requests are accepted through an internal adapter, but they are **always validated under v3 rules**.

v2 compatibility cannot bypass v3 enforcement.

Legacy support is allowed only when it preserves:

- fail-closed validation
- deterministic output
- stable reason codes
- v3 contract authority
- no hidden escalation path

---

## Tests & Guarantees

Sentinel AI v3 is regression-locked with tests that enforce:

- strict Shield Contract v3 validation
- fail-closed behavior
- deterministic `context_hash` generation
- bad number rejection
- unknown key rejection
- toxic telemetry rejection
- telemetry size limits
- v2 → v3 no-drift behavior
- API smoke coverage
- CLI smoke coverage
- server endpoint coverage
- model loader coverage
- scoring and correlation coverage
- wrapper workflow coverage
- Adaptive Core bridge and hook coverage
- Adaptive Core bridge unavailable-path isolation
- deterministic safe no-op behavior when Adaptive Core is unavailable

The CI workflow enforces:

```bash
pytest --cov=sentinel_ai_v2 --cov-report=term-missing --cov-fail-under=100 -q
```

Current verified result:

```text
95 passed
TOTAL 704 statements, 0 missed
Coverage 100.00%
```

**Tests define truth. No release is considered locked unless CI proves 100% coverage.**

---

## Continuous Integration

The CI workflow runs on:

- Python 3.10
- Python 3.11
- Python 3.12

The workflow performs:

- repository checkout
- Python setup
- pip upgrade
- editable package install with development dependencies
- syntax check with `compileall`
- full package test suite
- 100% coverage gate

See `.github/workflows/tests.yml`.

---

## Status

**Sentinel AI v3 is COMPLETE, LOCKED, and hardened to the Shield v3.1.0 coverage and determinism standard.**

Stable release baseline:

- `v3.0.0`

Current hardening track:

- `v3.1.0`

Current Sentinel hardening proof:

- 95 tests passing
- 704 statements covered
- 0 missed statements
- 100% coverage enforced in CI
- Adaptive Core bridge availability tests isolated from environment state

Further changes require:

- contract version review
- regression tests
- CI proof
- no weakening of the 100% coverage gate
- no undocumented behavior change
- no new authority path
- no fail-open behavior

---

## Security Position

Sentinel AI is a signal layer only.

A Sentinel signal may inform another component, but it must not become execution authority by itself.

Required security posture:

- **observe only**
- **report only**
- **fail closed**
- **deny silent fallback**
- **preserve human/governance gates at higher layers**
- **never allow AI/telemetry output to become direct authority**

---

## License

MIT License  
© 2025 DarekDGB
