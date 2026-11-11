"""
SQLite bağlantısı ve sürümlü şema göçleri.

Şema sürümü `PRAGMA user_version` içinde tutulur. Şemayı değiştirmek için MIGRATIONS
listesinin SONUNA yeni bir fonksiyon ekleyin; var olanları asla değiştirmeyin.
"""
import json
import sqlite3
from contextlib import closing

from flask import current_app, g


def connect(path):
    db = sqlite3.connect(path, timeout=10)
    db.row_factory = sqlite3.Row
    return db


def get_db():
    if "db" not in g:
        g.db = connect(current_app.config["DB_PATH"])
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def _columns(db, table):
    return {r["name"] for r in db.execute(f"PRAGMA table_info({table})")}


def _add_column(db, table, column, ddl):
    if column not in _columns(db, table):
        db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")


def _m1_initial(db):
    # v2 sürümünün şeması (o sürümden kalan veritabanları da bu adımı sorunsuz geçer)
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


def _m2_autosave_and_settings(db):
    db.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    _add_column(db, "exams", "duration", "INTEGER")
    _add_column(db, "exams", "results", "TEXT")
    _add_column(db, "exams", "saved_at", "REAL")
    _add_column(db, "exams", "auto_submitted", "INTEGER NOT NULL DEFAULT 0")
    db.execute("CREATE INDEX IF NOT EXISTS idx_exams_no ON exams(no)")


def _m3_exam_title(db):
    _add_column(db, "exams", "title", "TEXT NOT NULL DEFAULT ''")
    db.execute("CREATE INDEX IF NOT EXISTS idx_exams_title ON exams(title)")


MIGRATIONS = [_m1_initial, _m2_autosave_and_settings, _m3_exam_title]


def schema_version(db):
    return db.execute("PRAGMA user_version").fetchone()[0]


def init_db(path, default_settings):
    with closing(connect(path)) as db:
        db.execute("PRAGMA journal_mode=WAL")  # eşzamanlı okuma/yazma için
        version = schema_version(db)
        for number, migrate in enumerate(MIGRATIONS[version:], start=version + 1):
            migrate(db)
            db.execute(f"PRAGMA user_version = {number}")
        for key, value in default_settings.items():
            db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, json.dumps(value)))
        db.commit()
