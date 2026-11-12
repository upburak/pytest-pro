"""Pratik modu öğrenme yardımları: ipucu, kod izi, aynı konudan yeni soru, yanlışın nedeni."""
import random

import pytest
from conftest import TEACHER

from pytest_pro.questions import UNITS


@pytest.fixture
def open_client(client):
    client.put("/api/settings", json={"practice_open": True}, headers=TEACHER)
    return client


def nxt(c, **body):
    return c.post("/api/practice/next", json=body)


def test_hint_and_trace_flow(open_client, app):
    r = nxt(open_client, unit="temel", gen="temel.print_sep").get_json()
    assert r["gen"] == "temel.print_sep" and r["topic"] == "Print Parametreleri (sep)"
    assert "hint" not in r["question"] and "trace" not in r["question"]
    t = open_client.post("/api/practice/trace", json={"token": r["token"]}).get_json()
    assert t["steps"][-1]["output"].rstrip("\n") == app.extensions["pytest_pro_practice"].get(r["token"])["answer"]


def _no_hint_question(monkeypatch):
    """Tüm ünitelerde ipucu olduğu için ipucusuz bir soruyu taklit eder."""
    from pytest_pro import questions as qs
    fake = {"type": "tf", "text": "?", "code": None, "answer": "True", "solution": "s", "whys": {},
            "topic": "T", "unit": "nesne", "gen": "nesne.sahte", "trace": None}
    monkeypatch.setattr(qs, "generate_one", lambda unit, gen=None, avoid=(): dict(fake))


def test_hint_404_when_template_has_no_hint(open_client, monkeypatch):
    _no_hint_question(monkeypatch)
    r = nxt(open_client, unit="nesne").get_json()
    resp = open_client.post("/api/practice/hint", json={"token": r["token"]})
    assert resp.status_code == 404 and resp.is_json and resp.get_json()["error"]


def test_check_returns_why_for_wrong_option(open_client, app):
    r = nxt(open_client, unit="veri_tipleri", gen="veri_tipleri.str_concat").get_json()
    q = app.extensions["pytest_pro_practice"].get(r["token"])
    wrong = next(o for o in q["options"] if o != q["answer"])
    d = open_client.post("/api/practice/check", json={"token": r["token"], "answer": wrong}).get_json()
    assert d["correct"] is False and d["why"] == q["whys"][wrong] and d["has_trace"] is True and d["gen"] == r["gen"]
    ok = open_client.post("/api/practice/check", json={"token": r["token"], "answer": q["answer"]}).get_json()
    assert ok["why"] is None


def test_check_returns_gen_and_has_trace(open_client, app):
    r = nxt(open_client, unit="temel", gen="temel.swap").get_json()
    d = open_client.post("/api/practice/check", json={"token": r["token"], "answer": "x"}).get_json()
    assert d["gen"] == "temel.swap" and d["has_trace"] is True and "why" in d


def test_gen_from_other_unit_is_400(open_client):
    assert nxt(open_client, unit="temel", gen="metinler.indexing").status_code == 400


def test_next_with_everything_avoided_still_returns_question(open_client):
    avoid = [g.name for g in UNITS["operatorler"].generators]
    assert nxt(open_client, unit="operatorler", avoid=avoid).status_code == 200


def test_avoid_is_respected(open_client, monkeypatch):
    monkeypatch.setattr(random, "random", lambda: 0.99)
    names = [g.name for g in UNITS["metinler"].generators]
    for _ in range(20):
        assert nxt(open_client, unit="metinler", avoid=names[1:]).get_json()["gen"] == names[0]


def test_trace_404_for_true_false(open_client):
    r = nxt(open_client, unit="temel", gen="temel.input_type").get_json()
    resp = open_client.post("/api/practice/trace", json={"token": r["token"]})
    assert resp.status_code == 404 and resp.is_json and resp.get_json()["error"]


def test_new_endpoints_closed_when_practice_closed(client):
    for path in ("/api/practice/hint", "/api/practice/trace"):
        assert client.post(path, json={"token": "x"}).status_code == 403


def test_catalog_lists_template_count_per_topic(open_client):
    units = {u["id"]: u for u in open_client.get("/api/practice/units").get_json()}
    counts = units["veri_tipleri"]["topic_templates"]
    assert counts["Metin ve Sayı Birleştirme"] == 2 and sum(counts.values()) == units["veri_tipleri"]["templates"]
    assert set(counts) == set(units["veri_tipleri"]["topics"])


def test_next_reports_has_hint(open_client, monkeypatch):
    assert nxt(open_client, unit="nesne").get_json()["has_hint"] is True
    _no_hint_question(monkeypatch)
    assert nxt(open_client, unit="nesne").get_json()["has_hint"] is False
