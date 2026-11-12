"""Öğretmen API'si (şifreli)."""
import csv
import io
import json
import math
from datetime import datetime

from flask import Blueprint, Response, jsonify, request

from .. import clock, exams, settings
from .. import questions as qs
from ..auth import teacher_required
from ..db import get_db
from ..questions.tracer import trace
from .common import error, student_url

bp = Blueprint("teacher", __name__, url_prefix="/api")


def _title_filter():
    """?sinav=<başlık> verilmişse o sınavın kayıtları, verilmemişse tümü."""
    return request.args.get("sinav") if "sinav" in request.args else None


@bp.get("/info")
@teacher_required
def info():
    return jsonify({"url": student_url(), "settings": settings.get_settings(get_db()),
                    "units": qs.catalog(), "count_choices": list(settings.COUNT_CHOICES)})


@bp.put("/settings")
@teacher_required
def update_settings():
    try:
        updates = settings.validate(request.get_json(silent=True))
    except ValueError as exc:
        return error(str(exc), 400)
    db = get_db()
    settings.save(db, updates)
    return jsonify(settings.get_settings(db))


@bp.get("/qr.svg")
def qr():
    import qrcode
    import qrcode.image.svg
    img = qrcode.make(student_url(), image_factory=qrcode.image.svg.SvgPathImage, box_size=10, border=2)
    buf = io.BytesIO()
    img.save(buf)
    return Response(buf.getvalue(), mimetype="image/svg+xml")


@bp.get("/results")
@teacher_required
def results():
    db = get_db()
    exams.finalize_expired(db)
    title = _title_filter()
    t = clock.now()
    rows = []
    for r, attempt in exams.rows_with_attempts(db, title):
        done = r["submitted_at"] is not None
        rows.append({
            "id": r["id"], "no": r["no"], "name": r["name"], "title": r["title"], "attempt": attempt,
            "started": exams.fmt(r["started_at"], "%d.%m %H:%M:%S"),
            "submitted": exams.fmt(r["submitted_at"], "%H:%M:%S"),
            "correct": r["correct"], "wrong": r["wrong"], "score": r["score"],
            "status": "bitti" if done else "sinavda",
            "auto": bool(r["auto_submitted"]),
            "remaining": None if done else int(exams.remaining(r, t)),
            "answered": len(json.loads(r["answers"] or "{}")),
            "total": len(json.loads(r["questions"])),
        })
    rows.reverse()

    done = [r for r in rows if r["status"] == "bitti"]
    summary = {
        "done": len(done),
        "live": len(rows) - len(done),
        "average": round(sum(r["score"] for r in done) / len(done), 1) if done else None,
        "pass_rate": round(sum(r["score"] >= 50 for r in done) * 100 / len(done)) if done else None,
    }
    titles = [r["title"] for r in db.execute("SELECT DISTINCT title FROM exams ORDER BY title")]
    return jsonify({"rows": rows, "summary": summary, "topics": exams.topic_stats(db, title), "titles": titles})


@bp.get("/results/<exam_id>")
@teacher_required
def result_detail(exam_id):
    db = get_db()
    exams.finalize_expired(db)
    row = exams.get(db, exam_id)
    if row is None:
        return error("Kayıt bulunamadı.", 404)
    if row["submitted_at"] is None:
        return error("Bu öğrencinin sınavı henüz bitmedi.", 409)
    questions = json.loads(row["questions"])
    answers = json.loads(row["answers"] or "{}")
    details = []
    for q, res in zip(questions, exams.results_of(row, questions, answers)):
        details.append({"id": q["id"], "type": q["type"], "unit": qs.unit_title(q.get("unit")), "topic": q["topic"],
                        "text": q["text"], "code": q.get("code"), "user_answer": answers.get(str(q["id"]), ""),
                        "answer": q["answer"], "correct": res["correct"], "note": res["note"],
                        "why": exams.why_of(q, answers.get(str(q["id"]), ""), res["correct"]),
                        "has_trace": bool(qs.trace_source(q))})
    return jsonify({"id": row["id"], "name": row["name"], "no": row["no"], "title": row["title"],
                    "score": row["score"], "correct": row["correct"], "wrong": row["wrong"],
                    "auto": bool(row["auto_submitted"]), "started": exams.fmt(row["started_at"], "%d.%m.%Y %H:%M"),
                    "submitted": exams.fmt(row["submitted_at"], "%H:%M"), "details": details})


@bp.get("/results/<exam_id>/trace/<question_id>")
@teacher_required
def result_trace(exam_id, question_id):
    db = get_db()
    row = exams.get(db, exam_id)
    if row is None:
        return error("Kayıt bulunamadı.", 404)
    if row["submitted_at"] is None:
        return error("Bu öğrencinin sınavı henüz bitmedi.", 409)
    q = exams.question_by_id(row, question_id)
    source = qs.trace_source(q) if q else None
    if not source:
        return error("Bu soru için adım adım izlenecek kod yok.", 404)
    return jsonify(trace(source["code"], source.get("stdin", "")))


@bp.delete("/results/<exam_id>")
@teacher_required
def delete_one(exam_id):
    db = get_db()
    cur = db.execute("DELETE FROM exams WHERE id = ?", (exam_id,))
    db.commit()
    if cur.rowcount == 0:
        return error("Kayıt bulunamadı.", 404)
    return jsonify({"status": "ok"})


@bp.delete("/results")
@teacher_required
def delete_many():
    db = get_db()
    title = _title_filter()
    if title is None:
        cur = db.execute("DELETE FROM exams")
    else:
        cur = db.execute("DELETE FROM exams WHERE title = ?", (title,))
    db.commit()
    return jsonify({"status": "ok", "deleted": cur.rowcount})


def csv_safe(value):
    """Excel'in hücreyi formül olarak çalıştırmasını engeller (CSV enjeksiyonu)."""
    if isinstance(value, str) and value[:1] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + value
    return value


@bp.get("/results.csv")
@teacher_required
def export_csv():
    db = get_db()
    exams.finalize_expired(db)
    rows = [(r, a) for r, a in exams.rows_with_attempts(db, _title_filter()) if r["submitted_at"] is not None]
    rows.sort(key=lambda ra: (ra[0]["title"], int(ra[0]["no"]) if ra[0]["no"].isdigit() else math.inf,
                              ra[0]["no"], ra[1]))

    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";")  # Türkçe Excel ; ayırıcı kullanır
    w.writerow(["Sınav", "Okul No", "Ad Soyad", "Deneme", "Başlama", "Bitiş", "Süre (dk)",
                "Doğru", "Yanlış", "Puan", "Gönderim"])
    for r, attempt in rows:
        minutes = f"{(r['submitted_at'] - r['started_at']) / 60:.1f}".replace(".", ",")
        w.writerow([
            csv_safe(r["title"]), csv_safe(r["no"]), csv_safe(r["name"]), attempt,
            exams.fmt(r["started_at"], "%d.%m.%Y %H:%M"), exams.fmt(r["submitted_at"], "%H:%M"), minutes,
            r["correct"], r["wrong"], r["score"], "Otomatik" if r["auto_submitted"] else "Öğrenci",
        ])
    data = "﻿" + buf.getvalue()  # BOM: Excel'de Türkçe karakterler bozulmaz
    fname = f"python_sinav_{datetime.now():%Y%m%d_%H%M}.csv"
    return Response(data.encode("utf-8"), mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment; filename={fname}"})
