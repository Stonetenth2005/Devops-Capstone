from datetime import UTC, datetime

# ---- ops endpoints ----------------------------------------------------------


def test_health(client):
    assert client.get("/health").json() == {"status": "UP"}


def test_ready_checks_database(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "READY"}


def test_root_identifies_service(client):
    assert client.get("/").json()["service"] == "ClinicFlow API"


def test_metrics_exposes_prometheus_format(client, appointment):
    body = client.get("/metrics").text
    assert "http_requests_total" in body
    assert "clinicflow_appointments_booked_total" in body


# ---- doctors ----------------------------------------------------------------


def test_create_and_list_doctors(client, doctor):
    doctors = client.get("/api/doctors").json()
    assert [d["name"] for d in doctors] == ["Dr. Test"]
    assert doctors[0]["specialty"] == "Cardiology"


def test_create_doctor_validation(client):
    assert client.post("/api/doctors", json={"name": "X", "specialty": "Cardiology"}).status_code == 422


def test_delete_doctor_removes_their_appointments(client, doctor, appointment):
    assert client.delete(f"/api/doctors/{doctor['id']}").status_code == 204
    assert client.get(f"/api/appointments/{appointment['id']}").status_code == 404
    assert client.delete(f"/api/doctors/{doctor['id']}").status_code == 404


# ---- appointments: CRUD -----------------------------------------------------


def test_create_appointment(client, doctor, appointment):
    assert appointment["status"] == "SCHEDULED"
    assert appointment["doctor_name"] == "Dr. Test"
    assert appointment["specialty"] == "Cardiology"
    assert datetime.fromisoformat(appointment["scheduled_at"]) == datetime(2030, 1, 15, 10, tzinfo=UTC)


def test_get_appointment_by_id(client, appointment):
    response = client.get(f"/api/appointments/{appointment['id']}")
    assert response.status_code == 200
    assert response.json()["patient_name"] == "Asha Verma"


def test_get_missing_appointment_returns_404(client):
    assert client.get("/api/appointments/999").status_code == 404


def test_create_appointment_for_unknown_doctor(client):
    response = client.post(
        "/api/appointments",
        json={"patient_name": "Ravi", "doctor_id": 42, "scheduled_at": "2030-01-15T10:00:00Z"},
    )
    assert response.status_code == 404


def test_update_appointment_reason(client, appointment):
    response = client.put(f"/api/appointments/{appointment['id']}", json={"reason": "Follow-up on ECG"})
    assert response.status_code == 200
    assert response.json()["reason"] == "Follow-up on ECG"


def test_delete_appointment(client, appointment):
    assert client.delete(f"/api/appointments/{appointment['id']}").status_code == 204
    assert client.get(f"/api/appointments/{appointment['id']}").status_code == 404


def test_list_appointments_filters(client, doctor, appointment):
    client.post(
        "/api/appointments",
        json={"patient_name": "Ravi Kumar", "doctor_id": doctor["id"], "scheduled_at": "2030-01-16T09:00:00Z"},
    )
    assert len(client.get("/api/appointments").json()) == 2
    assert len(client.get("/api/appointments", params={"on": "2030-01-16"}).json()) == 1
    assert len(client.get("/api/appointments", params={"status": "COMPLETED"}).json()) == 0
    assert client.get("/api/appointments", params={"status": "BOGUS"}).status_code == 422


# ---- appointments: business rules ------------------------------------------


def test_double_booking_is_rejected(client, doctor, appointment):
    overlapping = {"patient_name": "Ravi Kumar", "doctor_id": doctor["id"], "scheduled_at": "2030-01-15T10:15:00Z"}
    response = client.post("/api/appointments", json=overlapping)
    assert response.status_code == 409


def test_back_to_back_booking_is_allowed(client, doctor, appointment):
    next_slot = {"patient_name": "Ravi Kumar", "doctor_id": doctor["id"], "scheduled_at": "2030-01-15T10:30:00Z"}
    assert client.post("/api/appointments", json=next_slot).status_code == 201


def test_cancelled_slot_can_be_rebooked(client, doctor, appointment):
    client.put(f"/api/appointments/{appointment['id']}", json={"status": "CANCELLED"})
    same_slot = {"patient_name": "Ravi Kumar", "doctor_id": doctor["id"], "scheduled_at": "2030-01-15T10:00:00Z"}
    assert client.post("/api/appointments", json=same_slot).status_code == 201


def test_status_workflow(client, appointment):
    url = f"/api/appointments/{appointment['id']}"
    assert client.put(url, json={"status": "CHECKED_IN"}).json()["status"] == "CHECKED_IN"
    assert client.put(url, json={"status": "COMPLETED"}).json()["status"] == "COMPLETED"
    # A completed visit cannot be re-opened or cancelled.
    assert client.put(url, json={"status": "SCHEDULED"}).status_code == 409
    assert client.put(url, json={"status": "CANCELLED"}).status_code == 409


def test_stats(client, doctor, appointment):
    client.put(f"/api/appointments/{appointment['id']}", json={"status": "CHECKED_IN"})
    stats = client.get("/api/appointments/stats").json()
    assert stats["total"] == 1
    assert stats["checkedIn"] == 1
    assert stats["scheduled"] == 0
    assert stats["doctors"] == 1
