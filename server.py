"""
PyTest Pro - Python Giriş Dinamik Ölçme ve Değerlendirme Sistemi

Çalıştırma : python server.py
Öğrenciler : http://<IP>:5000
Öğretmen   : http://<IP>:5000/ogretmen   (şifre konsolda yazar)
"""
import csv
import io
import json
import math
import os
import secrets
import socket
import sqlite3
import threading
import time
import uuid
from contextlib import closing
from datetime import datetime
from functools import wraps

from flask import Blueprint, Flask, Response, current_app, g, jsonify, render_template, request

import questions as qs

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GRACE_SECONDS = 30            # ağ gecikmesi toleransı
MAX_FAILS, LOCK_SECONDS = 10, 60  # öğretmen şifresi: 10 hatalı denemede 60 sn kilit
COUNT_CHOICES = (5, 10, 15, 20)
BOOL_SETTINGS = ("exam_open", "show_solutions", "allow_retake")

bp = Blueprint("pytest_pro", __name__)


def now():
    return time.time()


def _env_int(name, default, lo, hi):
    try:
        value = int(os.environ.get(name, default))
    except ValueError:
        return default
    return min(max(value, lo), hi)


# ======================================================================
# Veritabanı
# ======================================================================
def connect(path):
    db = sqlite3.connect(path, timeout=10)
    db.row_factory = sqlite3.Row
    return db


def get_db():
    if "db" not in g:
        g.db = connect(current_app.config["DB_PATH"])
    return g.db


@bp.teardown_app_request
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(path, default_settings):
    with closing(connect(path)) as db:
        db.execute("PRAGMA journal_mode=WAL")  # eşzamanlı okuma/yazma için
        db.execute(
            """CREATE TABLE IF NOT EXISTS exams (
                id TEXT PRIMARY KEY,
                no TEXT NOT NULL,
                name TEXT NOT NULL,
                questions TEXT NOT NULL,
                answers TEXT,
                started_at REAL NOT NULL,
                submitted_at REAL,
                correct INTEGER,
                wrong INTEGER,
                score INTEGER
            )"""
        )
        db.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        # v2 veritabanlarını yerinde güncelle
        cols = {r["name"] for r in db.execute("PRAGMA table_info(exams)")}
        for col, ddl in (("duration", "INTEGER"), ("results", "TEXT"), ("saved_at", "REAL"),
                         ("auto_submitted", "INTEGER NOT NULL DEFAULT 0")):
            if col not in cols:
                db.execute(f"ALTER TABLE exams ADD COLUMN {col} {ddl}")
        db.execute("CREATE INDEX IF NOT EXISTS idx_exams_no ON exams(no)")
        for key, value in default_settings.items():
            db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, json.dumps(value)))
        db.commit()


# ======================================================================
# Ayarlar (öğretmen panelinden değiştirilir, veritabanında saklanır)
# ======================================================================
def get_settings(db):
    s = dict(current_app.config["DEFAULT_SETTINGS"])
    for r in db.execute("SELECT key, value FROM settings"):
        if r["key"] in s:
            s[r["key"]] = json.loads(r["value"])
    return s


def validate_settings(data):
    if not isinstance(data, dict):
        raise ValueError("Geçersiz istek.")
    out = {}
    for key in BOOL_SETTINGS:
        if key in data:
            if not isinstance(data[key], bool):
                raise ValueError(f"{key} true/false olmalı.")
            out[key] = data[key]
    if "question_count" in data:
        if data["question_count"] not in COUNT_CHOICES or isinstance(data["question_count"], bool):
            raise ValueError("Soru sayısı 5, 10, 15 veya 20 olmalı.")
        out["question_count"] = data["question_count"]
    if "duration_min" in data:
        d = data["duration_min"]
        if isinstance(d, bool) or not isinstance(d, int) or not 1 <= d <= 180:
            raise ValueError("Süre 1-180 dakika arasında bir tam sayı olmalı.")
        out["duration_min"] = d
    return out


# ======================================================================
# Sınav yardımcıları
# ======================================================================
def clean(s, n):
    return " ".join(str(s or "").split())[:n]


def exam_duration(row):
    return row["duration"] or current_app.config["EXAM_SECONDS"]


def remaining(row, t):
    return max(0, row["started_at"] + exam_duration(row) - t)


def is_expired(row, t):
    return t > row["started_at"] + exam_duration(row) + GRACE_SECONDS


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


def row_results(row, questions, answers):
    """Kayıtlı puanlama sonuçları (eski v2 kayıtlarında yeniden hesaplanır)."""
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


def finalize_expired(db):
    """Süresi dolduğu hâlde gönderilmemiş sınavları son kaydedilen cevaplarla kapatır."""
    t = now()
    for row in db.execute("SELECT * FROM exams WHERE submitted_at IS NULL").fetchall():
        if is_expired(row, t):
            finalize(db, row, json.loads(row["answers"] or "{}"),
                     row["started_at"] + exam_duration(row), auto=True)


def exam_state(row, t):
    return {
        "exam_id": row["id"],
        "name": row["name"],
        "no": row["no"],
        "remaining": int(remaining(row, t)),
        "questions": [qs.public_question(q) for q in json.loads(row["questions"])],
        "answers": json.loads(row["answers"] or "{}"),
    }


def get_exam(db, exam_id):
    return db.execute("SELECT * FROM exams WHERE id = ?", (str(exam_id or ""),)).fetchone()


def error(message, status):
    return jsonify({"error": message}), status


def _fmt(ts, fmt):
    return datetime.fromtimestamp(ts).strftime(fmt) if ts else None


def rows_with_attempts(db):
    rows = db.execute(
        "SELECT id, no, name, started_at, duration, submitted_at, correct, wrong, score, auto_submitted "
        "FROM exams ORDER BY started_at, rowid"
    ).fetchall()
    counts, out = {}, []
    for r in rows:
        counts[r["no"]] = counts.get(r["no"], 0) + 1
        out.append((r, counts[r["no"]]))
    return out


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))  # paket gönderilmez, internet gerekmez
        ip = s.getsockname()[0]
    except OSError:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def student_url():
    return f"http://{get_local_ip()}:{current_app.config['PORT']}"


# ======================================================================
# Öğretmen kimlik doğrulama + kaba kuvvet koruması
# ======================================================================
class LoginLimiter:
    def __init__(self):
        self._lock = threading.Lock()
        self._fails = {}  # ip -> (hata sayısı, kilit bitişi)

    def locked(self, ip):
        with self._lock:
            _, until = self._fails.get(ip, (0, 0))
            return until > now()

    def fail(self, ip):
        with self._lock:
            count, _ = self._fails.get(ip, (0, 0))
            count += 1
            if count >= MAX_FAILS:
                self._fails[ip] = (0, now() + LOCK_SECONDS)
            else:
                self._fails[ip] = (count, 0)

    def reset(self, ip):
        with self._lock:
            self._fails.pop(ip, None)


def teacher_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        ip = request.remote_addr or "?"
        limiter = current_app.extensions["pytest_pro_limiter"]
        if limiter.locked(ip):
            resp = jsonify({"error": "Çok fazla hatalı deneme. 1 dakika sonra tekrar dene."})
            resp.headers["Retry-After"] = str(LOCK_SECONDS)
            return resp, 429
        key = request.headers.get("X-Ogretmen-Sifre", "")
        if not secrets.compare_digest(key.encode("utf-8"), current_app.config["TEACHER_KEY"].encode("utf-8")):
            limiter.fail(ip)
            return error("Yetkisiz. Öğretmen şifresi hatalı.", 401)
        limiter.reset(ip)
        return f(*args, **kwargs)
    return wrapper


# ======================================================================
# Sayfalar
# ======================================================================
@bp.route("/")
def student_page():
    return render_template("index.html")


@bp.route("/ogretmen")
def teacher_page():
    return render_template("teacher.html")


# ======================================================================
# Öğrenci API
# ======================================================================
@bp.get("/api/status")
def api_status():
    s = get_settings(get_db())
    return jsonify({"open": s["exam_open"], "question_count": s["question_count"],
                    "duration_min": s["duration_min"]})


@bp.post("/api/start")
def api_start():
    data = request.get_json(silent=True) or {}
    name, no = clean(data.get("name"), 60), clean(data.get("no"), 20)
    if not name or not no:
        return error("Ad Soyad ve Okul No zorunludur.", 400)

    db = get_db()
    settings = get_settings(db)
    finalize_expired(db)
    t = now()

    active = db.execute(
        "SELECT * FROM exams WHERE no = ? AND submitted_at IS NULL ORDER BY started_at DESC", (no,)
    ).fetchone()
    if active:
        # Aynı öğrenci (sayfa yenileme, cihaz değişikliği) -> kaldığı yerden devam
        if active["name"].casefold() == name.casefold():
            return jsonify(exam_state(active, t))
        return error("Bu okul numarasıyla devam eden başka bir sınav var. Öğretmenine başvur.", 409)

    if not settings["exam_open"]:
        return error("Sınav şu an kapalı. Öğretmenin sınavı açınca tekrar dene.", 403)
    if not settings["allow_retake"] and db.execute("SELECT 1 FROM exams WHERE no = ?", (no,)).fetchone():
        return error("Bu okul numarasıyla sınav zaten tamamlandı. Tekrar giriş kapalı.", 409)

    exam_id = uuid.uuid4().hex
    questions = qs.generate_questions(settings["question_count"])
    db.execute(
        "INSERT INTO exams (id, no, name, questions, answers, started_at, duration) VALUES (?,?,?,?,?,?,?)",
        (exam_id, no, name, json.dumps(questions, ensure_ascii=False), "{}", t, settings["duration_min"] * 60),
    )
    db.commit()
    return jsonify(exam_state(get_exam(db, exam_id), t))


@bp.post("/api/resume")
def api_resume():
    data = request.get_json(silent=True) or {}
    db = get_db()
    row = get_exam(db, data.get("exam_id"))
    if row is None:
        return error("Sınav bulunamadı.", 404)
    if row["submitted_at"] is not None:
        return error("Bu sınav zaten gönderildi.", 410)
    t = now()
    if is_expired(row, t):
        finalize(db, row, json.loads(row["answers"] or "{}"), row["started_at"] + exam_duration(row), auto=True)
        return error("Süre doldu; sınavın son kaydedilen cevaplarla otomatik gönderildi.", 410)
    return jsonify(exam_state(row, t))


@bp.post("/api/save")
def api_save():
    """Cevapların ara kaydı: tarayıcı kapanır veya bağlantı koparsa cevaplar kaybolmaz."""
    data = request.get_json(silent=True) or {}
    db = get_db()
    row = get_exam(db, data.get("exam_id"))
    if row is None:
        return error("Sınav bulunamadı.", 404)
    if row["submitted_at"] is not None:
        return error("Bu sınav zaten gönderildi.", 409)
    t = now()
    if is_expired(row, t):
        return error("Süre doldu.", 409)
    answers = sanitize_answers(data.get("answers"), json.loads(row["questions"]))
    db.execute("UPDATE exams SET answers=?, saved_at=? WHERE id=? AND submitted_at IS NULL",
               (json.dumps(answers, ensure_ascii=False), t, row["id"]))
    db.commit()
    return jsonify({"ok": True, "remaining": int(remaining(row, t))})


@bp.post("/api/submit")
def api_submit():
    data = request.get_json(silent=True) or {}
    db = get_db()
    row = get_exam(db, data.get("exam_id"))
    if row is None:
        return error("Sınav bulunamadı.", 404)
    if row["submitted_at"] is not None:
        return error("Bu sınav zaten gönderildi.", 409)

    t = now()
    questions = json.loads(row["questions"])
    late = is_expired(row, t)
    if late:
        # Süre aşıldı: gönderilen değil, süre içinde son kaydedilen cevaplar geçerlidir
        answers = json.loads(row["answers"] or "{}")
        submitted_at = row["started_at"] + exam_duration(row)
    else:
        answers = sanitize_answers(data.get("answers"), questions)
        submitted_at = t
    if not finalize(db, row, answers, submitted_at, auto=late):
        return error("Bu sınav zaten gönderildi.", 409)

    row = get_exam(db, row["id"])
    show = get_settings(db)["show_solutions"]
    results = json.loads(row["results"])
    details = []
    for q, res in zip(questions, results):
        item = {"id": q["id"], "topic": q["topic"], "correct": res["correct"]}
        if show:
            item.update({"type": q["type"], "text": q["text"], "code": q.get("code"),
                         "user_answer": answers.get(str(q["id"]), ""), "answer": q["answer"],
                         "note": res["note"], "solution": q["solution"]})
        details.append(item)
    return jsonify({"correct": row["correct"], "wrong": row["wrong"], "score": row["score"],
                    "late": late, "show_solutions": show, "details": details})


# ======================================================================
# Öğretmen API (şifreli)
# ======================================================================
@bp.get("/api/info")
@teacher_required
def api_info():
    return jsonify({"url": student_url(), "settings": get_settings(get_db())})


@bp.put("/api/settings")
@teacher_required
def api_settings():
    try:
        updates = validate_settings(request.get_json(silent=True))
    except ValueError as exc:
        return error(str(exc), 400)
    db = get_db()
    for key, value in updates.items():
        db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, json.dumps(value)))
    db.commit()
    return jsonify(get_settings(db))


@bp.get("/api/qr.svg")
def api_qr():
    import qrcode
    import qrcode.image.svg
    img = qrcode.make(student_url(), image_factory=qrcode.image.svg.SvgPathImage, box_size=10, border=2)
    buf = io.BytesIO()
    img.save(buf)
    return Response(buf.getvalue(), mimetype="image/svg+xml")


@bp.get("/api/results")
@teacher_required
def api_results():
    db = get_db()
    finalize_expired(db)
    t = now()
    rows = []
    for r, attempt in rows_with_attempts(db):
        done = r["submitted_at"] is not None
        rows.append({
            "id": r["id"], "no": r["no"], "name": r["name"], "attempt": attempt,
            "started": _fmt(r["started_at"], "%d.%m %H:%M:%S"),
            "submitted": _fmt(r["submitted_at"], "%H:%M:%S"),
            "correct": r["correct"], "wrong": r["wrong"], "score": r["score"],
            "status": "bitti" if done else "sinavda",
            "auto": bool(r["auto_submitted"]),
            "remaining": None if done else int(remaining(r, t)),
        })
    rows.reverse()

    done = [r for r in rows if r["status"] == "bitti"]
    summary = {
        "done": len(done),
        "live": len(rows) - len(done),
        "average": round(sum(r["score"] for r in done) / len(done), 1) if done else None,
        "pass_rate": round(sum(r["score"] >= 50 for r in done) * 100 / len(done)) if done else None,
    }

    topics = {}
    for r in db.execute("SELECT questions, answers, results FROM exams WHERE submitted_at IS NOT NULL"):
        questions = json.loads(r["questions"])
        for q, res in zip(questions, row_results(r, questions, json.loads(r["answers"] or "{}"))):
            stat = topics.setdefault(q["topic"], [0, 0])
            stat[0] += bool(res["correct"])
            stat[1] += 1
    topic_list = sorted(
        ({"topic": k, "correct": c, "total": n, "rate": round(c * 100 / n)} for k, (c, n) in topics.items()),
        key=lambda x: (x["rate"], x["topic"]),
    )
    return jsonify({"rows": rows, "summary": summary, "topics": topic_list})


@bp.get("/api/results/<exam_id>")
@teacher_required
def api_result_detail(exam_id):
    db = get_db()
    finalize_expired(db)
    row = get_exam(db, exam_id)
    if row is None:
        return error("Kayıt bulunamadı.", 404)
    if row["submitted_at"] is None:
        return error("Bu öğrencinin sınavı henüz bitmedi.", 409)
    questions = json.loads(row["questions"])
    answers = json.loads(row["answers"] or "{}")
    details = []
    for q, res in zip(questions, row_results(row, questions, answers)):
        details.append({"id": q["id"], "type": q["type"], "topic": q["topic"], "text": q["text"],
                        "code": q.get("code"), "user_answer": answers.get(str(q["id"]), ""),
                        "answer": q["answer"], "correct": res["correct"], "note": res["note"]})
    return jsonify({"id": row["id"], "name": row["name"], "no": row["no"], "score": row["score"],
                    "correct": row["correct"], "wrong": row["wrong"], "auto": bool(row["auto_submitted"]),
                    "started": _fmt(row["started_at"], "%d.%m.%Y %H:%M"),
                    "submitted": _fmt(row["submitted_at"], "%H:%M"), "details": details})


@bp.delete("/api/results/<exam_id>")
@teacher_required
def api_delete_one(exam_id):
    db = get_db()
    cur = db.execute("DELETE FROM exams WHERE id = ?", (exam_id,))
    db.commit()
    if cur.rowcount == 0:
        return error("Kayıt bulunamadı.", 404)
    return jsonify({"status": "ok"})


@bp.delete("/api/results")
@teacher_required
def api_clear():
    db = get_db()
    db.execute("DELETE FROM exams")
    db.commit()
    return jsonify({"status": "ok"})


def csv_safe(value):
    """Excel'in hücreyi formül olarak çalıştırmasını engeller (CSV enjeksiyonu)."""
    if isinstance(value, str) and value[:1] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + value
    return value


@bp.get("/api/results.csv")
@teacher_required
def api_csv():
    db = get_db()
    finalize_expired(db)
    rows = [(r, a) for r, a in rows_with_attempts(db) if r["submitted_at"] is not None]
    rows.sort(key=lambda ra: (int(ra[0]["no"]) if ra[0]["no"].isdigit() else math.inf, ra[0]["no"], ra[1]))

    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";")  # Türkçe Excel ; ayırıcı kullanır
    w.writerow(["Okul No", "Ad Soyad", "Deneme", "Başlama", "Bitiş", "Süre (dk)",
                "Doğru", "Yanlış", "Puan", "Gönderim"])
    for r, attempt in rows:
        minutes = f"{(r['submitted_at'] - r['started_at']) / 60:.1f}".replace(".", ",")
        w.writerow([
            csv_safe(r["no"]), csv_safe(r["name"]), attempt,
            _fmt(r["started_at"], "%d.%m.%Y %H:%M"), _fmt(r["submitted_at"], "%H:%M"), minutes,
            r["correct"], r["wrong"], r["score"], "Otomatik" if r["auto_submitted"] else "Öğrenci",
        ])
    data = "\ufeff" + buf.getvalue()  # BOM: Excel'de Türkçe karakterler bozulmaz
    fname = f"python_sinav_{datetime.now():%Y%m%d_%H%M}.csv"
    return Response(data.encode("utf-8"), mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment; filename={fname}"})


# ======================================================================
# Uygulama
# ======================================================================
CSP = ("default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; "
       "connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'")


def security_headers(resp):
    resp.headers.setdefault("Content-Security-Policy", CSP)
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("X-Frame-Options", "DENY")
    resp.headers.setdefault("Referrer-Policy", "no-referrer")
    if request.path.startswith("/api/"):
        resp.headers.setdefault("Cache-Control", "no-store")
    return resp


def create_app(db_path=None, teacher_key=None, exam_seconds=None, port=None):
    app = Flask(__name__)
    exam_seconds = exam_seconds or _env_int("PYTEST_SURE", 900, 60, 10800)
    app.config.update(
        DB_PATH=db_path or os.environ.get("PYTEST_DB") or os.path.join(BASE_DIR, "results.db"),
        TEACHER_KEY=teacher_key or os.environ.get("PYTEST_SIFRE") or f"{secrets.randbelow(900000) + 100000}",
        EXAM_SECONDS=exam_seconds,
        PORT=port or _env_int("PYTEST_PORT", 5000, 1, 65535),
        MAX_CONTENT_LENGTH=256 * 1024,
        DEFAULT_SETTINGS={
            "exam_open": True,
            "question_count": 10,
            "duration_min": max(1, round(exam_seconds / 60)),
            "show_solutions": True,
            "allow_retake": True,
        },
    )
    app.json.ensure_ascii = False
    app.extensions["pytest_pro_limiter"] = LoginLimiter()
    init_db(app.config["DB_PATH"], app.config["DEFAULT_SETTINGS"])
    app.register_blueprint(bp)
    app.after_request(security_headers)
    return app


def main():
    app = create_app()
    ip, port = get_local_ip(), app.config["PORT"]
    print("\n" + "=" * 56)
    print("  PYTEST PRO - ÖĞRETMEN SUNUCUSU AKTİF")
    print(f"  Öğrenci adresi  : http://{ip}:{port}")
    print(f"  Öğretmen paneli : http://{ip}:{port}/ogretmen")
    print(f"  Öğretmen şifresi: {app.config['TEACHER_KEY']}")
    print("  Kapatmak için    : Ctrl+C")
    print("=" * 56 + "\n")
    try:
        try:
            from waitress import serve
        except ImportError:
            app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
        else:
            serve(app, host="0.0.0.0", port=port, threads=16)
    except OSError as exc:
        print(f"Sunucu başlatılamadı ({exc}). Port {port} kullanımda olabilir; "
              f"farklı bir port için PYTEST_PORT ayarlayın.")


if __name__ == "__main__":
    main()
