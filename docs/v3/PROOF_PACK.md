# DGB Sentinel AI — v3.2.0 Proof Pack

Author attribution: DarekDGB

Status: Historical v3 compatibility proof mapping. The current candidate
proof pack is [the v4 proof pack](../v4/PROOF_PACK.md).

## Proof Mapping

- Invariant: deny-by-default / fail-closed → `tests/test_v3_2_manifest_verdict_lock.py` negative-path parametrized test.
- Invariant: deterministic hashing → `test_v3_2_verdict_is_canonical_and_deterministic`.
- Manifest rule → `test_v3_2_manifest_declares_boundary_and_registries`.
- Verdict fields → `test_v3_2_verdict_is_canonical_and_deterministic`.
- Reason ID registry → unknown and duplicate reason ID negative cases.
- Evidence family registry → unknown, duplicate, and empty evidence family negative cases.
- AdamantineOS boundary → manifest states Orchestrator receipt is the only visibility path.

The original v3 release required fresh-ZIP and authorized review gates. This
historical mapping does not instruct creation of a v3.2.0 tag or authorize v4.
