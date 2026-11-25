"""Uçtan uca API testleri."""
import csv
import io
import json
import sqlite3

import pytest
from conftest import KEY, TEACHER

from pytest_pro import auth, create_app
from pytest_pro.db import MIGRATIONS


def start(client, name="Ayşe Yılmaz", no="1042"):
    r = client.post("/api/start", json={"name": name, "no": no})
    return r, r.get_json()


def submit(client, exam_id, answers=None):
    return client.post("/api/submit", json={"exam_id": exam_id, "answers": answers or {}})


def reopen(client, **kw):
    """Sınavı kapatıp yeniden açar: yeni bir sınav oturumu başlar."""
    set_settings(client, exam_open=False)
    return set_settings(client, exam_open=True, **kw)


def sessions(client):
    r = client.get("/api/sessions", headers=TEACHER)
    assert r.status_code == 200
    return r.get_json()["sessions"]


def set_settings(client, **kw):
    r = client.put("/api/settings", json=kw, headers=TEACHER)
    assert r.status_code == 200, r.get_json()
    return r.get_json()


# ---------------------------------------------------------------- sınav akışı
def test_full_exam_flow(client, correct_answers):
    r, d = start(client)
    assert r.status_code == 200
    assert len(d["questions"]) == 10 and d["remaining"] == 900
    assert all("answer" not in q and "solution" not in q for q in d["questions"])

    res = submit(client, d["exam_id"], correct_answers(d["exam_id"])).get_json()
    assert (res["score"], res["correct"], res["wrong"], res["late"]) == (100, 10, 0, False)
    assert res["show_solutions"] and "solution" in res["details"][0]
    assert submit(client, d["exam_id"]).status_code == 409


@pytest.mark.parametrize("unit", ["temel", "donguler", "listeler", "fonksiyonlar", "hatalar", "nesne"])
def test_every_unit_works_end_to_end(client, correct_answers, unit):
    set_settings(client, units=[unit], question_count=5)
    _, d = start(client, no=unit)
    assert len(d["questions"]) == 5
    assert submit(client, d["exam_id"], correct_answers(d["exam_id"])).get_json()["score"] == 100


def test_empty_submission_scores_zero(client):
    _, d = start(client)
    res = submit(client, d["exam_id"]).get_json()
    assert res["score"] == 0 and res["wrong"] == 10


def test_start_validation(client):
    assert client.post("/api/start", json={"name": " ", "no": "1"}).status_code == 400
    assert client.post("/api/start", data="bozuk", content_type="application/json").status_code == 400
    assert submit(client, "yok").status_code == 404


def test_same_student_resumes_instead_of_new_attempt(client):
    _, d1 = start(client)
    client.post("/api/save", json={"exam_id": d1["exam_id"], "answers": {"1": "x"}})
    r, d2 = start(client, name="ayşe yılmaz")  # büyük/küçük harf farkı
    assert r.status_code == 200
    assert d2["exam_id"] == d1["exam_id"] and d2["answers"] == {"1": "x"}
    r, _ = start(client, name="Başka Biri")
    assert r.status_code == 409


def test_resume_endpoint(client):
    _, d = start(client)
    r = client.post("/api/resume", json={"exam_id": d["exam_id"]})
    assert r.status_code == 200 and r.get_json()["exam_id"] == d["exam_id"]
    submit(client, d["exam_id"])
    assert client.post("/api/resume", json={"exam_id": d["exam_id"]}).status_code == 410


def test_answers_are_sanitized(app, client):
    _, d = start(client)
    payload = {"1": "a" * 10_000, "999": "x", "2": True, "3": {"x": 1}, "4": "  "}
    client.post("/api/save", json={"exam_id": d["exam_id"], "answers": payload})
    with sqlite3.connect(app.config["DB_PATH"]) as db:
        saved = json.loads(db.execute("SELECT answers FROM exams").fetchone()[0])
    assert saved == {"1": "a" * 2000}


# ---------------------------------------------------------------- süre
def test_late_submit_uses_last_saved_answers(client, clock_at, correct_answers):
    _, d = start(client)
    assert client.post("/api/save", json={"exam_id": d["exam_id"],
                                          "answers": correct_answers(d["exam_id"])}).status_code == 200
    clock_at.t += 900 + 31  # süre + tolerans aşıldı
    assert client.post("/api/save", json={"exam_id": d["exam_id"], "answers": {}}).status_code == 409
    res = submit(client, d["exam_id"]).get_json()
    assert res["late"] is True and res["score"] == 100  # boş gönderilse bile kayıtlı cevaplar geçerli


def test_submit_within_grace_period_is_on_time(client, clock_at):
    _, d = start(client)
    clock_at.t += 900 + 20
    assert submit(client, d["exam_id"]).get_json()["late"] is False


def test_abandoned_exam_is_auto_finalized(client, clock_at, correct_answers):
    _, d = start(client)
    client.post("/api/save", json={"exam_id": d["exam_id"], "answers": correct_answers(d["exam_id"])})
    clock_at.t += 2000
    rows = client.get("/api/results", headers=TEACHER).get_json()["rows"]
    assert rows[0]["status"] == "bitti" and rows[0]["auto"] is True and rows[0]["score"] == 100
    assert client.post("/api/resume", json={"exam_id": d["exam_id"]}).status_code == 410


def test_duration_change_does_not_affect_running_exam(client, clock_at):
    _, d = start(client)
    set_settings(client, duration_min=1)
    clock_at.t += 300
    r = client.post("/api/save", json={"exam_id": d["exam_id"], "answers": {}})
    assert r.status_code == 200 and r.get_json()["remaining"] == 600


# ---------------------------------------------------------------- ayarlar
def test_closed_exam_blocks_new_students_only(client):
    _, d = start(client, no="1")
    set_settings(client, exam_open=False)
    assert client.get("/api/status").get_json()["open"] is False
    r, _ = start(client, no="2")
    assert r.status_code == 403
    r, d2 = start(client, no="1")  # sınavdaki öğrenci devam edebilir
    assert r.status_code == 200 and d2["exam_id"] == d["exam_id"]


def test_question_count_duration_and_units(client):
    set_settings(client, question_count=25, duration_min=20, units=["metinler", "kosullar"])
    _, d = start(client)
    assert len(d["questions"]) == 25 and d["remaining"] == 1200
    allowed = {t for u in client.get("/api/info", headers=TEACHER).get_json()["units"]
               if u["id"] in ("metinler", "kosullar") for t in u["topics"]}
    assert {q["topic"] for q in d["questions"]} <= allowed


def test_retake_is_per_exam_session(client):
    set_settings(client, title="Sınav 1", allow_retake=False)
    _, d = start(client)
    submit(client, d["exam_id"])
    r, _ = start(client)
    assert r.status_code == 409
    set_settings(client, title="Sınav 1 (düzeltildi)")  # açıkken başlık değişmesi aynı sınavdır
    assert start(client)[0].status_code == 409
    reopen(client)  # yeniden açmak yeni sınav demektir: aynı numara tekrar girebilir
    r, _ = start(client)
    assert r.status_code == 200


def test_retake_allowed_by_default(client):
    _, d = start(client)
    submit(client, d["exam_id"])
    r, _ = start(client)
    assert r.status_code == 200


def test_hide_solutions(client):
    set_settings(client, show_solutions=False)
    _, d = start(client)
    res = submit(client, d["exam_id"]).get_json()
    assert res["show_solutions"] is False
    assert all(set(item) == {"id", "topic", "correct"} for item in res["details"])


def test_settings_defaults_and_title_cleanup(client):
    info = client.get("/api/info", headers=TEACHER).get_json()
    s = info["settings"]
    assert s["units"] == ["temel", "veri_tipleri"] and s["practice_open"] is False and s["title"] == ""
    assert len(info["units"]) >= 11
    assert set_settings(client, title="  9-A   Sınav  1 ")["title"] == "9-A Sınav 1"


@pytest.mark.parametrize("body", [
    {"question_count": 7}, {"question_count": True}, {"duration_min": 0}, {"duration_min": "15"},
    {"duration_min": 500}, {"exam_open": "evet"}, [], {"units": []}, {"units": ["yok"]},
    {"units": ["temel", "yok"]}, {"units": "temel"}, {"title": 5},
])
def test_settings_validation(client, body):
    assert client.put("/api/settings", json=body, headers=TEACHER).status_code == 400


# ---------------------------------------------------------------- sınav oturumları
def test_each_opening_is_a_separate_exam(client, clock_at):
    set_settings(client, title="9-A")
    _, d = start(client, no="1")
    submit(client, d["exam_id"])
    clock_at.t += 3600
    reopen(client)  # aynı başlıkla ikinci açılış
    start(client, no="2")

    newest, oldest = sessions(client)
    assert (newest["title"], oldest["title"]) == ("9-A", "9-A")
    assert newest["open"] is True and oldest["open"] is False
    assert (newest["students"], newest["live"], newest["done"]) == (1, 1, 0)
    assert (oldest["students"], oldest["done"], oldest["average"]) == (1, 1, 0.0)
    assert newest["opened"] and newest["opened_ts"] > oldest["opened_ts"]

    only_old = client.get(f"/api/results?oturum={oldest['id']}", headers=TEACHER).get_json()
    assert [r["no"] for r in only_old["rows"]] == ["1"] and only_old["summary"]["done"] == 1
    everything = client.get("/api/results", headers=TEACHER).get_json()
    assert len(everything["rows"]) == 2


def test_session_opens_lazily_and_closes(client):
    assert sessions(client) == []  # öğrenci girmeden boş sınav görünmez
    set_settings(client, title="Deneme")
    start(client)
    [s] = sessions(client)
    assert s["open"] is True and s["title"] == "Deneme"
    set_settings(client, title="Deneme 2")  # açıkken başlığı değiştirmek açık sınavın adını değiştirir
    assert sessions(client)[0]["title"] == "Deneme 2"
    set_settings(client, exam_open=False)
    assert sessions(client)[0]["open"] is False
    assert start(client, no="99")[0].status_code == 403


def test_attempts_are_counted_per_session(client):
    for _ in range(2):
        _, d = start(client)
        submit(client, d["exam_id"])
    reopen(client)
    _, d = start(client)
    submit(client, d["exam_id"])
    newest = sessions(client)[0]["id"]
    rows = client.get(f"/api/results?oturum={newest}", headers=TEACHER).get_json()["rows"]
    assert [r["attempt"] for r in rows] == [1]


def test_delete_session(client):
    _, d = start(client, no="1")
    submit(client, d["exam_id"])
    reopen(client)
    start(client, no="2")  # açık sınavda süren bir öğrenci
    newest, oldest = sessions(client)

    r = client.delete(f"/api/sessions/{newest['id']}", headers=TEACHER)
    assert r.status_code == 409 and "kapat" in r.get_json()["error"]
    set_settings(client, exam_open=False)  # kapatmak yalnızca yeni girişi durdurur; süren öğrenci hâlâ korunur
    assert client.delete(f"/api/sessions/{newest['id']}", headers=TEACHER).status_code == 409
    r = client.delete(f"/api/sessions/{oldest['id']}", headers=TEACHER)
    assert r.status_code == 200 and r.get_json()["deleted"] == 1
    assert [s["id"] for s in sessions(client)] == [newest["id"]]
    assert client.delete(f"/api/sessions/{oldest['id']}", headers=TEACHER).status_code == 404
    assert client.delete("/api/sessions/abc", headers=TEACHER).status_code == 404


def test_delete_closed_session_with_finished_students(client):
    _, d = start(client)
    submit(client, d["exam_id"])
    [s] = sessions(client)
    assert client.delete(f"/api/sessions/{s['id']}", headers=TEACHER).status_code == 200  # açık ama süren yok
    assert sessions(client) == []
    _, d = start(client)  # sınav hâlâ açık: yeni öğrenci yeni bir oturuma girer
    assert sessions(client)[0]["students"] == 1


def test_delete_everything(client):
    _, d = start(client, no="1")
    submit(client, d["exam_id"])
    reopen(client)
    start(client, no="2")
    r = client.delete("/api/results", headers=TEACHER)
    assert r.status_code == 409  # sınavı süren öğrenci varken hepsi silinemez
    set_settings(client, exam_open=False)
    live = client.get("/api/results", headers=TEACHER).get_json()["rows"][0]
    submit(client, live["id"])
    assert client.delete("/api/results", headers=TEACHER).get_json()["deleted"] == 2
    assert sessions(client) == [] and client.get("/api/results", headers=TEACHER).get_json()["rows"] == []


def test_exam_left_open_overnight_starts_a_new_session(client, clock_at):
    _, d = start(client, no="1")
    submit(client, d["exam_id"])
    clock_at.t += 86400  # öğretmen sınavı kapatmayı unuttu; ertesi gün başka bir sınıf giriyor
    start(client, no="2")
    newest, oldest = sessions(client)
    assert (newest["students"], oldest["students"]) == (1, 1) and oldest["open"] is False


def test_session_filter_validation(client):
    assert client.get("/api/results?oturum=abc", headers=TEACHER).status_code == 400
    assert client.get("/api/results?oturum=999", headers=TEACHER).get_json()["rows"] == []
    assert client.get("/api/sessions").status_code == 401


# ---------------------------------------------------------------- öğretmen
def test_teacher_auth(client):
    assert client.get("/api/results").status_code == 401
    assert client.get("/api/results?sifre=" + KEY).status_code == 401  # URL'de şifre kabul edilmez
    assert client.get("/api/results", headers={"X-Ogretmen-Sifre": "çşğ"}).status_code == 401
    assert client.get("/api/results", headers=TEACHER).status_code == 200


def test_teacher_bruteforce_lockout(client):
    for _ in range(auth.MAX_FAILS):
        assert client.get("/api/info", headers={"X-Ogretmen-Sifre": "0000"}).status_code == 401
    r = client.get("/api/info", headers=TEACHER)
    assert r.status_code == 429 and r.headers["Retry-After"] == str(auth.LOCK_SECONDS)


def test_results_summary_topics_and_detail(client, correct_answers):
    _, d1 = start(client, no="1")
    submit(client, d1["exam_id"], correct_answers(d1["exam_id"]))
    _, d2 = start(client, no="2")
    submit(client, d2["exam_id"])
    start(client, no="3")

    data = client.get("/api/results", headers=TEACHER).get_json()
    assert data["summary"] == {"done": 2, "live": 1, "average": 50.0, "pass_rate": 50}
    assert sum(t["total"] for t in data["topics"]) == 20
    assert sum(t["correct"] for t in data["topics"]) == 10
    rates = [t["rate"] for t in data["topics"]]
    assert rates == sorted(rates)  # en zayıf konu en üstte
    assert all(t["unit"] for t in data["topics"])

    detail = client.get(f"/api/results/{d1['exam_id']}", headers=TEACHER).get_json()
    assert detail["score"] == 100 and all(q["correct"] and q["unit"] for q in detail["details"])
    live_id = data["rows"][0]["id"]
    assert client.get(f"/api/results/{live_id}", headers=TEACHER).status_code == 409


def test_attempt_numbering(client):
    for _ in range(2):
        _, d = start(client)
        submit(client, d["exam_id"])
    rows = client.get("/api/results", headers=TEACHER).get_json()["rows"]
    assert sorted(r["attempt"] for r in rows) == [1, 2]


def test_delete_one_and_clear(client):
    _, d1 = start(client, no="1")
    _, d2 = start(client, no="2")
    assert client.delete(f"/api/results/{d1['exam_id']}", headers=TEACHER).status_code == 200
    assert client.delete(f"/api/results/{d1['exam_id']}", headers=TEACHER).status_code == 404
    assert len(client.get("/api/results", headers=TEACHER).get_json()["rows"]) == 1
    submit(client, d2["exam_id"])
    client.delete("/api/results", headers=TEACHER)
    assert client.get("/api/results", headers=TEACHER).get_json()["rows"] == []


def test_csv_export(client):
    set_settings(client, title="9-A")
    for no, name in (("10", "=HYPERLINK(\"x\")"), ("2", "Çağrı Öz")):
        _, d = start(client, name=name, no=no)
        submit(client, d["exam_id"])
    start(client, name="Sınavda", no="3")  # bitmemiş sınav CSV'ye girmez

    raw = client.get("/api/results.csv", headers=TEACHER).data.decode("utf-8")
    assert raw.startswith("﻿")
    lines = list(csv.reader(io.StringIO(raw[1:]), delimiter=";"))
    assert lines[0][:4] == ["Sınav", "Okul No", "Ad Soyad", "Deneme"]
    assert len(lines) == 3
    assert lines[1][:4] == ["9-A", "2", "Çağrı Öz", "1"]          # sayısal sıralama: 2 < 10
    assert lines[2][1:3] == ["10", "'=HYPERLINK(\"x\")"]           # formül etkisizleştirildi
    sid = sessions(client)[0]["id"]
    same = client.get(f"/api/results.csv?oturum={sid}", headers=TEACHER).data.decode("utf-8")
    assert len(same.strip().splitlines()) == 3
    other = client.get(f"/api/results.csv?oturum={sid + 1}", headers=TEACHER).data.decode("utf-8")
    assert len(other.strip().splitlines()) == 1  # yalnızca başlık satırı


# ---------------------------------------------------------------- pratik modu
def test_practice_is_closed_by_default(client):
    assert client.get("/api/practice/units").status_code == 403
    assert client.post("/api/practice/next", json={"unit": "temel"}).status_code == 403


def test_practice_flow(client, app):
    set_settings(client, practice_open=True)
    assert client.get("/api/status").get_json()["practice_open"] is True
    units = client.get("/api/practice/units").get_json()
    assert units[0]["id"] == "temel"

    r = client.post("/api/practice/next", json={"unit": "listeler"}).get_json()
    assert set(r) == {"token", "unit", "gen", "topic", "has_hint", "question"} and "answer" not in r["question"]
    secret = app.extensions["pytest_pro_practice"].get(r["token"])

    wrong = client.post("/api/practice/check", json={"token": r["token"], "answer": "yanlış cevap"}).get_json()
    assert wrong["correct"] is False and wrong["answer"] == secret["answer"] and wrong["solution"]
    right = client.post("/api/practice/check", json={"token": r["token"], "answer": secret["answer"]}).get_json()
    assert right["correct"] is True

    assert client.post("/api/practice/next", json={"unit": "yok"}).status_code == 404
    assert client.post("/api/practice/check", json={"token": "yok", "answer": "x"}).status_code == 404
    # pratik soruları sınav sonuçlarına yazılmaz
    assert client.get("/api/results", headers=TEACHER).get_json()["rows"] == []


# ---------------------------------------------------------------- genel
def test_pages_and_security_headers(client):
    for path in ("/", "/pratik", "/ogretmen", "/static/css/style.css", "/static/js/common.js",
                 "/static/js/student.js", "/static/js/teacher.js", "/static/js/practice.js", "/static/js/tracer.js",
                 "/static/fonts/atkinson-hyperlegible-next-latin-ext-700-normal.woff2",
                 "/static/fonts/jetbrains-mono-latin-400-normal.woff2", "/static/fonts/fraunces-latin-700-normal.woff2"):
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


# ---------------------------------------------------------------- veritabanı göçleri
def test_new_database_is_at_latest_schema(app):
    with sqlite3.connect(app.config["DB_PATH"]) as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == len(MIGRATIONS)


def test_migrates_v2_database(tmp_path):
    path = tmp_path / "v2.db"
    with sqlite3.connect(path) as db:
        db.execute("""CREATE TABLE exams (id TEXT PRIMARY KEY, no TEXT NOT NULL, name TEXT NOT NULL,
            questions TEXT NOT NULL, answers TEXT, started_at REAL NOT NULL, submitted_at REAL,
            correct INTEGER, wrong INTEGER, score INTEGER)""")
        q = [{"id": 1, "type": "short", "topic": "T", "text": "?", "code": None, "answer": "5", "solution": ""}]
        db.execute("INSERT INTO exams VALUES ('old', '7', 'Eski', ?, ?, 1700000000, 1700000300, 1, 0, 100)",
                   (json.dumps(q), json.dumps({"1": "5"})))
    c = create_app(db_path=str(path), teacher_key=KEY).test_client()
    data = c.get("/api/results", headers=TEACHER).get_json()
    assert data["rows"][0]["score"] == 100 and data["rows"][0]["title"] == ""
    assert data["topics"][0]["rate"] == 100 and data["topics"][0]["unit"] == "Diğer"
    assert c.get("/api/results/old", headers=TEACHER).get_json()["details"][0]["correct"] is True
    with sqlite3.connect(path) as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == len(MIGRATIONS)


def test_old_records_are_grouped_into_sessions(tmp_path):
    """v3.2 veritabanındaki kayıtlar başlık ve güne göre sınav oturumlarına dönüşür."""
    path = tmp_path / "v32.db"
    create_app(db_path=str(path), teacher_key=KEY)
    with sqlite3.connect(path) as db:
        db.execute("PRAGMA user_version = 3")
        db.execute("DROP TABLE IF EXISTS sessions")
        db.execute("DROP INDEX IF EXISTS idx_exams_session")
        db.execute("ALTER TABLE exams DROP COLUMN session_id")
        q = json.dumps([{"id": 1, "type": "short", "topic": "T", "text": "?", "code": None, "answer": "5", "solution": ""}])
        day = 1_800_000_000
        for i, (title, t) in enumerate([("9-A", day), ("9-A", day + 600), ("9-B", day + 60), ("9-A", day + 86400 * 3)]):
            db.execute("INSERT INTO exams (id, no, name, title, questions, answers, started_at, submitted_at, correct,"
                       " wrong, score) VALUES (?, ?, 'X', ?, ?, '{}', ?, ?, 0, 1, 0)", (f"e{i}", str(i), title, q, t, t + 60))
    c = create_app(db_path=str(path), teacher_key=KEY).test_client()
    got = sorted((s["title"], s["students"], s["open"]) for s in sessions(c))
    assert got == [("9-A", 1, False), ("9-A", 2, False), ("9-B", 1, False)]


def test_migration_is_idempotent(tmp_path):
    path = str(tmp_path / "x.db")
    create_app(db_path=path, teacher_key=KEY)
    create_app(db_path=path, teacher_key=KEY)  # ikinci açılışta hata vermemeli


def test_pages_load_trace_component(client):
    for path in ("/", "/pratik", "/ogretmen"):
        html = client.get(path).data.decode("utf-8")
        assert html.index("js/common.js") < html.index("js/tracer.js"), path


@pytest.mark.parametrize("path", ["/api/start", "/api/resume", "/api/save", "/api/submit", "/api/exam/trace",
                                  "/api/practice/next", "/api/practice/hint", "/api/practice/trace",
                                  "/api/practice/check"])
@pytest.mark.parametrize("body", [[1, 2], "metin", 5])
def test_non_object_json_is_rejected_cleanly(client, path, body):
    client.put("/api/settings", json={"practice_open": True}, headers=TEACHER)
    r = client.post(path, json=body)
    assert r.status_code < 500 and r.is_json, (path, body, r.status_code)


def test_results_show_live_progress(client):
    _, d = start(client)
    client.post("/api/save", json={"exam_id": d["exam_id"], "answers": {"1": "x", "2": "y"}})
    row = client.get("/api/results", headers=TEACHER).get_json()["rows"][0]
    assert (row["answered"], row["total"]) == (2, 10)
    submit(client, d["exam_id"])
    row = client.get("/api/results", headers=TEACHER).get_json()["rows"][0]
    assert row["total"] == 10
