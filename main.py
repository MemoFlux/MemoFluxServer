from fastapi import FastAPI
from log.logger import logger
from router.log_test import router as log_test_router


app = FastAPI(
    title="Study API",
    version="1.0",
    description="Study API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# 包含路由
app.include_router(log_test_router, prefix="/api/v1")
