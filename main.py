from fastapi import FastAPI


app = FastAPI(
    title="Study API",
    version="1.0",
    description="Study API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",

)