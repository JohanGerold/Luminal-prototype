"""Read-only projection of saved evidence; never execute or re-evaluate a run."""
import json


def project(run):
    result = run.results.select_related('scenario').first()
    before, after = (result.before, result.after) if result else ({}, {})
    paths = sorted(set(before) | set(after))
    state_rows = [{'id': f'state-{i}', 'path': path,
        'before': json.dumps(before.get(path), indent=2) if before else 'Snapshot unavailable',
        'after': json.dumps(after.get(path), indent=2) if after else 'Snapshot unavailable',
        # The owned fixture always contains directories. Empty snapshots mean
        # unavailable evidence, never an observed empty workspace.
        'change': 'Not established' if not before or not after else 'Added' if path not in before else 'Removed' if path not in after else
            'Unchanged' if before[path] == after[path] else 'Changed'} for i, path in enumerate(paths)]

    def references(items):
        rows = []
        for item in items:
            row = dict(item)
            row['evidence'] = []
            for ref in item.get('evidence', []):
                sequence, state, path = ref.get('event_sequence'), ref.get('state'), ref.get('path')
                if sequence is not None:
                    url, label = f'/runs/{run.id}/trace#event-{sequence}', f'Event #{sequence}'
                else:
                    url = f'#state-{paths.index(path)}' if path in paths else '#filesystem'
                    label = f'{state or "Saved state"}: {path or "snapshot"}'
                row['evidence'].append({'url': url, 'label': label})
            row['operands_text'] = json.dumps(item.get('operands', {}), indent=2)
            rows.append(row)
        return rows

    duration = (run.completed_at - run.started_at).total_seconds() if run.started_at and run.completed_at else None
    return {'run': run, 'result': result, 'scenario': result.scenario if result else None,
        'version': run.input_snapshot.get('agent_version', 'Not recorded'),
        'model': run.input_snapshot.get('model'), 'tools': run.input_snapshot.get('tools', []),
        'instruction': result.scenario_snapshot.get('instruction', 'Not recorded') if result else 'Not recorded',
        'verdict': result.verdict if result else None, 'duration': duration,
        'tool_count': result.events.filter(kind='tool_requested').count() if result else 0,
        'complete': bool(result and result.evidence_complete), 'state_rows': state_rows,
        'assertions': references(result.assertions) if result else [],
        'findings': references(result.findings) if result else [],
        'missing': result.evaluation_metadata.get('missing_evidence', []) if result else ['No scenario evidence recorded.'],
        'rules': result.evaluation_metadata.get('evaluator_version', 'Not recorded') if result else 'Not recorded'}
