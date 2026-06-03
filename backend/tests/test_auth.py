def test_register_success(client):
    resp = client.post("/api/auth/register", json={
        "name": "Maria Silva",
        "email": "maria@example.com",
        "password": "senha123",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert "token" in data
    assert data["user"]["email"] == "maria@example.com"


def test_register_duplicate_email(client):
    payload = {"name": "Joao", "email": "joao@dup.com", "password": "senha123"}
    client.post("/api/auth/register", json=payload)
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 409


def test_register_invalid_email(client):
    resp = client.post("/api/auth/register", json={
        "name": "X",
        "email": "nao-e-email",
        "password": "senha123",
    })
    assert resp.status_code == 422


def test_register_short_password(client):
    resp = client.post("/api/auth/register", json={
        "name": "Ana",
        "email": "ana@example.com",
        "password": "123",
    })
    assert resp.status_code == 422


def test_login_success(client):
    client.post("/api/auth/register", json={
        "name": "Pedro",
        "email": "pedro@example.com",
        "password": "senha123",
    })
    resp = client.post("/api/auth/login", json={
        "email": "pedro@example.com",
        "password": "senha123",
    })
    assert resp.status_code == 200
    assert "token" in resp.get_json()


def test_login_wrong_password(client):
    resp = client.post("/api/auth/login", json={
        "email": "pedro@example.com",
        "password": "errada",
    })
    assert resp.status_code == 401


def test_me_requires_auth(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401
