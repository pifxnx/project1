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


app.include_router(batches.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(webhooks.router, prefix="/api/v1")
app.include_router(work_centers.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
