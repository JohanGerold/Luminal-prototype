import pytest


def response():
    return {"contract_version": "1", "run_id": "run", "scenario_id": "case",
            "execution_mode": "LIVE_MODEL", "status": "completed", "final_response": "done",
            "tool_call_count": None, "started_at": "2026-10-03T00:00:00Z",
            "completed_at": "2026-10-03T00:00:01Z", "error": None}


def test_valid_response_is_not_a_verdict():
    from aap.n8n_client import validate_response
    result = validate_response(response(), "run", "case")
    assert result["final_response"] == "done"
    assert "verdict" not in result


@pytest.mark.parametrize("field,value", [("run_id", "other"), ("scenario_id", "other"),
    ("execution_mode", "DEMO_FALLBACK"), ("contract_version", "2"), ("error", {"code": "error"}),
    ("final_response", "x" * 17000), ("completed_at", "not-a-date")])
def test_response_mismatch_is_rejected(field, value):
    from aap.n8n_client import validate_response
    data = response()
    data[field] = value
    with pytest.raises(ValueError):
        validate_response(data, "run", "case")
