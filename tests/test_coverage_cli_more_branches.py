import io
import json
import types
import pytest

import sentinel_ai_v2.cli as cli


class _DummyResult:
    status = "OK"
    risk_score = 0.33
    details = ["d"]


class _DummyWrapper:
    def evaluate(self, snapshot):
        return _DummyResult()


def test_load_snapshot_from_stdin_dict(monkeypatch):
    monkeypatch.setattr(cli.sys, "stdin", io.StringIO('{"block_height": 1}'))
    data = cli._load_snapshot("-")
    assert data == {"block_height": 1}


def test_load_snapshot_from_file_dict(tmp_path):
    p = tmp_path / "tel.json"
    p.write_text('{"mempool_size": 2}', encoding="utf-8")
    data = cli._load_snapshot(str(p))
    assert data == {"mempool_size": 2}


def test_load_snapshot_invalid_json_raises_systemexit(monkeypatch):
    monkeypatch.setattr(cli.sys, "stdin", io.StringIO("{bad json"))
    with pytest.raises(SystemExit) as e:
        cli._load_snapshot("-")
    assert "Invalid JSON input" in str(e.value)


def test_load_snapshot_non_dict_raises_systemexit(monkeypatch):
    monkeypatch.setattr(cli.sys, "stdin", io.StringIO('["not a dict"]'))
    with pytest.raises(SystemExit) as e:
        cli._load_snapshot("-")
    assert "must be a single object" in str(e.value)


def test_cmd_snapshot_pretty_and_compact(monkeypatch):
    # Patch SentinelWrapper to avoid real execution paths
    monkeypatch.setattr(cli, "SentinelWrapper", lambda: _DummyWrapper())

    # Patch stdout to capture output
    buf = io.StringIO()
    monkeypatch.setattr(cli.sys, "stdout", buf)

    # Also patch stdin snapshot input
    monkeypatch.setattr(cli.sys, "stdin", io.StringIO('{"x": 1}'))

    # Pretty
    args = types.SimpleNamespace(file="-", pretty=True)
    rc = cli._cmd_snapshot(args)
    assert rc == 0
    out = buf.getvalue()
    assert '"status": "OK"' in out
    assert "\n" in out  # newline written

    # Compact
    buf2 = io.StringIO()
    monkeypatch.setattr(cli.sys, "stdout", buf2)
    monkeypatch.setattr(cli.sys, "stdin", io.StringIO('{"x": 2}'))

    args2 = types.SimpleNamespace(file="-", pretty=False)
    rc2 = cli._cmd_snapshot(args2)
    assert rc2 == 0
    out2 = buf2.getvalue()
    # compact JSON still contains keys
    assert '"risk_score"' in out2


def test_main_version_command(monkeypatch):
    buf = io.StringIO()
    monkeypatch.setattr(cli.sys, "stdout", buf)
    rc = cli.main(["version"])
    assert rc == 0
    data = json.loads(buf.getvalue())
    assert "sentinel_ai_v2" in data


def test_main_snapshot_command(monkeypatch):
    monkeypatch.setattr(cli, "SentinelWrapper", lambda: _DummyWrapper())
    monkeypatch.setattr(cli.sys, "stdin", io.StringIO('{"x": 1}'))

    buf = io.StringIO()
    monkeypatch.setattr(cli.sys, "stdout", buf)

    rc = cli.main(["snapshot", "--file", "-", "--pretty"])
    assert rc == 0
    data = json.loads(buf.getvalue())
    assert data["status"] == "OK"
