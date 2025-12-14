from celery import Celery
from celery.schedules import crontab

from src.core.config import get_settings

settings = get_settings()

app = Celery("snippetly")
app.conf.update(
    broker_url=settings.redis_url,
    result_backend=settings.redis_url,
    timezone="UTC",
    result_expires=3600,
)

app.conf.beat_schedule = {
    "cleanup_expired_activation_password_tokens": {
        "task": "tokens.delete_expired_activation_reset",
        "schedule": crontab(minute=0, hour="*/6"),
    },
    "cleanup_expired_refresh_tokens": {
        "task": "tokens.delete_expired_refresh",
        "schedule": crontab(minute=0, hour="*/6"),
    },
    "cleanup_unused_tags": {
        "task": "tags.delete_unused_tags",
        "schedule": crontab(minute=0, hour=0),
    },
}

from .tasks import tags, tokens  # noqa
