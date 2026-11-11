"""Öğretmen kimlik doğrulama ve kaba kuvvet koruması."""
import secrets
import threading
from functools import wraps

from flask import current_app, jsonify, request

from . import clock

MAX_FAILS, LOCK_SECONDS = 10, 60  # 10 hatalı denemede 60 sn kilit


class LoginLimiter:
    def __init__(self):
        self._lock = threading.Lock()
        self._fails = {}  # ip -> (hata sayısı, kilit bitişi)

    def locked(self, ip):
        with self._lock:
            _, until = self._fails.get(ip, (0, 0))
            return until > clock.now()

    def fail(self, ip):
        with self._lock:
            count = self._fails.get(ip, (0, 0))[0] + 1
            self._fails[ip] = (0, clock.now() + LOCK_SECONDS) if count >= MAX_FAILS else (count, 0)

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
            return jsonify({"error": "Yetkisiz. Öğretmen şifresi hatalı."}), 401
        limiter.reset(ip)
        return f(*args, **kwargs)
    return wrapper
