from __future__ import annotations

import hashlib
import json
from typing import Any, Dict


def canonical_sha256(payload: Dict[str, Any]) -> str:
    """
    Deterministic SHA-256 of a canonical JSON representation.
    """
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
