# Changelog

All notable changes to **DGB Sentinel AI** are documented in this file.

This project follows **semantic versioning** and enforces **contract stability**.
Breaking changes are only introduced with a **major version bump**.

---

## v3.2.0 — Manifest / Verdict / Receipt Lock

- Added Shield v3.2.0 manifest documentation under `docs/v3/`.
- Added reason ID and evidence family registries.
- Added canonical verdict or Orchestrator receipt validation code with negative-first fail-closed tests.
- Preserved 100% coverage gate.
- Locked AdamantineOS boundary language: Shield is consumed only through the deterministic Orchestrator receipt.


## [v3.1.0] — 2026-06-02

### 🛡️ Shield Hardening Release

This release hardens Sentinel AI for the Shield v3.1.0 upgrade track while preserving the existing Shield Contract v3 surface.

#### Changed
- Package and runtime version metadata updated to `3.1.0`.
- README, security references, auditor summary, and documentation index aligned with the 100% coverage gate.
- Adaptive Core bridge availability tests isolated from environment state.
- Deprecated naive UTC timestamp usage replaced with timezone-aware UTC.

#### Fixed
- Removed CLI module-entrypoint runtime warning in tests.
- Replaced deprecated event-loop test usage with `asyncio.run(...)`.
- Cleaned release documentation so v3.1.0 reflects the hardened test and CI posture.

#### Verification
- 95 tests passing.
- 704 statements covered.
- 0 missed statements.
- 100% coverage enforced in CI.
- Warning-free test output verified.

#### Security
- No new Sentinel authority was added.
- Sentinel remains read-only, non-consensus, non-signing, and non-executing.
- Fail-closed and deterministic Shield Contract v3 behavior remains unchanged.

---

## [v3.0.0] — 2026-01-07

### 🚀 Major Release — Shield Contract v3

This release marks the **formal stabilization of Sentinel AI v3** as a
deterministic, fail-closed, non-authoritative security component within the
DigiByte Quantum Immune Shield.

#### Added
- Shield Contract v3 with strict request/response schema
- Deterministic `context_hash` generation (SHA-256, canonical JSON)
- Explicit fail-closed validation semantics
- Stable, contract-facing reason codes
- Toxic telemetry regression test pack (DoS, NaN/Inf, size & depth limits)
- Shared v3 test fixtures for deterministic test construction
- Auditor Summary (`AUDITOR_SUMMARY.md`)
- Hardened Security Policy with explicit scope and non-goals
- CI enforcement with ≥90% test coverage gate
- Unicode hashing behavior explicitly tested and documented

#### Changed
- All request validation now occurs **before** any processing
- v2 behavior routed through v3 adapter (no bypass possible)
- Internal helpers hardened for determinism and safety
- Documentation rewritten to reflect strict non-authoritative boundaries

#### Fixed
- Edge cases in telemetry validation
- Inconsistent error handling paths
- Coverage gaps in adaptive bridges and hooks
- CI and packaging inconsistencies

#### Security
- Enforced deny-by-default behavior across all validation paths
- Added regression tests for adversarial input patterns
- Locked hashing behavior to prevent silent contract changes

---

## [v2.x] — Legacy Series (Maintenance Only)

### Notes
- v2 APIs remain available via internal adapter
- v2 behavior is regression-locked
- No new features will be added to v2
- All security guarantees are defined by Shield Contract v3

---

## Versioning Policy

- **MAJOR** — Contract or semantic breaking change
- **MINOR** — Backward-compatible feature additions
- **PATCH** — Bug fixes, tests, documentation, CI improvements

Any change that weakens determinism, fail-closed behavior, or non-authoritative
design will require a major version bump and explicit documentation.

---

*This changelog is authoritative. Undocumented changes are considered invalid.*
