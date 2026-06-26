# DGB Sentinel AI Shield v4 Manifest

Author attribution: DarekDGB

## Component

```text
name: DGB Sentinel AI
component_id: sentinel_ai
component_role: shield_component_sentinel_ai
contract_version: 4
schema_version: shield.verdict.v2
```

## Purpose

DGB Sentinel AI Shield v4 emits cryptographically verifiable component verdict evidence for the Shield Orchestrator.

DGB Sentinel AI remains an evidence producer, not a transaction signer, broadcaster, consensus layer, wallet custody layer, or AdamantineOS override layer.

## Frozen Profiles

```text
canonicalization_profile: shield-v4-canon.v1
signature_policy: policy.v1
signature_bundle_schema: shield.signature_bundle.v1
key_registry_schema: shield.key_registry.v1
```

## Required Signature Paths

```text
classical-ed25519
ml-dsa
```

Both required paths must verify for policy.v1.

V4.8F-C adds a real OQS-backed adapter for the `ml-dsa` path only. It does not weaken the requirement for `classical-ed25519`.

## Optional Signature Path

```text
fn-dsa
```

FN-DSA may provide additional evidence, but it never overrides a failed required path.

## Algorithm Naming

ML-DSA is the NIST-standardized name for the signature direction formerly known as CRYSTALS-Dilithium.

FN-DSA is based on Falcon.

FN-DSA and ML-DSA are separate signature directions.

## Trust Profile

The DGB Sentinel AI v4 trust profile requires:

```text
role
key_id
key_version
algorithm
not_before
not_after
status
public_key
```

The only valid DGB Sentinel AI role in this component package is:

```text
shield_component_sentinel_ai
```

A revoked key, unknown key, wrong role, wrong algorithm, invalid validity window, malformed real binary key, or deterministic TEST-ONLY key in real backend mode fails closed.

## Real Backend Files

V4.8F-C adds:

```text
src/sentinel_ai_v2/v4/real_crypto_backend.py
src/sentinel_ai_v2/v4/oqs_mldsa_backend.py
docs/v4/REAL_CRYPTO_BACKEND.md
THIRD_PARTY_NOTICES.md
```

The OQS adapter maps:

```text
Shield algorithm: ml-dsa
OQS mechanism:    ML-DSA-65
```

It lazily imports `oqs` only when used and does not add a hard dependency to `pyproject.toml`.

## Current Implementation Status

V4.5C provided:

- a parallel `sentinel_ai_v2.v4` package;
- canonical component-verdict signed payload construction;
- deterministic TEST-ONLY signature entries;
- strict signature-bundle validation;
- DGB Sentinel AI role-bound trust profile validation;
- negative tests for tampering, context mismatch, and missing signatures.

V4.8F-C adds:

- a backend-neutral real crypto adapter for DGB Sentinel AI component verdict evidence;
- strict `b64u:<unpadded-base64url-bytes>` real binary material encoding;
- a lazy OQS/liboqs ML-DSA backend mapped to `ML-DSA-65`;
- tests proving OQS missing, disabled, wrong mechanism, malformed binary material, native OQS/liboqs exceptions, generic backend exceptions, non-boolean verify results, resolver exceptions, exact field-set violations, and TEST-ONLY material all fail closed.


V4.8G adds:

- a gated real-liboqs ML-DSA proof test for DGB Sentinel AI;
- a JUnit not-skipped guard for the dedicated real-OQS workflow;
- optional backend-reported public-key/signature length enforcement before native verify;
- `.github/workflows/shield-v4-real-oqs.yml` as an optional real-OQS proof harness.

The gated workflow is not a hard dependency for normal CI. It becomes proof only when `SHIELD_V4_REAL_OQS=1` runs on a liboqs-enabled runner and the JUnit guard confirms the test did not skip.
