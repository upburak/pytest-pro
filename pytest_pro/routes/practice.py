"""Pratik modu API'si: kayıt tutulmaz, cevap anında kontrol edilir."""
from flask import Blueprint, current_app, jsonify, request

from .. import questions as qs
from ..db import get_db
from ..settings import get_settings
from .common import error

bp = Blueprint("practice", __name__, url_prefix="/api/practice")


def _store():
    return current_app.extensions["pytest_pro_practice"]


def _closed():
    return not get_settings(get_db())["practice_open"]


@bp.get("/units")
def units():
    if _closed():
        return error("Pratik modu şu an kapalı.", 403)
    return jsonify(qs.catalog())


@bp.post("/next")
def next_question():
    if _closed():
        return error("Pratik modu şu an kapalı.", 403)
    data = request.get_json(silent=True) or {}
    unit = str(data.get("unit", ""))
    if unit not in qs.UNITS:
        return error("Ünite bulunamadı.", 404)
    q = qs.generate_one(unit)
    q["id"] = 1
    token = _store().put(q)
    return jsonify({"token": token, "unit": qs.unit_title(unit), "question": qs.public_question(q)})


@bp.post("/check")
def check():
    if _closed():
        return error("Pratik modu şu an kapalı.", 403)
    data = request.get_json(silent=True) or {}
    q = _store().get(data.get("token"))
    if q is None:
        return error("Soru süresi doldu, yeni soru al.", 404)
    answer = str(data.get("answer") or "")[:qs.MAX_CODE_LEN]
    ok, note = qs.grade(q, answer)
    return jsonify({"correct": bool(ok), "note": note, "answer": q["answer"], "solution": q["solution"],
                    "type": q["type"]})
