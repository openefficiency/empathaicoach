"""FastAPI server for R2C2 Voice Coach API endpoints."""

import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from database.session_db import SessionDatabase


# Global database instance
db: Optional[SessionDatabase] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application."""
    global db
    
    # Startup: Initialize database
    logger.info("Initializing R2C2 Voice Coach API server")
    db = SessionDatabase()
    logger.info("Database initialized successfully")
    
    yield
    
    # Shutdown: Cleanup if needed
    logger.info("Shutting down R2C2 Voice Coach API server")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title="R2C2 Voice Coach API",
        description="API endpoints for managing R2C2 coaching sessions and feedback data",
        version="0.1.0",
        lifespan=lifespan
    )
    
    # Configure CORS
    # In production, restrict origins to specific domains
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Import and include routers
    from api.routes import router
    app.include_router(router, prefix="/api")
    
    logger.info("FastAPI application created successfully")
    
    return app


# Create the app instance
app = create_app()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "r2c2-voice-coach-api",
        "version": "0.1.0"
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("API_PORT", "8000"))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    logger.info(f"Starting R2C2 Voice Coach API server on {host}:{port}")
    
    uvicorn.run(
        "api.server:app",
        host=host,
        port=port,
        reload=os.getenv("ENV", "local") == "local",
        log_level="info"
    )
