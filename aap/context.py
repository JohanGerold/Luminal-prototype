from django.conf import settings


def live_provider(request):
    """Name the configured LIVE_MODEL provider; saved runs show their own recorded provider instead."""
    return {"live_provider": settings.AAP_LIVE["provider"], "live_model": settings.AAP_LIVE["model"]}
