# Security Policy — DGB Sentinel AI

**Repository:** DGB-Sentinel-AI  
**Component:** Sentinel AI - Shield v4 threat-signal evidence and v3 compatibility
**Maintainer:** DarekDGB  
**License:** MIT

This document defines the security policy and disclosure process for the
Shield v4.0.0 candidate and its retained v3 compatibility interfaces.
The candidate is a controlled pre-release; not released and not tagged.

---

## Supported Versions

Select the contract matching the interface under review. The distribution
version does not replace protocol versions or grant release authorization.

| Component | Status |
|---|---|
| Sentinel AI v4.0.0 candidate | Controlled pre-release component-evidence surface |
| Retained v3 adapter and 3.2.0 manifest | Compatibility surface with frozen identities |
| Older archived behavior | ❌ Unsupported |

Legacy scenarios are historical and non-authoritative. Current v4 claims are
bounded by `docs/v4/PROOF_PACK.md` and `docs/v4/RELEASE_STATUS_v4.0.0.md`.

---

## Security Model

Sentinel AI is a **deterministic threat-signal evidence layer**.

Security is enforced through:

- strict input validation
- deterministic outputs
- stable reason codes
- stable evidence families
- canonical context hashing
- fail-closed behavior
- no hidden authority
- tests for manifest / verdict behavior

Sentinel AI is **consensus-neutral**.

It does not:

- alter DigiByte consensus rules
- sign transactions
- broadcast transactions
- hold, derive, or access wallet private keys
- approve AdamantineOS execution directly
- override the Shield Orchestrator

Sentinel produces evidence only.

---

## Non-Negotiable Design Invariants

### 1. Fail-Closed by Default

Any invalid, ambiguous, incomplete, unsafe, or malformed input must produce an explicit rejection path.

Expected fail-closed behavior includes:

- deterministic reject decision
- explicit reason code
- no silent fallback
- no implicit allow
- no authority escalation

### 2. Determinism

The same valid input must always produce the same output.

Deterministic decisions and canonical payload hashes must not depend on
undeclared ambient state such as:

- timestamps
- randomness
- environment state
- network state
- file-system state
- dictionary iteration order
- runtime-dependent side effects

Canonical hashes must be reproducible for the same explicit inputs. Native
signature bytes need not be deterministic. Time windows and supplied context
are explicit verification inputs, not hidden sources of execution authority.

### 3. Evidence-Only Authority

Sentinel may:

- observe defensive context
- classify local threat indicators
- produce deterministic threat-signal evidence
- provide evidence to DQSN or the Shield Orchestrator path

Sentinel must never:

- sign transactions or use wallet keys
- modify consensus behavior
- perform final approval
- approve AdamantineOS execution directly
- override the Shield Orchestrator
- create hidden authority through fallback behavior

### 4. No Silent Fallbacks

All error paths must be explicit, deterministic, and test-covered.

A fallback that changes authority, weakens validation, or allows execution is a security defect.

---

## Retained v3 and Current v4 Security Boundaries

The retained v3.2.0 manifest boundary and the parallel v4 component-verdict
boundary both preserve the Orchestrator-first receipt path.

Sentinel component verdicts are **evidence only**.

Sentinel must not be treated as final execution authority. The parallel v4
interface may sign domain-separated component evidence through an explicit
backend, which does not add transaction-signing or wallet-custody authority.

AdamantineOS must consume Shield decisions only through the deterministic **Shield Orchestrator receipt**.

Raw Sentinel outputs must not be consumed directly by AdamantineOS as final signing, execution, or approval authority.

A Shield `ALLOW` result only permits AdamantineOS to continue its own checks.

It is **not** final signing or execution approval.

---

## Fail-Closed Requirements

The following conditions must reject deterministically:

- missing required verdict data
- malformed verdict data
- unknown fields in strict contract paths
- duplicated authority claims
- unknown reason IDs
- unknown evidence families
- mismatched component identity
- mismatched contract version
- mismatched context hash
- unsafe or unserialisable input
- non-canonical verdict data
- ambiguity affecting authority, determinism, or auditability

---

## Security Testing

Security guarantees are enforced through tests covering:

- fail-closed behavior
- deterministic output behavior
- unsupported contract versions
- reason-code stability
- evidence-family validation
- manifest/verdict alignment
- Orchestrator-first boundary assumptions
- regression protection against behavior drift

Security-sensitive changes must include tests.

Tests define truth.

Documentation must never claim behavior that tests do not enforce.

---

## Release Requirements

No v4.0.0 candidate release is authorized by this document. Before an explicit
release decision, require all of the following:

- roadmap checklist is complete
- tests pass locally or in CI
- coverage gate remains satisfied
- manifest files are present and aligned
- reason IDs are documented and tested
- evidence families are documented and tested
- v3 compatibility and v4 verdict boundary tests pass
- required classical and ML-DSA paths retain strict AND policy
- optional draft FN-DSA cannot replace or rescue either required path
- dedicated native-OQS proof executes both required nodes with no skips
- Orchestrator receipt boundary is respected
- final fresh ZIP audit is complete
- Red Team report is complete
- no docs-vs-tests mismatch remains

Draft Falcon-1024 evidence is not final FIPS 206 proof. The repository does
not supply a production classical Ed25519 backend. Backend-contract tests,
native PQC round trips, and 100 percent statement coverage do not establish
production key custody, HSM assurance, universal attack detection, or a full
production deployment. Runtime/backend reproducibility remains a later
roadmap gate; E4 does not pin the existing floating workflows.

---

## Reporting a Vulnerability

If you believe you have found a security issue:

1. Do **not** disclose it publicly first.
2. Open a private security advisory through GitHub if available.
3. Alternatively, contact the maintainer through the GitHub profile: **@DarekDGB**.

Please include:

- clear description of the issue
- steps to reproduce, if applicable
- expected behavior
- actual behavior
- affected commit hash or tag
- potential security impact

Coordinated disclosure is strongly encouraged.

---

## In Scope

Security issues in scope include:

- Sentinel threat-signal contract behavior
- determinism violations
- fail-closed bypasses
- reason ID ambiguity
- evidence-family ambiguity
- manifest/verdict mismatch
- context hash mismatch
- Orchestrator boundary bypass risk
- AdamantineOS raw-output bypass risk
- CI or test coverage gaps affecting security

---

## Out of Scope

The following are out of scope unless they create a direct security defect:

- DigiByte consensus vulnerabilities
- mining-layer issues
- wallet UI preferences
- performance tuning
- cosmetic documentation changes
- non-security refactors
- unsupported archived behavior

---

## Security Updates

Security fixes may:

- tighten validation
- improve fail-closed behavior
- add negative tests
- update documentation
- clarify reason IDs or evidence families

Breaking changes to security semantics require:

- documentation updates
- explicit version notes
- regression tests
- coverage proof

---

## Disclaimer

This software is provided **as-is**, without warranty of any kind.

Use at your own risk.

---

## Final Security Rule

Any change that weakens determinism, fail-closed behavior, explicit authority boundaries, evidence-only behavior, or the Orchestrator-first receipt model must be rejected.

© 2025 DarekDGB
