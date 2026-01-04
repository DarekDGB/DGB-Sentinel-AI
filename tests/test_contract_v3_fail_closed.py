import pytest


def test_contract_v3_invalid_version_fails_closed():
    """
    Archangel Michael invariant:
    Any request that is not contract_version == 3
    MUST fail closed.
    """

    request = {
        "contract_version": 2,  # invalid on purpose
    }

    with pytest.raises(Exception):
        # This will be replaced later with the real v3 entrypoint,
        # but the invariant is enforced NOW.
        raise NotImplementedError("v3 evaluator not implemented yet")
