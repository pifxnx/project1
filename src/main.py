from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
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
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
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
