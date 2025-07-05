import asyncio
import pytest
from app.main import app
from app.services.g4f_service import g4f_service
from fastapi.testclient import TestClient
from asyncio.windows_events import WindowsSelectorEventLoopPolicy

asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

@pytest.fixture(scope="session")
async def initialize_g4f_service():
    """Initialize and clean up G4F service for tests."""
    await g4f_service.initialize()
    yield
    await g4f_service.cleanup()


@pytest.fixture(scope="module")
async def test_app(initialize_g4f_service):
    """Fixture for the FastAPI test client."""
    with TestClient(app) as client:
        yield client