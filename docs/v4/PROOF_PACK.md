# DGB Sentinel AI Shield v4 Proof Pack

Author attribution: DarekDGB
Status: controlled pre-release evidence
Distribution version: 4.0.0
Candidate tag: v4.0.0

## Claim boundary

This pack covers the implemented Sentinel AI component-evidence boundary and
the retained v3 compatibility interfaces. Sentinel evaluates defensive context
and may sign or verify domain-separated component verdicts using an explicit
evidence-key backend. It cannot sign or broadcast transactions, access wallet
keys, change DigiByte consensus, or approve execution.

The Shield Orchestrator produces the only Shield receipt AdamantineOS may
consume. AdamantineOS remains the final fail-closed policy and execution boundary.
Neither statement coverage nor native PQC round trips prove universal attack
detection, production protection, key custody, or deployment readiness.

## Frozen identity and compatibility

```text
component_id: sentinel_ai
component_role: shield_component_sentinel_ai
contract_version: 4
schema_version: shield.verdict.v2
canonicalization_profile: shield-v4-canon.v1
signature_policy: policy.v1
signature_bundle_schema: shield.signature_bundle.v1
key_registry_schema: shield.key_registry.v1
```

The distribution, import, CLI, and server display version is 4.0.0. The import
path and CLI JSON key remain `sentinel_ai_v2`. Existing CLI and HTTP behavior
continues through the v3 compatibility adapter; no endpoint is converted to a
v4 signed-verdict interface. The retained v3 manifest remains
`PACKAGE_VERSION = "3.2.0"` with contract version 3.

## Signature policy

```text
classical-ed25519 -> rfc8032-ed25519-v1          required, first
ml-dsa            -> fips204-ml-dsa-65-v1       required, second
fn-dsa            -> fips206-draft-falcon1024-v1 optional, last
```

Optional evidence cannot replace or rescue a failed or missing required path.
Present-invalid FN-DSA is fatal. The draft Falcon-1024 profile is not final
FIPS 206 proof. The package supplies real ML-DSA-65 and Falcon-1024 adapters;
it does not supply a production classical Ed25519 backend. Both required
policy paths must be satisfied in a production deployment.

## Frozen KAT file hashes

```text
176d9d8f7d16be456f2bf783c3031b65c46fd5f9efed1aba89d216b98406b0ff  tests/fixtures/v4/component_verdict_policy_v1_kat.json
b799b963cb46ccf579a0380cffeecd81f99fa616267e6d69fec4f2bf06e9f6ef  tests/fixtures/v4/fn_dsa_signed_message_draft_profile_kat.json
```

The separate component KAT signed-payload hash is
`a3881f27444ce73de875a15c8b413785a4fec4f4c03baaa6f8ee2fbf839736ae`.
E4 changes none of these fixture bytes or identities.

## Local preparation verification

Preparation interpreters: CPython 3.10.18, 3.11.15, and 3.12.13.
Test tools: pytest 8.4.2 and pytest-cov 7.0.0.
FastAPI 0.141.1, requests 2.34.2, and httpx 0.28.1 are present in the test
environments. These are recorded preparation versions, not new project pins.

The project is installed editable and `python -m compileall -q src` runs
before the workflow test command. Bytecode, pytest caches, Git metadata, and
coverage output remain enabled.

```text
pytest --cov=sentinel_ai_v2 --cov-report=term-missing --cov-fail-under=100 -q
247 passed
2 expected environment-gated native-OQS skips
1513/1513 statements
100 percent statement coverage
E4 release-pack lock: 10 passed
```

The two ordinary skips are not native proof. Existing tests cover malformed
inputs, required-signature failures, optional rescue attempts, canonical order,
role/domain/profile/key separation, context mutation, native exceptions,
non-boolean verification, and TEST-ONLY material at real boundaries.
The repository hygiene lock checks source encoding and attribution while
handling normal generated output; delivery checks separately reject such
output from the copy-only archive.

## Required native proof

The unchanged dedicated workflow must run exactly:

```text
tests/test_v48g_real_oqs_mldsa_backend.py::test_v48g_real_oqs_mldsa65_sentinel_backend_round_trip_and_negatives
tests/test_v48h_e_real_oqs_falcon_backend.py::test_v48h_e_real_oqs_falcon1024_backend_round_trip_and_negatives
```

The JUnit guard must report tests=2, skipped=0, failures=0, errors=0, and both
required testcase identities on the E4 commit. Native execution on that future
commit is pending. The workflow currently fetches floating liboqs and
liboqs-python sources; reproducible backend builds remain a later roadmap gate.

## Release decision

E4 is package preparation, not release authorization. Require external
re-audit, DarekDGB's commit, standard CI on Python 3.10/3.11/3.12, the exact
two-node native proof, and a fresh post-commit ZIP matching the audited delta.
Do not create or move v4.0.0 without an explicit release decision.
