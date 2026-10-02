from django.db import connection
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import Agent, Scenario


def home(request):
    return redirect("/agents/file-organization")


def health(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()
    return JsonResponse({"service": "aap-prototype", "database": "ready"})


def agents(request):
    return render(request, "agents.html", {"agents": Agent.objects.all()})


def agent_detail(request, agent_id):
    agent = get_object_or_404(Agent, pk=agent_id)
    return render(request, "agent.html", {"agent": agent, "versions": agent.versions.order_by("version")})


def scenarios(request):
    return render(request, "scenarios.html", {"scenarios": Scenario.objects.all()})
