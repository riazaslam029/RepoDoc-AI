import pytest
from fastapi.testclient import TestClient
from app.main import app


def test_health_check():
    client = TestClient(app)
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_validate_endpoint_valid_url():
    client = TestClient(app)
    response = client.post('/api/v1/validate', json={'repo_url': 'https://github.com/riazaslam029/RepoDoc-AI'})
    assert response.status_code == 200
    data = response.json()
    assert data['valid'] is True
    assert data['owner'] == 'riazaslam029'
    assert data['repo'] == 'RepoDoc-AI'


def test_validate_endpoint_invalid_url():
    client = TestClient(app)
    response = client.post('/api/v1/validate', json={'repo_url': 'not-a-url'})
    assert response.status_code == 200
    data = response.json()
    assert data['valid'] is False
    assert 'error' in data


def test_analyze_endpoint_returns_422_for_invalid_url():
    client = TestClient(app)
    response = client.post('/api/v1/analyze', json={'repo_url': 'not-a-url'})
    assert response.status_code == 422