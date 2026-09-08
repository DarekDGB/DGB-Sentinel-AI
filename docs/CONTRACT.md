# Sentinel AI — Shield Contract v3

Author attribution: DarekDGB

Scope: retained v3 request/response compatibility contract. The current
distribution is the v4.0.0 candidate; its parallel signed component-evidence
interface is specified in [the v4 contract](v4/CONTRACT.md). Existing CLI and
HTTP adapters continue to use the v3 surface described below.

This document defines the **authoritative contract** for interacting with  
**Sentinel AI v3**. Any integration that does not follow this contract is  
considered **unsupported and unsafe**.

---

## 1. Supported Contract Version

This compatibility adapter accepts **Shield Contract v3 only**.

- Requests with any other version are rejected
- Version validation occurs **before** schema parsing
- Invalid versions fail closed

```
contract_version == 3
```

---

## 2. Required Request Fields

All requests **must** include the following top-level fields:

| Field | Type | Description |
|-----|------|-------------|
| `contract_version` | int | Must be `3` |
| `component` | string | Must be `"sentinel"` |
| `request_id` | string | Caller-defined identifier |
| `telemetry` | object | JSON-serializable telemetry payload |
| `constraints` | object | Optional execution constraints |

Unknown top-level fields are **rejected**.

---

## 3. Failure Semantics (Fail-Closed)

Sentinel AI is **fail-closed by design**.

Any invalid request results in:
- `decision = ERROR`
- `fail_closed = true`

Upstream systems **must treat this as BLOCK**.

Sentinel does not attempt to:
- repair malformed requests
- infer missing fields
- downgrade validation errors

---

## 4. Determinism Guarantees

For any request (valid or invalid):

- Output is deterministic
- Output schema is stable
- A canonical `context_hash` is produced

This guarantees:
- reproducible audits
- replay-safe aggregation
- deterministic orchestration in higher layers

---

## 5. Context Hashing & Canonicalization (Normative)

Sentinel AI computes `context_hash` as a **deterministic SHA-256 hash** of a
**canonical JSON payload**.

Important: The hashed payload is **explicitly defined** below.
Consumers must **not** guess which fields are included.

### 5.1 Canonicalization Rules

Canonicalization applies to all hashed payloads:

- JSON keys are sorted lexicographically
- Serialization uses compact JSON (no whitespace)
- UTF-8 encoding is used
- `ensure_ascii=false` is used (Unicode preserved deterministically)
- Floating-point values must be finite (no NaN / ±Inf)
- No locale-dependent behavior exists

### Unicode Normalization Rule (Important)

Sentinel AI **does not apply Unicode normalization** (e.g. NFC / NFD).

This means:
- Visually identical strings with different Unicode codepoint sequences  
  **produce different hashes**
- Hashing is deterministic over **raw Unicode codepoints as provided**

**Callers are responsible** for Unicode normalization *before submission*
if canonical equivalence is required.

This behavior is intentional and contract-stable.

---

### 5.2 Hashed Context — SUCCESS / WARN / BLOCK

When evaluation completes without a fatal error, `context_hash` is computed
from the canonical JSON object containing:

```json
{
  "component": "sentinel",
  "contract_version": 3,
  "telemetry": { ... },
  "thresholds": "<stable thresholds fingerprint>",
  "model_used": true
}
```

Rules:
- All listed fields **must** influence the hash
- Any semantic change in telemetry, thresholds fingerprint, or model_used
  **must change the hash**
- The following fields are **not guaranteed to be included** in the hashed payload:
  - `request_id`
  - `constraints`
  - `decision`
  - `reason_codes`
  - `evidence`

Consumers must not assume those fields are hash inputs.

---

### 5.3 Hashed Context — ERROR (Fail-Closed)

If request validation or evaluation fails, Sentinel AI **still produces a hash**.

In this case, `context_hash` is computed from the canonical JSON object:

```json
{
  "component": "sentinel",
  "contract_version": 3,
  "request_id": "<string>",
  "reason_code": "<error_code>"
}
```

Rules:
- Raw telemetry is **not included**
- Internal exception messages are **never included**
- `reason_code` is the **only semantic error signal** used for hashing
- Same invalid input + same validation failure → same hash

---

### 5.4 Explicit Exclusions (Hard Rules)

The following **must never influence `context_hash`**:

- Stack traces
- Exception strings
- Timestamps
- Memory addresses
- Random values
- Non-contract diagnostic logs

Violation of this rule breaks determinism and is a contract breach.

---

## 6. Output Schema (v3)

Sentinel AI returns a deterministic, versioned response containing:

| Field | Description |
|-----|-------------|
| `contract_version` | Always `3` |
| `component` | `"sentinel"` |
| `request_id` | Echoed from request |
| `context_hash` | Deterministic SHA-256 hash |
| `decision` | `ALLOW`, `WARN`, `BLOCK`, or `ERROR` |
| `risk` | Risk object (`score`, `tier`) |
| `reason_codes` | Stable contract-facing codes |
| `evidence` | Diagnostic payload |
| `meta.fail_closed` | Always `true` |

---

## 7. Reason Codes

Reason codes are **stable identifiers**, not free-form messages.

Examples:
- `SNTL_OK`
- `SNTL_V2_SIGNAL`
- `SNTL_ERROR_SCHEMA_VERSION`
- `SNTL_ERROR_INVALID_REQUEST`
- `SNTL_ERROR_UNKNOWN_TOP_LEVEL_KEY`
- `SNTL_ERROR_BAD_NUMBER`
- `SNTL_ERROR_TELEMETRY_TOO_LARGE`

Consumers must **not rely on string messages**, only codes.

---

## 8. Compatibility

Sentinel AI maintains a **legacy v2 API** via an internal adapter.

Important rules:
- All logic flows through Shield Contract v3
- v2 behavior is regression-locked
- v2 callers cannot bypass v3 validation

---

## 9. Integration Rules

All consumers **must**:

- Send Shield Contract v3 requests
- Treat `ERROR` as BLOCK
- Respect fail-closed semantics
- Never call internal Sentinel modules directly

Violation of these rules invalidates security guarantees.

---

## 10. Non-Goals

Sentinel AI explicitly does **not**:

- execute transactions
- enforce policy
- modify blockchain state
- replace DigiByte Core
- act as a consensus participant

---

## 11. Summary

Shield Contract v3 defines a **strict, minimal, deterministic interface**.

Sentinel AI exists to:
- observe
- analyze
- signal

It does not:
- decide
- enforce
- execute

This contract is **binding and non-negotiable**.
