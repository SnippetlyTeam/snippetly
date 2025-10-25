from celery import Celery
from celery.schedules import crontab

from src.core.config import get_settings

settings = get_settings()

app = Celery("snippetly")
app.conf.broker_url = settings.redis_url
app.conf.result_backend = settings.redis_url
app.conf.timezone = "UTC"

app.conf.beat_schedule = {
    "cleanup_expired_activation_password_tokens": {
        "task": "delete_expired_activation_reset_tokens",
        "schedule": crontab(minute=0, hour="*/6"),
    },
    "cleanup_expired_refresh_tokens": {
        "task": "delete_expired_refresh_tokens",
        "schedule": crontab(minute=0, hour=0),
    }
}
