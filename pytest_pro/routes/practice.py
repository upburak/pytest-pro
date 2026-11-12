"""Pratik modu API'si: kayıt tutulmaz, cevap anında kontrol edilir."""
from flask import Blueprint, current_app, jsonify, request

from .. import questions as qs
from ..questions.tracer import trace
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
    gen = data.get("gen")
    avoid = data.get("avoid")
    avoid = [str(a) for a in avoid] if isinstance(avoid, list) else []
    try:
        q = qs.generate_one(unit, gen=str(gen) if gen else None, avoid=avoid)
    except ValueError:
        return error("Bu soru şablonu bu üniteye ait değil.", 400)
    q["id"] = 1
    token = _store().put(q)
    return jsonify({"token": token, "unit": qs.unit_title(unit), "gen": q["gen"], "topic": q["topic"],
                    "question": qs.public_question(q)})


def _question_or_error():
    """(soru, None) ya da (None, hata yanıtı)."""
    if _closed():
        return None, error("Pratik modu şu an kapalı.", 403)
    data = request.get_json(silent=True) or {}
    q = _store().get(data.get("token"))
    if q is None:
        return None, error("Bu soru artık yok, yeni soru al.", 404)
    return q, None


@bp.post("/hint")
def hint():
    q, err = _question_or_error()
    if err:
        return err
    if not q.get("hint"):
        return error("Bu soru için ipucu yok.", 404)
    return jsonify({"hint": q["hint"]})


@bp.post("/trace")
def trace_question():
    q, err = _question_or_error()
    if err:
        return err
    source = qs.trace_source(q)
    if not source:
        return error("Bu soru için adım adım izlenecek kod yok.", 404)
    return jsonify(trace(source["code"], source.get("stdin", "")))


@bp.post("/check")
def check():
    q, err = _question_or_error()
    if err:
        return err
    data = request.get_json(silent=True) or {}
    answer = str(data.get("answer") or "")[:qs.MAX_CODE_LEN]
    ok, note = qs.grade(q, answer)
    if ok:
        why = None
    elif q["type"] == "code":
        why = note
    else:
        why = qs.why_for(q, answer)
    return jsonify({"correct": bool(ok), "note": note, "answer": q["answer"], "solution": q["solution"],
                    "type": q["type"], "why": why, "gen": q.get("gen"),
                    "has_trace": bool(qs.trace_source(q))})
