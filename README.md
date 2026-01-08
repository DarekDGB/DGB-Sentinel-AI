# 🛡️ DGB Sentinel AI (Shield Contract v3)

[![CI](https://github.com/DarekDGB/DGB-Sentinel-AI/actions/workflows/tests.yml/badge.svg)](https://github.com/DarekDGB/DGB-Sentinel-AI/actions)
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
│  • Canonical context_hash                    │
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

Sentinel AI is a **sensor**, not a controller.

---

## Shield Contract v3 — What It Guarantees

Shield Contract v3 enforces:

- **Deterministic evaluation** (same input → same output)
- **Versioned contract semantics**
- **Fail-closed behavior**  
  (unknown, malformed, or unsafe inputs are rejected)
- **Stable reason codes + hashing anchors** for auditability

Authoritative documents:
- `docs/CONTRACT.md`
- `docs/ARCHITECTURE.md`
- Upgrade rationale: `docs/upgrade/SENTINEL_AI_V3_UPGRADE_PLAN.md`

---

## Code Layout

- Source: `src/sentinel_ai_v2/`
- Contract helpers:
  - `src/sentinel_ai_v2/contracts/v3_hash.py`
  - `src/sentinel_ai_v2/contracts/v3_reason_codes.py`
- Wrapper / monitor tooling:
  - `src/sentinel_ai_v2/wrapper/`
- Examples: `examples/`
- Tests: `tests/`

> **Note:** the internal Python package name remains `sentinel_ai_v2` for compatibility,  
> while the repository enforces **Shield Contract v3 behavior**.

---

## Install (Developer)

This repository uses `pyproject.toml`.

```bash
python -m pip install -U pip
pip install -e .
pip install pytest
```

---

## Run Tests

```bash
pytest -q
```

CI runs tests across multiple Python versions and treats failures as
**contract violations**.

---

## Documentation Index

- `docs/INDEX.md` — starting point
- `docs/CONTRACT.md` — Shield Contract v3 (binding)
- `docs/ARCHITECTURE.md` — system placement
- `docs/AUDITOR_SUMMARY.md` — auditor-focused overview
- `SECURITY.md` — responsible disclosure

Legacy references live in `docs/legacy/` for historical context only.

---

## Security

Please see `SECURITY.md` for responsible vulnerability disclosure guidance.

---

## License

MIT License  
© 2026 **DarekDGB**
