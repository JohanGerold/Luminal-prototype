from django.urls import path
from aap import views
from aap import api
from aap import run_api
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path("", views.home),
    path("health", views.health),
    path("agents", views.agents),
    path("agents/<slug:agent_id>", views.agent_detail),
    path("scenarios", views.scenarios),
    path("api/tools/<str:tool>", api.tool),
    path("api/runs", run_api.start),
    path("api/runs/<uuid:run_id>", run_api.status),
    path("api/reset", run_api.reset),
    path("runs/new", views.new_run),
    path("runs/<uuid:run_id>", views.run_detail),
    path("runs/<uuid:run_id>/trace", views.trace),
    path("design-preview", views.design_preview),
    path("design-assets/<path:path>", serve, {'document_root': settings.BASE_DIR / 'design-preview' / 'assets'}),
]
