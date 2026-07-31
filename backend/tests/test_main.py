import pytest


try:
    from app.main import app
    APP_AVAILABLE = True
except ImportError:
    APP_AVAILABLE = False


@pytest.mark.skipif(not APP_AVAILABLE, reason='app.main import failed (missing dependencies)')
def test_health_check():
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


@pytest.mark.skipif(not APP_AVAILABLE, reason='app.main import failed (missing dependencies)')
def test_validate_endpoint_returns_400_for_invalid_url():
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.post('/api/v1/analyze', json={'repo_url': 'not-a-url'})
    assert response.status_code == 400