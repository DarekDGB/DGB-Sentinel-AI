from sentinel_ai_v2.contracts.v3_hash import canonical_sha256


def test_package_import_and_contract_hash_is_deterministic():
    payload = {"b": 2, "a": 1}
    h1 = canonical_sha256(payload)
    h2 = canonical_sha256({"a": 1, "b": 2})

    assert isinstance(h1, str)
    assert len(h1) == 64
    assert h1 == h2
