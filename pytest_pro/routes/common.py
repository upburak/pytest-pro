"""Rotalarda ortak yardımcılar."""
import socket

from flask import current_app, jsonify


def error(message, status):
    return jsonify({"error": message}), status


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
