"""Uçtan uca API testleri."""
import csv
import io
import json
import sqlite3

import pytest
from conftest import TEACHER

import server


def start(client, name="Ayşe Yılmaz", no="1042"):
    r = client.post("/api/start", json={"name": name, "no": no})
    return r, r.get_json()


def secret_questions(app, exam_id):
    with sqlite3.connect(app.config["DB_PATH"]) as db:
        return json.loads(db.execute("SELECT questions FROM exams WHERE id=?", (exam_id,)).fetchone()[0])


def correct_answers(app, exam_id):
    return {str(q["id"]): q["answer"] for q in secret_questions(app, exam_id)}


def set_settings(client, **kw):
    r = client.put("/api/settings", json=kw, headers=TEACHER)
    assert r.status_code == 200, r.get_json()
    return r.get_json()


# ---------------------------------------------------------------- sınav akışı
def test_full_exam_flow(app, client):
    r, d = start(client)
    assert r.status_code == 200
    assert len(d["questions"]) == 10 and d["remaining"] == 900
    assert all("answer" not in q and "solution" not in q for q in d["questions"])

    r = client.post("/api/submit", json={"exam_id": d["exam_id"], "answers": correct_answers(app, d["exam_id"])})
    res = r.get_json()
    assert r.status_code == 200
    assert (res["score"], res["correct"], res["wrong"], res["late"]) == (100, 10, 0, False)
    assert res["show_solutions"] and "solution" in res["details"][0]

    assert client.post("/api/submit", json={"exam_id": d["exam_id"], "answers": {}}).status_code == 409


def test_empty_submission_scores_zero(client):
    _, d = start(client)
    res = client.post("/api/submit", json={"exam_id": d["exam_id"], "answers": {}}).get_json()
    assert res["score"] == 0 and res["wrong"] == 10


def test_start_validation(client):
    assert client.post("/api/start", json={"name": " ", "no": "1"}).status_code == 400
    assert client.post("/api/start", data="bozuk", content_type="application/json").status_code == 400
    assert client.post("/api/submit", json={"exam_id": "yok"}).status_code == 404


def test_same_student_resumes_instead_of_new_attempt(client):
    _, d1 = start(client)
    client.post("/api/save", json={"exam_id": d1["exam_id"], "answers": {"1": "x"}})
    r, d2 = start(client, name="ayşe yılmaz")  # büyük/küçük harf farkı
    assert r.status_code == 200
    assert d2["exam_id"] == d1["exam_id"] and d2["answers"] == {"1": "x"}

    r, d3 = start(client, name="Başka Biri")
    assert r.status_code == 409


def test_resume_endpoint(client):
    _, d = start(client)
    r = client.post("/api/resume", json={"exam_id": d["exam_id"]})
    assert r.status_code == 200 and r.get_json()["exam_id"] == d["exam_id"]
    client.post("/api/submit", json={"exam_id": d["exam_id"], "answers": {}})
    assert client.post("/api/resume", json={"exam_id": d["exam_id"]}).status_code == 410


def test_answers_are_sanitized(app, client):
    _, d = start(client)
    payload = {"1": "a" * 10_000, "999": "x", "2": True, "3": {"x": 1}, "4": "  "}
    client.post("/api/save", json={"exam_id": d["exam_id"], "answers": payload})
    with sqlite3.connect(app.config["DB_PATH"]) as db:
        saved = json.loads(db.execute("SELECT answers FROM exams").fetchone()[0])
    assert saved == {"1": "a" * 2000}


# ---------------------------------------------------------------- süre
def test_late_submit_uses_last_saved_answers(app, client, clock):
    _, d = start(client)
    answers = correct_answers(app, d["exam_id"])
    assert client.post("/api/save", json={"exam_id": d["exam_id"], "answers": answers}).status_code == 200

    clock.t += 900 + 31  # süre + tolerans aşıldı
    assert client.post("/api/save", json={"exam_id": d["exam_id"], "answers": {}}).status_code == 409
    res = client.post("/api/submit", json={"exam_id": d["exam_id"], "answers": {}}).get_json()
    assert res["late"] is True and res["score"] == 100  # boş gönderilse bile kayıtlı cevaplar geçerli


def test_submit_within_grace_period_is_on_time(client, clock):
    _, d = start(client)
    clock.t += 900 + 20
    assert client.post("/api/submit", json={"exam_id": d["exam_id"], "answers": {}}).get_json()["late"] is False


def test_abandoned_exam_is_auto_finalized(app, client, clock):
    _, d = start(client)
    client.post("/api/save", json={"exam_id": d["exam_id"], "answers": correct_answers(app, d["exam_id"])})
    clock.t += 2000
    rows = client.get("/api/results", headers=TEACHER).get_json()["rows"]
    assert rows[0]["status"] == "bitti" and rows[0]["auto"] is True and rows[0]["score"] == 100
    assert client.post("/api/resume", json={"exam_id": d["exam_id"]}).status_code == 410


def test_duration_change_does_not_affect_running_exam(client, clock):
    _, d = start(client)
    set_settings(client, duration_min=1)
    clock.t += 300
    r = client.post("/api/save", json={"exam_id": d["exam_id"], "answers": {}})
    assert r.status_code == 200 and r.get_json()["remaining"] == 600


# ---------------------------------------------------------------- ayarlar
def test_settings_closed_exam_blocks_new_students_only(client):
    _, d = start(client, no="1")
    set_settings(client, exam_open=False)
    assert client.get("/api/status").get_json()["open"] is False
    r, _ = start(client, no="2")
    assert r.status_code == 403
    r, d2 = start(client, no="1")  # sınavdaki öğrenci devam edebilir
    assert r.status_code == 200 and d2["exam_id"] == d["exam_id"]


def test_settings_question_count_and_duration(client):
    set_settings(client, question_count=5, duration_min=20)
    _, d = start(client)
    assert len(d["questions"]) == 5 and d["remaining"] == 1200


def test_settings_retake(client):
    _, d = start(client)
    client.post("/api/submit", json={"exam_id": d["exam_id"], "answers": {}})
    r, _ = start(client)
    assert r.status_code == 200  # varsayılan: tekrar girişe izin var
    client.post("/api/submit", json={"exam_id": r.get_json()["exam_id"], "answers": {}})
    set_settings(client, allow_retake=False)
    r, _ = start(client)
    assert r.status_code == 409


def test_settings_hide_solutions(client):
    set_settings(client, show_solutions=False)
    _, d = start(client)
    res = client.post("/api/submit", json={"exam_id": d["exam_id"], "answers": {}}).get_json()
    assert res["show_solutions"] is False
    assert all(set(item) == {"id", "topic", "correct"} for item in res["details"])


@pytest.mark.parametrize("body", [
    {"question_count": 7}, {"question_count": True}, {"duration_min": 0}, {"duration_min": "15"},
    {"duration_min": 500}, {"exam_open": "evet"}, [],
])
def test_settings_validation(client, body):
    assert client.put("/api/settings", json=body, headers=TEACHER).status_code == 400


# ---------------------------------------------------------------- öğretmen
def test_teacher_auth(client):
    assert client.get("/api/results").status_code == 401
    assert client.get("/api/results?sifre=1234").status_code == 401  # URL'de şifre kabul edilmez
    assert client.get("/api/results", headers={"X-Ogretmen-Sifre": "çşğ"}).status_code == 401
    assert client.get("/api/results", headers=TEACHER).status_code == 200


def test_teacher_bruteforce_lockout(client):
    for _ in range(server.MAX_FAILS):
        assert client.get("/api/info", headers={"X-Ogretmen-Sifre": "0000"}).status_code == 401
    r = client.get("/api/info", headers=TEACHER)
    assert r.status_code == 429 and r.headers["Retry-After"] == str(server.LOCK_SECONDS)


def test_results_summary_topics_and_detail(app, client):
    _, d1 = start(client, no="1")
    client.post("/api/submit", json={"exam_id": d1["exam_id"], "answers": correct_answers(app, d1["exam_id"])})
    _, d2 = start(client, no="2")
    client.post("/api/submit", json={"exam_id": d2["exam_id"], "answers": {}})
    start(client, no="3")

    data = client.get("/api/results", headers=TEACHER).get_json()
    assert data["summary"] == {"done": 2, "live": 1, "average": 50.0, "pass_rate": 50}
    assert sum(t["total"] for t in data["topics"]) == 20
    assert sum(t["correct"] for t in data["topics"]) == 10
    rates = [t["rate"] for t in data["topics"]]
    assert rates == sorted(rates)  # en zayıf konu en üstte

    detail = client.get(f"/api/results/{d1['exam_id']}", headers=TEACHER).get_json()
    assert detail["score"] == 100 and all(q["correct"] for q in detail["details"])
    live_id = data["rows"][0]["id"]
    assert client.get(f"/api/results/{live_id}", headers=TEACHER).status_code == 409


def test_attempt_numbering(client):
    for _ in range(2):
        _, d = start(client)
        client.post("/api/submit", json={"exam_id": d["exam_id"], "answers": {}})
    rows = client.get("/api/results", headers=TEACHER).get_json()["rows"]
    assert sorted(r["attempt"] for r in rows) == [1, 2]


def test_delete_one_and_clear(client):
    _, d1 = start(client, no="1")
    start(client, no="2")
    assert client.delete(f"/api/results/{d1['exam_id']}", headers=TEACHER).status_code == 200
    assert client.delete(f"/api/results/{d1['exam_id']}", headers=TEACHER).status_code == 404
    assert len(client.get("/api/results", headers=TEACHER).get_json()["rows"]) == 1
    client.delete("/api/results", headers=TEACHER)
    assert client.get("/api/results", headers=TEACHER).get_json()["rows"] == []


def test_csv_export(client):
    for no, name in (("10", "=HYPERLINK(\"x\")"), ("2", "Çağrı Öz")):
        _, d = start(client, name=name, no=no)
        client.post("/api/submit", json={"exam_id": d["exam_id"], "answers": {}})
    start(client, name="Sınavda", no="3")  # bitmemiş sınav CSV'ye girmez

    r = client.get("/api/results.csv", headers=TEACHER)
    raw = r.data.decode("utf-8")
    assert raw.startswith("\ufeff")
    lines = list(csv.reader(io.StringIO(raw[1:]), delimiter=";"))
    assert lines[0][:3] == ["Okul No", "Ad Soyad", "Deneme"]
    assert len(lines) == 3
    assert lines[1][:3] == ["2", "Çağrı Öz", "1"]           # sayısal sıralama: 2 < 10
    assert lines[2][:2] == ["10", "'=HYPERLINK(\"x\")"]    # formül etkisizleştirildi


# ---------------------------------------------------------------- genel
def test_pages_and_security_headers(client):
    for path in ("/", "/ogretmen", "/static/style.css", "/static/student.js", "/static/teacher.js"):
        r = client.get(path)
        assert r.status_code == 200, path
        assert "script-src 'self'" in r.headers["Content-Security-Policy"]
        assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert client.get("/api/status").headers["Cache-Control"] == "no-store"


def test_qr_code(client):
    r = client.get("/api/qr.svg")
    assert r.status_code == 200 and r.mimetype == "image/svg+xml" and b"<svg" in r.data


def test_request_size_limit(client):
    r = client.post("/api/save", data="x" * 300_000, content_type="application/json")
    assert r.status_code == 413


def test_migrates_v2_database(tmp_path):
    path = tmp_path / "v2.db"
    with sqlite3.connect(path) as db:
        db.execute("""CREATE TABLE exams (id TEXT PRIMARY KEY, no TEXT NOT NULL, name TEXT NOT NULL,
            questions TEXT NOT NULL, answers TEXT, started_at REAL NOT NULL, submitted_at REAL,
            correct INTEGER, wrong INTEGER, score INTEGER)""")
        q = [{"id": 1, "type": "short", "topic": "T", "text": "?", "code": None, "answer": "5", "solution": ""}]
        db.execute("INSERT INTO exams VALUES ('old', '7', 'Eski', ?, ?, 1700000000, 1700000300, 1, 0, 100)",
                   (json.dumps(q), json.dumps({"1": "5"})))
    app = server.create_app(db_path=str(path), teacher_key="1234")
    c = app.test_client()
    data = c.get("/api/results", headers=TEACHER).get_json()
    assert data["rows"][0]["score"] == 100 and data["topics"][0]["rate"] == 100
    assert c.get("/api/results/old", headers=TEACHER).get_json()["details"][0]["correct"] is True
