from sentinel_ai_v2.correlation_engine import correlate_signals
from sentinel_ai_v2.adversarial_engine import analyse_for_adversarial_patterns
from sentinel_ai_v2.scoring import compute_risk_score
from sentinel_ai_v2.config import CircuitBreakerThresholds


def test_correlate_signals_paths():
    r = correlate_signals({"mempool_score": 0.2, "reorg_score": 0.3})
    assert r.base_score > 0
    assert 0.0 <= r.adjusted_score <= 1.0
    assert any("mempool_score" in d for d in r.details)
    assert any("reorg_score" in d for d in r.details)


def test_adversarial_analysis_paths():
    r1 = analyse_for_adversarial_patterns({"suspicious_smoothness": True})
    assert r1.risk_boost > 0
    assert r1.reasons

    r2 = analyse_for_adversarial_patterns({})
    assert r2.risk_boost == 0.0


def test_compute_risk_score_smoke():
    thresholds = CircuitBreakerThresholds()
    score = compute_risk_score(
        features={"mempool_score": 0.1, "reorg_score": 0.1},
        thresholds=thresholds,
    )
    assert 0.0 <= score.risk_score <= 1.0
    assert isinstance(score.details, list)
