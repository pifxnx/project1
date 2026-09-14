from celery import Celery
from celery.signals import worker_process_init
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .core.config import settings

celery_app = Celery(
    "tasks", 
    broker="amqp://guest:guest@localhost:5672//",
    backend="redis://localhost:6379/0",
    include=[
        "src.tasks.aggregation",
        "src.tasks.webhooks"
        ]
)


_session_local = None

@worker_process_init.connect
def init_worker_db():
    global session_local
    engine = create_engine(settings.db_url_sync)
    session_local = sessionmaker(engine, expire_on_commit=False)


def get_session():
    return _session_local()