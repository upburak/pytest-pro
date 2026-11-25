"""
Soru bankası: üniteler, şablonlar, soru üretimi ve puanlama.

Yeni ünite eklemek için `units/` klasörüne bir dosya ekleyip `units/__init__.py`
içindeki listeye yazmak yeterlidir. Ayrıntılar: docs/GELISTIRME.md
"""
import random

from .units import MODULES as UNIT_MODULES  # ünite dosyalarını yükler (kayıt yan etkisi)
from .codecheck import MAX_CODE_LEN, check_code
from .fill import blank_why, fill_in, grade_fill, marks as _fill_marks
from .registry import UNITS, all_generators, ordered_units
from .short import legacy_norm, short_correct, short_key

PUBLIC_KEYS = ("id", "type", "topic", "text", "code", "options")
DEFAULT_UNITS = ["temel", "veri_tipleri"]
# İpucu ve yanlış şık açıklamaları tamamlanmış üniteler (testle zorunlu tutulur)
CONTENT_UNITS = tuple(UNITS)  # ikinci teslimat: tüm üniteler


def catalog():
    """Ünite listesi (öğretmen paneli ve pratik modu için)."""
    return [u.to_public() for u in ordered_units()]


def valid_unit_ids(ids):
    return [u for u in dict.fromkeys(ids) if u in UNITS and UNITS[u].generators]


def generate_questions(count, unit_ids=None):
    """
    Seçilen ünitelerden dengeli soru üretir: üniteler sırayla birer soru verir,
    her ünite kendi şablonlarını tekrar etmeden karışık sırayla kullanır.
    Sorular müfredat sırasına (kolaydan zora) dizilir.
    """
    chosen = [UNITS[u] for u in valid_unit_ids(unit_ids or DEFAULT_UNITS)] or [UNITS[u] for u in DEFAULT_UNITS]
    order = chosen[:]
    random.shuffle(order)
    queues = {u.id: [] for u in chosen}
    pool = []
    while len(pool) < count:
        for unit in order:
            if len(pool) == count:
                break
            if not queues[unit.id]:
                queues[unit.id] = random.sample(unit.generators, len(unit.generators))
            pool.append(queues[unit.id].pop())
    random.shuffle(pool)
    pool.sort(key=lambda g: UNITS[g.unit].order)
    return [{"id": i + 1, **gen()} for i, gen in enumerate(pool)]


REVISIT_CHANCE = 0.2  # tamamlanmış konudan tekrar sorusu gelme olasılığı


def generate_one(unit_id, gen=None, avoid=()):
    """Üniteden tek soru. gen verilirse o şablondan (aynı konudan yeni soru); verilmezse
    avoid dışındaki şablonlardan, REVISIT_CHANCE olasılıkla avoid yok sayılarak."""
    generators = UNITS[unit_id].generators
    if gen is not None:
        match = [g for g in generators if g.name == gen]
        if not match:
            raise ValueError(f"{gen} bu üniteye ait değil")
        return match[0]()
    avoid = set(avoid)
    candidates = [g for g in generators if g.name not in avoid]
    if not candidates or random.random() < REVISIT_CHANCE:
        candidates = generators
    return random.choice(candidates)()


def public_question(q):
    """Öğrenciye giden sürüm: cevap, çözüm ve denetim bilgisi içermez."""
    return {k: q.get(k) for k in PUBLIC_KEYS}


def unit_title(unit_id):
    unit = UNITS.get(unit_id or "")
    return unit.title if unit else "Diğer"


def _norm_short(s):
    """Eski kısa cevap biçimi ("3,5" = "3.5", boşluklar önemsenmez). Yeni kod short_key kullanır."""
    return legacy_norm(s)


def why_for(question, answer):
    """Öğrencinin verdiği yanlış cevabın açıklaması; yoksa None."""
    whys = question.get("whys") or {}
    qtype = question["type"]
    if qtype in ("mc", "tf"):
        return whys.get(answer)
    if qtype == "short":
        if not str(answer or "").strip():
            return None
        target = short_key(question, answer)
        for value, why in whys.items():
            if short_key(question, value) == target:
                return why
    if qtype == "fill":
        return blank_why(question, "" if answer is None else str(answer))
    return None


def trace_source(question):
    """İzlenecek kod {code, stdin}; eski kayıtlarda soru kodundan türetilir. Yoksa None."""
    if "trace" in question:
        return question["trace"]
    if question.get("type") in ("mc", "short") and question.get("code"):
        return {"code": question["code"], "stdin": question.get("stdin", "")}
    if question.get("type") == "fill" and question.get("code") and question.get("answer"):
        # cevap anahtarı yerleştirilmiş kod
        return {"code": fill_in(question["code"], [alts[0] for alts in question["answer"]]),
                "stdin": question.get("stdin", "")}
    return None


def fill_marks(question, user_ans):
    """Boşluk doldurma sorusunda her boşluğun doğru olup olmadığı; başka tiplerde None."""
    if question.get("type") != "fill":
        return None
    return _fill_marks(question, "" if user_ans is None else str(user_ans))


def grade(question, user_ans):
    """(doğru_mu, not) döndürür. Not yalnızca kod ve boşluk doldurma sorularında doludur."""
    raw = "" if user_ans is None else str(user_ans)
    qtype = question["type"]
    if not raw.strip():
        return False, ("Boş bırakıldı." if qtype in ("code", "fill") else None)
    if qtype == "code":
        return check_code(raw.strip(), question["check"])
    if qtype == "fill":
        return grade_fill(question, raw)
    if qtype == "short":
        return short_correct(question, raw), None
    return raw == question["answer"], None


__all__ = ["UNITS", "UNIT_MODULES", "DEFAULT_UNITS", "CONTENT_UNITS", "fill_marks", "why_for", "trace_source",
           "MAX_CODE_LEN", "PUBLIC_KEYS", "all_generators", "catalog", "generate_one", "generate_questions", "grade",
           "public_question", "short_key", "unit_title", "valid_unit_ids"]
