# 🛡️ Sentinel AI v2  
### *DigiByte Quantum Shield — External Telemetry, Threat Modeling & Anomaly Detection Layer*  
**Architecture by @DarekDGB — MIT Licensed**

---

## 🚀 Purpose

**Sentinel AI v2** is the *external, non-consensus* security layer of the **DigiByte Quantum Shield**.  
It observes, analyzes, correlates, and surfaces emergent threats to the DigiByte network using a
multi-source telemetry model. Sentinel does **not** interfere with consensus — it informs higher layers.

It is designed as a **whitepaper-level architecture reference**, ready for DigiByte Core developers and
security researchers to extend and harden.

---

# 🔥 Position in the Quantum Shield (5-Layer Model)

```
        ┌────────────────────────────────────────┐
        │           Guardian Wallet             │
        │  (User-Side Defence, Rules Engine)    │
        └────────────────────────────────────────┘
                        ▲
                        │
        ┌────────────────────────────────────────┐
        │        Quantum Wallet Guard (QWG)      │
        │ Filters, PQC Safety, Behavioural Logic │
        └────────────────────────────────────────┘
                        ▲
                        │
        ┌────────────────────────────────────────┐
        │        ADN v2 — Active Defence         │
        │  Network Response, Isolation, Tactics  │
        └────────────────────────────────────────┘
                        ▲
                        │
        ┌────────────────────────────────────────┐
        │      Sentinel AI v2 (THIS REPO)        │
        │  Telemetry, Threat Intel, AI Scoring   │
        └────────────────────────────────────────┘
                        ▲
                        │
        ┌────────────────────────────────────────┐
        │  DQSN v2 — DigiByte Quantum Shield Net │
        │  Entropy, Node Health, UTXO Patterns   │
        └────────────────────────────────────────┘
```

Sentinel is the **eyes and ears** of the Quantum Shield.

---

# 🎯 Core Mission

### ✓ Observe  
Collect distributed measurements about the network: blocks, peers, latencies, forks, propagation.

### ✓ Identify  
Detect patterns correlated with attacks:  
- chain reorg attempts  
- eclipse attacks  
- sudden miner dominance  
- timestamp manipulation  
- hashpower anomalies  
- low-entropy block sequences  
- suspicious geographic clustering  

### ✓ Signal  
Emit **risk scores** and **structured signals** to ADN v2 and QWG.

### ✓ Never interfere with consensus  
Sentinel is **external**. Zero consensus impact.

---

# 🧠 Threat Model (Formal)

Sentinel evaluates threats across five planes:

1. **Entropy Plane** — randomness quality, difficulty adjustments, timestamp divergence  
2. **Topology Plane** — peer distribution, clustering, asynchrony  
3. **Hashrate Plane** — dominance, sudden power shifts, orphan spikes  
4. **Fork Plane** — fork depth, competitive chain behavior  
5. **Propagation Plane** — latency, bottlenecks, geographic imbalance  

Each plane forms part of a **multi-factor risk vector**.

---

# 🧩 Internal Architecture

```
sentinel_ai_v2/
│
├── collectors/
│     ├── block_collector.py
│     ├── peer_collector.py
│     ├── propagation_collector.py
│     └── entropy_collector.py
│
├── analytics/
│     ├── reorg_detector.py
│     ├── timestamp_analyzer.py
│     ├── miner_behavior.py
│     ├── anomaly_engine.py
│     └── score_fusion.py
│
├── outputs/
│     ├── risk_feed.py
│     ├── alert_bus.py
│     └── adn_signal_router.py
│
└── utils/
      ├── validators.py
      ├── config.py
      └── logging.py
```

This is a *reference structure*: DigiByte developers extend the logic safely.

---

# 📡 Data Flow Overview

```
[Attacker → Network Activity] 
          ↓
   (Collectors)
          ↓
  [Raw Telemetry Streams]
          ↓
   (Analytics Engines)
          ↓
   [Threat Scores + Vectors]
          ↓
   (Signal Router)
          ↓
 [ADN v2 / QWG / Guardian Wallet]
```

---

# 🛡️ Security Philosophy

Sentinel follows six principles:

1. **Zero Consensus Influence**  
   Observes—never rules.

2. **Explainable Detection**  
   AI assists but never becomes a black box.

3. **Multi‑Source Validation**  
   No single metric determines a threat.

4. **Hard Fail-Safe**  
   If uncertain → downgrade risk, not upgrade.

5. **Immutable Audit Trail**  
   Reproducible detection paths.

6. **Integration with Higher Layers**  
   Sentinel sends signals; ADN responds.

---

# 📈 Example Threat Analytics

### **Reorg Detection**
- Competing chain growth  
- Block timestamp deviations  
- Missing expected difficulty patterns  
- Sudden orphan spikes  

### **Hashrate Dominance**
- Single pool > 51%  
- New miner with anomalous behavior  

### **Propagation Attacks**
- Regional latency spikes  
- Eclipse attempts  
- Partition anomalies  

---

# 🔗 Interaction with Other Shield Layers

### **With DQSN v2**  
Consumes low-level entropy, node health, block structure metrics.

### **With ADN v2**  
Provides risk signals that trigger:
- node isolation recommendations  
- propagation warnings  
- defensive mode transitions  

### **With Guardian Wallet / QWG**  
Can warn user-side systems about:
- ongoing attacks  
- suspicious chain conditions  

---

# ⚙️ Code Status

Sentinel AI v2 includes:

- Reference Python implementation  
- Deterministic analytics stubs  
- Ready-to-extend module architecture  
- GitHub Actions test pipeline  
- Smoke tests ensuring structure integrity

This repo is **architecturally complete** and awaits community expansion.

---

# 🧪 Tests

The test suite includes:

- Structural smoke tests  
- Block progress monitor tests  
- Expandable framework for threat simulations  

Passing CI ensures repository integrity.

---

# 🤝 Contribution Policy

Please see `CONTRIBUTING.md`.

In summary:
- Improvements = welcome  
- Removals of architecture = rejected  
- Sentinel must *always* remain an **external, non-consensus monitoring layer**

---

# 📜 License

MIT License  
© 2025 **DarekDGB**

This architecture is free to use with mandatory attribution.

---
