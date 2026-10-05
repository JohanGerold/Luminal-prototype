import threading
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.wsgi import get_wsgi_application
from django.utils import timezone
from waitress import create_server
from aap.models import AgentVersion, EvaluationRun, Scenario, ScenarioResult
from aap.filesystem.service import workspace
from aap.n8n_client import invoke_agent


class Command(BaseCommand):
    help = "Run one real-model filesystem smoke with temporary local callback server. Stop existing app first."

    def handle(self, *args, **options):
        before = workspace.reset()
        version = AgentVersion.objects.get(agent_id="file-organization", version="v1")
        scenario = Scenario.objects.get(pk="normal-organization")
        run = EvaluationRun.objects.create(agent_version=version, execution_mode="LIVE_MODEL", status="executing",
            started_at=timezone.now(), input_snapshot={"agent_version": version.version, "system_prompt": version.system_prompt,
                "provider": settings.AAP_LIVE["provider"], "model": settings.AAP_LIVE["model"]})
        result = ScenarioResult.objects.create(run=run, scenario=scenario,
            scenario_snapshot={**scenario.definition, "instruction": scenario.instruction}, before=before)
        token = workspace.activate(result)
        server = create_server(get_wsgi_application(), host="127.0.0.1", port=8001, threads=4)
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        try:
            response = invoke_agent(result, token)
            if response["status"] != "completed":
                raise ValueError("Real agent did not complete.")
            result.final_response = response["final_response"] or ""
            run.status = "completed"
        except Exception:
            run.status = "failed"
            run.error = {"code": "LIVE_SMOKE_FAILED", "message": "Check recorded tool events and n8n configuration."}
            raise CommandError("Live smoke failed; no response or secrets printed. Inspect persisted evidence.") from None
        finally:
            workspace.close(token)
            result.after = workspace.snapshot()
            result.evidence_complete = run.status == "completed" and result.events.filter(kind="tool_requested").count() == result.events.filter(kind="tool_result").count()
            result.save()
            run.completed_at = timezone.now()
            run.save()
            server.close()
            server.task_dispatcher.shutdown()
        self.stdout.write(f"LIVE_MODEL run {run.id}: {result.events.filter(kind='tool_requested').count()} tool attempts; real file state captured. Verdict not implemented yet.")
