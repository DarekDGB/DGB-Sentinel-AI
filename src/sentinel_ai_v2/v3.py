"""
Sentinel AI — Shield Contract v3 entrypoint (fail-closed only)

Archangel Michael invariant:
- contract_version must be exactly 3
- invalid / unknown / missing input fails closed
- no scoring / heuristics / ML in this phase
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict
import hashlib
import json


@dataclass(frozen=True)
class SentinelV3:
    """
    Single supported v3 entrypoint.

    NOTE: Phase 1 implementation is validation + fail-closed response only.
    No intelligence, no heuristics, no ML, no v2 routing.
    """

    COMPONENT: str = "sentinel"
    CONTRACT_VERSION: int = 3

    @staticmethod
    def evaluate(request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a Shield Contract v3 request.

        Fail-closed rules:
        - Any non-dict request -> ERROR (fail_closed=True)
        - contract_version != 3 -> ERROR (fail_closed=True)
        - missing telemetry -> ERROR (fail_closed=True)

        Returns a v3-shaped response, but decision remains ERROR until later phases.
        """
        # 1) Type guard
        if not isinstance(request, dict):
            return SentinelV3._error_response(
                request_id="unknown",
                reason_code="SNTL_ERROR_INVALID_REQUEST",
                details={"error": "request must be a dict"},
            )

        # 2) Pull request_id early (for traceability), but never trust it
        request_id = request.get("request_id", "unknown")

        # 3) Strict version check (fail closed)
        contract_version = request.get("contract_version", None)
        if contract_version != SentinelV3.CONTRACT_VERSION:
            return SentinelV3._error_response(
                request_id=str(request_id),
                reason_code="SNTL_ERROR_SCHEMA_VERSION",
                details={"error": "contract_version must be 3"},
            )

        # 4) Minimal required field: telemetry (can be empty dict, but must exist and be dict)
        telemetry = request.get("telemetry", None)
        if telemetry is None or not isinstance(telemetry, dict):
            return SentinelV3._error_response(
                request_id=str(request_id),
                reason_code="SNTL_ERROR_INVALID_REQUEST",
                details={"error": "telemetry must exist and be a dict"},
            )

        # 5) Deterministic context hash from canonical JSON (safe subset)
        context_hash = SentinelV3._context_hash(
            component=SentinelV3.COMPONENT,
            contract_version=SentinelV3.CONTRACT_VERSION,
            telemetry=telemetry,
        )

        # 6) Phase 1: fail-closed placeholder response (no scoring yet)
        return {
            "contract_version": SentinelV3.CONTRACT_VERSION,
            "component": SentinelV3.COMPONENT,
            "request_id": str(request_id),
            "context_hash": context_hash,
            "decision": "ERROR",
            "risk": {"score": 0.0, "tier": "LOW"},
            "reason_codes": ["SNTL_ERROR_NOT_IMPLEMENTED"],
            "evidence": {"features": {}, "details": {}},
            "meta": {"model_used": False, "latency_ms": 0, "fail_closed": True},
        }

    @staticmethod
    def _context_hash(component: str, contract_version: int, telemetry: Dict[str, Any]) -> str:
        """
        Deterministic, canonical hashing for v3.

        WARNING: Do not include timestamps here unless they are normalized/clamped first.
        """
        payload = {
            "component": component,
            "contract_version": contract_version,
            "telemetry": telemetry,
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @staticmethod
    def _error_response(request_id: str, reason_code: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fail-closed error response. Upstream must treat ERROR as BLOCK.
        """
        # Context hash for error paths: hash the minimal error envelope for determinism
        payload = {
            "component": SentinelV3.COMPONENT,
            "contract_version": SentinelV3.CONTRACT_VERSION,
            "request_id": str(request_id),
            "reason_code": reason_code,
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        context_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

        return {
            "contract_version": SentinelV3.CONTRACT_VERSION,
            "component": SentinelV3.COMPONENT,
            "request_id": str(request_id),
            "context_hash": context_hash,
            "decision": "ERROR",
            "risk": {"score": 0.0, "tier": "LOW"},
            "reason_codes": [reason_code],
            "evidence": {"features": {}, "details": details},
            "meta": {"model_used": False, "latency_ms": 0, "fail_closed": True},
        }
