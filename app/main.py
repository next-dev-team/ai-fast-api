from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .config import settings
from .utils.logger import logger
from .utils.middleware import (
    RateLimitMiddleware,
    LoggingMiddleware,
    ErrorHandlingMiddleware
)
from .api import chat, images, models, health
from . import __version__


# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# Add CORS middleware
if settings.cors_enabled:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info(f"CORS enabled with origins: {settings.cors_origins}")


# Add custom middleware
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(LoggingMiddleware)
# app.add_middleware(
#     RateLimitMiddleware,
#     max_requests=settings.rate_limit_requests,
#     time_window=settings.rate_limit_window
# )


# Include API routers
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(images.router)
app.include_router(models.router)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": "Internal server error",
                "type": "internal_error",
                "code": "internal_error"
            }
        }
    )


# Startup event
async def startup_event():
    app.add_event_handler("startup", startup_event)
    """Application startup event."""
    logger.info(f"Starting {settings.api_title} v{__version__}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Server will run on {settings.host}:{settings.port}")
    logger.info(f"G4F provider: {settings.g4f_provider}")
    logger.info(f"Rate limiting: {settings.rate_limit_requests} requests per {settings.rate_limit_window}s")
    
    # Initialize G4F service
    try:
        from .services.g4f_service import g4f_service
        await g4f_service.initialize()
        logger.info("G4F service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize G4F service: {str(e)}")


# Shutdown event
async def shutdown_event():
    app.add_event_handler("shutdown", shutdown_event)
    """Application shutdown event."""
    logger.info(f"Shutting down {settings.api_title}")
    
    # Cleanup G4F service
    try:
        from .services.g4f_service import g4f_service
        await g4f_service.cleanup()
        logger.info("G4F service cleaned up successfully")
    except Exception as e:
        logger.error(f"Error during G4F service cleanup: {str(e)}")


def create_app() -> FastAPI:
    """Factory function to create FastAPI application."""
    return app


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
        access_log=True
    )