from django.urls import path
from aap import views

urlpatterns = [
    path("", views.home),
    path("health", views.health),
    path("agents", views.agents),
    path("agents/<slug:agent_id>", views.agent_detail),
    path("scenarios", views.scenarios),
]
