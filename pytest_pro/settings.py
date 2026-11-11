"""Öğretmen panelinden değiştirilen ayarlar (veritabanında saklanır)."""
import json

from flask import current_app

from . import questions as qs

COUNT_CHOICES = (5, 10, 15, 20, 25, 30)
BOOL_KEYS = ("exam_open", "show_solutions", "allow_retake", "practice_open")
MAX_TITLE = 80


def default_settings(exam_seconds):
    return {
        "exam_open": True,
        "title": "",
        "units": list(qs.DEFAULT_UNITS),
        "question_count": 10,
        "duration_min": max(1, round(exam_seconds / 60)),
        "show_solutions": True,
        "allow_retake": True,
        "practice_open": False,
    }


def get_settings(db):
    s = dict(current_app.config["DEFAULT_SETTINGS"])
    for r in db.execute("SELECT key, value FROM settings"):
        if r["key"] in s:
            s[r["key"]] = json.loads(r["value"])
    s["units"] = qs.valid_unit_ids(s["units"]) or list(qs.DEFAULT_UNITS)
    return s


def validate(data):
    """Gelen ayarları doğrular; hatada Türkçe mesajla ValueError fırlatır."""
    if not isinstance(data, dict):
        raise ValueError("Geçersiz istek.")
    out = {}
    for key in BOOL_KEYS:
        if key in data:
            if not isinstance(data[key], bool):
                raise ValueError(f"{key} true/false olmalı.")
            out[key] = data[key]
    if "question_count" in data:
        c = data["question_count"]
        if isinstance(c, bool) or c not in COUNT_CHOICES:
            raise ValueError("Soru sayısı " + ", ".join(map(str, COUNT_CHOICES)) + " olabilir.")
        out["question_count"] = c
    if "duration_min" in data:
        d = data["duration_min"]
        if isinstance(d, bool) or not isinstance(d, int) or not 1 <= d <= 180:
            raise ValueError("Süre 1-180 dakika arasında bir tam sayı olmalı.")
        out["duration_min"] = d
    if "title" in data:
        if not isinstance(data["title"], str):
            raise ValueError("Sınav başlığı metin olmalı.")
        out["title"] = " ".join(data["title"].split())[:MAX_TITLE]
    if "units" in data:
        units = data["units"]
        if not isinstance(units, list) or not all(isinstance(u, str) for u in units):
            raise ValueError("Üniteler liste olmalı.")
        valid = qs.valid_unit_ids(units)
        if not valid or len(valid) != len(set(units)):
            raise ValueError("En az bir geçerli ünite seçilmeli.")
        out["units"] = valid
    return out


def save(db, updates):
    for key, value in updates.items():
        db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, json.dumps(value)))
    db.commit()
