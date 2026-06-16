from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from app.routes import router
from app.services.metrics import ShadowMetrics
from app.settings import Settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()
    app.state.settings = settings
    app.state.http_client = httpx.AsyncClient(timeout=settings.llm_timeout_seconds)
    app.state.shadow_tasks = set()
    app.state.shadow_metrics = ShadowMetrics()
    try:
        yield
    finally:
        for task in app.state.shadow_tasks:
            task.cancel()
        await app.state.http_client.aclose()


app = FastAPI(title="LLM Proxy", version="0.1.0", lifespan=lifespan)
app.include_router(router)
