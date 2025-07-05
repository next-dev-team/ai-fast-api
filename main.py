#!/usr/bin/env python3
"""
Main entry point for the AI FastAPI server.
This file serves as the application entry point and imports the modular FastAPI app.
"""

import uvicorn
from app.main import create_app
from app.config import settings
from app.utils.logger import logger


def main():
    """Main function to run the FastAPI server."""
    try:
        # Create the FastAPI application
        app = create_app()
        
        # Log startup information
        logger.info(f"Starting {settings.api_title} server...")
        logger.info(f"Server configuration:")
        logger.info(f"  - Host: {settings.host}")
        logger.info(f"  - Port: {settings.port}")
        logger.info(f"  - Debug: {settings.debug}")
        logger.info(f"  - G4F Provider: {settings.g4f_provider}")
        logger.info(f"  - Rate Limit: {settings.rate_limit_requests} req/{settings.rate_limit_window}s")
        
        # Run the server
        # Run the FastAPI application using uvicorn
        # Pass the application as an import string to enable 'reload' or 'workers'
        uvicorn.run(
            "app.main:create_app",  # Pass the import string to the create_app factory
            host=settings.host,
            port=settings.port,
            log_level="info" if not settings.debug else "debug",
            reload=settings.debug,
            factory=True  # Indicate that create_app is a factory function
        )
        
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise


if __name__ == "__main__":
    main()