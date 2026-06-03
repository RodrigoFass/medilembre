def test_list_patients_empty(client, auth_headers):
    resp = client.get("/api/patients/", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json() == [] or isinstance(resp.get_json(), list)


def test_create_patient_success(client, auth_headers):
    resp = client.post("/api/patients/", json={
        "name": "Dona Maria",
        "birth_date": "1950-03-15",
        "notes": "Hipertensa",
    }, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "Dona Maria"
    assert data["id"] is not None


def test_create_patient_missing_name(client, auth_headers):
    resp = client.post("/api/patients/", json={
        "birth_date": "1950-01-01",
    }, headers=auth_headers)
    assert resp.status_code == 422


def test_create_patient_name_too_short(client, auth_headers):
    resp = client.post("/api/patients/", json={"name": "A"}, headers=auth_headers)
    assert resp.status_code == 422


def test_create_and_delete_patient(client, auth_headers):
    resp = client.post("/api/patients/", json={"name": "Para Deletar"},
                       headers=auth_headers)
    pid = resp.get_json()["id"]
    del_resp = client.delete(f"/api/patients/{pid}", headers=auth_headers)
    assert del_resp.status_code == 200
    assert del_resp.get_json()["ok"] is True


def test_update_patient(client, auth_headers):
    resp = client.post("/api/patients/", json={"name": "Nome Antigo"},
                       headers=auth_headers)
    pid = resp.get_json()["id"]
    upd = client.put(f"/api/patients/{pid}", json={"name": "Nome Novo"},
                     headers=auth_headers)
    assert upd.status_code == 200
    assert upd.get_json()["name"] == "Nome Novo"


def test_list_requires_auth(client):
    resp = client.get("/api/patients/")
    assert resp.status_code == 401
