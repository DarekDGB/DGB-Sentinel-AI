# DGB Sentinel AI Shield v4.0.0 Release Status

Author attribution: DarekDGB
Status: CONTROLLED PRE-RELEASE
Release decision: NOT YET AUTHORIZED
Distribution version: 4.0.0
Candidate tag: v4.0.0
Tag created: no

## Prepared scope

V4.10-E4 aligns package, import, CLI, and server display versions, current v4
documentation, historical v3 references, and release regression locks.
Existing CLI/HTTP interfaces retain v3 compatibility behavior. The v3
manifest stays at package_version 3.2.0 and contract_version 3.

Frozen v4 protocols, schema identities, signature policy, trust profiles,
cryptographic implementation, workflow bytes, and KAT fixtures are unchanged.

## Required gates

- External re-audit of the exact package.
- DarekDGB commits the complete package.
- Standard Python 3.10/3.11/3.12 CI passes with 100 percent coverage.
- Dedicated native ML-DSA/Falcon-1024 proof executes exactly the two required
  nodes with zero skips, failures, or errors on the same commit.
- A fresh post-commit repository ZIP exactly matches the approved candidate.
- Remaining roadmap release gates and explicit tag authorization are complete.

Local preparation results are in [the proof pack](PROOF_PACK.md). They do not
stand in for workflow execution on the eventual E4 commit.

## Authority and assurance limits

Sentinel is a component-evidence producer. It cannot sign or broadcast
transactions, access wallet keys, change DigiByte consensus, override the
Shield Orchestrator, or approve AdamantineOS execution.

AdamantineOS remains the final fail-closed policy and execution boundary.
Optional draft FN-DSA cannot replace or rescue required classical or ML-DSA
evidence. Native Falcon-1024 tests are not final FIPS 206 proof, production key
custody assurance, or proof of a complete production classical backend.

Do not create or move `v4.0.0` without DarekDGB's explicit authorization.
