import json
import sqlite3

import pytest

from pytest_pro import clock, create_app

KEY = "1234"
TEACHER = {"X-Ogretmen-Sifre": KEY}


@pytest.fixture
def app(tmp_path):
    return create_app(db_path=str(tmp_path / "test.db"), teacher_key=KEY, exam_seconds=900, port=5000)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def clock_at(monkeypatch):
    """Sunucunun saatini kontrol etmeye yarar: clock_at.t += 1000 gibi."""
    class Clock:
        t = 1_800_000_000.0

    monkeypatch.setattr(clock, "now", lambda: Clock.t)
    return Clock


@pytest.fixture
def secrets_of(app):
    """Sınavın cevap anahtarını veritabanından okur (öğrenciye hiç gönderilmez)."""
    def read(exam_id):
        with sqlite3.connect(app.config["DB_PATH"]) as db:
            return json.loads(db.execute("SELECT questions FROM exams WHERE id=?", (exam_id,)).fetchone()[0])
    return read


@pytest.fixture
def correct_answers(secrets_of):
    def build(exam_id):
        out = {}
        for q in secrets_of(exam_id):
            out[str(q["id"])] = q["answer"]
        return out
    return build
