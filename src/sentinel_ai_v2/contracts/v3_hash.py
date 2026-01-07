from __future__ import annotations

import hashlib
import json
from typing import Any, Dict


# v3 hash algorithm is explicit and MUST NOT change in-place.
# If we ever upgrade hashes, it must happen via a new contract version (e.g., v4).
HASH_ALGO_V3: str = "sha256"


def _canonical_json_bytes(payload: Dict[str, Any]) -> bytes:
    """
    Deterministic JSON encoding:
    - sorted keys
    - compact separators
    - UTF-8
    - ensure_ascii=False to preserve unicode deterministically
    """
    s = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return s.encode("utf-8")


def canonical_sha256(payload: Dict[str, Any]) -> str:
    """
    Canonical SHA-256 hash used by v3 for context_hash.
    """
    b = _canonical_json_bytes(payload)
    return hashlib.sha256(b).hexdigest()


def canonical_hash_v3(payload: Dict[str, Any]) -> str:
    """
    v3 hash entrypoint. This is intentionally non-agile in-place:
    v3 is pinned to SHA-256 for determinism + stable contracts.
    """
    if HASH_ALGO_V3 != "sha256":
        # deny-by-default if misconfigured
        raise RuntimeError("v3 hash algo misconfigured")
    return canonical_sha256(payload)
