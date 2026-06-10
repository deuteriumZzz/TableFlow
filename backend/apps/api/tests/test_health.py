import pytest


@pytest.mark.django_db
def test_health_check_returns_ok(api_client):
    resp = api_client.get('/api/health/')
    assert resp.status_code == 200
    assert resp.data['status'] == 'ok'
    assert resp.data['db'] is True


@pytest.mark.django_db
def test_health_check_no_auth_required(api_client):
    """Health endpoint must be accessible without a token."""
    resp = api_client.get('/api/health/')
    assert resp.status_code == 200
