from fastapi import FastAPI
from src.log.logger import logger


app = FastAPI(
    title="Study API",
    version="1.0",
    description="Study API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
