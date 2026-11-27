"""Soru içeriği: ipucu, yanlış şık açıklamaları ve izlenecek kod."""
import re
from pytest_pro import questions as qs
from pytest_pro.questions.helpers import FILLER_WHY_NUMBER, Wrong, output_question


def test_wrong_reasons_become_whys_for_shown_options_only():
    q = output_question("print(1)", "1", "s", wrongs=[Wrong("2", "neden2"), "3", Wrong("4", "neden4")], hint="h")
    assert q["hint"] == "h"
    assert q["whys"] == {"2": "neden2", "4": "neden4"}
    assert set(q["whys"]) <= set(q["options"]) and "1" not in q["whys"]


def test_filler_options_get_generic_why():
    q = output_question("print(10)", "10", "s", wrongs=[Wrong("11", "x")])  # 2 yedek çeldirici eklenir
    fillers = [o for o in q["options"] if o not in ("10", "11")]
    assert fillers and all(q["whys"][f] == FILLER_WHY_NUMBER for f in fillers)


def test_short_answer_common_wrongs():
    q = output_question("print(int(7.9))", "7", "s", common_wrongs=[Wrong("8", "yuvarlamaz")])
    assert q["type"] == "short"
    assert qs.why_for(q, " 8 ") == "yuvarlamaz" and qs.why_for(q, "9") is None


def test_why_for_unknown_answer_is_none():
    q = output_question("print(1)", "1", "s", wrongs=[Wrong("2", "n")])
    assert qs.why_for(q, "<b>x</b>") is None and qs.why_for(q, "") is None


def test_trace_field_is_filled_by_generator():
    from pytest_pro.questions.registry import UNITS
    by_name = {g.name: g for u in UNITS.values() for g in u.generators}
    assert by_name["temel.print_sep"]()["trace"]["code"].startswith("print(")
    q = by_name["temel.write_mult"]()
    assert q["trace"] == {"code": q["answer"], "stdin": ""}
    assert by_name["temel.input_type"]()["trace"] is None
    assert by_name["veri_tipleri.input_concat"]()["trace"]["stdin"]


def test_trace_source_legacy_and_none():
    assert qs.trace_source({"type": "mc", "code": "print(1)"}) == {"code": "print(1)", "stdin": ""}
    assert qs.trace_source({"type": "tf", "code": "x = 1"}) is None
    assert qs.trace_source({"type": "mc", "code": None, "trace": None}) is None


def test_public_question_hides_new_fields():
    for q in qs.generate_questions(20, list(qs.UNITS)):
        pub = qs.public_question(q)
        assert not {"hint", "whys", "trace", "gen", "unit"} & set(pub)


# ---------------------------------------------------------------- içerik kapsamı
import json  # noqa: E402
import random  # noqa: E402

import pytest  # noqa: E402

from pytest_pro.questions.registry import UNITS  # noqa: E402

COVERED = [g for u in qs.CONTENT_UNITS for g in UNITS[u].generators]


@pytest.mark.parametrize("gen", COVERED, ids=lambda g: g.name)
def test_content_complete(gen):
    for seed in range(40):
        random.seed(seed)
        q = gen()
        assert q.get("hint"), "ipucu yok"
        if q["type"] == "fill":
            for alts in q["answer"]:
                assert all(a not in q["hint"] for a in alts if len(a) > 3), "ipucu cevabı içeriyor"
            continue
        if len(q["answer"]) > 3 and q["type"] != "tf":  # D/Y'de "True" sözcüğü cevabı ele vermez
            assert q["answer"] not in q["hint"], "ipucu cevabı içeriyor"
        assert q["answer"] not in q.get("whys", {})
        if q["type"] == "mc":
            for opt in q["options"]:
                if opt != q["answer"]:
                    assert q["whys"].get(opt), f"açıklamasız şık: {opt!r}"
        if q["type"] == "short":
            assert q["whys"], "sık yanlış yok"
        if q["type"] == "tf":
            wrong = "False" if q["answer"] == "True" else "True"
            assert q.get("whys", {}).get(wrong), "doğru/yanlış sorusunda yanlış seçeneğin açıklaması yok"


VARIETY_MIN = 12  # yan yana iki öğrencinin aynı soruyu görme olasılığı en fazla ~%8


@pytest.mark.parametrize("gen", [g for u in UNITS.values() for g in u.generators], ids=lambda g: g.name)
def test_template_variety(gen):
    seen = set()
    for seed in range(500):
        random.seed(seed)
        q = gen()
        seen.add((q["text"], q.get("code"), json.dumps(q["answer"]), tuple(sorted(q.get("options") or []))))
    assert len(seen) >= VARIETY_MIN, f"yalnızca {len(seen)} farklı soru"


def test_tf_statement_reasons_become_whys():
    from pytest_pro.questions.helpers import tf_question
    for seed in range(20):
        random.seed(seed)
        q = tf_question([("D", "neden-d")], [("Y", "neden-y")], "s")
        wrong = "False" if q["answer"] == "True" else "True"
        assert q["whys"] == {wrong: "neden-d" if q["text"] == "D" else "neden-y"}



# ---------------------------------------------------------------- sayıdan sonra gelen ekler (uzman denetimi)
_UNITS_WORD = {0: "sıfır", 1: "bir", 2: "iki", 3: "üç", 4: "dört", 5: "beş", 6: "altı", 7: "yedi", 8: "sekiz",
               9: "dokuz"}
_TENS_WORD = {10: "on", 20: "yirmi", 30: "otuz", 40: "kırk", 50: "elli", 60: "altmış", 70: "yetmiş", 80: "seksen",
              90: "doksan"}
_VOWELS = "aeıioöuü"


def _number_word(n):
    """Sayının okunuşundaki son sözcük (ekin uyumu buna göre belirlenir): 6 -> altı, 40 -> kırk, 300 -> yüz."""
    n = abs(n)
    if n == 0:
        return "sıfır"
    if n % 1000 == 0:
        return "bin"
    if n % 100 == 0:
        return "yüz"
    if n % 10 == 0:
        return _TENS_WORD[n % 100]
    return _UNITS_WORD[n % 10]


def _suffixes(word):
    """Sözcüğe gelebilecek doğru ekler (yönelme, bulunma, ayrılma, belirtme, ilgi, vasıta, ek-fiil, üleştirme)."""
    last = [ch for ch in word if ch in _VOWELS][-1]
    two = "e" if last in "eiöü" else "a"
    four = {"a": "ı", "ı": "ı", "e": "i", "i": "i", "o": "u", "u": "u", "ö": "ü", "ü": "ü"}[last]
    vowel_end = word[-1] in _VOWELS
    d = "t" if word[-1] in "fstkçşhp" else "d"
    return {("y" if vowel_end else "") + two, d + two, d + two + "n", ("y" if vowel_end else "") + four,
            ("n" if vowel_end else "") + four + "n", ("y" if vowel_end else "") + "l" + two, d + four + "r",
            ("ş" if vowel_end else "") + two + "r"}


def test_number_suffix_helper():
    assert {"e", "te", "ten", "ü", "ün"} <= _suffixes(_number_word(4)) and "den" not in _suffixes(_number_word(4))
    assert {"şer", "ye", "yi", "nin"} <= _suffixes(_number_word(2)) and "er" not in _suffixes(_number_word(2))
    assert {"ya", "da", "dan", "yı", "nın"} <= _suffixes(_number_word(6))
    assert {"e", "te", "ten", "ü", "ün"} <= _suffixes(_number_word(3))
    assert {"a", "ta", "tan", "ı", "ın"} <= _suffixes(_number_word(40))
    assert "dan" in _suffixes(_number_word(0)) and "den" in _suffixes(_number_word(1))


_NUM_SUFFIX = re.compile(r"(?<![\w.])(-?\d+)'([a-zçğıöşü]+)")


@pytest.mark.parametrize("gen", [g for u in UNITS.values() for g in u.generators], ids=lambda g: g.name)
def test_number_suffixes_follow_vowel_harmony(gen):
    """Sayıdan sonra gelen ek, sayının okunuşuna uymalı: "6'ya", "4'e", "40'tan" (ör. "{n}'e" 6 için yanlıştır).
    Kılavuz değişken sayılarda eksiz yazımı önerir ("1 ile n arasında")."""
    for seed in range(60):
        random.seed(seed)
        q = gen()
        texts = [q.get("text") or "", q.get("solution") or "", q.get("hint") or ""]
        texts += [str(v) for v in (q.get("whys") or {}).values()]
        texts += [str(v) for bw in q.get("blank_whys") or [] for v in bw.values()]
        for text in texts:
            for m in _NUM_SUFFIX.finditer(text):
                assert m.group(2) in _suffixes(_number_word(int(m.group(1)))), f"ek uyumsuz: {m.group(0)!r} ({text[:80]})"


# ---------------------------------------------------------------- kod yazımına uygun gösterim
_MATH_NOTATION = [
    (re.compile(r"[≥≤≠÷×]"), "matematik işareti; kodda >=, <=, !=, /, * yazılır"),
    (re.compile(r"→"), "ok işareti; sonucu sözle yazın (\"... True olur\")"),
    (re.compile(r"(?<![\w(])(?:[a-zA-Z]|\d+)!(?!=)"), "n! gösterimi; faktöriyel(n) ya da çarpım olarak yazın"),
    (re.compile(r"\b\w+ = [^\s,;:]+ (iken|olduğunda|olursa|olunca|ise)\b"),
     "durumu = ile anlatma; kodda = atamadır, karşılaştırma için == yazın"),
]


@pytest.mark.parametrize("gen", [g for u in UNITS.values() for g in u.generators], ids=lambda g: g.name)
def test_texts_use_code_notation(gen):
    """Soru metni, şıklar, ipucu ve açıklamalarda matematik defteri yazımı yerine kod yazımı kullanılır."""
    for seed in range(40):
        random.seed(seed)
        q = gen()
        texts = [q.get("text") or "", q.get("solution") or "", q.get("hint") or "", q.get("note") or ""]
        texts += [str(o) for o in q.get("options") or []]
        texts += [str(v) for v in (q.get("whys") or {}).values()]
        texts += [str(v) for bw in q.get("blank_whys") or [] for v in bw.values()]
        for text in texts:
            plain = re.sub(r"<[^>]+>", "", text)
            for pattern, why in _MATH_NOTATION:
                m = pattern.search(plain)
                assert not m, f"{why}: {m.group(0)!r} … {plain[max(0, m.start() - 40):m.end() + 40]!r}"
