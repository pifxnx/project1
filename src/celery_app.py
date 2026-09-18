from celery import Celery
from celery.schedules import crontab
from celery.signals import worker_process_init
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .core.config import settings

celery_app = Celery(
    "tasks", 
    broker=settings.rabbitmq_url,
    backend=settings.redis_url,
    include=[
        "src.tasks.aggregation",
        "src.tasks.webhooks",
        "src.tasks.reports",
        "src.tasks.imports",
        "src.tasks.scheduled"
        ]
)


_session_local = None

@worker_process_init.connect
def init_worker_db(**kwargs):
    global _session_local
    engine = create_engine(settings.db_url_sync)
    _session_local = sessionmaker(engine, expire_on_commit=False)


def get_session():
    return _session_local()


celery_app.conf.beat_schedule = {
    # Закрытие просроченных партий - каждый день в 01:00
    "auto-close-expired-batches": {
        "task": "tasks.auto_close_expired_batches",
        "schedule": crontab(hour=1, minute=0),
    },
    
    # Очистка старых файлов - каждый день в 02:00
    "cleanup-old-files": {
        "task": "tasks.cleanup_old_files",
        "schedule": crontab(hour=2, minute=0),
    },
    
    # Обновление статистики - каждые 5 минут
    "update-statistics": {
        "task": "tasks.update_cached_statistics",
        "schedule": crontab(minute="*/5"),
    },
    
    # Повторная отправка webhooks - каждые 15 минут
    "retry-failed-webhooks": {
        "task": "tasks.retry_failed_webhooks",
        "schedule": crontab(minute="*/15"),
    },
}