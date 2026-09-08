# Sentinel AI Documentation Index

Author attribution: DarekDGB

## Current Shield v4.0.0 candidate

These documents describe the parallel v4 component-evidence interface:

- [Contract](v4/CONTRACT.md)
- [Manifest and trust profile](v4/MANIFEST.md)
- [Real crypto backend](v4/REAL_CRYPTO_BACKEND.md)
- [Test matrix](v4/TEST_MATRIX.md)
- [Proof pack](v4/PROOF_PACK.md)
- [Release status](v4/RELEASE_STATUS_v4.0.0.md)
- [README](../README.md)
- [Changelog](../CHANGELOG.md)
- [Security policy](../SECURITY.md)

The distribution is a controlled pre-release; not released and not tagged.

## Retained v3 compatibility

The existing CLI, HTTP service, and compatibility adapter retain v3 behavior.
Their displayed distribution version is 4.0.0; their contract is not rewritten.

- [v3 request contract](CONTRACT.md)
- [v3 architecture](ARCHITECTURE.md)
- [v3 auditor summary](AUDITOR_SUMMARY.md)
- [v3 manifest](v3/MANIFEST.md)
- [v3 reason IDs](v3/REASON_IDS.md)
- [v3 evidence families](v3/EVIDENCE_FAMILIES.md)
- [v3 proof mapping](v3/PROOF_PACK.md)
- [v3 release history](v3/RELEASE_STATUS_v3.2.0.md)
- [Historical upgrade plan](upgrade/SENTINEL_AI_V3_UPGRADE_PLAN.md)
- [Integration guide](INTEGRATION.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [Migration from v2](MIGRATION_V2_TO_V3.md)

## Verification

- [Standard workflow](../.github/workflows/tests.yml): Python 3.10/3.11/3.12,
  complete suite and 100 percent coverage.
- [Native proof workflow](../.github/workflows/shield-v4-real-oqs.yml):
  exactly two required native-OQS nodes and no skips.
- [Repository tests](../tests/): contracts, negative paths, compatibility,
  encoding, attribution, and release-document locks.

## Historical, non-authoritative material

[Legacy technical notes](legacy/technical-spec.md),
[legacy whitepaper](legacy/whitepaper-sentinel-ai-v2.md), and
[synthetic attack scenario](legacy/ATTACK-SIMULATION-REPORT.md) do not prove
production protection or define current integration behavior.

Sentinel produces evidence. The Shield Orchestrator produces the Shield
receipt; AdamantineOS remains the final fail-closed policy and execution boundary.
