from celery import Celery

celery_app = Celery(
    "tasks", 
    broker="amqp://guest:guest@localhost:5672//",
    backend="redis://localhost:6379/0",
    include=[
        "src.tasks.aggregation",
        "src.tasks.webhooks"
        ]
)