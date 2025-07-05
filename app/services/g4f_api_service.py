import asyncio
import multiprocessing
from g4f.api import run_api
from ..config import settings
from ..utils.logger import logger

class G4FApiService:
    def __init__(self):
        self.process = None

    def start(self):
        """Start the G4F API server in a separate process."""
        if self.process and self.process.is_alive():
            logger.info("G4F API server is already running.")
            return

        try:
            logger.info(f"Starting G4F API server on {settings.g4f_api_host}:{settings.g4f_api_port}")
            self.process = multiprocessing.Process(
                target=run_api,
                kwargs={
                    "bind": f"{settings.g4f_api_host}:{settings.g4f_api_port}",
                    "workers": settings.g4f_api_workers
                }
            )
            self.process.start()
            logger.info(f"G4F API server started with PID: {self.process.pid}")
        except Exception as e:
            logger.error(f"Failed to start G4F API server: {e}")
            raise

    def stop(self):
        """Stop the G4F API server."""
        if self.process and self.process.is_alive():
            logger.info("Stopping G4F API server...")
            self.process.terminate()
            self.process.join()
            logger.info("G4F API server stopped.")
        else:
            logger.info("G4F API server is not running.")

g4f_api_service = G4FApiService()