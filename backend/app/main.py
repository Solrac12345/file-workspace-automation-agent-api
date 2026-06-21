"""
Main entry point for the FastAPI application.
Configures routes, lifespan events, and middleware.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.mongodb import MongoDB, ping_database
from app.routers import auth_routes
from app.routers import auth_routes, user_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events for resource management.
    """
    # Startup: connect to MongoDB
    await MongoDB.connect()
    yield
    # Shutdown: disconnect from MongoDB
    await MongoDB.disconnect()


# Initialize FastAPI app with metadata
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="REST API for File & Workspace Automation Agent - SENA GA4",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS (will be refined in Phase 6)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_routes.router)
app.include_router(user_routes.router)

@app.get(
    "/",
    tags=["Root"],
    summary="Root endpoint",
    description="Returns basic API information"
)
async def root():
    """Root endpoint returning basic API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
        },
        "endpoints": {
            "health": "/api/health",
            "info": "/api/info",
        },
    }


@app.get(
    "/api/health",
    tags=["Monitoring"],
    summary="Health check",
    description="Returns API status and MongoDB connection status"
)
async def health_check():
    """
    Health check endpoint.
    Returns API status and MongoDB connection status.
    """
    db_status = await ping_database()
    return {
        "api_status": "healthy",
        "version": settings.APP_VERSION,
        "mongodb": db_status,
    }


@app.get(
    "/api/info",
    tags=["Monitoring"],
    summary="API information",
    description="Returns detailed information about the API"
)
async def api_info():
    """
    API information endpoint.
    Returns metadata about the API configuration.
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug_mode": settings.DEBUG,
        "database": {
            "name": settings.DB_NAME,
            "status": "connected",
        },
        "features": [
            "Authentication module",
            "Users management",
            "Services/Rules automation",
            "Products/Files management",
        ],
    }