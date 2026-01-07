import json

import sentinel_ai_v2.cli as cli
import sentinel_ai_v2.server as server


def test_cli_version_command_writes_json(capsys):
    rc = cli.main(["version"])
    assert rc == 0
    out = capsys.readouterr().out.strip()
    data = json.loads(out)
    assert "sentinel_ai_v2" in data


def test_server_app_exists_and_status_endpoint(monkeypatch):
    # Avoid depending on internal Monitor state: patch wrapper.last_status
    monkeypatch.setattr(server.wrapper, "last_status", lambda: {"status": "OK", "risk_score": 0.1, "details": []})

    # Call the endpoint function directly (async)
    import asyncio
    resp = asyncio.get_event_loop().run_until_complete(server.status())
    assert resp.status == "OK"
    assert resp.risk_score == 0.1
