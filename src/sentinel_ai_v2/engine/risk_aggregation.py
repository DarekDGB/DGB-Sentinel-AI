from __future__ import annotations
from typing import Dict, Any

from .threat_models import THREAT_MODELS


def aggregate_risk(features: Dict[str, Any]) -> float:
    """
    Aggregate risk across all threat models, blending classical + quantum indicators.

    Returns a final risk score between 0.0 and 1.0.
    """

    # 1. Run all threat models
    model_scores = []
    for model in THREAT_MODELS:
        score = model.evaluate(features)
        model_scores.append(score)

    # 2. Base risk from models
    combined = max(model_scores)

    # 3. AI model contribution (optional)
    ai_signal = features.get("model_score")
    if ai_signal is not None:
        combined = max(combined, ai_signal)

    # 4. Hard anomaly boost for catastrophic markers
    if features.get("reorg_depth", 0) >= 5:
        combined = 1.0

    if features.get("entropy_drop", 0) > 0.75:
        combined = 1.0

    # 5. Final normalization
    return min(combined, 1.0)


def build_risk_report(features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a human- and machine-readable risk report.

    This is what the ADN receives and uses to trigger defense actions.
    """

    model_outputs = {
        model.name: model.evaluate(features)
        for model in THREAT_MODELS
    }

    final_score = aggregate_risk(features)

    level = "normal"
    if final_score >= 0.95:
        level = "critical"
    elif final_score >= 0.75:
        level = "high"
    elif final_score >= 0.50:
        level = "elevated"

    return {
        "score": final_score,
        "level": level,
        "models": model_outputs,
    }
