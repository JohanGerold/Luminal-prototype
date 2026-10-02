from django.core.management.base import BaseCommand
from aap.models import ScenarioResult
from aap.evaluation import evaluate_result


class Command(BaseCommand):
    help = 'Evaluate terminal saved runs using only their recorded evidence.'

    def handle(self, *args, **options):
        for result in ScenarioResult.objects.select_related('run').exclude(run__completed_at=None):
            outcome = evaluate_result(result)
            self.stdout.write(f'{result.run_id} {result.run.execution_mode} {outcome["verdict"]}')
