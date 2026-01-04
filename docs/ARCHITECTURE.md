# Sentinel AI — Architecture
## Shield Contract v3

---

## Purpose of This Document

This document defines the **authoritative architecture** of Sentinel AI as a
**Shield Contract v3 component** within the DigiByte Quantum Shield.

It is written to:
- prevent architectural drift
- prevent misuse or overreach
- provide a stable reference for downstream layers (DQSN, ADN, Adaptive Core)
- support independent security review

This document is **normative**.  
If code or future documentation conflicts with this file, **this file wins**.

---

## Role in the Shield

Sentinel AI is the **outer perimeter sensor** of the shield architecture.

It:
- observes network telemetry
- evaluates risk patterns
- emits deterministic signals

It does **not**:
- execute transactions
- hold keys
- alter consensus
- modify wallet or node state

```
[ Telemetry Sources ]
        ↓
[ Sentinel AI (v3) ]
        ↓
[ DQSN v3 ]
        ↓
[ ADN v3 ]
        ↓
[ Guardian Wallet / QWG ]
```

Sentinel **signals**.  
Higher layers **decide and act**.

---

## Contract Authority

Sentinel AI operates exclusively under **Shield Contract v3**.

### Version gate
- `contract_version == 3` is mandatory
- Any other version is rejected **before parsing**

### Schema enforcement
- Unknown top-level keys → reject
- Missing required fields → reject
- Invalid values (NaN / Infinity) → reject
- Oversized telemetry → reject

All failures are **fail-closed**.

---

## Determinism Guarantees

Sentinel AI is **deterministic by design**.

- Canonical JSON hashing
- Stable reason codes
- No randomness in evaluation
- No time-based branching affecting decisions

Given the same input:
- output is identical
- `context_hash` is identical

This enables:
- reproducibility
- auditability
- cross-layer correlation

---

## Read-Only Guarantees

Sentinel AI enforces strict read-only behavior.

It cannot:
- write to consensus state
- trigger execution
- mutate inputs
- self-authorize actions

This is enforced by:
- architecture boundaries
- single v3 entrypoint
- test coverage
- explicit non-goals

---

## Failure Semantics

Sentinel AI is **fail-closed**.

Any invalid input produces:
- `decision = ERROR`
- `fail_closed = true`

Upstream systems must treat this as:
- **BLOCK**
- never as ALLOW
- never as WARN

Sentinel does not attempt recovery, correction, or guessing.

---

## Integration Rules (Mandatory)

Consumers of Sentinel AI **must**:

1. Use Shield Contract v3
2. Treat `ERROR` as BLOCK
3. Never bypass the v3 entrypoint
4. Never call internal modules directly
5. Preserve `context_hash` in downstream processing

Violation of these rules breaks the security model.

---

## Relationship to Other Layers

### DQSN v3
- Aggregates Sentinel signals
- Does not modify Sentinel outputs
- Uses `context_hash` for deduplication

### ADN v3
- Consumes risk signals
- Performs active defense
- May isolate, throttle, or alert

### Guardian Wallet / QWG
- Uses signals for user-side protection
- Never trusts Sentinel alone
- Combines with local policy

---

## Non-Goals (Explicit)

Sentinel AI is **not**:
- a wallet
- a node
- a consensus engine
- an execution engine
- an enforcement authority

Any attempt to extend Sentinel beyond these boundaries
must be rejected.

---

## Change Control

Any change to:
- contract semantics
- failure behavior
- determinism guarantees

requires:
- explicit documentation update
- regression tests
- security review

---

## Status

Sentinel AI is **architecturally complete** as a Shield Contract v3 component.

Future work may:
- extend analytics
- add new telemetry sources
- improve scoring models

But **must not** weaken:
- contract authority
- fail-closed behavior
- read-only guarantees

---

**Author:** DarekDGB  
**License:** MIT
