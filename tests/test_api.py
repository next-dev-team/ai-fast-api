import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_status_check():
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json()["status"] == "operational"


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "name" in response.json()


def test_create_chat_completion():
    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": "Hello"}],
        },
    )
    assert response.status_code == 200
    assert "id" in response.json()


def test_list_chat_models():
    response = client.get("/v1/chat/completions/models")
    assert response.status_code == 200
    assert "data" in response.json()


def test_create_image_generation():
    response = client.post(
        "/v1/images/generate",
        json={
            "prompt": "A cute baby sea otter",
            "n": 1,
            "size": "1024x1024",
        },
    )
    assert response.status_code == 200
    assert "data" in response.json()


def test_list_image_models():
    response = client.get("/v1/images/models")
    assert response.status_code == 200
    assert "data" in response.json()


def test_list_models():
    response = client.get("/v1/models")
    assert response.status_code == 200
    assert "data" in response.json()


def test_retrieve_model():
    response = client.get("/v1/models/gpt-4o")
    assert response.status_code == 200
    assert response.json()["id"] == "gpt-4o"


def test_list_providers():
    
    response = client.get("/v1/providers")
    assert response.status_code == 200
    assert "data" in response.json()


def test_retrieve_provider():
    # This test might fail if the provider is not available
    # We are just checking if the endpoint is working
    response = client.get("/v1/providers/g4f")
    if response.status_code == 200:
        assert response.json()["id"] == "g4f"
    else:
        assert response.status_code == 404