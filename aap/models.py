import uuid
from django.db import models


class Agent(models.Model):
    id = models.SlugField(primary_key=True)
    name = models.CharField(max_length=160)
    description = models.TextField()
    domain = models.CharField(max_length=160)
    goals = models.JSONField(default=list)
    constraints = models.JSONField(default=list)


class AgentVersion(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.PROTECT, related_name="versions")
    version = models.CharField(max_length=20)
    system_prompt = models.TextField()
    tools = models.JSONField(default=list)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["agent", "version"], name="agent_version_unique")]


class Scenario(models.Model):
    id = models.SlugField(primary_key=True)
    name = models.CharField(max_length=160)
    instruction = models.TextField()
    definition = models.JSONField(default=dict)
    ordinal = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordinal", "id"]


class ExecutionMode(models.TextChoices):
    LIVE_MODEL = "LIVE_MODEL"
    DEMO_FALLBACK = "DEMO_FALLBACK"


class EvaluationRun(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_version = models.ForeignKey(AgentVersion, on_delete=models.PROTECT)
    execution_mode = models.CharField(max_length=20, choices=ExecutionMode.choices)
    status = models.CharField(max_length=20, default="preparing")
    input_snapshot = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    error = models.JSONField(null=True)

    class Meta:
        constraints = [models.CheckConstraint(
            condition=models.Q(execution_mode__in=["LIVE_MODEL", "DEMO_FALLBACK"]),
            name="run_requires_execution_mode",
        )]


class ScenarioResult(models.Model):
    run = models.ForeignKey(EvaluationRun, on_delete=models.CASCADE, related_name="results")
    scenario = models.ForeignKey(Scenario, on_delete=models.PROTECT)
    scenario_snapshot = models.JSONField(default=dict)
    before = models.JSONField(default=dict)
    after = models.JSONField(default=dict)
    verdict = models.CharField(max_length=20, null=True)
    assertions = models.JSONField(default=list)
    findings = models.JSONField(default=list)
    evidence_complete = models.BooleanField(default=False)
    final_response = models.TextField(blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["run", "scenario"], name="run_scenario_unique")]


class TraceEvent(models.Model):
    result = models.ForeignKey(ScenarioResult, on_delete=models.CASCADE, related_name="events")
    sequence = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    kind = models.CharField(max_length=30)
    tool = models.CharField(max_length=40, blank=True)
    arguments = models.JSONField(default=dict)
    success = models.BooleanField(null=True)
    data = models.JSONField(default=dict)
    error = models.JSONField(null=True)

    class Meta:
        ordering = ["sequence"]
        constraints = [models.UniqueConstraint(fields=["result", "sequence"], name="result_sequence_unique")]
