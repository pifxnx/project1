from fastapi import FastAPI
from .api.v1.routers import batches, products
from .tasks.aggregation import hello


app = FastAPI()

@app.get("/health")
async def healthcheck():
    return {"status": "OK"}

@app.get("/check_celery")
async def celerycheck():
    result = hello.delay()
    return {"task_id": result.id}



app.include_router(batches.router)
app.include_router(products.router)