from fastapi import FastAPI
from src.api.v1.routers import batches


app = FastAPI()

@app.get("/health")
async def healthcheck():
    return {"status": "OK"}


app.include_router(batches.router)