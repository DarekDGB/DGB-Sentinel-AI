# DGB Sentinel AI v3.0.0 — Shield Contract v3 (Stable)

**Release date:** 2026-01-07  
**Maintainer:** DarekDGB  
**License:** MIT

---

## Overview

This release marks the **formal stabilization of Sentinel AI under Shield Contract v3**.

Sentinel AI v3 is a **deterministic, fail-closed, non-authoritative telemetry analysis layer**
within the DigiByte Quantum Shield. It observes, analyzes, and signals risk — **without**
executing, enforcing, or modifying blockchain state.

This release is **auditor-ready** and **integration-safe**.

---

## What’s New

### Shield Contract v3 (Locked)
- Strict request / response schema
- Versioned semantics (`contract_version = 3`)
- Unknown fields rejected (fail-closed)
- Stable, contract-facing reason codes
- Deterministic `context_hash` (canonical SHA-256)

### Security & Testing
- ≥ **90% test coverage enforced in CI**
- Toxic telemetry regression pack (NaN / Inf / size / depth / DoS patterns)
- Determinism tests across Python 3.10, 3.11, 3.12
- Regression lock for legacy v2 behavior

### Architecture & Boundaries
- Explicit **glass-box rule**: observe & report only
- No authority over funds, consensus, or execution
- v2 adapter preserved but **cannot bypass v3 validation**

---

## Documentation Included

- `README.md` — Public contract, architecture diagram, integration example
- `docs/CONTRACT.md` — Authoritative Shield Contract v3
- `docs/ARCHITECTURE.md` — Shield positioning
- `INTEGRATION.md` — Safe usage examples
- `TROUBLESHOOTING.md` — Common errors & fixes
- `MIGRATION_V2_TO_V3.md` — Legacy adapter behavior
- `SECURITY.md` — Responsible disclosure
- `AUDITOR_SUMMARY.md` — Independent audit overview
- `CHANGELOG.md` — Versioned change history

---

## Breaking Changes

- All requests are validated under **Shield Contract v3**
- Unknown top-level fields now **fail closed**
- Free-form error strings are deprecated — **use reason codes only**

> `decision = ERROR` must always be treated as **BLOCK** upstream.

---

## Backward Compatibility

- Legacy v2 requests are supported via an internal adapter
- All v2 requests are converted to v3 and validated
- v2 behavior is **maintenance-only** and regression-locked

---

## Non-Goals

Sentinel AI does **not**:
- execute transactions
- sign data
- enforce policy
- modify blockchain state
- participate in consensus

---

## Release Status

- Contract enforced
- CI green
- Coverage gate active
- Auditor-aligned
- Ready for integration

---

## Tag

```
v3.0.0
```
