from copy import deepcopy
from itertools import product

import pytest
from django.core.management import call_command
from django.utils import timezone


@pytest.fixture
def pair(db):
    from aap.models import AgentVersion, EvaluationRun, Scenario, ScenarioResult
    call_command('seed_demo')
    scenario = Scenario.objects.get(pk='normal-organization')
    results = []
    for version in ('v1', 'v2'):
        run = EvaluationRun.objects.create(agent_version=AgentVersion.objects.get(version=version),
            execution_mode='LIVE_MODEL', status='completed', started_at=timezone.now(), completed_at=timezone.now(),
            input_snapshot={'agent_version': version, 'tools': ['list_directory'], 'provider': 'Google Gemini',
                'model': 'models/gemini-3-flash-preview', 'execution_limits': {'run_seconds': 100}})
        results.append(ScenarioResult.objects.create(run=run, scenario=scenario,
            scenario_snapshot={**scenario.definition, 'instruction': scenario.instruction},
            before={'Downloads': {'type': 'directory'}}, verdict='PASS', evidence_complete=True,
            evaluation_metadata={'evaluator_version': 'rules-v1', 'loop_threshold': 3}))
    return results


@pytest.mark.parametrize('before,after', list(product(('PASS', 'FAIL', 'UNCERTAIN'), repeat=2)))
def test_all_saved_transitions_are_honest(pair, before, after):
    from aap.comparison import compare_pair
    pair[0].verdict, pair[1].verdict = before, after
    result = compare_pair(*pair)
    assert result['comparable']
    assert result['transition'] == f'{before} → {after}'
    assert result['fixed'] == (before == 'FAIL' and after == 'PASS')
    assert result['introduced'] == (before == 'PASS' and after == 'FAIL')
    assert result['unchanged_failure'] == (before == after == 'FAIL')
    assert result['uncertain'] == ('UNCERTAIN' in (before, after))


@pytest.mark.parametrize('change', ['scenario','fixture','rules','limits','tools','model','mode','legacy'])
def test_mismatched_or_unknown_contract_never_claims_improvement(pair, change):
    from aap.comparison import compare_pair
    left, right = pair
    left.verdict, right.verdict = 'FAIL', 'PASS'
    if change == 'scenario': right.scenario_snapshot['instruction'] = 'Different task'
    if change == 'fixture': right.before = {'Another': {'type': 'directory'}}
    if change == 'rules': right.evaluation_metadata['evaluator_version'] = 'different'
    if change == 'limits': right.run.input_snapshot['execution_limits']['run_seconds'] = 50
    if change == 'tools': right.run.input_snapshot['tools'] = ['delete_path']
    if change == 'model': right.run.input_snapshot['model'] = 'different'
    if change == 'mode': right.run.execution_mode = 'DEMO_FALLBACK'
    if change == 'legacy': del right.run.input_snapshot['execution_limits']
    result = compare_pair(left, right)
    assert not result['comparable'] and result['reasons']
    assert not result['fixed'] and not result['introduced']
    assert result['transition'] is None


def test_comparison_read_only_missing_and_mode_separation(client, pair, monkeypatch):
    from aap import runs, evaluation
    from aap.models import EvaluationRun
    monkeypatch.setattr(runs, 'start', lambda *a: pytest.fail('comparison dispatched'))
    monkeypatch.setattr(evaluation, 'evaluate', lambda **kw: pytest.fail('comparison re-evaluated'))
    count = EvaluationRun.objects.count()
    response = client.get('/compare')
    assert response.status_code == 200
    assert response.context['comparable_count'] == 1
    assert response.context['pending_count'] == 5
    assert b'LIVE VERIFICATION/DATA PENDING' in response.content
    assert f'/runs/{pair[0].run_id}/report'.encode() in response.content
    fallback = client.get('/compare?mode=DEMO_FALLBACK')
    assert fallback.context['comparable_count'] == 0
    assert b'Scripted' in fallback.content
    assert EvaluationRun.objects.count() == count


def test_newest_pending_result_is_not_replaced_by_older_success(client, pair):
    from aap.models import EvaluationRun, ScenarioResult
    old = pair[1]
    run = EvaluationRun.objects.create(agent_version=old.run.agent_version, execution_mode='LIVE_MODEL',
        status='executing', input_snapshot=deepcopy(old.run.input_snapshot))
    ScenarioResult.objects.create(run=run, scenario=old.scenario, scenario_snapshot=old.scenario_snapshot)
    row = client.get('/compare').context['rows'][0]
    assert row['right'].run_id == run.pk
    assert not row['comparable'] and not row['fixed']


def test_live_metadata_does_not_hide_fixture_identity_or_escaping(client, pair):
    pair[0].scenario.name = '<script>unsafe()</script>'
    pair[0].scenario.save()
    response = client.get('/compare')
    assert b'&lt;script&gt;unsafe()&lt;/script&gt;' in response.content
    assert b'<script>unsafe()</script>' not in response.content
