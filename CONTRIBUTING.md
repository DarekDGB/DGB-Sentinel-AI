# Contributing to DGB Sentinel AI

Author attribution: DarekDGB

## Scope

The current distribution is the Shield v4.0.0 candidate. It contains parallel
v4 component-evidence primitives and the retained v3 compatibility adapter.
Use [the documentation index](docs/INDEX.md) to select the contract for the
interface being changed.

Sentinel observes defensive context and produces evidence. It cannot sign or
broadcast DigiByte transactions, hold wallet keys, change DigiByte consensus,
act as final policy or execution authority, or bypass the Shield Orchestrator.
Signing domain-separated component evidence through an explicit backend is
within the v4 contract. It does not grant transaction-signing authority.

The Shield Orchestrator produces the Shield receipt; AdamantineOS remains
the final fail-closed policy and execution boundary.

## Required invariants

- Preserve deterministic decisions, canonical hashes, and explicit inputs.
- Reject invalid or ambiguous input through explicit fail-closed paths.
- Keep required classical and ML-DSA verification under strict AND policy.
- Optional draft FN-DSA evidence cannot replace or rescue a required path.
- Keep optional evidence last; reject noncanonical received bundle order.
- Keep TEST-ONLY material separate from real backends, with no silent fallback.
- Preserve component roles, domain binding, and wallet-key separation.
- Preserve the v3 compatibility contract and frozen manifest identity.
- Preserve legitimate third-party notices and DarekDGB first-party attribution.

Signature bytes from native cryptography need not be deterministic. Do not
confuse canonical payload determinism with randomized signature generation.

## Welcome changes

Detection and analysis improvements, clearer specifications, fail-closed
hardening, and useful negative tests are welcome within the declared scope.
Reject opaque behavior, permissive parsing, hidden execution authority,
consensus changes, or production claims unsupported by evidence.
Legacy v2 concepts remain historical references.

## Review and verification

Explain the concrete problem, the resulting behavior, and the validation.
Contract or security changes require tests; keep the 100 percent coverage
gate. Run the full suite after editable installation and compilation, with
normal checkout metadata, bytecode, and test caches enabled.

```text
python -m pip install -e ".[dev]"
python -m compileall -q src
pytest --cov=sentinel_ai_v2 --cov-report=term-missing --cov-fail-under=100 -q
```

The standard matrix is Python 3.10/3.11/3.12. The dedicated real-OQS workflow
must report both required native nodes with no skips for native proof.
Do not infer a live-crypto pass from ordinary environment-gated skips.

## Release and license

The v4.0.0 distribution remains a controlled pre-release; no tag is authorized
by documentation or local tests. Follow the living roadmap, exact-commit CI,
external audit, and fresh-ZIP verification gates.

The architect, DarekDGB, reviews direction and invariants. Contributions are
released under the MIT License.
