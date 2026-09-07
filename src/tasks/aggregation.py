from ..celery_app import celery_app

@celery_app.task
def hello():
    return {"message": "hello from celery"}