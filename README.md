# DGB Sentinel AI - Shield v4.0.0 Candidate

Author attribution: DarekDGB

![Tests](https://github.com/DarekDGB/DGB-Sentinel-AI/actions/workflows/tests.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

Status: controlled pre-release; not released and not tagged.
Distribution version: `4.0.0`
Candidate tag: `v4.0.0`

## Purpose and authority

Sentinel AI evaluates observed defensive context and produces threat-signal
evidence. The parallel Shield v4 package constructs, signs, and verifies
domain-separated component-verdict evidence. These bounded capabilities do
not prove detection of every attack or protection of a production wallet.

Sentinel cannot sign or broadcast DigiByte transactions, change DigiByte
consensus, access wallet keys, approve execution, or override another layer.
Component signing uses a deployment-supplied evidence-key backend; it does
not grant wallet-key custody or transaction-signing authority.

The Shield Orchestrator verifies component evidence and produces the only
Shield receipt AdamantineOS may consume. AdamantineOS remains the final
fail-closed policy and execution boundary. A Shield ALLOW is permission to
continue those checks, not final execution approval.

## Current v4 release pack

- [Component contract](docs/v4/CONTRACT.md)
- [Manifest and trust profile](docs/v4/MANIFEST.md)
- [Real crypto backend](docs/v4/REAL_CRYPTO_BACKEND.md)
- [Test matrix](docs/v4/TEST_MATRIX.md)
- [Proof pack](docs/v4/PROOF_PACK.md)
- [Release status](docs/v4/RELEASE_STATUS_v4.0.0.md)
- [Documentation index](docs/INDEX.md)
- [Security policy](SECURITY.md)
- [Third-party notices](THIRD_PARTY_NOTICES.md)

Frozen identities:

```text
component_id: sentinel_ai
component_role: shield_component_sentinel_ai
contract_version: 4
schema_version: shield.verdict.v2
canonicalization_profile: shield-v4-canon.v1
signature_policy: policy.v1
```

Required signatures are `classical-ed25519` and `ml-dsa`, in that order.
Optional `fn-dsa` is last and cannot replace or rescue either required path.
Present-invalid optional evidence is fatal. The optional
`fips206-draft-falcon1024-v1` profile is draft Falcon-1024 evidence, not final
FIPS 206 proof.

Real adapters cover ML-DSA-65 and optional Falcon-1024 component evidence.
The repository does not provide a production classical Ed25519 backend.
A production deployment must satisfy both required policy paths.

## Retained compatibility surfaces

The import name `sentinel_ai_v2`, the CLI JSON key `sentinel_ai_v2`, and the
existing HTTP endpoint shapes are retained. Their displayed distribution
version is `4.0.0`. The CLI and HTTP service continue to use the v3
compatibility adapter; a version bump does not make those endpoints emit
v4 signed verdicts.

[The v3 request contract](docs/CONTRACT.md) remains contract version `3`.
Its frozen manifest keeps `PACKAGE_VERSION = "3.2.0"`.
[The v3 proof pack](docs/v3/PROOF_PACK.md) and
[v3 release history](docs/v3/RELEASE_STATUS_v3.2.0.md) are compatibility
references, not pending tag instructions. The package-version bump changes
none of the frozen v3 or v4 protocol identities, schemas, or KAT bytes.

## Verification and release gate

Python 3.10, 3.11, and 3.12 are the standard workflow matrix. The existing
workflow is named `Sentinel AI Tests (v3)`; it runs the complete current
suite, including v4 tests.

```text
python -m pip install -e ".[dev]"
python -m compileall -q src
pytest --cov=sentinel_ai_v2 --cov-report=term-missing --cov-fail-under=100 -q
```

Ordinary CI may skip the two explicitly environment-gated native-OQS nodes.
That is not native proof. The dedicated
`Shield v4 Real OQS ML-DSA and Falcon-1024 Proof` workflow must execute both
exact nodes with tests=2, skipped=0, failures=0, and errors=0 on the release
candidate commit.

E4 preparation does not authorize a tag. The package must pass external
re-audit, be committed by DarekDGB, pass both workflows on that commit, and
match a fresh post-commit ZIP before this component step is complete.

## Contributions and license

Preserve determinism of decisions and canonical payloads, strict input
validation, fail-closed verification, and explicit authority boundaries.
See [CONTRIBUTING.md](CONTRIBUTING.md). MIT License; copyright DarekDGB.
