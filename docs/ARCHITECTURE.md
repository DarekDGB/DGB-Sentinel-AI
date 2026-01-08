# Sentinel AI — Architecture  
## Shield Contract v3

---

## Purpose of This Document

This document defines the **authoritative architecture** of Sentinel AI as a  
**Shield Contract v3 component** within the DigiByte Quantum Shield.

It exists to:

- prevent architectural drift  
- prevent misuse or authority creep  
- provide a stable reference for downstream layers  
- support independent security and auditor review  

This document is **normative**.  
If code, tests, or other documentation conflict with this file, **this file wins**.

---

## Role in the DigiByte Quantum Shield

Sentinel AI is the **outer‑perimeter, read‑only sensor layer** of the shield.

It exists to **observe and evaluate**, not to decide or enforce.

Sentinel AI:

- observes network and node telemetry  
- evaluates risk patterns deterministically  
- emits structured, contract‑bound signals  

Sentinel AI **does not**:

- execute transactions  
- hold or derive keys  
- alter consensus  
- modify wallet, node, or chain state  
- enforce mitigation or policy  

```
[ Telemetry Sources ]
        ↓
[ Sentinel AI (Shield v3) ]
        ↓
[ DQSN v3 ]
        ↓
[ ADN v3 ]
        ↓
[ Guardian Wallet / QWG ]
```

Sentinel **signals only**.  
All **decisions and actions** occur in higher layers.

---

## Contract Authority

Sentinel AI operates **exclusively** under **Shield Contract v3**.

There is **one authoritative entrypoint**: the v3 contract interface.

### Version Gate (Hard)

- `contract_version == 3` is mandatory  
- Any other version is rejected **before schema parsing**  

### Schema Enforcement

All requests are strictly validated:

- unknown top‑level keys → reject  
- missing required fields → reject  
- invalid types → reject  
- NaN / Infinity → reject  
- oversized or deeply nested telemetry → reject  

All validation failures are **fail‑closed**.

---

## Determinism Guarantees

Sentinel AI is **deterministic by design**.

Guarantees:

- canonical JSON hashing  
- stable reason codes (no free‑form strings)  
- no randomness in evaluation  
- no time‑based branching affecting outcomes  

Given the same valid input:

- response is identical  
- `context_hash` is identical  

This enables:

- reproducible audits  
- replay‑safe aggregation  
- cross‑layer correlation  
- independent verification  

---

## Read‑Only & Non‑Authority Guarantees

Sentinel AI is **structurally incapable of authority**.

It cannot:

- write to chain state  
- trigger execution paths  
- mutate telemetry  
- self‑authorize actions  
- bypass higher layers  

This is enforced by:

- architectural boundaries  
- a single v3 entrypoint  
- deny‑by‑default semantics  
- regression‑locked tests  
- explicit non‑goals  

---

## Failure Semantics (Fail‑Closed)

Sentinel AI is **fail‑closed by definition**.

Any invalid input produces:

- `decision = ERROR`  
- `meta.fail_closed = true`  

Upstream systems **must treat this as BLOCK**.

Sentinel AI:

- does not repair input  
- does not infer missing data  
- does not downgrade errors  
- does not guess intent  

---

## Integration Rules (Mandatory)

All consumers of Sentinel AI **must**:

1. Use Shield Contract v3  
2. Treat `decision = ERROR` as BLOCK  
3. Never bypass the v3 entrypoint  
4. Never call internal modules directly  
5. Preserve `context_hash` downstream  

Violating any of these rules **breaks the security model**.

---

## Relationship to Other Shield Layers

### DQSN v3 (Signal Network)

- aggregates Sentinel signals  
- performs correlation and deduplication  
- does **not** modify Sentinel outputs  
- uses `context_hash` as an anchor  

### ADN v3 (Active Defense Network)

- consumes Sentinel risk signals  
- performs active mitigation  
- may isolate, throttle, or alert  
- never delegates authority to Sentinel  

### Guardian Wallet / QWG

- uses Sentinel signals as one input  
- combines with local policy and user consent  
- never trusts Sentinel alone  

---

## Legacy v2 Compatibility

Sentinel AI maintains a **v2 adapter** for compatibility.

Rules:

- all v2 requests are converted to v3 internally  
- all validation occurs **after conversion**  
- v2 cannot bypass v3 rules  
- v2 behavior is regression‑locked  

v3 is the **only authoritative contract**.

---

## Non‑Goals (Explicit)

Sentinel AI is **not**:

- a wallet  
- a node  
- a consensus participant  
- an execution engine  
- a policy authority  

Any proposal to extend Sentinel beyond these boundaries  
**must be rejected**.

---

## Change Control

Any change affecting:

- contract semantics  
- validation rules  
- determinism guarantees  
- failure behavior  

requires:

- documentation update  
- regression tests  
- security review  

Undocumented behavior is **invalid behavior**.

---

## Status

Sentinel AI is **architecturally complete** as a Shield Contract v3 component.

Future work may:

- expand analytics  
- add telemetry sources  
- improve scoring models  

But must **never weaken**:

- contract authority  
- fail‑closed behavior  
- read‑only guarantees  

---

**Author:** DarekDGB  
**License:** MIT
