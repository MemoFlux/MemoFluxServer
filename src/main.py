from fastapi import FastAPI
import asyncio
from src.db import Base, engine
from src.auth.token_manager import start_token_cleanup_task
from src.auth.router import router as auth_router
from fastapi.concurrency import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    asyncio.create_task(start_token_cleanup_task())
    yield


app = FastAPI(
    title="Memoflux",
    version="1.0",
    description="Memoflux API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# 包含鉴权路由
app.include_router(auth_router, prefix="/auth")
