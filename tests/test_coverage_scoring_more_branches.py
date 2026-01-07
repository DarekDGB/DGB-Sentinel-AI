import sentinel_ai_v2.scoring as s
from sentinel_ai_v2.config import CircuitBreakerThresholds


def test_compute_risk_score_cb_triggered_forces_critical(monkeypatch):
    class _CB:
        triggered = True
        reasons = ["X"]

    class _Corr:
        adjusted_score = 0.1
        details = ["corr"]

    class _Adv:
        risk_boost = 0.1
        reasons = ["adv"]

    monkeypatch.setattr(s, "correlate_signals", lambda features: _Corr())
    monkeypatch.setattr(s, "analyse_for_adversarial_patterns", lambda features: _Adv())
    monkeypatch.setattr(s, "evaluate_circuit_breakers", lambda features, thresholds: _CB())

    out = s.compute_risk_score(features={"x": 1}, thresholds=CircuitBreakerThresholds())
    assert out.status == "CRITICAL"
    assert out.risk_score >= 0.99
    assert "adversarial:adv" in out.details
    assert "circuit_breaker:X" in out.details


def test_compute_risk_score_status_branches(monkeypatch):
    class _CB:
        triggered = False
        reasons = []

    class _Adv:
        risk_boost = 0.0
        reasons = []

    monkeypatch.setattr(s, "analyse_for_adversarial_patterns", lambda features: _Adv())
    monkeypatch.setattr(s, "evaluate_circuit_breakers", lambda features, thresholds: _CB())

    class _Corr:
        def __init__(self, adjusted_score):
            self.adjusted_score = adjusted_score
            self.details = ["corr"]

    # HIGH
    monkeypatch.setattr(s, "correlate_signals", lambda features: _Corr(0.85))
    out = s.compute_risk_score(features={"x": 1}, thresholds=CircuitBreakerThresholds())
    assert out.status == "HIGH"

    # ELEVATED
    monkeypatch.setattr(s, "correlate_signals", lambda features: _Corr(0.45))
    out = s.compute_risk_score(features={"x": 1}, thresholds=CircuitBreakerThresholds())
    assert out.status == "ELEVATED"

    # NORMAL
    monkeypatch.setattr(s, "correlate_signals", lambda features: _Corr(0.10))
    out = s.compute_risk_score(features={"x": 1}, thresholds=CircuitBreakerThresholds())
    assert out.status == "NORMAL"
