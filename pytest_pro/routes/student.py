"""Öğrenci sınav API'si."""
import json
import uuid

from flask import Blueprint, jsonify, request

from .. import clock, exams
from ..db import get_db
from ..settings import get_settings
from .common import error

bp = Blueprint("student", __name__, url_prefix="/api")


@bp.get("/status")
def status():
    s = get_settings(get_db())
    return jsonify({"open": s["exam_open"], "title": s["title"], "question_count": s["question_count"],
                    "duration_min": s["duration_min"], "practice_open": s["practice_open"]})


@bp.post("/start")
def start():
    data = request.get_json(silent=True) or {}
    name, no = exams.clean(data.get("name"), 60), exams.clean(data.get("no"), 20)
    if not name or not no:
        return error("Ad Soyad ve Okul No zorunludur.", 400)

    db = get_db()
    settings = get_settings(db)
    exams.finalize_expired(db)
    t = clock.now()

    active = db.execute(
        "SELECT * FROM exams WHERE no = ? AND submitted_at IS NULL ORDER BY started_at DESC", (no,)
    ).fetchone()
    if active:
        # Aynı öğrenci (sayfa yenileme, cihaz değişikliği) -> kaldığı yerden devam
        if active["name"].casefold() == name.casefold():
            return jsonify(exams.state(active, t))
        return error("Bu okul numarasıyla devam eden başka bir sınav var. Öğretmenine başvur.", 409)

    if not settings["exam_open"]:
        return error("Sınav şu an kapalı. Öğretmenin sınavı açınca tekrar dene.", 403)
    if not settings["allow_retake"] and db.execute(
            "SELECT 1 FROM exams WHERE no = ? AND title = ?", (no, settings["title"])).fetchone():
        return error("Bu okul numarasıyla sınav zaten tamamlandı. Tekrar giriş kapalı.", 409)

    row = exams.create(db, name, no, settings, t, uuid.uuid4().hex)
    return jsonify(exams.state(row, t))


@bp.post("/resume")
def resume():
    data = request.get_json(silent=True) or {}
    db = get_db()
    row = exams.get(db, data.get("exam_id"))
    if row is None:
        return error("Sınav bulunamadı.", 404)
    if row["submitted_at"] is not None:
        return error("Bu sınav zaten gönderildi.", 410)
    t = clock.now()
    if exams.is_expired(row, t):
        exams.finalize_on_timeout(db, row)
        return error("Süre doldu; sınavın son kaydedilen cevaplarla otomatik gönderildi.", 410)
    return jsonify(exams.state(row, t))


@bp.post("/save")
def save():
    """Cevapların ara kaydı: tarayıcı kapanır veya bağlantı koparsa cevaplar kaybolmaz."""
    data = request.get_json(silent=True) or {}
    db = get_db()
    row = exams.get(db, data.get("exam_id"))
    if row is None:
        return error("Sınav bulunamadı.", 404)
    if row["submitted_at"] is not None:
        return error("Bu sınav zaten gönderildi.", 409)
    t = clock.now()
    if exams.is_expired(row, t):
        return error("Süre doldu.", 409)
    answers = exams.sanitize_answers(data.get("answers"), json.loads(row["questions"]))
    db.execute("UPDATE exams SET answers=?, saved_at=? WHERE id=? AND submitted_at IS NULL",
               (json.dumps(answers, ensure_ascii=False), t, row["id"]))
    db.commit()
    return jsonify({"ok": True, "remaining": int(exams.remaining(row, t))})


@bp.post("/submit")
def submit():
    data = request.get_json(silent=True) or {}
    db = get_db()
    row = exams.get(db, data.get("exam_id"))
    if row is None:
        return error("Sınav bulunamadı.", 404)
    if row["submitted_at"] is not None:
        return error("Bu sınav zaten gönderildi.", 409)

    t = clock.now()
    questions = json.loads(row["questions"])
    late = exams.is_expired(row, t)
    if late:
        # Süre aşıldı: gönderilen değil, süre içinde son kaydedilen cevaplar geçerlidir
        answers = json.loads(row["answers"] or "{}")
        submitted_at = row["started_at"] + exams.duration(row)
    else:
        answers = exams.sanitize_answers(data.get("answers"), questions)
        submitted_at = t
    if not exams.finalize(db, row, answers, submitted_at, auto=late):
        return error("Bu sınav zaten gönderildi.", 409)

    row = exams.get(db, row["id"])
    show = get_settings(db)["show_solutions"]
    details = []
    for q, res in zip(questions, json.loads(row["results"])):
        item = {"id": q["id"], "topic": q["topic"], "correct": res["correct"]}
        if show:
            item.update({"type": q["type"], "text": q["text"], "code": q.get("code"),
                         "user_answer": answers.get(str(q["id"]), ""), "answer": q["answer"],
                         "note": res["note"], "solution": q["solution"]})
        details.append(item)
    return jsonify({"correct": row["correct"], "wrong": row["wrong"], "score": row["score"],
                    "late": late, "show_solutions": show, "details": details})
