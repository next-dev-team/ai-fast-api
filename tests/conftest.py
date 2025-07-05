import pytest
from app.main import app
from app.services.g4f_service import g4f_service


@pytest.fixture(scope="session", autouse=True)
async def initialize_g4f_service():
    """Initialize and clean up G4F service for tests."""
    await g4f_service.initialize()
    yield
    await g4f_service.cleanup()


@pytest.fixture(scope="module")
def test_app():
    """Fixture for the FastAPI test client."""
    with TestClient(app) as client:
        yield client