"""
Testlerde ortak yardımcılar. Ünite test dosyaları (`tests/test_unit_XX.py`) bunları şöyle kullanır:

    from helpers import accepts, code_q, gens, outcome, rejects, run, samples

Burada çalıştırılan kod YALNIZCA öğretmenin (şablonun ürettiği) kodudur. Öğrenci kodu hiçbir
zaman çalıştırılmaz; kod yazma soruları `accepts` / `rejects` ile AST denetleyicisinden geçirilir.
"""
import builtins
import contextlib
import io
import json
import random
from collections import Counter

from pytest_pro import questions as qs
from pytest_pro.questions.helpers import FILLER_WHY_NUMBER, FILLER_WHY_OTHER, err
from pytest_pro.questions.registry import UNITS, all_generators

OK = "Kod tüm kriterleri sağlıyor."


# ---------------------------------------------------------------- öğretmen kodunu çalıştırma
def run(code, stdin=""):
    """Şablon kodunu çalıştırıp ekran çıktısını döndürür (input() için stdin satırları kullanılır)."""
    out = io.StringIO()
    lines = iter(stdin.splitlines())
    original = builtins.input
    builtins.input = lambda prompt="": next(lines)
    try:
        with contextlib.redirect_stdout(out):
            exec(code, {"__name__": "__soru__"})  # noqa: S102 - yalnızca bizim ürettiğimiz kod
    finally:
        builtins.input = original
    return out.getvalue()


def outcome(code, stdin=""):
    """Kodun sonucu: hata vermezse sondaki satır sonu atılmış çıktı, verirse 'Hata verir (TürAdı)'."""
    try:
        return run(code, stdin).rstrip("\n")
    except Exception as exc:  # noqa: BLE001 - hata türünün adı cevaptır
        return err(type(exc).__name__)


# ---------------------------------------------------------------- şablon seçme ve üretme
def gens(unit=None, names=None):
    """Şablonlar: gens("temel") bir ünitenin, gens(names=["temel.swap"]) adı verilenlerin."""
    out = list(UNITS[unit].generators) if unit else all_generators()
    if names is not None:
        wanted = set(names)
        out = [g for g in out if g.name in wanted]
    return out


def gen_by_name(name):
    return next(g for g in all_generators() if g.name == name)


def samples(gen, n=120, start=0):
    """Şablondan tohum sabitlenerek n soru üretir (her çalıştırmada aynı sorular)."""
    for seed in range(start, start + n):
        random.seed(seed)
        yield gen()


# ---------------------------------------------------------------- kalite ölçüleri
def filler_rate(gen, n=300):
    """Genel (dolgu) açıklamalı şık içeren soruların oranı. ÇS dışı şablonlarda 0."""
    hits = total = 0
    for q in samples(gen, n):
        total += 1
        whys = q.get("whys") or {}
        if q["type"] == "mc" and any(w in (FILLER_WHY_NUMBER, FILLER_WHY_OTHER) for w in whys.values()):
            hits += 1
    return hits / total


def answer_key(q):
    """Cevap dağılımında sayılacak değer (D/Y'de iddia + cevap, diğerlerinde cevap)."""
    if q["type"] == "tf":
        return json.dumps([q["text"], q["answer"]], ensure_ascii=False)
    return json.dumps(q["answer"], ensure_ascii=False)


def top_answer_share(gen, n=300):
    """En sık doğru cevabın oranı ve kendisi: (0.45, '"4"')."""
    counts = Counter(answer_key(q) for q in samples(gen, n))
    value, count = counts.most_common(1)[0]
    return count / n, value


def variety(gen, n=500):
    """Farklı soru sayısı (metin, kod, cevap ve şıklar birlikte)."""
    seen = set()
    for q in samples(gen, n):
        seen.add((q["text"], q.get("code"), json.dumps(q["answer"]), tuple(sorted(q.get("options") or []))))
    return len(seen)


# ---------------------------------------------------------------- kod yazma denetleyicileri
def code_q(kind, **params):
    """Denetleyici testi için en küçük kod yazma sorusu: code_q("mult", v1="a", v2="b", n1=7, n2=3)."""
    return {"type": "code", "check": {"kind": kind, **params}}


def accepts(question, src):
    """Öğrenci kodu kabul ediliyor mu? (kod çalıştırılmaz, AST ile denetlenir)"""
    return qs.grade(question, src) == (True, OK)


def rejects(question, src, reason=""):
    """Öğrenci kodu reddediliyor ve not `reason` metnini içeriyor mu?"""
    ok, note = qs.grade(question, src)
    return ok is False and reason in (note or "")
