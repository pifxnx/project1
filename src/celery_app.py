from celery import Celery

celery_app = Celery(
    "tasks", 
    broker="amqp://guest:guest@localhost:5672//",
    include=["src.tasks.aggregation"]
)