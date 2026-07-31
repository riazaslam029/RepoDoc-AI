import pytest
from fastapi.testclient import TestClient


def _get_app():
    try:
        from app.main import app
        return app
    except Exception:
        return None


def test_health_check():
    app = _get_app()
    assert app is not None, 'Failed to import app'
    client = TestClient(app)
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_validate_endpoint_returns_422_for_invalid_url():
    app = _get_app()
    assert app is not None, 'Failed to import app'
    client = TestClient(app)
    response = client.post('/api/v1/analyze', json={'repo_url': 'not-a-url'})
    assert response.status_code == 422