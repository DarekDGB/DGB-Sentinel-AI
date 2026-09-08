# DGB Sentinel AI Shield v4 Test Matrix

Author attribution: DarekDGB

## Scope

This matrix covers the DGB Sentinel AI Shield v4 component-verdict contract,
the real ML-DSA-65 and optional draft Falcon-1024 backend paths, and the
v4.0.0 controlled pre-release package. The distribution is not released or tagged.

The goal is to prove DGB Sentinel AI can produce and verify v4 component evidence while keeping TEST-ONLY deterministic signatures separate from real backend mode.

## Positive Tests

| Test | Expected result |
|---|---|
| build unsigned DGB Sentinel AI v4 payload | deterministic payload with `contract_version: 4` |
| add required classical + ML-DSA test signatures | signed envelope validates under TEST-ONLY verifier |
| validate with matching context hash | verification summary returned |
| verify required role | `shield_component_sentinel_ai` only |
| build real crypto signature input | frozen DGB Sentinel AI component domain bytes with authenticated `standard_profile` |
| build real ML-DSA signature entry through backend adapter | `b64u:` signature entry produced |
| verify real ML-DSA signature entry through backend adapter | verification returns true |
| lazy OQS fake backend exposes version | backend metadata includes locked mechanism |
| optional gated real-liboqs ML-DSA proof workflow | runs only with `SHIELD_V4_REAL_OQS=1` and JUnit not-skipped guard |
| shared frozen component-verdict KAT vector | canonical JSON, domain-separated bytes, and signed payload hash match the shared V4.8G-R4 fixture |
| FN-DSA signed-message KAT | `fn-dsa`, `fips206-draft-falcon1024-v1`, and component domain bytes match fixture |
| valid optional FN-DSA evidence with required signatures | accepted and recorded as optional evidence |
| bundle builder receives supported entries in noncanonical order | emits a new outer list in canonical required-first, optional-last order without mutating the caller's list |

## Negative Tests

| Test | Expected result |
|---|---|
| tampered signature | fail closed |
| changed context hash after signing | fail closed |
| missing required signature | fail closed before trust lookup or cryptographic verification |
| duplicate algorithm entry | fail closed before trust lookup or cryptographic verification |
| unsupported algorithm | fail closed before trust lookup or cryptographic verification |
| wrong domain tag | fail closed |
| wrong signed payload hash | fail closed |
| revoked key | fail closed |
| artifact outside key validity window | fail closed |
| forbidden authority metadata | fail closed |
| null in signed payload | fail closed |
| float in signed payload | fail closed |
| KAT payload mutated with null or float | fail closed before signing |
| duplicate JSON key while parsing | fail closed |
| real backend missing required algorithm support | fail closed |
| real backend algorithm discovery exception | fail closed through DGB Sentinel AI backend error hierarchy |
| real backend sign exception | fail closed through DGB Sentinel AI backend error hierarchy |
| real backend verify exception | fail closed through DGB Sentinel AI backend error hierarchy |
| real backend verify returns non-boolean result | fail closed |
| real backend receives TEST-ONLY key id or public key | fail closed |
| real backend receives TEST-ONLY private key reference | fail closed |
| real backend emits malformed non-`b64u:` signature | fail closed |
| malformed real `b64u:` public key | fail closed |
| malformed real `b64u:` signature | fail closed |
| surrounding whitespace in real backend fields | fail closed |
| empty decoded real binary material | fail closed |
| OQS import missing when backend selected | fail closed |
| OQS import raises native exception | fail closed through DGB Sentinel AI backend error hierarchy |
| OQS `ML-DSA-65` mechanism disabled | fail closed |
| wrong OQS mechanism requested | fail closed |
| OQS mechanism discovery exception or non-iterable mechanism result | fail closed through DGB Sentinel AI backend error hierarchy |
| OQS backend asked to sign or verify non-`ml-dsa` algorithm | fail closed |
| native OQS version discovery exception | fail closed through DGB Sentinel AI backend error hierarchy |
| native OQS sign exception on backend-invalid key material | fail closed through DGB Sentinel AI backend error hierarchy |
| native OQS verify exception on structurally valid but backend-invalid key/signature bytes | fail closed through DGB Sentinel AI backend error hierarchy |
| OQS verify returns truthy non-boolean result | fail closed with `verify must return bool` |
| private key resolver exception | fail closed through DGB Sentinel AI backend error hierarchy |
| extra fields in real-backend signature entry or registry key record | fail closed |
| empty OQS message, secret key, or signature bytes | fail closed |
| wrong-length real liboqs public key in gated proof | fail closed through component backend error hierarchy |
| gated real-liboqs proof skips in dedicated job | rejected by JUnit not-skipped guard |
| FN-DSA present but invalid | fail closed |
| FN-DSA valid cannot rescue invalid ML-DSA | fail closed |
| FN-DSA valid cannot rescue invalid classical signature | fail closed |
| FN-DSA valid cannot replace missing ML-DSA | fail closed |
| FN-DSA wrong role or missing trust-profile key | fail closed |
| FN-DSA wrong payload hash or wrong domain | fail closed |
| duplicate FN-DSA entry | fail closed |
| unsupported FN-DSA `standard_profile` | fail closed |
| FN-DSA `standard_profile` flipped after signing | fail closed |
| reversed required signature order | fail closed before trust lookup or cryptographic verification |
| optional-first or interleaved signature order | fail closed before trust lookup or cryptographic verification |
| late structurally malformed, wrong-profile, wrong-domain, or wrong-hash entry | fail closed before any trust lookup or cryptographic verification |

## Required CI Gate

The unchanged `Sentinel AI Tests (v3)` workflow runs the complete suite on
Python 3.10, 3.11, and 3.12. Its historical name does not limit it to v3 tests.
Editable installation and compilation precede the test command; ordinary
checkout metadata, bytecode, pytest caches, and coverage output are supported.

```text
pytest --cov=sentinel_ai_v2 --cov-report=term-missing --cov-fail-under=100 -q
```


## Optional Real-OQS Proof Gate

The backend dependency is optional in ordinary CI. This dedicated two-node
proof is mandatory for E4 closure and for a release claim of native execution.

Default CI does not require liboqs. The live liboqs proof is a separate gated
job that executes both required guarded nodes:

```text
SHIELD_V4_REAL_OQS=1 SHIELD_V4_REAL_OQS_FALCON=1 \
python -m pytest --override-ini addopts='' \
  tests/test_v48g_real_oqs_mldsa_backend.py \
  tests/test_v48h_e_real_oqs_falcon_backend.py \
  -q --junitxml=shield-v4-real-oqs-results.xml

python scripts/assert_real_oqs_junit_not_skipped.py \
  shield-v4-real-oqs-results.xml \
  --min-tests 2 \
  --require-testcase "tests/test_v48g_real_oqs_mldsa_backend.py::test_v48g_real_oqs_mldsa65_sentinel_backend_round_trip_and_negatives" \
  --require-testcase "tests/test_v48h_e_real_oqs_falcon_backend.py::test_v48h_e_real_oqs_falcon1024_backend_round_trip_and_negatives"
```

The guard must prove that both exact testcase nodes ran and that `skipped == 0`,
`failures == 0`, and `errors == 0` before the run can support a live-liboqs
claim.

## V4.8G-R4 Audit Cleanup Checks

The component test suite now includes a shared frozen component-verdict KAT fixture:

```text
tests/fixtures/v4/component_verdict_policy_v1_kat.json
```

Every component repo must reproduce this signed payload hash exactly:

```text
a3881f27444ce73de875a15c8b413785a4fec4f4c03baaa6f8ee2fbf839736ae
```

The KAT is TEST-ONLY deterministic canonicalization evidence only. It does not sign transactions, broadcast, change DigiByte consensus, or claim live liboqs execution.

## V4.8H-C FN-DSA Optional Evidence Checks

The component test suite now includes:

```text
tests/test_v48h_fn_dsa_optional_evidence.py
tests/test_v48h_fn_dsa_signed_message_kat.py
tests/fixtures/v4/fn_dsa_signed_message_draft_profile_kat.json
```

These tests prove:

- FN-DSA absent + required signatures valid -> ACCEPT;
- FN-DSA valid + required signatures valid -> ACCEPT with optional evidence recorded;
- FN-DSA valid + ML-DSA invalid -> DENY;
- FN-DSA valid + classical invalid -> DENY;
- FN-DSA valid but ML-DSA missing -> DENY;
- FN-DSA invalid while present -> DENY;
- FN-DSA wrong payload hash or wrong domain -> DENY;
- FN-DSA wrong role or missing trust-profile key -> DENY;
- duplicate FN-DSA entries -> DENY;
- unsupported FN-DSA `standard_profile` -> DENY;
- `standard_profile` flipped after signing -> DENY.

## V4.8H-E Full Hybrid and Live-Falcon Checks

V4.8H-E adds these checks:

```text
tests/test_v48h_e_oqs_falcon_backend.py
tests/test_v48h_e_real_oqs_falcon_backend.py
```

The deterministic backend-contract test proves Falcon-1024 adapter wiring, `b64u:` binary material parsing, wrong-algorithm denial, disabled-mechanism denial, native exception fail-closed handling, and `standard_profile` binding.

The real-liboqs test is gated and must be run only by the dedicated PQC workflow with:

```text
SHIELD_V4_REAL_OQS=1
SHIELD_V4_REAL_OQS_FALCON=1
```

A live Falcon-1024 claim requires the dedicated PQC workflow JUnit guard to report `skipped == 0`, `failures == 0`, and `errors == 0`. FN-DSA remains optional evidence and is not final FIPS 206 proof.

## Authority Boundary

Passing these tests provides evidence for the bounded v4 component-verdict
contract and the ML-DSA/Falcon-1024 adapter paths exercised by those tests.

It does not grant transaction-signing authority, broadcast authority, DigiByte consensus authority, Shield Orchestrator final receipt authority, or AdamantineOS final authority.

## E4 release-pack regression lock

`tests/test_v410e4_release_pack_lock.py` locks active version surfaces, retained
v3 identities, frozen v4 profiles and KAT hashes, document links, candidate-only
status, compatibility-interface wording, and the existing exact native nodes.
It uses the established repository hygiene detectors, including C1 rejection,
and explicitly exercises generated-output handling and source attribution.

Preparation result: 247 passed, 2 expected environment-gated native-OQS skips,
1513/1513 statements, 100 percent coverage. The E4 lock has 10 tests.
See [the proof pack](PROOF_PACK.md) for the preparation environment and limits.
