"""src/main.py-ийн автомат тестүүд (US-05, US-07, US-09, US-10, US-11, US-14, US-15)."""


def make_schedule(client, teacher=1, subject=1, room=1, day="Даваа", slot="1"):
    return client.post("/schedules/generate", json={
        "teacher_id": teacher, "subject_id": subject, "room_id": room,
        "day_of_week": day, "time_slot": slot,
    })


# ---------- US-14: Бүртгэл ----------
def test_register_user_ok(client):
    r = client.post("/auth/register", json={"username": "bold", "password": "pass123", "role": "student"})
    assert r.status_code == 200
    assert r.json()["role"] == "student"


def test_register_duplicate_username(client):
    body = {"username": "bold", "password": "pass123", "role": "student"}
    client.post("/auth/register", json=body)
    r = client.post("/auth/register", json=body)
    assert r.status_code == 400


# ---------- US-15: Үндсэн мэдээлэл ----------
def test_create_room_ok(client):
    r = client.post("/admin/rooms", json={"name": "201", "capacity": 30})
    assert r.status_code == 200


def test_create_room_duplicate(client):
    client.post("/admin/rooms", json={"name": "201", "capacity": 30})
    r = client.post("/admin/rooms", json={"name": "201", "capacity": 25})
    assert r.status_code == 400


def test_create_subject_duplicate(client):
    client.post("/admin/subjects", json={"name": "Физик", "max_students": 30})
    r = client.post("/admin/subjects", json={"name": "Физик", "max_students": 20})
    assert r.status_code == 400


# ---------- US-05: Давхцал ----------
def test_generate_schedule_ok(client):
    assert make_schedule(client).status_code == 200


def test_teacher_conflict(client):
    make_schedule(client, teacher=1, room=1)
    r = make_schedule(client, teacher=1, room=2)  # ижил багш, ижил цаг
    assert r.status_code == 400
    assert "багшийн" in r.json()["detail"]


def test_room_conflict(client):
    make_schedule(client, teacher=1, room=1)
    r = make_schedule(client, teacher=2, room=1)  # ижил танхим, ижил цаг
    assert r.status_code == 400
    assert "танхим" in r.json()["detail"]


# ---------- US-09: Ачааллын хязгаар (20 цаг) ----------
def test_teacher_workload_limit(client):
    for i in range(20):
        assert make_schedule(client, teacher=1, room=i + 1, slot=str(i)).status_code == 200
    r = make_schedule(client, teacher=1, room=99, slot="99")
    assert r.status_code == 400
    assert "US-09" in r.json()["detail"]


# ---------- US-10 / US-07: Суудлын хязгаар, сонголт ----------
def test_select_subject_ok(client):
    client.post("/admin/subjects", json={"name": "Хими", "max_students": 2})
    r = client.post("/students/select-subject", json={"student_id": 10, "subject_id": 1})
    assert r.status_code == 200


def test_select_subject_seat_limit(client):
    client.post("/admin/subjects", json={"name": "Хими", "max_students": 2})
    client.post("/students/select-subject", json={"student_id": 10, "subject_id": 1})
    client.post("/students/select-subject", json={"student_id": 11, "subject_id": 1})
    r = client.post("/students/select-subject", json={"student_id": 12, "subject_id": 1})
    assert r.status_code == 400
    assert "US-10" in r.json()["detail"]


def test_select_unknown_subject(client):
    r = client.post("/students/select-subject", json={"student_id": 10, "subject_id": 999})
    assert r.status_code == 404


def test_cancel_subject(client):
    client.post("/admin/subjects", json={"name": "Хими", "max_students": 2})
    client.post("/students/select-subject", json={"student_id": 10, "subject_id": 1})
    r = client.delete("/students/cancel-subject", params={"student_id": 10, "subject_id": 1})
    assert r.status_code == 200
    r = client.delete("/students/cancel-subject", params={"student_id": 10, "subject_id": 1})
    assert r.status_code == 404


# ---------- US-03: Мэдэгдэл ----------
def test_update_schedule_creates_notification(client):
    make_schedule(client, teacher=1)
    r = client.put("/schedules/update/1", params={"new_slot": "5"})
    assert r.status_code == 200
    notes = client.get("/notifications/1").json()["notifications"]
    assert len(notes) == 1 and "5" in notes[0]["message"]


def test_update_missing_schedule(client):
    assert client.put("/schedules/update/999", params={"new_slot": "5"}).status_code == 404


# ---------- US-11 / US-16: Батлах, нийтлэх ----------
def test_student_sees_only_published(client):
    make_schedule(client, slot="1")
    make_schedule(client, teacher=2, room=2, slot="2")
    assert client.get("/students/schedules/10").json()["schedules"] == []
    client.put("/schedules/publish/1")
    schedules = client.get("/students/schedules/10").json()["schedules"]
    assert len(schedules) == 1 and schedules[0]["id"] == 1


def test_publish_missing_schedule(client):
    assert client.put("/schedules/publish/999").status_code == 404
