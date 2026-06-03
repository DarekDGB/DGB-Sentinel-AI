# DGB Sentinel AI — Shield v3.2.0 Manifest

Author attribution: DarekDGB

## Component Identity

- `component_id`: `sentinel_ai`
- `contract_version`: `3`
- `package_version`: `3.2.0`
- `output_schema_version`: `shield.verdict.v1`

## Supported Decisions

- `ALLOW`
- `ESCALATE`
- `DENY`
- `ERROR`
- `SKIPPED`

## Reason ID Registry

- `SNTL_OK_TELEMETRY_ALLOW`
- `SNTL_ESCALATE_THREAT_REVIEW`
- `SNTL_DENY_THREAT_DETECTED`
- `SNTL_ERROR_AI_OUTPUT_UNTRUSTED`
- `SNTL_ERROR_CONTEXT_HASH_MISMATCH`

## Evidence Family Registry

- `telemetry`
- `monitor_signal`
- `threat_observation`
- `adaptive_core_bridge_event`

## Authority Boundary

This component is evidence-only. It does not sign, broadcast, hold keys, expand authority, override the Orchestrator, or approve AdamantineOS execution directly.

## Orchestrator Role

The component verdict is input evidence only. Final Shield outcome must be produced by the Shield Orchestrator deterministic receipt.

## AdamantineOS Visibility

AdamantineOS must not consume this component directly. AdamantineOS consumes Shield only through one deterministic Orchestrator receipt.
