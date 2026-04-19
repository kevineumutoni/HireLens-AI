# src/app.py
"""
HireLens-AI FastAPI Application
Main entry point for the backend API server.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

from src.config.settings import settings
from src.api.routes import api_router
from src.db import client as mongodb_client

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HireLens-AI Backend",
    description="AI-powered talent screening system for HR",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Check API and MongoDB status."""
    try:
        mongodb_client.admin.command("ping")
        mongodb_connected = True
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        mongodb_connected = False

    return {
        "status": "healthy" if mongodb_connected else "degraded",
        "timestamp": datetime.now().isoformat(),
        "mongodb_connected": mongodb_connected,
        "message": "API is running" if mongodb_connected else "MongoDB connection failed",
    }


app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    logger.info("🚀 HireLens-AI Backend Starting...")
    logger.info(f"📝 API Docs: http://localhost:{settings.API_PORT}/docs")
    logger.info(f"🗄️  MongoDB: {settings.MONGODB_URI}")
    logger.info(f"🌐 Frontend URL: {settings.FRONTEND_URL}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 HireLens-AI Backend Shutting Down...")
    mongodb_client.close()


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "Request failed", "detail": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions.
    MUST return a Response, not a dict.
    """
    logger.exception("Unhandled exception")  # logs full stack trace

    detail = str(exc) if getattr(settings, "DEBUG", False) else "An error occurred"

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": detail,
        },
    )


@app.get("/")
async def root():
    return {
        "message": "HireLens-AI Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )