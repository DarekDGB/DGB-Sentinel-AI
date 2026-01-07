import pytest
from pathlib import Path

from sentinel_ai_v2.model_loader import (
    compute_file_hash,
    load_and_verify_model,
    run_model_inference,
    ModelVerificationError,
)


def test_compute_file_hash_and_load(tmp_path: Path):
    p = tmp_path / "m.bin"
    p.write_bytes(b"hello")

    h = compute_file_hash(p)
    model = load_and_verify_model(str(p), expected_hash=h)
    assert model.path == p
    assert model.hash == h

    assert 0.0 <= run_model_inference(model, {"x": 1}) <= 1.0


def test_load_model_missing_file(tmp_path: Path):
    p = tmp_path / "missing.bin"
    with pytest.raises(ModelVerificationError):
        load_and_verify_model(str(p), expected_hash=None)


def test_load_model_hash_mismatch(tmp_path: Path):
    p = tmp_path / "m.bin"
    p.write_bytes(b"hello")
    with pytest.raises(ModelVerificationError):
        load_and_verify_model(str(p), expected_hash="deadbeef")
