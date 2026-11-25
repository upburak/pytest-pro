"""Soru bankası altyapısı: hesaplanan D/Y (tf_claim), karma sonuç (outcome), boşluk doldurma
açıklamaları ve bağlı boşluklar, kısa cevapta accept/norm, müfredat modülü."""
import json
import random

import pytest
from helpers import outcome, passing_options, run

from pytest_pro import questions as qs
from pytest_pro.questions.helpers import LOOP_OUTCOME, Wrong, err, fill_question, output_question, tf_claim
from pytest_pro.questions.registry import VERIFY_KINDS, register_unit


def ans(*values):
    return json.dumps(list(values), ensure_ascii=False)


# ---------------------------------------------------------------- tf_claim
def test_tf_claim_true_and_false_sides():
    seen = set()
    for seed in range(40):
        random.seed(seed)
        q = tf_claim("print(2 + 3)", "5", [Wrong("23", "Sayılar toplanır, yan yana yazılmaz."),
                                           Wrong("5", "aynı"), Wrong("6", "Hesabı tekrar et.")],
                     "2 + 3 = 5.", hint="+ ne yapar?")
        assert q["type"] == "tf" and q["code"] == "print(2 + 3)" and q["hint"] == "+ ne yapar?"
        assert q["output"] == "5" and "<code>" in q["text"]
        assert (q["claim"] == "5") == (q["answer"] == "True")
        wrong = "False" if q["answer"] == "True" else "True"
        assert q["whys"][wrong]
        if q["answer"] == "False":
            assert q["whys"]["True"] in ("Sayılar toplanır, yan yana yazılmaz.", "Hesabı tekrar et.")
        assert "<code>5</code>" in q["solution"]
        seen.add(q["answer"])
        assert not {"claim", "output"} & set(qs.public_question(q))
    assert seen == {"True", "False"}


def test_tf_claim_text_forms():
    random.seed(0)
    multi = tf_claim("print(1)\nprint(2)", "1\n2", [Wrong("1 2", "n")], "s")
    while multi["answer"] != "True":
        multi = tf_claim("print(1)\nprint(2)", "1\n2", [Wrong("1 2", "n")], "s")
    assert "alt alta" in multi["text"] and "<code>1</code>" in multi["text"] and "<code>2</code>" in multi["text"]
    error = tf_claim("print(1 / 0)", err("ZeroDivisionError"), [Wrong("0", "n")], "s", true_why="Sıfıra bölünmez.")
    while error["answer"] != "True":
        error = tf_claim("print(1 / 0)", err("ZeroDivisionError"), [Wrong("0", "n")], "s", true_why="Sıfıra bölünmez.")
    assert "ZeroDivisionError" in error["text"] and "hata" in error["text"] and error["whys"]["False"] == "Sıfıra bölünmez."
    custom = tf_claim("x = 3\nprint(x)", "3", [Wrong("x", "n")], "s", text="Kod çalışınca {claim} görünür.")
    assert custom["text"].startswith("Kod çalışınca <code>")
    with pytest.raises(ValueError):
        tf_claim("print(1)", "1", [Wrong("1", "aynı")], "s")


def _true_side(*args, **kw):
    for seed in range(50):
        random.seed(seed)
        q = tf_claim(*args, **kw)
        if q["answer"] == "True":
            return q
    raise AssertionError("doğru iddia üretilemedi")


def test_tf_claim_default_true_why_is_proper_turkish():
    """Varsayılan "neden" cümlesi hata iddiasında da düzgün Türkçe olmalı."""
    error = _true_side("print(1 / 0)", err("ZeroDivisionError"), [Wrong("0", "n")], "s")
    why = error["whys"]["False"]
    assert why == "İddia doğru: bu kodda gerçekten <code>ZeroDivisionError</code> hatası oluşur."
    assert "kod gerçekten" not in why
    out = _true_side("print(5)", "5", [Wrong("6", "n")], "s")
    assert out["whys"]["False"] == "İddia doğru: bu kod çalıştırıldığında gerçekten ekrana <code>5</code> yazılır."
    multi = _true_side("print(1)\nprint(2)", "1\n2", [Wrong("1 2", "n")], "s")
    assert multi["whys"]["False"].startswith("İddia doğru: bu kod çalıştırıldığında gerçekten ekrana alt alta")


def test_tf_claim_registered_as_tf_output_and_traced():
    assert "tf_output" in VERIFY_KINDS and "outcome" in VERIFY_KINDS
    unit = register_unit("_deneme_tf", "Deneme", "Başlangıç", "deneme", order=900)
    try:
        @unit.question("Deneme", verify="tf_output")
        def deneme():
            return tf_claim("print(4)", "4", [Wrong("5", "n")], "s", hint="h")

        q = unit.generators[0]()
        assert q["trace"] == {"code": "print(4)", "stdin": ""}
        assert outcome(q["code"]) == q["output"]
    finally:
        from pytest_pro.questions.registry import UNITS
        del UNITS["_deneme_tf"]


def test_outcome_helper_reports_errors_as_answers():
    assert outcome("print(1)\nprint(2)") == "1\n2"
    assert outcome('print("a" + 1)') == err("TypeError")
    assert outcome("print(input() * 2)", "ab") == "abab"


# ---------------------------------------------------------------- boşluk doldurma
def test_fill_wrong_answers_get_whys():
    q = fill_question("print(____(\"3\") + 1)", [["int"]], "4", "Doldur.", "Açıklama", hint="İpucu",
                      wrongs=[[Wrong("str", "Metin + sayı TypeError verir."), Wrong("float", "4.0 yazar.")]])
    assert q["blank_whys"] == [{"str": "Metin + sayı TypeError verir.", "float": "4.0 yazar."}]
    assert qs.why_for(q, ans("str")) == "Metin + sayı TypeError verir."
    assert qs.why_for(q, ans(" float ")) == "4.0 yazar."
    assert qs.why_for(q, ans("int")) is None and qs.why_for(q, ans("bool")) is None
    assert qs.why_for(q, "bozuk") is None
    two = fill_question("print(____ + ____)", [["1"], ["2"]], "3", "D", "A",
                        wrongs=[[], [Wrong("3", "Toplam değil ikinci terim isteniyor.")]])
    assert qs.why_for(two, ans("1", "3")) == "2. boşluk: Toplam değil ikinci terim isteniyor."
    with pytest.raises(ValueError):
        fill_question("print(____)", [["1"]], "1", "D", "A", wrongs=[[], []])
    same = fill_question("print(____)", [["1"]], "1", "D", "A", wrongs=[[Wrong(" 1", "x"), Wrong("2", "y")]])
    assert same["blank_whys"] == [{"2": "y"}]  # kabul edilen cevaba "yanlış" açıklaması verilmez


def test_fill_answer_sets_for_dependent_blanks():
    q = fill_question("yas = 18\nif yas ____ ____:\n    print(\"Ehliyet\")", None, "Ehliyet", "Doldur.", "A",
                      answer_sets=[[">=", "18"], [">", "17"]])
    assert q["answer"] == [[">=", ">"], ["18", "17"]]
    assert qs.grade(q, ans(">=", "18"))[0] and qs.grade(q, ans(">", "17"))[0]
    ok, note = qs.grade(q, ans(">=", "17"))
    assert not ok and note == "2 boşluktan 1'i doğru."
    assert qs.fill_marks(q, ans(">", "18")) in ([True, False], [False, True])
    assert qs.fill_marks(q, ans(">", "17")) == [True, True]
    with pytest.raises(ValueError):
        fill_question("print(____)", None, "1", "D", "A", answer_sets=[["1", "2"]])


def test_fill_expression_blanks_match_by_syntax_tree():
    q = {"type": "fill", "code": "a, b = ____", "answer": [["b, a"]], "expect": ""}
    for same in ("(b, a)", "b,a", " ( b , a ) "):
        assert qs.grade(q, ans(same))[0], same
    assert not qs.grade(q, ans("a, b"))[0]
    assert not qs.grade(q, ans("[b, a]"))[0]
    op = {"type": "fill", "code": "x ____ 3", "answer": [[">="]], "expect": ""}
    assert qs.grade(op, ans(" >= "))[0] and not qs.grade(op, ans("=>"))[0]


def test_fill_stdin_is_used_for_trace():
    q = fill_question("print(____(input()) + 1)", [["int"]], "16", "D", "A", stdin="15")
    assert q["stdin"] == "15"
    assert qs.trace_source(q)["stdin"] == "15"
    assert run("print(int(input()) + 1)", q["stdin"]).strip() == "16"


# ---------------------------------------------------------------- kısa cevap
def short(answer, **kw):
    return output_question("print(1)", answer, "s", common_wrongs=[Wrong("x", "y")], **kw)


def test_short_default_behaviour_is_unchanged():
    q = short("3.5")
    assert "norm" not in q and "accept" not in q
    assert qs.grade(q, " 3,5 ")[0] and qs.grade(q, "3 .5")[0] and not qs.grade(q, "35")[0]


def test_short_accept_list():
    q = short("Merhaba Ali", norm="metin", accept=["Merhaba, Ali"])
    assert q["accept"] == ["Merhaba, Ali"] and q["norm"] == "metin"
    assert qs.grade(q, "Merhaba Ali")[0] and qs.grade(q, "  Merhaba   Ali ")[0] and qs.grade(q, "Merhaba, Ali")[0]
    assert qs.grade(q, '"Merhaba Ali"')[0] and qs.grade(q, "'Merhaba Ali'")[0]
    assert not qs.grade(q, "MerhabaAli")[0] and not qs.grade(q, "merhaba ali")[0]


@pytest.mark.parametrize("norm, answer, good, bad", [
    ("sayi", "5", ["5", " 5 ", "'5'"], ["5.0", "05", "6"]),
    ("sayi", "-3.5", ["−3,5", "-3.5", "- 3.5"], ["3.5", "-3.50"]),
    ("sayi_degeri", "5", ["5.0", "5,0", "5", "+5"], ["5.1", "beş"]),
    ("metin", "PYTHON DERSI", ["PYTHON DERSI", "PYTHON  DERSI", '"PYTHON DERSI"'], ["PYTHON DERSİ", "python dersi"]),
    ("metin_esnek", "Çift", ["çift", "Cift", "CIFT", "ÇİFT", " cift "], ["Tek", "Çift sayı"]),
    ("python", "['a', 1]", ['["a",1]', "['a', 1]", "[ 'a' , 1 ]"], ["['a', 1.0]", "[1, 'a']", "['a',1"]),
    ("python", "True", ["True", " True"], ["true", "1"]),
    ("python", "(1, 2)", ["(1,2)", "1, 2"], ["[1, 2]", "(2, 1)"]),
])
def test_short_norm_modes(norm, answer, good, bad):
    q = short(answer, norm=norm)
    for g in good:
        assert qs.grade(q, g)[0], (norm, g)
    for b in bad:
        assert not qs.grade(q, b)[0], (norm, b)


def test_short_norm_is_used_for_whys_and_stats_key():
    q = output_question("print(1)", "Çift", "s", common_wrongs=[Wrong("Tek", "Kalan 0.")], norm="metin_esnek")
    assert qs.why_for(q, " tek ") == "Kalan 0."
    assert qs.short_key(q, "TEK") == qs.short_key(q, "tek")
    legacy = {"type": "short", "answer": "3.5"}
    assert qs.short_key(legacy, "3,5") == qs.short_key(legacy, "3.5")


def test_unknown_norm_is_refused():
    with pytest.raises(ValueError):
        short("1", norm="yok")


def test_short_hostile_python_values():
    q = short("[1]", norm="python")
    for raw in ("[" * 5000, "9" * 5000, "__import__('os')", "(" * 100 + ")" * 100):
        assert qs.grade(q, raw)[0] is False


# ---------------------------------------------------------------- müfredat modülü
def test_curriculum_module_does_not_shadow_catalog_function():
    import importlib

    mod = importlib.import_module("pytest_pro.questions.mufredat")
    assert callable(qs.catalog) and isinstance(qs.catalog(), list)
    assert mod.render().startswith("# Müfredat Haritası")
    assert "python -m pytest_pro.questions.mufredat" in mod.render()
    assert set(mod.VERIFY_NAMES) == set(VERIFY_KINDS), "her doğrulama türünün müfredatta bir adı olmalı"


# ---------------------------------------------------------------- seçenekleri kod olan ÇS
def test_code_options_question_fields():
    from pytest_pro.questions.helpers import code_options_question
    q = code_options_question(
        "Hangisi <code>x</code> 3'e tam bölünüyorsa True verir?", "x % 3 == 0",
        [Wrong("x / 3 == 0", "Yalnızca x 0 iken True olur."), Wrong("x // 3 == 0", "0, 1, 2 için True olur."),
         Wrong("x % 3 == 1", "Kalan 1 ise bölünmez.")],
        cases=[{"setup": f"x = {v}", "expect": str(v % 3 == 0)} for v in range(-6, 7)],
        solution="Tam bölünen sayının kalanı 0'dır.", hint="Kalan kaç olmalı?", harness="print({option})")
    assert q["type"] == "mc" and q["answer"] == "x % 3 == 0" and len(q["options"]) == 4
    assert q["harness"] == "print({option})" and len(q["cases"]) == 13
    assert q["whys"]["x / 3 == 0"] == "Yalnızca x 0 iken True olur."
    assert not {"cases", "harness"} & set(qs.public_question(q))
    assert passing_options(q) == ["x % 3 == 0"]
    broken = dict(q, cases=[{"setup": "x = 0", "stdin": "", "expect": "True"}])  # x = 0 için hepsi True
    assert len(passing_options(broken)) > 1  # test bunu yakalar: tek durum ayırt etmeye yetmiyor
    loops = code_options_question(
        "Hangisi sonsuz döngüdür?", "i = 0\nwhile i < 3:\n    print(i)",
        [Wrong("i = 0\nwhile i < 3:\n    i += 1", "i her turda artar; döngü biter.")],
        cases=[{"expect": LOOP_OUTCOME}], solution="s")
    assert passing_options(loops) == [loops["answer"]]
    with pytest.raises(ValueError):
        code_options_question("t", "a", [Wrong("b", "n")], cases=[{"setup": ""}], solution="s")


def test_outcome_stops_infinite_loops():
    from pytest_pro.questions.helpers import LOOP_OUTCOME
    assert outcome("while True:\n    pass") == LOOP_OUTCOME
    assert outcome("i = 0\nwhile i < 5:\n    i += 1\nprint(i)") == "5"


# ---------------------------------------------------------------- kalite istisnası şablonda
def test_quality_exemption_is_declared_on_the_template():
    from pytest_pro.questions.registry import QUALITY_CHECKS, UNITS
    unit = register_unit("_deneme_istisna", "Deneme", "Başlangıç", "deneme", order=901)
    try:
        @unit.question("Deneme", verify="output", exempt={"top_answer": "Anahtar sözcük sorusu; cevap sabit."})
        def deneme():
            return output_question("print(1)", "1", "s", wrongs=[Wrong("2", "n")], hint="h")

        assert unit.generators[0].exempt == {"top_answer": "Anahtar sözcük sorusu; cevap sabit."}
        assert set(QUALITY_CHECKS) == {"filler", "top_answer", "error_giveaway"}
        with pytest.raises(ValueError):
            unit.question("Deneme", exempt={"yok": "x"})
        with pytest.raises(ValueError):
            unit.question("Deneme", exempt={"filler": "  "})
    finally:
        del UNITS["_deneme_istisna"]
