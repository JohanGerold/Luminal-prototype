"""Read-only dashboard projection. Saved results are never re-evaluated here."""
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.db.models import Count, Q
from django.utils import timezone

from .models import EvaluationRun, Scenario

DISPLAY_TIMEZONE = ZoneInfo('Asia/Kolkata')


def overview(mode='LIVE_MODEL', days=7):
    mode = mode if mode in ('LIVE_MODEL', 'DEMO_FALLBACK') else 'LIVE_MODEL'
    days = 28 if str(days) == '28' else 7
    today = timezone.now().astimezone(DISPLAY_TIMEZONE).date()
    first_day = today - timedelta(days=days - 1)
    start = datetime.combine(first_day, time.min, tzinfo=DISPLAY_TIMEZONE)
    end = datetime.combine(today + timedelta(days=1), time.min, tzinfo=DISPLAY_TIMEZONE)
    runs = list(EvaluationRun.objects.filter(execution_mode=mode)
                .select_related('agent_version')
                .prefetch_related('results__scenario')
                .annotate(tool_count=Count('results__events', filter=Q(results__events__kind='tool_requested')))
                .order_by('-created_at', '-id'))
    window = [run for run in runs if start <= run.created_at < end]
    latest = {}
    summaries = {}
    for run in runs:
        result = next(iter(run.results.all()), None)
        duration = (run.completed_at - run.started_at).total_seconds() if run.started_at and run.completed_at else None
        row = {'run': run, 'verdict': result.verdict if result else None,
               'scenario': result.scenario if result else None, 'tool_count': run.tool_count,
               'duration': duration, 'version': run.input_snapshot.get('agent_version', run.agent_version.version)}
        summaries[run.pk] = row
        if result:
            latest.setdefault(result.scenario_id, row)
    counts = {verdict: sum(summaries[run.pk]['verdict'] == verdict for run in window)
              for verdict in ('PASS', 'FAIL', 'UNCERTAIN')}
    evaluated = sum(counts.values())
    durations = [summaries[run.pk]['duration'] for run in window if summaries[run.pk]['duration'] is not None]
    chart_days = []
    for offset in range(days):
        day = first_day + timedelta(days=offset)
        cohort = [run for run in window if run.created_at.astimezone(DISPLAY_TIMEZONE).date() == day]
        chart_days.append({'date': day.isoformat(), 'label': day.strftime('%d %b'),
                           'total': len(cohort), 'passed': sum(summaries[run.pk]['verdict'] == 'PASS' for run in cohort)})
    scenario_rows = []
    for scenario in Scenario.objects.all():
        scenario_rows.append(latest.get(scenario.pk, {'scenario': scenario, 'run': None,
                            'verdict': None, 'duration': None, 'tool_count': None, 'version': None}))
    return {'execution_mode': mode, 'days': days, 'total': len(window), 'evaluated': evaluated,
            'passed': counts['PASS'], 'failed': counts['FAIL'], 'uncertain': counts['UNCERTAIN'],
            'attention': counts['FAIL'] + counts['UNCERTAIN'], 'pending': len(window) - evaluated,
            'pass_rate': round(100 * counts['PASS'] / evaluated, 1) if evaluated else None,
            'average_duration': sum(durations) / len(durations) if durations else None,
            'duration_count': len(durations), 'chart_days': chart_days, 'scenario_rows': scenario_rows,
            'recent': [summaries[run.pk] for run in runs[:3]], 'scenario_count': len(scenario_rows)}
