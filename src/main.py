from fastapi import FastAPI
from .api.v1.routers import (
    batches,
    products,
    webhooks,
    work_centers,
    analytics,
    tasks,
)
from .api.v1.routers.exception_handlers import register_exception_handler


app = FastAPI()
register_exception_handler(app)


@app.get("/health")
async def healthcheck():
    return {"status": "OK"}


app.include_router(batches.router)
app.include_router(products.router)
app.include_router(webhooks.router)
app.include_router(work_centers.router)
app.include_router(analytics.router)
app.include_router(tasks.router)
