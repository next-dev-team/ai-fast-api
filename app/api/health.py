from fastapi import APIRouter, HTTPException
import time
from typing import Dict, Any

from ..models import HealthResponse
from ..config import settings
from ..utils.logger import logger
from .. import __version__


router = APIRouter(tags=["Health & Status"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check the health status of the API server"
)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    try:
        return HealthResponse(
            status="healthy",
            version=__version__,
            timestamp=int(time.time())
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Service unavailable"
        )


@router.get(
    "/status",
    summary="Detailed status",
    description="Get detailed status information about the API server"
)
async def status_check() -> Dict[str, Any]:
    """Detailed status endpoint."""
    try:
        return {
            "status": "operational",
            "version": __version__,
            "timestamp": int(time.time()),
            "config": {
                "debug": settings.debug,
                "host": settings.host,
                "port": settings.port,
                "rate_limit": {
                    "requests": settings.rate_limit_requests,
                    "window": settings.rate_limit_window
                }
            },
            "features": {
                "chat_completions": True,
                "image_generation": True,
                "streaming": True,
                "web_search": True,
                "provider_selection": True
            },
            "endpoints": {
                "chat": "/v1/chat/completions",
                "images": "/v1/images/generate",
                "models": "/v1/models",
                "providers": "/v1/providers",
                "health": "/health",
                "docs": "/docs"
            }
        }
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Service unavailable"
        )


@router.get(
    "/",
    summary="API information",
    description="Get basic API information and available endpoints"
)
async def root() -> Dict[str, Any]:
    """Root endpoint with API information."""
    return {
        "name": settings.api_title,
        "description": settings.api_description,
        "version": __version__,
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
        "endpoints": {
            "chat_completions": "/v1/chat/completions",
            "image_generation": "/v1/images/generate",
            "models": "/v1/models",
            "providers": "/v1/providers",
            "health": "/health",
            "status": "/status"
        },
        "features": [
            "OpenAI-compatible API",
            "Multiple AI providers via G4F",
            "Streaming responses",
            "Image generation",
            "Web search integration",
            "Rate limiting",
            "Request logging"
        ],
        "compatibility": "OpenAI API v1"
    }