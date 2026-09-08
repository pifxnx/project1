from fastapi import FastAPI
from .api.v1.routers import (
    batches, products,
    webhooks, work_centers
)


app = FastAPI()

@app.get("/health")
async def healthcheck():
    return {"status": "OK"}





app.include_router(batches.router)
app.include_router(products.router)
app.include_router(webhooks.router)
app.include_router(work_centers.router)