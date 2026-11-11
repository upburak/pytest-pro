"""Uygulama fabrikası ve sunucu başlatıcı."""
import os
import secrets

from flask import Flask, request

from . import __version__
from .auth import LoginLimiter
from .db import close_db, init_db
from .practice import PracticeStore
from .routes import BLUEPRINTS
from .routes.common import get_local_ip
from .settings import default_settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CSP = ("default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; "
       "connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'")


def _env_int(name, default, lo, hi):
    try:
        value = int(os.environ.get(name, default))
    except ValueError:
        return default
    return min(max(value, lo), hi)


def security_headers(resp):
    resp.headers.setdefault("Content-Security-Policy", CSP)
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("X-Frame-Options", "DENY")
    resp.headers.setdefault("Referrer-Policy", "no-referrer")
    if request.path.startswith("/api/"):
        resp.headers.setdefault("Cache-Control", "no-store")
    return resp


def create_app(db_path=None, teacher_key=None, exam_seconds=None, port=None):
    """
    Ayarlar parametreyle verilmezse ortam değişkenlerinden okunur:
    PYTEST_DB, PYTEST_SIFRE, PYTEST_SURE (saniye), PYTEST_PORT.
    """
    app = Flask(__name__)
    exam_seconds = exam_seconds or _env_int("PYTEST_SURE", 900, 60, 10800)
    app.config.update(
        DB_PATH=db_path or os.environ.get("PYTEST_DB") or os.path.join(BASE_DIR, "results.db"),
        TEACHER_KEY=teacher_key or os.environ.get("PYTEST_SIFRE") or f"{secrets.randbelow(900000) + 100000}",
        EXAM_SECONDS=exam_seconds,
        PORT=port or _env_int("PYTEST_PORT", 5000, 1, 65535),
        MAX_CONTENT_LENGTH=256 * 1024,
        DEFAULT_SETTINGS=default_settings(exam_seconds),
    )
    app.json.ensure_ascii = False
    app.extensions["pytest_pro_limiter"] = LoginLimiter()
    app.extensions["pytest_pro_practice"] = PracticeStore()
    init_db(app.config["DB_PATH"], app.config["DEFAULT_SETTINGS"])
    for bp in BLUEPRINTS:
        app.register_blueprint(bp)
    app.teardown_appcontext(close_db)
    app.after_request(security_headers)

    @app.context_processor
    def inject_version():
        return {"version": __version__}

    return app


def main():
    app = create_app()
    ip, port = get_local_ip(), app.config["PORT"]
    print("\n" + "=" * 56)
    print(f"  PYTEST PRO {__version__} - ÖĞRETMEN SUNUCUSU AKTİF")
    print(f"  Öğrenci adresi  : http://{ip}:{port}")
    print(f"  Pratik modu     : http://{ip}:{port}/pratik")
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
