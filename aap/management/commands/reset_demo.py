from django.core.management.base import BaseCommand
from aap.filesystem.service import workspace


class Command(BaseCommand):
    help = "Restore the owned synthetic demonstration fixture."

    def handle(self, *args, **options):
        snapshot = workspace.reset()
        self.stdout.write(f"Reset owned demo workspace: {len(snapshot)} entries.")
