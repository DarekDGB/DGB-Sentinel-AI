# Sentinel AI v2 – Technical Specification (Developer-Oriented)

## 1. Overview

Sentinel AI v2 is the adversarial-hardened threat engine in the 3-layer DigiByte
defense architecture:

> DQSN → Sentinel AI v2 → ADN

It consumes DigiByte telemetry (entropy, mempool, reorg, peers, timestamps, etc.),
computes a multi-layer risk score, and outputs a discrete state:

- NORMAL  
- ELEVATED  
- HIGH  
- CRITICAL  

This document defines the internal architecture, module responsibilities,
interfaces, and extension points for developers.

---

## 2. Architecture

Sentinel AI v2 consists of five main modules:

1. **Data Intake Layer**  
   Normalizes raw telemetry into structured objects.

2. **Model Loader & Integrity Verification**  
   Verifies AI model hash/signature before loading.

3. **Adversarial Intelligence Engine**  
   Detects poisoning, masking, “too-normal” synthetic behaviour.

4. **Correlation Graph Engine**  
   Multi-signal cross-correlation of entropy, mempool, reorg and peers.

5. **Circuit Breakers (Non-bypassable)**  
   Hard-coded rules that override AI if dangerous combinations appear.

Public interface is exposed via `SentinelClient`.

---

## 3. Data Model

### 3.1 TelemetrySnapshot

```python
@dataclass
class TelemetrySnapshot:
    entropy: Dict[str, Any] | None = None
    mempool: Dict[str, Any] | None = None
    reorg: Dict[str, Any] | None = None
    peers: Dict[str, Any] | None = None
    hashrate: Dict[str, Any] | None = None
    wallet_signals: Dict[str, Any] | None = None
    extra: Dict[str, Any] | None = None
```

DigiByte integrators may replace dictionaries with stronger schemas.

---

## 4. Model Loader & Verification

Defined in **model_loader.py**.

Responsibilities:

- Read model file from disk  
- Compute hash using SHA3-256 (default)  
- Compare to trusted expected hash from config  
- Reject models if hash mismatch  
- Provide minimal `run_model_inference()` interface  

Notes:

- Sentinel v2 does **not** bind to ONNX/Torch/TF → avoids legal/licensing issues  
- Developers can plug in real runtimes internally  

---

## 5. Correlation Engine

Defined in **correlation_engine.py**.

The engine aggregates multi-dimensional features:

- entropy_score  
- mempool_score  
- reorg_score  
- hashrate anomalies  
- peer churn  
- time-drift patterns  

Cross-signal boosts identify coordinated manipulation.

---

## 6. Adversarial Engine

Defined in **adversarial_engine.py**.

Detects:

- artificially stable behaviour  
- suppressed variance  
- borderline patterns just below thresholds  
- synthetic “normal-looking” telemetry  
- long-term drift poisoning  

Output:

```python
AdversarialAnalysisResult(
    risk_boost: float,
    reasons: list[str]
)
```

---

## 7. Circuit Breakers (Non-Bypassable)

Defined in **circuit_breakers.py**.

Triggers **CRITICAL** when:

### Combo A (immediate kill-switch)
- entropy_drop > threshold  
- mempool_anomaly > threshold  
- reorg_depth > threshold  

### Combo B (pattern toxicity)
- abnormal timestamp sequences  
- multi-region anomalies  
- repeated sudden reorgs  

Circuit breakers override **everything**, including AI.

---

## 8. Scoring Pipeline

1. Correlation Engine  
2. Adversarial Engine  
3. Circuit Breakers  
4. Final Score Mapping  

### Score → Status
- **CRITICAL** → any circuit breaker  
- **HIGH** → score ≥ 0.8  
- **ELEVATED** → score ≥ 0.4  
- **NORMAL** → otherwise  

Output:

```python
SentinelScore(
    status: str,
    risk_score: float,
    details: list[str]
)
```

---

## 9. Public API

`SentinelClient` evaluates raw telemetry:

```python
result = client.evaluate_snapshot(raw)
```

Returns:

```python
SentinelResult(
    status="NORMAL|ELEVATED|HIGH|CRITICAL",
    risk_score=float,
    details=list[str]
)
```

---

## 10. Testing Requirements

- unit tests  
- regression tests  
- adversarial attack simulations  
- DQSN integration tests  
- ADN integration tests  

---

## 11. Security & Licensing Notes

- No model weights included → **safe under MIT**  
- No external ML dependency  
- No consensus modifications  
- No wallet-key interaction  

---

## 12. Future Extensions

- full graph neural network inference  
- quantum anomaly classifiers  
- deeper wallet signal analysis  
- swarm-enabled anomaly correlation  
