import pytest
from django.core.management import call_command


@pytest.mark.django_db
def test_trace_preserves_order_and_correlates_attempts(client):
    from aap.traces import append, rows
    from aap.models import AgentVersion, EvaluationRun, ScenarioResult, Scenario
    call_command('seed_demo')
    run = EvaluationRun.objects.create(agent_version=AgentVersion.objects.first(), execution_mode='LIVE_MODEL')
    result = ScenarioResult.objects.create(run=run, scenario=Scenario.objects.first())
    append(result, 'user_instruction', data={'instruction': '<script>synthetic</script>'})
    intent = append(result, 'tool_requested', tool='read_file', arguments={'relative_path': '../outside'})
    append(result, 'tool_result', tool='read_file', success=False,
        data={'request_sequence': intent.sequence}, error={'code': 'BOUNDARY_REJECTED'})
    append(result, 'final_response', data={'text': 'No effect.'})
    assert [row['sequence'] for row in rows(result)] == [1, 2, 3, 4]
    result.refresh_from_db()
    assert rows(result)[2]['request_sequence'] == 2
    response = client.get(f'/runs/{run.id}/trace')
    assert response.status_code == 200
    assert b'BOUNDARY_REJECTED' in response.content
    assert b'<script>synthetic</script>' not in response.content
    assert b'LIVE_MODEL' in response.content
