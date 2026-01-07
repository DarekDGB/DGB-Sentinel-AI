from sentinel_ai_v2.wrapper import sentinel_wrapper


class _DummyClient:
    def __init__(self):
        self.seen = None

    def evaluate_snapshot(self, raw_telemetry):
        self.seen = raw_telemetry
        class _R:
            status = "OK"
            risk_score = 0.34
            details = ["y"]
        return _R()


def test_run_full_workflow_uses_provided_client_and_passes_telemetry():
    dummy = _DummyClient()
    tel = {"block_height": 999}

    res = sentinel_wrapper.run_full_workflow(tel, client=dummy)  # type: ignore[arg-type]

    assert dummy.seen == tel
    assert res.status == "OK"
    assert res.risk_score == 0.34
    assert res.details == ["y"]
