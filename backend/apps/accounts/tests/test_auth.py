import pytest


@pytest.mark.django_db
class TestRegister:
    URL = '/api/auth/register/'

    def test_register_creates_user(self, api_client):
        resp = api_client.post(self.URL, {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'X7k!mP9qR2',
        })
        assert resp.status_code == 201
        assert resp.data['username'] == 'newuser'

    def test_register_sets_role_client(self, api_client):
        resp = api_client.post(self.URL, {
            'username': 'clientuser',
            'password': 'X7k!mP9qR2',
        })
        assert resp.status_code == 201
        assert resp.data['role'] == 'client'

    def test_register_password_too_short(self, api_client):
        resp = api_client.post(self.URL, {
            'username': 'u',
            'password': '12',
        })
        assert resp.status_code == 400

    def test_register_duplicate_username(self, api_client, admin_user):
        resp = api_client.post(self.URL, {
            'username': admin_user.username,
            'password': 'X7k!mP9qR2',
        })
        assert resp.status_code == 400


@pytest.mark.django_db
class TestLogin:
    URL = '/api/auth/token/'

    def test_login_returns_tokens(self, api_client, admin_user):
        resp = api_client.post(self.URL, {
            'username': 'admin_test',
            'password': 'pass123',
        })
        assert resp.status_code == 200
        assert 'access' in resp.data
        assert 'refresh' in resp.data

    def test_login_wrong_password(self, api_client, admin_user):
        resp = api_client.post(self.URL, {
            'username': 'admin_test',
            'password': 'wrong',
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, api_client):
        resp = api_client.post(self.URL, {
            'username': 'ghost',
            'password': 'pass123',
        })
        assert resp.status_code == 401


@pytest.mark.django_db
class TestMe:
    URL = '/api/users/me/'

    def test_me_returns_current_user(self, admin_client, admin_user):
        resp = admin_client.get(self.URL)
        assert resp.status_code == 200
        assert resp.data['username'] == admin_user.username
        assert resp.data['role'] == 'admin'

    def test_me_requires_auth(self, api_client):
        resp = api_client.get(self.URL)
        assert resp.status_code == 401
