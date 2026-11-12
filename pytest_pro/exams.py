"""Sınav iş mantığı: süre, cevap temizleme, puanlama ve kapanış."""
import json
from datetime import datetime

from flask import current_app

from . import clock
from . import questions as qs

GRACE_SECONDS = 30  # ağ gecikmesi toleransı


def clean(s, n):
    return " ".join(str(s or "").split())[:n]


def fmt(ts, pattern):
    return datetime.fromtimestamp(ts).strftime(pattern) if ts else None


def duration(row):
    return row["duration"] or current_app.config["EXAM_SECONDS"]


def remaining(row, t):
    return max(0, row["started_at"] + duration(row) - t)


def is_expired(row, t):
    return t > row["started_at"] + duration(row) + GRACE_SECONDS


def get(db, exam_id):
    return db.execute("SELECT * FROM exams WHERE id = ?", (str(exam_id or ""),)).fetchone()


def sanitize_answers(raw, questions):
    """Yalnızca bu sınavın soru numaralarını ve makul uzunlukta metinleri kabul eder."""
    if not isinstance(raw, dict):
        return {}
    ids = {str(q["id"]) for q in questions}
    out = {}
    for k, v in raw.items():
        k = str(k)
        if k in ids and isinstance(v, (str, int, float)) and not isinstance(v, bool):
            v = str(v)[:qs.MAX_CODE_LEN]
            if v.strip():
                out[k] = v
    return out


def results_of(row, questions, answers):
    """Kayıtlı puanlama sonuçları (eski kayıtlarda yeniden hesaplanır)."""
    if row["results"]:
        return json.loads(row["results"])
    return [dict(zip(("correct", "note"), qs.grade(q, answers.get(str(q["id"]), "")))) for q in questions]


def finalize(db, row, answers, submitted_at, auto):
    """Sınavı puanlayıp kapatır. Başka bir istek önce kapattıysa False döner."""
    questions = json.loads(row["questions"])
    results = []
    for q in questions:
        ok, note = qs.grade(q, answers.get(str(q["id"]), ""))
        results.append({"correct": bool(ok), "note": note})
    total = len(questions)
    correct = sum(r["correct"] for r in results)
    score = round(correct * 100 / total) if total else 0
    cur = db.execute(
        "UPDATE exams SET answers=?, results=?, submitted_at=?, correct=?, wrong=?, score=?, auto_submitted=? "
        "WHERE id=? AND submitted_at IS NULL",
        (json.dumps(answers, ensure_ascii=False), json.dumps(results, ensure_ascii=False),
         submitted_at, correct, total - correct, score, int(auto), row["id"]),
    )
    db.commit()
    return cur.rowcount == 1


def finalize_on_timeout(db, row):
    return finalize(db, row, json.loads(row["answers"] or "{}"), row["started_at"] + duration(row), auto=True)


def finalize_expired(db):
    """Süresi dolduğu hâlde gönderilmemiş sınavları son kaydedilen cevaplarla kapatır."""
    t = clock.now()
    for row in db.execute("SELECT * FROM exams WHERE submitted_at IS NULL").fetchall():
        if is_expired(row, t):
            finalize_on_timeout(db, row)


def state(row, t):
    """Öğrenciye giden sınav durumu (cevap anahtarı içermez)."""
    return {
        "exam_id": row["id"],
        "name": row["name"],
        "no": row["no"],
        "title": row["title"],
        "remaining": int(remaining(row, t)),
        "questions": [qs.public_question(q) for q in json.loads(row["questions"])],
        "answers": json.loads(row["answers"] or "{}"),
    }


def create(db, name, no, settings, t, exam_id):
    questions = qs.generate_questions(settings["question_count"], settings["units"])
    db.execute(
        "INSERT INTO exams (id, no, name, title, questions, answers, started_at, duration) VALUES (?,?,?,?,?,?,?,?)",
        (exam_id, no, name, settings["title"], json.dumps(questions, ensure_ascii=False), "{}", t,
         settings["duration_min"] * 60),
    )
    db.commit()
    return get(db, exam_id)


def rows_with_attempts(db, title=None):
    """Tüm kayıtlar + her okul numarasının kaçıncı denemesi olduğu (başlangıç sırasına göre)."""
    rows = db.execute(
        "SELECT id, no, name, title, started_at, duration, submitted_at, correct, wrong, score, auto_submitted "
        "FROM exams ORDER BY started_at, rowid"
    ).fetchall()
    counts, out = {}, []
    for r in rows:
        key = (r["title"], r["no"])
        counts[key] = counts.get(key, 0) + 1
        if title is None or r["title"] == title:
            out.append((r, counts[key]))
    return out


def why_of(question, answer, correct):
    """Sınav sonucunda gösterilecek 'neden yanlış' açıklaması (doğru ve kod sorularında yok)."""
    if correct or question["type"] == "code":
        return None
    return qs.why_for(question, answer)


def question_by_id(row, question_id):
    """Sınav kaydındaki soru; numara geçersizse veya yoksa None."""
    try:
        qid = int(question_id)
    except (TypeError, ValueError):
        return None
    return next((q for q in json.loads(row["questions"]) if q["id"] == qid), None)


def topic_stats(db, title=None):
    """Tamamlanan sınavlarda ünite/konu bazında doğru oranı; en zayıf konu önce."""
    sql = "SELECT questions, answers, results FROM exams WHERE submitted_at IS NOT NULL"
    params = ()
    if title is not None:
        sql += " AND title = ?"
        params = (title,)
    stats = {}
    wrongs = {}  # konu -> {normalleştirilmiş cevap: [adet, gösterilen cevap, açıklama]}
    for r in db.execute(sql, params):
        questions = json.loads(r["questions"])
        answers = json.loads(r["answers"] or "{}")
        for q, res in zip(questions, results_of(r, questions, answers)):
            key = (qs.unit_title(q.get("unit")), q["topic"])
            s = stats.setdefault(key, [0, 0])
            s[0] += bool(res["correct"])
            s[1] += 1
            answer = answers.get(str(q["id"]), "")
            if res["correct"] or q["type"] not in ("mc", "short") or not str(answer).strip():
                continue
            norm = qs._norm_short(answer) if q["type"] == "short" else answer
            w = wrongs.setdefault(key, {}).setdefault(norm, [0, answer, qs.why_for(q, answer)])
            w[0] += 1

    def common(key, total):
        if key not in wrongs:
            return None
        count, shown, why = max(wrongs[key].values(), key=lambda w: w[0])
        return {"answer": shown, "share": round(count * 100 / total), "why": why}

    items = [{"unit": u, "topic": t, "correct": c, "total": n, "rate": round(c * 100 / n),
              "common_wrong": common((u, t), n)}
             for (u, t), (c, n) in stats.items()]
    return sorted(items, key=lambda x: (x["rate"], x["unit"], x["topic"]))
