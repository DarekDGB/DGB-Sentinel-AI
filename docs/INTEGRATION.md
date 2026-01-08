# Integration Guide — Sentinel AI v3

This guide shows how to integrate **Sentinel AI v3** safely and correctly.

---

## Installation

```bash
pip install dgb-sentinel-ai
```

(For development, use editable install.)

---

## Quick Start

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
    "telemetry": {
        "block_height": 12345,
        "entropy": {"score": 0.82},
    },
    "constraints": {"max_latency_ms": 2500},
}

response = sentinel.evaluate(request)

if response["decision"] == "ERROR":
    # Fail-closed: upstream MUST block
    raise RuntimeError(response["reason_codes"])

match response["risk"]["tier"]:
    case "LOW":
        action = "ALLOW"
    case "MEDIUM":
        action = "WARN"
    case "HIGH" | "CRITICAL":
        action = "BLOCK"
```

---

## Handling Responses

Always check in this order:

1. `decision == ERROR` → BLOCK
2. Inspect `risk.tier`
3. Use `reason_codes` for logic (never messages)
4. Persist `context_hash` for audits

---

## Reason Codes

Reason codes are **stable identifiers**.

Examples:
- `SNTL_OK`
- `SNTL_V2_SIGNAL`
- `SNTL_ERROR_SCHEMA_VERSION`
- `SNTL_ERROR_INVALID_REQUEST`
- `SNTL_ERROR_UNKNOWN_TOP_LEVEL_KEY`
- `SNTL_ERROR_BAD_NUMBER`
- `SNTL_ERROR_TELEMETRY_TOO_LARGE`

See full list in:
`src/sentinel_ai_v2/contracts/v3_reason_codes.py`

---

## Determinism Guarantee

Same request → same response → same `context_hash`.

This enables:
- Audit replay
- Cross-system verification
- Deterministic orchestration

---

## Security Rules

- Never bypass Sentinel
- Never treat ERROR as ALLOW
- Never rely on string messages
- Never mutate telemetry mid-flight
