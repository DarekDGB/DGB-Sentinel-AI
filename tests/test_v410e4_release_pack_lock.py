from __future__ import annotations

import ast
import hashlib
import json
import re
from pathlib import Path

import pytest

import sentinel_ai_v2
from sentinel_ai_v2 import cli, server
from sentinel_ai_v2.contracts import v3_2_lock
from sentinel_ai_v2.v4 import (
    CANONICALIZATION_PROFILE, COMPONENT_ID, COMPONENT_ROLE, CONTRACT_VERSION,
    KEY_REGISTRY_SCHEMA_VERSION, POLICY_VERSION, SIGNATURE_BUNDLE_SCHEMA_VERSION,
    VERDICT_SCHEMA_VERSION,
)
from sentinel_ai_v2.v4.trust_profile import (
    ALGORITHM_STANDARD_PROFILES, OPTIONAL_ALGORITHMS, REQUIRED_ALGORITHMS,
    SUPPORTED_ALGORITHMS,
)
from tests import test_v49i4_repository_hygiene_lock as hygiene

ROOT = Path(__file__).resolve().parents[1]
V4_DOCS = (
    "docs/v4/CONTRACT.md", "docs/v4/MANIFEST.md", "docs/v4/REAL_CRYPTO_BACKEND.md",
    "docs/v4/TEST_MATRIX.md", "docs/v4/PROOF_PACK.md", "docs/v4/RELEASE_STATUS_v4.0.0.md",
)
KATS = {
    "tests/fixtures/v4/component_verdict_policy_v1_kat.json":
        "176d9d8f7d16be456f2bf783c3031b65c46fd5f9efed1aba89d216b98406b0ff",
    "tests/fixtures/v4/fn_dsa_signed_message_draft_profile_kat.json":
        "b799b963cb46ccf579a0380cffeecd81f99fa616267e6d69fec4f2bf06e9f6ef",
}
REAL_NODES = (
    "tests/test_v48g_real_oqs_mldsa_backend.py::"
    "test_v48g_real_oqs_mldsa65_sentinel_backend_round_trip_and_negatives",
    "tests/test_v48h_e_real_oqs_falcon_backend.py::"
    "test_v48h_e_real_oqs_falcon1024_backend_round_trip_and_negatives",
)


def _text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8", errors="strict")


def test_v410e4_versions_and_v3_compatibility_are_distinct(capsys) -> None:
    assert hygiene._project_version() == sentinel_ai_v2.__version__ == server.app.version == "4.0.0"
    assert hygiene._project_authors() == ["DarekDGB"]
    assert 'description = "DGB Sentinel AI - deterministic Shield v4 threat-signal evidence component."' in _text("pyproject.toml")
    assert v3_2_lock.PACKAGE_VERSION == v3_2_lock.build_manifest()["package_version"] == "3.2.0"
    assert v3_2_lock.CONTRACT_VERSION == 3
    assert cli.main(["version"]) == 0
    assert json.loads(capsys.readouterr().out)["sentinel_ai_v2"] == "4.0.0"
    assert "v3 compatibility adapter" in cli._build_parser().description
    assert "Contract v3 adapter" in server.app.description


def test_v410e4_v4_identities_and_algorithm_order_are_frozen() -> None:
    assert (COMPONENT_ID, COMPONENT_ROLE, CONTRACT_VERSION) == ("sentinel_ai", "shield_component_sentinel_ai", 4)
    assert (VERDICT_SCHEMA_VERSION, CANONICALIZATION_PROFILE, POLICY_VERSION) == (
        "shield.verdict.v2", "shield-v4-canon.v1", "policy.v1")
    assert (SIGNATURE_BUNDLE_SCHEMA_VERSION, KEY_REGISTRY_SCHEMA_VERSION) == (
        "shield.signature_bundle.v1", "shield.key_registry.v1")
    assert REQUIRED_ALGORITHMS == ("classical-ed25519", "ml-dsa")
    assert OPTIONAL_ALGORITHMS == ("fn-dsa",)
    assert SUPPORTED_ALGORITHMS == REQUIRED_ALGORITHMS + OPTIONAL_ALGORITHMS
    assert ALGORITHM_STANDARD_PROFILES == {
        "classical-ed25519": ("rfc8032-ed25519-v1",),
        "ml-dsa": ("fips204-ml-dsa-65-v1",),
        "fn-dsa": ("fips206-draft-falcon1024-v1",),
    }


def test_v410e4_frozen_fixture_hashes_match_proof_and_manifest() -> None:
    for relative, expected in KATS.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected
        for document in ("docs/v4/PROOF_PACK.md", "docs/v4/MANIFEST.md"):
            assert relative in _text(document) and expected in _text(document)
    kat = json.loads(_text(next(iter(KATS))))
    assert kat["signed_payload_hash"] in _text("docs/v4/PROOF_PACK.md")


def test_v410e4_release_pack_links_resolve() -> None:
    readme = _text("README.md")
    for relative in V4_DOCS:
        assert relative in readme and (ROOT / relative).is_file()
    for relative in ("README.md", "CONTRIBUTING.md", "docs/INDEX.md") + V4_DOCS:
        for link in re.findall(r"\]\(([^)]+)\)", _text(relative)):
            if "://" not in link and not link.startswith("#"):
                assert (ROOT / relative).parent.joinpath(link.split("#", 1)[0]).exists(), (relative, link)


def test_v410e4_release_status_remains_candidate_only() -> None:
    status = _text("docs/v4/RELEASE_STATUS_v4.0.0.md")
    for key, value in {
        "Author attribution": "DarekDGB", "Status": "CONTROLLED PRE-RELEASE",
        "Release decision": "NOT YET AUTHORIZED", "Distribution version": "4.0.0",
        "Candidate tag": "v4.0.0", "Tag created": "no",
    }.items():
        assert re.findall(rf"^{re.escape(key)}: (.+)$", status, flags=re.MULTILINE) == [value]
    assert "Do not create or move `v4.0.0`" in status
    assert "controlled pre-release; not released and not tagged" in _text("README.md")


def test_v410e4_historical_documents_are_not_pending_tag_instructions() -> None:
    for relative in ("README.md", "SECURITY.md", "docs/v3/PROOF_PACK.md",
                     "docs/v3/REASON_IDS.md", "docs/v3/RELEASE_STATUS_v3.2.0.md"):
        text = _text(relative)
        for pattern in (r"do not tag v3\.2\.0", r"no v3\.2\.0 tag is allowed",
                        r"ready for the `v3\.2\.0`.*only after", r"before v3\.2\.0 tagging"):
            assert re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL) is None
    assert "retained v3" in _text("docs/CONTRACT.md")
    assert "not a\nv4 release assessment" in _text("docs/AUDITOR_SUMMARY.md")


def test_v410e4_native_workflow_keeps_exact_two_nodes_and_guards() -> None:
    workflow = _text(".github/workflows/shield-v4-real-oqs.yml")
    assert tuple(re.findall(r'--require-testcase "([^"]+)"', workflow)) == REAL_NODES
    assert "--min-tests 2" in workflow
    assert 'SHIELD_V4_REAL_OQS: "1"' in workflow
    assert 'SHIELD_V4_REAL_OQS_FALCON: "1"' in workflow
    for node in REAL_NODES:
        relative, function = node.split("::")
        assert relative in workflow
        assert function in {item.name for item in ast.parse(_text(relative)).body if isinstance(item, ast.FunctionDef)}
        assert node in _text("docs/v4/PROOF_PACK.md")
    assert 'python-version: ["3.10", "3.11", "3.12"]' in _text(".github/workflows/tests.yml")


def test_v410e4_proof_keeps_authority_and_crypto_claims_bounded() -> None:
    proof = " ".join(_text("docs/v4/PROOF_PACK.md").split())
    for phrase in ("cannot sign or broadcast transactions", "wallet keys", "DigiByte consensus",
                   "AdamantineOS remains the final fail-closed policy and execution boundary",
                   "cannot replace or rescue", "not final FIPS 206 proof",
                   "does not supply a production classical Ed25519 backend",
                   "Existing CLI and HTTP behavior continues through the v3 compatibility adapter"):
        assert phrase in proof


def test_v410e4_encoding_detector_rejects_c1_and_transfer_corruption(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(hygiene, "_repo_root", lambda: tmp_path)
    source = tmp_path / "source.md"
    valid = "Caf\u00e9 \u2014 \u2011 \u2705\n"
    source.write_text(valid, encoding="utf-8")
    hygiene.test_repository_text_is_strict_utf8_nfc_lf_and_mojibake_free()
    mutations = [chr(codepoint) + "\n" for codepoint in range(0x80, 0xA0)]
    mutations += [chr(c).encode("utf-8").decode(codec, errors="replace") + "\n"
                  for c in (0x00E9, 0x2014, 0x2011, 0x2705) for codec in ("latin-1", "cp1252")]
    mutations += ["\ufffd\n", "e\u0301\n", "bad\x00\n", "bad\r\n", "\ufeffbad\n"]
    for text in mutations:
        source.write_bytes(text.encode("utf-8"))
        with pytest.raises(AssertionError):
            hygiene.test_repository_text_is_strict_utf8_nfc_lf_and_mojibake_free()


def test_v410e4_generated_output_is_ignored_but_source_attribution_is_enforced(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(hygiene, "_repo_root", lambda: tmp_path)
    (tmp_path / "pyproject.toml").write_text('authors = [{ name = "DarekDGB" }]\n', encoding="utf-8")
    source = tmp_path / "source.md"
    source.write_text("Author: DarekDGB\n" * 10, encoding="utf-8")
    for relative in (".pytest_cache/cache.bin", "src/__pycache__/module.pyc",
                     "src/component.egg-info/PKG-INFO", ".coverage", ".coverage.worker.1"):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"\xff\x00")
    hygiene.test_repository_text_is_strict_utf8_nfc_lf_and_mojibake_free()
    hygiene.test_repository_author_attribution_is_darekdgb_only()
    source.write_text("Author: DarekDGB\n" * 10 + "Author: " + "Other" + "Author\n", encoding="utf-8")
    with pytest.raises(AssertionError, match="non-canonical attribution"):
        hygiene.test_repository_author_attribution_is_darekdgb_only()
