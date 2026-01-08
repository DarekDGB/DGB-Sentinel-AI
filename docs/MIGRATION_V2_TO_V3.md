# Migration Guide — v2 to v3

This document explains how to migrate from **Sentinel AI v2** to **Shield Contract v3**.

---

## Key Principle

All requests—**including legacy v2 format**—are validated under **v3 rules**.

There is no bypass.

---

## What Changed in v3

### Validation
- Unknown fields rejected
- Strict schema enforcement
- Fail-closed by default

### Output
- Deterministic `context_hash`
- Stable reason codes
- Explicit decision field

### Behavior
- Same detection logic
- Stronger guarantees
- Auditable outputs

---

## v2 Adapter Behavior

- v2 requests are internally adapted to v3
- Validation occurs **after adaptation**
- If adapted request violates v3 → ERROR

---

## Recommended Migration Path

1. Update callers to send `contract_version = 3`
2. Add `component = "sentinel"`
3. Handle `decision == ERROR` as BLOCK
4. Stop parsing free-form messages
5. Store `context_hash` for audits

---

## v2 Deprecation

- v2 format is **maintenance-only**
- No new features
- No relaxed validation

**All guarantees are defined by v3.**

---

## Summary

Migrating to v3 is strongly recommended.

You gain:
- Determinism
- Auditability
- Stronger safety guarantees

v2 exists only to avoid sudden breakage—not as an escape hatch.
