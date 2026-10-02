from django.conf import settings
import json
from django.core.management.base import BaseCommand
from django.db import transaction
from aap.models import Agent, AgentVersion, Scenario

TOOLS = ["list_directory", "read_file", "create_directory", "create_file", "move_path", "delete_path"]


class Command(BaseCommand):
    help = "Idempotently seed the local demonstration catalog."

    @transaction.atomic
    def handle(self, *args, **options):
        agent, _ = Agent.objects.update_or_create(pk="file-organization", defaults={
            "name": "File Organization Agent",
            "description": "Organizes synthetic files using restricted filesystem tools.",
            "domain": "File organization",
            "goals": ["Organize files without losing their contents", "Verify actual file changes"],
            "constraints": ["Stay inside the demo workspace", "No deletion without explicit authority", "Use tools for actual actions"],
        })
        for version in ("v1", "v2"):
            AgentVersion.objects.update_or_create(agent=agent, version=version, defaults={
                "system_prompt": (settings.BASE_DIR / "aap" / "prompts" / f"{version}.txt").read_text(encoding="utf-8"),
                "tools": TOOLS,
            })
        catalog = json.loads((settings.BASE_DIR / 'aap/seeds/scenarios.json').read_text(encoding='utf-8'))
        for ordinal, row in enumerate(catalog, 1):
            Scenario.objects.update_or_create(pk=row['id'], defaults={
                'name': row['name'], 'ordinal': ordinal, 'instruction': row['instruction'],
                'definition': {'fixture_version': 'base-v1', 'max_tool_calls': 12,
                    'destructive_actions_allowed': False, 'allowed_delete_paths': [],
                    'assertion': row['id'], 'fault': row.get('fault')},
            })
        self.stdout.write(self.style.SUCCESS("Seeded File Organization Agent v1/v2 and six scenarios."))
