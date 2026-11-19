from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware import Middleware

from app import models  # noqa: F401  (register models on Base.metadata)
from app.api import approvals  # noqa: F401
from app.api import metrics  # noqa: F401
from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api import deps  # noqa: F401
from app.database import Base, engine
from app.middleware import RequestLoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Simple bootstrap: create tables on startup (Alembic not required for prototype)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="AI-Powered Internal Platform Prototype",
    version="0.1.0",
    lifespan=lifespan,
    middleware=[Middleware(RequestLoggingMiddleware)],
)


app.include_router(auth_router)
app.include_router(health_router)
app.include_router(approvals.router)
app.include_router(metrics.router)
