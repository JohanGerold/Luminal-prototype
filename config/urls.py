from django.urls import path
from aap import views
from aap import api

urlpatterns = [
    path("", views.home),
    path("health", views.health),
    path("agents", views.agents),
    path("agents/<slug:agent_id>", views.agent_detail),
    path("scenarios", views.scenarios),
    path("api/tools/<str:tool>", api.tool),
]
