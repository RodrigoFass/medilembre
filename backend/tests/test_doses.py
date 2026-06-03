import pytest
from datetime import datetime, timedelta
from app import db
from app.models.dose_log import DoseLog
from app.models.medication import Medication


MED_PAYLOAD = {
    "name": "Atenolol",
    "dose": "25mg",
    "frequency": "1x ao dia",
    "schedule_times": ["08:00"],
    "start_date": "2024-01-01",
}


@pytest.fixture()
def setup(client, auth_headers):
    """Create patient + medication + a dose log, return their IDs."""
    p = client.post("/api/patients/", json={"name": "Paciente Dose"}, headers=auth_headers)
    pid = p.get_json()["id"]
    m = client.post(f"/api/medications/patient/{pid}", json=MED_PAYLOAD, headers=auth_headers)
    mid = m.get_json()["id"]

    with client.application.app_context():
        log = DoseLog(
            medication_id=mid,
            scheduled_time=datetime.utcnow(),
            status="pending",
        )
        db.session.add(log)
        db.session.commit()
        log_id = log.id

    return {"patient_id": pid, "med_id": mid, "log_id": log_id}


def test_today_doses(client, auth_headers, setup):
    resp = client.get(f"/api/doses/today/{setup['patient_id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


def test_confirm_dose(client, auth_headers, setup):
    resp = client.post(f"/api/doses/confirm/{setup['log_id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "taken"


def test_confirm_dose_twice_returns_409(client, auth_headers, setup):
    client.post(f"/api/doses/confirm/{setup['log_id']}", headers=auth_headers)
    resp = client.post(f"/api/doses/confirm/{setup['log_id']}", headers=auth_headers)
    assert resp.status_code == 409


def test_skip_dose(client, auth_headers, setup):
    resp = client.post(f"/api/doses/skip/{setup['log_id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "missed"


def test_skip_taken_dose_returns_409(client, auth_headers, setup):
    client.post(f"/api/doses/confirm/{setup['log_id']}", headers=auth_headers)
    resp = client.post(f"/api/doses/skip/{setup['log_id']}", headers=auth_headers)
    assert resp.status_code == 409


def test_history(client, auth_headers, setup):
    resp = client.get(f"/api/doses/history/{setup['patient_id']}?days=30", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert "logs" in data
    assert "summary" in data


def test_history_invalid_days_defaults(client, auth_headers, setup):
    resp = client.get(f"/api/doses/history/{setup['patient_id']}?days=abc", headers=auth_headers)
    assert resp.status_code == 200


def test_history_days_capped_at_365(client, auth_headers, setup):
    resp = client.get(f"/api/doses/history/{setup['patient_id']}?days=99999", headers=auth_headers)
    assert resp.status_code == 200


def test_cross_user_cannot_access_doses(client, setup):
    """Second user must not access another user's doses."""
    client.post("/api/auth/register", json={
        "name": "Outro", "email": "outro@example.com", "password": "senha123"
    })
    r = client.post("/api/auth/login", json={"email": "outro@example.com", "password": "senha123"})
    other_headers = {"Authorization": f"Bearer {r.get_json()['token']}"}

    resp = client.get(f"/api/doses/today/{setup['patient_id']}", headers=other_headers)
    assert resp.status_code == 404


def test_cross_user_cannot_confirm_dose(client, auth_headers, setup):
    """Second user must not confirm another user's dose."""
    client.post("/api/auth/register", json={
        "name": "Invasor", "email": "invasor@example.com", "password": "senha123"
    })
    r = client.post("/api/auth/login", json={"email": "invasor@example.com", "password": "senha123"})
    other_headers = {"Authorization": f"Bearer {r.get_json()['token']}"}

    resp = client.post(f"/api/doses/confirm/{setup['log_id']}", headers=other_headers)
    assert resp.status_code == 403
