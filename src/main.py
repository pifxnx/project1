from fastapi import FastAPI
from .api.v1.routers import batches, products


app = FastAPI()

@app.get("/health")
async def healthcheck():
    return {"status": "OK"}





app.include_router(batches.router)
app.include_router(products.router)