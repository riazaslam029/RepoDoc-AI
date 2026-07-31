import pytest
from fastapi.testclient import TestClient
from app.main import app


def test_health_check():
    client = TestClient(app)
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_analyze_endpoint_returns_422_for_invalid_url():
    client = TestClient(app)
    response = client.post('/api/v1/analyze', json={'repo_url': 'not-a-url'})
    assert response.status_code == 422