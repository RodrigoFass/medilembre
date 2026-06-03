import pytest


@pytest.fixture()
def patient_id(client, auth_headers):
    resp = client.post("/api/patients/", json={"name": "Paciente Med"},
                       headers=auth_headers)
    return resp.get_json()["id"]


MED_PAYLOAD = {
    "name": "Losartana",
    "dose": "50mg",
    "frequency": "1x ao dia",
    "schedule_times": ["08:00"],
    "start_date": "2024-01-01",
}


def test_create_medication_success(client, auth_headers, patient_id):
    resp = client.post(f"/api/medications/patient/{patient_id}",
                       json=MED_PAYLOAD, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "Losartana"
    assert data["schedule_times"] == ["08:00"]


def test_create_medication_invalid_time_format(client, auth_headers, patient_id):
    payload = {**MED_PAYLOAD, "schedule_times": ["8h00", "14:00"]}
    resp = client.post(f"/api/medications/patient/{patient_id}",
                       json=payload, headers=auth_headers)
    assert resp.status_code == 422


def test_create_medication_missing_required(client, auth_headers, patient_id):
    resp = client.post(f"/api/medications/patient/{patient_id}",
                       json={"name": "Incompleto"}, headers=auth_headers)
    assert resp.status_code == 422


def test_list_medications(client, auth_headers, patient_id):
    client.post(f"/api/medications/patient/{patient_id}",
                json=MED_PAYLOAD, headers=auth_headers)
    resp = client.get(f"/api/medications/patient/{patient_id}",
                      headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.get_json()) >= 1


def test_delete_medication(client, auth_headers, patient_id):
    resp = client.post(f"/api/medications/patient/{patient_id}",
                       json=MED_PAYLOAD, headers=auth_headers)
    mid = resp.get_json()["id"]
    del_resp = client.delete(f"/api/medications/{mid}", headers=auth_headers)
    assert del_resp.status_code == 200
