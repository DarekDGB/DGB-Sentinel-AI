# Sentinel AI v2 → v3 Upgrade Plan (Shield Contract v3)

**Repo:** `DarekDGB/Sentinel-AI-v2`  
**Author attribution:** DarekDGB  
**License:** MIT  
**Mode:** Archangel Michael (invariants-first, deny-by-default, attacker mindset)

---

## 0. Non‑negotiable invariants (must hold after v3)

1. **Read‑only**: Sentinel must remain *observational only* (no wallet/key actions, no network mutations beyond its own telemetry reads).
2. **Deterministic outputs**: same input snapshot → same `context_hash`, same `decision`, same `reason_codes`.
3. **Deny-by-default**: unknown fields, unknown schema version, or invalid request must return **BLOCK** (or `ERROR` with `fail_closed=true`).
4. **Single public v3 entrypoint**: a single function/class method is the only supported v3 evaluation API.
5. **No caller-supplied “verdict shortcuts”**: never accept `cached_verdict`, `skip_checks`, `force_allow`, `unsafe`, etc.
6. **Regression-locked**: tests must prove (a) invalid v3 requests fail-closed, (b) v2 behavior remains stable until deprecation.

---

## 1. Current v2 public surface (what we preserve)

From the repo codebase (zip snapshot), the public consumer-facing interface is:

- `SentinelClient.evaluate_snapshot(raw_telemetry: Dict[str, Any]) -> SentinelResult`
- `SentinelResult(status: str, risk_score: float, details: Dict[str, Any])`

v3 must **not** break v2 immediately. We add v3 alongside v2, then migrate consumers later.

---

## 2. What “v3” means for Sentinel in the 5‑layer Shield

Sentinel v3 is **not** “new ML”. It is a **contract upgrade** so Sentinel can plug into:
- DQSN v3 aggregation
- ADN v3 local defense policy
- Guardian/QWG v3 enforcement
- Adaptive Core v3 orchestration

So the upgrade is about:
- stable input schema
- stable output schema
- stable reason codes
- stable context hashing

---

## 3. Shield Contract v3 (Sentinel‑specific)

### 3.1 Request object (v3)

A single request structure that is safe to pass across layers:

```json
{
  "contract_version": 3,
  "component": "sentinel",
  "request_id": "uuid-or-monotonic-id",
  "timestamp_utc": "2026-01-03T12:34:56Z",
  "source": {
    "node_id": "optional",
    "instance_id": "optional",
    "network": "mainnet|testnet|regtest|unknown"
  },
  "telemetry": {
    "...": "normalized telemetry fields (see 3.3)"
  },
  "constraints": {
    "fail_closed": true,
    "max_latency_ms": 2500
  }
}
```

**Rules**
- `contract_version` must be exactly `3` (fail closed otherwise).
- `telemetry` must be **normalized** (or normalization must happen internally in the v3 entrypoint).
- `constraints.fail_closed` defaults to `true` (ignore caller attempts to set it false).

### 3.2 Response object (v3)

```json
{
  "contract_version": 3,
  "component": "sentinel",
  "request_id": "...",
  "context_hash": "hex",
  "decision": "ALLOW|BLOCK|WARN|ERROR",
  "risk": {
    "score": 0.0,
    "tier": "LOW|MEDIUM|HIGH|CRITICAL"
  },
  "reason_codes": ["SNTL_OK", "SNTL_MEMPOOL_SPIKE", "..."],
  "evidence": {
    "features": { "optional": "safe subset" },
    "details": { "safe subset": "no secrets" }
  },
  "meta": {
    "model_used": false,
    "latency_ms": 0,
    "fail_closed": true
  }
}
```

**Rules**
- `context_hash` is mandatory and deterministic.
- `reason_codes` must be stable strings (versioned if needed).
- `evidence` must not contain secrets (no API keys, no filesystem paths, no full logs by default).
- `ERROR` must be fail-closed (treat as BLOCK upstream).

### 3.3 Minimal normalized telemetry fields (v3 baseline)

Do not over-specify v3 initially. Start with a safe baseline you already compute:

- block progress status + heights
- mempool size/tx rate (if present)
- peer count (if present)
- timestamp, node label/network
- optional “price feed deviation” fields (if present)

Everything else is **optional**, but must be carried in a namespaced way:
- `telemetry.extra.<name>` and treated as untrusted input.

---

## 4. Implementation plan (smallest safe steps)

### Step 1 — Add v3 contract module (no behavior change)
Add files:

- `src/sentinel_ai_v2/contracts/v3_types.py`
- `src/sentinel_ai_v2/contracts/v3_hash.py`
- `src/sentinel_ai_v2/contracts/v3_reason_codes.py`
- `src/sentinel_ai_v2/contracts/__init__.py`

**Design choices**
- Use `@dataclass(frozen=True)` to prevent mutation.
- Validate inputs strictly on construction (or via `validate()`).
- Keep hashing in one place.

### Step 2 — Add the single v3 entrypoint
Add:

- `src/sentinel_ai_v2/v3.py`

Expose exactly one public callable, e.g.:

- `SentinelV3.evaluate(request: SentinelV3Request) -> SentinelV3Response`

This entrypoint:
1. validates `contract_version == 3`
2. normalizes telemetry (reuse existing `normalize_raw_telemetry`)
3. computes deterministic features
4. computes risk score
5. maps to `decision + tier + reason_codes`
6. builds `context_hash` from canonical JSON of **(normalized telemetry + thresholds + model hash flag + contract_version)**

### Step 3 — Backward compatibility adapter (v2 calls into v3)
Modify existing `SentinelClient.evaluate_snapshot(...)` to:
- create a v3 request internally
- call `SentinelV3.evaluate(...)`
- map v3 response back to `SentinelResult`

This preserves v2 API while forcing all logic through v3.

### Step 4 — Add fail-closed tests (mandatory)
Add:

- `tests/test_contract_v3_fail_closed.py`
- `tests/test_contract_v3_determinism.py`
- `tests/test_v2_compatibility.py`

Minimum assertions:
- Invalid version → decision `ERROR` with `fail_closed=true`
- Missing telemetry → `ERROR`/BLOCK
- Same input twice → same `context_hash`
- v2 `evaluate_snapshot` still returns same shape (`status`, `risk_score`, `details`)

### Step 5 — Update docs (contract + integration)
Add:

- `docs/contracts/SHIELD_CONTRACT_v3.md` (Sentinel’s section)
- `docs/INTEGRATION_v3.md` (how ADN/DQSN should call Sentinel)

---

## 5. Reason codes (starter set)

Create `v3_reason_codes.py` with stable codes. Example starters:

- `SNTL_OK`
- `SNTL_WARN_STALL_RISK`
- `SNTL_BLOCK_STALLED_CHAIN`
- `SNTL_WARN_MEMPOOL_SPIKE`
- `SNTL_WARN_REORG_PATTERN`
- `SNTL_ERROR_INVALID_REQUEST`
- `SNTL_ERROR_SCHEMA_VERSION`

These are **contract-facing**; internal details can vary.

---

## 6. Attacker mindset checklist (hostile inputs we must reject)

- Oversized telemetry blobs (DoS) → enforce size limits
- NaN/Infinity floats → sanitize or reject
- Time-travel timestamps → clamp or mark suspicious
- Negative heights → reject
- Caller attempting `fail_closed=false` → ignore, always true
- Unknown `decision` values → impossible (enum-locked)
- Injection into `reason_codes` via input → never allow (server-only)

---

## 7. CI / tooling considerations (iPhone-friendly)

- Keep dependencies minimal (std lib + existing project deps).
- Keep tests fast (<10s) and deterministic.
- Avoid heavyweight ML toolchains in CI; model remains optional as in v2.

---

## 8. Suggested commit sequence (safe & reviewable)

1. `feat(contract): add Shield Contract v3 datatypes + hashing`
2. `feat(sentinel): add v3 evaluator entrypoint (fail-closed)`
3. `refactor(api): route v2 evaluate_snapshot through v3`
4. `test(v3): add determinism + fail-closed regression locks`
5. `docs(v3): add contract + integration notes`

---

## 9. Definition of done (for Sentinel v3)

- [ ] v3 request/response dataclasses exist and validate strictly
- [ ] single v3 entrypoint exists
- [ ] v2 API still works, but internally routes through v3
- [ ] fail-closed tests pass
- [ ] determinism test passes
- [ ] docs added for contract and integration

---

## 10. Next repo dependency note

Once Sentinel v3 lands, the next upgrade in the chain should be:
1) DQSN v3 (aggregation contract)
2) ADN v3 (policy + local response)
3) Adaptive Core v3 (orchestrator)
…then wallet-facing layers.

---

### Notes from the repo scope statement
The repository README explicitly frames Sentinel as **external, read-only monitoring** and not a protocol-layer system. This scope must remain unchanged through v3. (See repo README.) 
