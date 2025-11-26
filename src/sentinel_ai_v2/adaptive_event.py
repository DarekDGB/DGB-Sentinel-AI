from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AdaptiveEvent:
    """
    Standard anomaly event format that Sentinel AI v2 will send
    into the DigiByte-Quantum-Adaptive-Core.

    This does NOT change Sentinel's behaviour yet.
    It only defines a clean, consistent structure for anomalies.
    """

    layer: str = "sentinel"
    anomaly_type: str = "unknown"

    severity: float = 0.0
    qri_before: float = 0.0
    qri_after: float = 0.0

    block_height: Optional[int] = None
    txid: Optional[str] = None

    was_mitigated: bool = False
    details: Optional[str] = None

    created_at: datetime = datetime.utcnow()
