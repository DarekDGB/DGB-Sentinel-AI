from __future__ import annotations

from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .wrapper.sentinel_wrapper import SentinelWrapper


# -----------------------------
# FastAPI app & global wrapper
# -----------------------------

app = FastAPI(
    title="Sentinel AI v2 API",
    description="Quantum-Resistant Threat Engine for DigiByte",
    version="0.1.0",
)

# Single shared wrapper instance – keeps last result in Monitor
wrapper = SentinelWrapper()


# -----------------------------
# Pydantic models (request/response)
# -----------------------------

class EvaluateRequest(BaseModel):
    """
    Request body for /evaluate endpoint.

    `telemetry` can contain any DigiByte node / network telemetry fields.
    """
    telemetry: Dict[str, Any] = Field(
        ...,
        description="Raw telemetry snapshot from DigiByte node / ADN.",
    )


class EvaluateResponse(BaseModel):
    status: str
    risk_score: float
    details: Any


class StatusResponse(BaseModel):
    status: str
    risk_score: float
    details: Any


class HealthResponse(BaseModel):
    ok: bool
    status: str


# -----------------------------
# Endpoints
# -----------------------------

@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """
    Lightweight health check for load balancers / monitoring.
    """
    last = wrapper.last_status()
    return HealthResponse(
        ok=True,
        status=str(last.get("status", "NO_DATA")),
    )


@app.post("/evaluate", response_model=EvaluateResponse)
async def evaluate(req: EvaluateRequest) -> EvaluateResponse:
    """
    Evaluate one telemetry snapshot and return risk assessment.

    This is what dashboards, bots and ADN nodes will typically call.
    """
    try:
        result = wrapper.evaluate(req.telemetry)
    except Exception as exc:  # noqa: BLE001 – simplified error handling for this reference implementation
        # In production, developers can replace this with more robust logging / error handling.
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return EvaluateResponse(
        status=result.status,
        risk_score=result.risk_score,
        details=result.details,
    )


@app.get("/status", response_model=StatusResponse)
async def status() -> StatusResponse:
    """
    Return last known Sentinel status snapshot (from Monitor).

    Useful for dashboards / widgets that only need:
    - status
    - last risk_score
    - last details
    """
    last = wrapper.last_status()
    return StatusResponse(
        status=str(last.get("status", "NO_DATA")),
        risk_score=float(last.get("risk_score", 0.0)),
        details=last.get("details", []),
    )
Add FastAPI server for Sentinel AI v2
