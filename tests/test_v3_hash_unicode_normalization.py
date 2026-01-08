import unicodedata

from sentinel_ai_v2.contracts.v3_hash import canonical_hash_v3


def test_v3_hash_distinguishes_unicode_normalization_forms():
    # "café" can be represented as:
    # - NFC: precomposed "é"
    # - NFD: "e" + combining acute accent
    nfc = unicodedata.normalize("NFC", "café")
    nfd = unicodedata.normalize("NFD", "café")

    assert nfc != nfd  # different codepoint sequences

    payload_nfc = {"s": nfc}
    payload_nfd = {"s": nfd}

    h1 = canonical_hash_v3(payload_nfc)
    h2 = canonical_hash_v3(payload_nfd)

    # v3 hash is deterministic over codepoints; these SHOULD differ.
    assert h1 != h2
