"""Sınav oturumları.

Öğretmenin "Sınavı aç"a her basışı ayrı bir sınavdır (oturum). Oturum, ilk öğrenci girdiğinde
oluşturulur; böylece kimsenin girmediği boş sınavlar listede görünmez. Sınav kapatılınca oturum kapanır.
Açık kalan bir sınava ertesi gün girilirse yeni bir oturum başlar (farklı sınıflar karışmasın).
"""
import json
from datetime import datetime

POINTER = "session_id"  # settings tablosunda açık oturumun numarası (öğretmen ayarlarında görünmez)


def _pointer(db):
    row = db.execute("SELECT value FROM settings WHERE key = ?", (POINTER,)).fetchone()
    return json.loads(row["value"]) if row else None


def _set_pointer(db, session_id):
    if session_id is None:
        db.execute("DELETE FROM settings WHERE key = ?", (POINTER,))
    else:
        db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (POINTER, json.dumps(session_id)))


def current(db):
    """Açık oturum; yoksa None."""
    sid = _pointer(db)
    if sid is None:
        return None
    return db.execute("SELECT * FROM sessions WHERE id = ? AND closed_at IS NULL", (sid,)).fetchone()


def _live_count(db, session_id):
    return db.execute("SELECT COUNT(*) FROM exams WHERE session_id = ? AND submitted_at IS NULL",
                      (session_id,)).fetchone()[0]


def close_current(db, t):
    cur = current(db)
    if cur is not None:
        db.execute("UPDATE sessions SET closed_at = ? WHERE id = ?", (t, cur["id"]))
    _set_pointer(db, None)


def ensure_open(db, title, t):
    """Öğrencinin gireceği oturumun numarası; gerekirse yeni oturum açar. (commit çağırana aittir)"""
    cur = current(db)
    if cur is not None:
        same_day = datetime.fromtimestamp(cur["opened_at"]).date() == datetime.fromtimestamp(t).date()
        if same_day or _live_count(db, cur["id"]):
            return cur["id"]
        close_current(db, t)
    sid = db.execute("INSERT INTO sessions (title, opened_at) VALUES (?, ?)", (title, t)).lastrowid
    _set_pointer(db, sid)
    return sid


def apply_settings_change(db, before, after, t):
    """Ayar değişikliğinin oturuma etkisi: aç/kapat yeni sınav başlatır, başlık açık sınavın adıdır."""
    if before["exam_open"] != after["exam_open"]:
        close_current(db, t)  # kapatınca biter; açınca ilk öğrenciyle yeni oturum başlar
    elif after["title"] != before["title"]:
        cur = current(db)
        if cur is not None:
            db.execute("UPDATE sessions SET title = ? WHERE id = ?", (after["title"], cur["id"]))


def listing(db):
    """Tüm oturumlar, en yenisi önce; öğrenci sayıları ve ortalamayla."""
    open_id = (current(db) or {"id": None})["id"]
    rows = db.execute(
        "SELECT s.id, s.title, s.opened_at, COUNT(e.id) AS students, "
        "COALESCE(SUM(e.submitted_at IS NULL), 0) AS live, "
        "AVG(CASE WHEN e.submitted_at IS NOT NULL THEN e.score END) AS average "
        "FROM sessions s LEFT JOIN exams e ON e.session_id = s.id "
        "GROUP BY s.id ORDER BY s.opened_at DESC, s.id DESC"
    ).fetchall()
    return [{
        "id": r["id"], "title": r["title"], "open": r["id"] == open_id,
        "opened_ts": r["opened_at"], "opened": datetime.fromtimestamp(r["opened_at"]).strftime("%d.%m.%Y %H:%M"),
        "students": r["students"], "live": r["live"], "done": r["students"] - r["live"],
        "average": None if r["average"] is None else round(r["average"], 1),
    } for r in rows]


class StillRunning(Exception):
    """Silinmek istenen oturumda sınavı süren öğrenciler var."""


def delete(db, session_id):
    """Oturumu ve öğrencilerini siler; silinen öğrenci kaydı sayısını döner, oturum yoksa None."""
    row = db.execute("SELECT id FROM sessions WHERE id = ?", (session_id,)).fetchone()
    if row is None:
        return None
    if _live_count(db, session_id):  # kapalı sınavda da süren öğrenci olabilir
        raise StillRunning()
    is_open = (current(db) or {"id": None})["id"] == session_id
    deleted = db.execute("DELETE FROM exams WHERE session_id = ?", (session_id,)).rowcount
    db.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    if is_open:
        _set_pointer(db, None)
    db.commit()
    return deleted


def delete_all(db):
    if db.execute("SELECT 1 FROM exams WHERE submitted_at IS NULL").fetchone():
        raise StillRunning()
    deleted = db.execute("DELETE FROM exams").rowcount
    db.execute("DELETE FROM sessions")
    _set_pointer(db, None)
    db.commit()
    return deleted
