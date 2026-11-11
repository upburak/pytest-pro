import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import server  # noqa: E402

KEY = "1234"
TEACHER = {"X-Ogretmen-Sifre": KEY}


@pytest.fixture
def app(tmp_path):
    return server.create_app(db_path=str(tmp_path / "test.db"), teacher_key=KEY, exam_seconds=900, port=5000)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def clock(monkeypatch):
    """Sunucunun saatini kontrol etmeye yarar: clock.t += 1000 gibi."""
    class Clock:
        t = 1_800_000_000.0

    monkeypatch.setattr(server, "now", lambda: Clock.t)
    return Clock
