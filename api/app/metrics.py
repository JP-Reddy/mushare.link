import posthog
from app.settings import settings

if settings.POSTHOG_API_KEY:
    posthog_client = posthog.Posthog(settings.POSTHOG_API_KEY, host=settings.POSTHOG_HOST, enable_exception_autocapture=True, sync_mode=True)
else:
    posthog.disabled = True

def track_conversion(status: str, properties: dict):
    posthog_client.capture(
        distinct_id="anonymous_user",
        event=status,
        properties={
            **properties
        }
    )