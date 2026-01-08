# Sentinel AI — Shield Contract v3

This document defines the **authoritative contract** for interacting with  
**Sentinel AI v3**. Any integration that does not follow this contract is  
considered **unsupported and unsafe**.

---

## 1. Supported Contract Version

Sentinel AI supports **Shield Contract v3 only**.

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

For any valid request:

- Output is deterministic
- Output schema is stable
- A canonical `context_hash` is produced

This guarantees:
- reproducible audits
- replay-safe aggregation
- deterministic orchestration in higher layers

---

## 5. Context Hashing & Canonicalization

Sentinel AI computes `context_hash` as a **deterministic SHA-256 hash** of the
canonical JSON representation of the request context.

Canonicalization rules:
- JSON keys are sorted
- Numeric values are validated and finite
- UTF-8 encoding is used
- No locale-dependent behavior exists

### Unicode Normalization Rule (Important)

Sentinel AI **does not apply Unicode normalization** (e.g. NFC / NFD).

This means:
- Visually identical strings with different Unicode codepoint sequences  
  (e.g. precomposed vs decomposed characters) **will produce different hashes**
- Hashing is deterministic over **raw Unicode codepoints as provided**

**Callers are responsible** for applying Unicode normalization *before*
submitting requests if canonical equivalence is required.

This behavior is intentional and contract-stable.

---

## 6. Output Schema (v3)

Sentinel AI returns a versioned, deterministic response:

| Field | Description |
|-----|-------------|
| `contract_version` | Always `3` |
| `component` | `"sentinel"` |
| `request_id` | Echoed from request |
| `context_hash` | Deterministic SHA-256 hash |
| `decision` | `ALLOW`, `WARN`, `BLOCK`, or `ERROR` |
| `risk.score` | Float risk score |
| `risk.tier` | LOW / MEDIUM / HIGH / CRITICAL |
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
