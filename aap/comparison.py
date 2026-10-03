"""Read-only comparisons of the latest saved results under matching contracts."""
from .models import Scenario, ScenarioResult

VERDICTS = {'PASS', 'FAIL', 'UNCERTAIN'}


def compare_pair(left, right):
    reasons = []
    if left is None or right is None:
        reasons.append('Awaiting a saved V1 and V2 result in this mode.')
    else:
        a, b = left.run.input_snapshot, right.run.input_snapshot
        if a.get('agent_version') != 'v1' or b.get('agent_version') != 'v2':
            reasons.append('Historical version identity is missing.')
        if left.run.agent_version.agent_id != right.run.agent_version.agent_id:
            reasons.append('Agent identities differ.')
        if left.run.execution_mode != right.run.execution_mode:
            reasons.append('Execution modes differ.')
        if any(item.verdict not in VERDICTS or not item.run.completed_at
               or item.run.status in ('preparing', 'executing') for item in (left, right)):
            reasons.append('Awaiting terminal, evaluated results.')
        required = {'instruction', 'fixture_version', 'max_tool_calls', 'assertion',
                    'destructive_actions_allowed', 'allowed_delete_paths', 'fault'}
        if (left.scenario_id != right.scenario_id or left.scenario_snapshot != right.scenario_snapshot
                or not required.issubset(left.scenario_snapshot)):
            reasons.append('Scenario contracts differ or are incomplete.')
        if not left.before or left.before != right.before:
            reasons.append('Initial filesystem fixtures differ or are missing.')
        for field in ('evaluator_version', 'loop_threshold'):
            if not left.evaluation_metadata.get(field) or left.evaluation_metadata.get(field) != right.evaluation_metadata.get(field):
                reasons.append(f'Recorded {field.replace("_", " ")} differs or is missing.')
        for field in ('tools', 'execution_limits'):
            if not a.get(field) or a.get(field) != b.get(field):
                reasons.append(f'Recorded {field.replace("_", " ")} differs or is missing.')
        if not isinstance(a.get('execution_limits'), dict) or not a['execution_limits'].get('run_seconds'):
            reasons.append('Recorded run timeout is missing; legacy limits are not inferred.')
        fields = ('provider', 'model') if left.run.execution_mode == 'LIVE_MODEL' else ('fallback_script_version',)
        for field in fields:
            if not a.get(field) or a.get(field) != b.get(field):
                reasons.append(f'Recorded {field.replace("_", " ")} differs or is missing.')
    comparable = not reasons
    return {'left': left, 'right': right, 'comparable': comparable, 'reasons': reasons,
        'transition': f'{left.verdict} → {right.verdict}' if comparable else None,
        'fixed': comparable and left.verdict == 'FAIL' and right.verdict == 'PASS',
        'introduced': comparable and left.verdict == 'PASS' and right.verdict == 'FAIL',
        'unchanged_failure': comparable and left.verdict == right.verdict == 'FAIL',
        'uncertain': comparable and 'UNCERTAIN' in (left.verdict, right.verdict)}


def project(mode=None):
    mode = mode if mode in ('LIVE_MODEL', 'DEMO_FALLBACK') else 'LIVE_MODEL'
    latest = {}
    records = ScenarioResult.objects.filter(run__execution_mode=mode,
        run__agent_version__agent_id='file-organization').select_related('run__agent_version').order_by('-run__created_at', '-pk')
    for result in records:
        version = result.run.input_snapshot.get('agent_version', result.run.agent_version.version)
        latest.setdefault((result.scenario_id, version), result)
    rows = []
    for scenario in Scenario.objects.all():
        rows.append({'scenario': scenario, **compare_pair(latest.get((scenario.id, 'v1')), latest.get((scenario.id, 'v2')))})
    comparable = sum(row['comparable'] for row in rows)
    return {'rows': rows, 'execution_mode': mode, 'comparable_count': comparable,
        'pending_count': len(rows) - comparable,
        'fixed_count': sum(row['fixed'] for row in rows),
        'introduced_count': sum(row['introduced'] for row in rows),
        'unchanged_count': sum(row['unchanged_failure'] for row in rows),
        'uncertain_count': sum(row['uncertain'] for row in rows)}
