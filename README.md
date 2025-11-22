# Sentinel AI v2 – Quantum-Resistant Threat Engine for DigiByte

**Sentinel AI v2** is the adversarial-hardened detection layer in the 3-layer DigiByte defense stack:

> **DQSN → Sentinel AI v2 → ADN**

It continuously monitors DigiByte telemetry, detects classical and quantum-era attacks, and emits clear machine-readable risk states for ADN.

Sentinel v2 is built for 2025–2035+ threats, including:
- 51% + time-warp + deep reorg attacks
- Quantum Shor/Grover threat scenarios
- Mempool spam/flood/RBF manipulation
- Adversarial ML poisoning and smoothing
- Sybil clustering & eclipse attacks

This repository provides the reference architecture and skeleton implementation for Sentinel AI v2 — a modular framework for DigiByte developers and security researchers.

---

## 3-Layer Defense Architecture

### 1. DQSN
Low-level entropy, timestamps, difficulty, and chain anomaly telemetry.

### 2. Sentinel AI v2 (this repository)
Turns telemetry into:
- risk scores
- attack classifications
- quantum anomaly alerts
- mempool manipulation signals

### 3. ADN (Autonomous Defense Node)
Executes defensive actions:
- hardened mode
- PQC activation
- peer filtering
- fee adjustments

Sentinel v2 never modifies DigiByte consensus — it is a sidecar security service.

---

## Design Goals

1. No live learning (no poisoning)  
2. Adversarial robustness  
3. Hard-coded circuit-breakers override AI  
4. Cryptographic integrity (verified model hashes/signatures)  
5. Deterministic output states: NORMAL, ELEVATED, HIGH, CRITICAL  

---

## Repository Layout

```
Sentinel-AI-v2/
├─ README.md
├─ LICENSE
├─ src/
│  └─ sentinel_ai_v2/
│     ├─ __init__.py
│     ├─ config.py
│     ├─ data_intake.py
│     ├─ model_loader.py
│     ├─ adversarial_engine.py
│     ├─ correlation_engine.py
│     ├─ circuit_breakers.py
│     ├─ scoring.py
│     ├─ api.py
│     ├─ cli.py
│     └─ server.py
└─ docs/
   ├─ technical-spec.md
   └─ whitepaper-sentinel-ai-v2.md
```

---

## Installation (Python Reference)

```bash
git clone https://github.com/DarekDGB/Sentinel-AI-v2.git
cd Sentinel-AI-v2

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

Run baseline tests:

```bash
pytest
```

---

## Basic Usage Example

```python
from sentinel_ai_v2.api import SentinelClient
from sentinel_ai_v2.config import load_config

config = load_config("config.yaml")
sentinel = SentinelClient(config=config)

telemetry = {
    "entropy": {...},
    "mempool": {...},
    "reorg": {...},
    "peers": {...},
    "hashrate": {...},
    "wallet_signals": {...},
}

result = sentinel.evaluate_snapshot(telemetry)

print(result.status)      # NORMAL / ELEVATED / HIGH / CRITICAL
print(result.risk_score)  # float 0.0 – 1.0
print(result.details)     # triggers / circuit-breakers
```

---

## Security Model

Sentinel AI v2 defends against:
- adversarial ML poisoning
- synthetic smoothed “too-normal” patterns
- slow drift attacks
- entropy/mempool manipulation
- tampered model/config files
- replayed telemetry

Sentinel AI v2 does NOT:
- change DigiByte consensus
- manage wallets or private keys
- replace DigiByte Core validation

---

## Documentation

- `docs/technical-spec.md` – full technical specification  
- `docs/whitepaper-sentinel-ai-v2.md` – whitepaper  

---

## License (MIT)

```
MIT License

Copyright (c) 2025 Darek (@Darek_DGB)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell  
copies of the Software, and to permit persons to whom the Software is  
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all  
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,  
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE  
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,  
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE  
SOFTWARE.
```
