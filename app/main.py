from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings
from app.core.logging_config import logger
from app.middleware.logging_middleware import RequestLoggingMiddleware
from app.api.routes import query, schema, health, metrics

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Enterprise NLP-to-SQL Platform — ask business questions in plain English, get SQL + results.",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(query.router, prefix="/api/v1", tags=["Query"])
app.include_router(schema.router, prefix="/api/v1", tags=["Schema"])
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(metrics.router, prefix="/api/v1", tags=["Monitoring"])


@app.on_event("startup")
async def startup():
    logger.info(f"Starting {settings.app_name} v{settings.app_version} [{settings.app_env}]")


app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")


@app.get("/")
def root():
    return FileResponse("frontend/index.html")
