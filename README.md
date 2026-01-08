# 🛡️ DGB Sentinel AI (Shield Contract v3)

[![CI](https://github.com/DarekDGB/DGB-Sentinel-AI/actions/workflows/tests.yml/badge.svg)](https://github.com/DarekDGB/DGB-Sentinel-AI/actions)
[![Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Contract](https://img.shields.io/badge/Shield%20Contract-v3-black.svg)](docs/CONTRACT.md)
[![Status](https://img.shields.io/badge/status-v3%20contract%20enforced-success.svg)](#)

### DigiByte Quantum Shield — External Telemetry Analysis & Threat Signal Generation  
**Architecture by @DarekDGB — MIT Licensed**

---

## Overview

**Sentinel AI** is the **external, non-consensus telemetry analysis layer** of the **DigiByte Quantum Shield**.

It ingests **read-only signals** (telemetry, observations, monitors), evaluates them under
**Shield Contract v3**, and emits **deterministic threat signals** for higher layers to consume.

Sentinel AI is intentionally **non-authoritative**.

**Sentinel AI does NOT and MUST NOT:**
- change consensus
- sign transactions
- execute wallet actions
- gain authority over funds
- enforce mitigation or policy

> **Glass-box rule:** Sentinel can **observe and report**, never **execute or override**.

---

## Where Sentinel AI Sits (Architecture)

```
┌──────────────────────────────────────────────┐
│        DigiByte Network / Environment         │
│                                              │
│  • Nodes                                     │
│  • Mempool                                   │
│  • Chain state                               │
│  • Telemetry / Metrics                       │
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
│  • Adaptive Core                              │
│  • Operators / Dashboards                    │
│                                              │
│  (Decision & enforcement happen here)        │
└──────────────────────────────────────────────┘
```

---

## Shield Contract v3 — What It Guarantees

- Deterministic evaluation
- Versioned contract semantics
- Fail-closed behavior
- Stable reason codes & hashing anchors

See `docs/CONTRACT.md` for the authoritative specification.

---

## Determinism Guarantees

- Same input → same output
- Stable schema
- Canonical SHA-256 `context_hash`
- Reproducible across Python 3.10–3.12

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
    "constraints": {"max_latency_ms": 2500}
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

Legacy v2 requests are accepted via an internal adapter but **always**
validated under v3 rules. v2 cannot bypass v3 enforcement.

---

## Continuous Integration

- Python 3.10 / 3.11 / 3.12
- ≥90% coverage enforced
- Contract & determinism tests on every commit

See `.github/workflows/tests.yml`.

---

## License

MIT License  
© 2026 DarekDGB
