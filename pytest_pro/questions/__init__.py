"""
Soru bankası: üniteler, şablonlar, soru üretimi ve puanlama.

Yeni ünite eklemek için `units/` klasörüne bir dosya ekleyip `units/__init__.py`
içindeki listeye yazmak yeterlidir. Ayrıntılar: docs/GELISTIRME.md
"""
import random

from .units import MODULES as UNIT_MODULES  # ünite dosyalarını yükler (kayıt yan etkisi)
from .codecheck import MAX_CODE_LEN, check_code
from .registry import UNITS, all_generators, ordered_units

PUBLIC_KEYS = ("id", "type", "topic", "text", "code", "options")
DEFAULT_UNITS = ["temel", "veri_tipleri"]
# İpucu ve yanlış şık açıklamaları tamamlanmış üniteler (testle zorunlu tutulur)
CONTENT_UNITS = ("temel", "veri_tipleri")  # Görev 9: + operatorler, metinler


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
    # "3,5" ve "3.5" aynı kabul edilir; boşluklar önemsenmez
    return "".join(str(s).split()).replace(",", ".")


def why_for(question, answer):
    """Öğrencinin verdiği yanlış cevabın açıklaması; yoksa None."""
    whys = question.get("whys") or {}
    qtype = question["type"]
    if qtype in ("mc", "tf"):
        return whys.get(answer)
    if qtype == "short":
        target = _norm_short(answer or "")
        if not target:
            return None
        for value, why in whys.items():
            if _norm_short(value) == target:
                return why
    return None


def trace_source(question):
    """İzlenecek kod {code, stdin}; eski kayıtlarda soru kodundan türetilir. Yoksa None."""
    if "trace" in question:
        return question["trace"]
    if question.get("type") in ("mc", "short") and question.get("code"):
        return {"code": question["code"], "stdin": question.get("stdin", "")}
    return None


def grade(question, user_ans):
    """(doğru_mu, not) döndürür. Not yalnızca kod sorularında doludur."""
    raw = "" if user_ans is None else str(user_ans)
    qtype = question["type"]
    if not raw.strip():
        return False, ("Boş bırakıldı." if qtype == "code" else None)
    if qtype == "code":
        return check_code(raw.strip(), question["check"])
    if qtype == "short":
        return _norm_short(raw) == _norm_short(question["answer"]), None
    return raw == question["answer"], None


__all__ = ["UNITS", "UNIT_MODULES", "DEFAULT_UNITS", "CONTENT_UNITS", "why_for", "trace_source", "MAX_CODE_LEN", "PUBLIC_KEYS", "all_generators", "catalog",
           "generate_one", "generate_questions", "grade", "public_question", "unit_title", "valid_unit_ids"]
