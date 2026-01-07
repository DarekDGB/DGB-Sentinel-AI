from sentinel_ai_v2.wrapper.workflow import SentinelWorkflow
from sentinel_ai_v2.wrapper.sentinel_wrapper import SentinelWrapper


def test_workflow_constructs_and_runs_minimal():
    wf = SentinelWorkflow()
    assert wf is not None

    # Smoke the wrapper wiring
    w = SentinelWrapper()
    assert w is not None


def test_workflow_status_and_last_decision_smoke():
    wf = SentinelWorkflow()
    status = wf.status()
    assert isinstance(status, dict)
    assert "status" in status

    last = wf.last_decision()
    assert isinstance(last, dict)
