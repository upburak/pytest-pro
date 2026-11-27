"""Ünite 2 (Veri Tipleri ve Dönüşümler) özel testleri."""
import json

import pytest
from helpers import accepts, code_q, gen_by_name, outcome, rejects, samples, top_answer_share, variety

from pytest_pro import questions as qs
from pytest_pro.questions.fill import fill_in

NEW = ["veri_tipleri.type_claim", "veri_tipleri.input_int_blank", "veri_tipleri.conv_direction_blank",
       "veri_tipleri.mixed_conv", "veri_tipleri.bool_arith", "veri_tipleri.write_text_sum",
       "veri_tipleri.write_celsius"]


@pytest.mark.parametrize("name", NEW)
def test_new_templates_are_varied(name):
    gen = gen_by_name(name)
    assert variety(gen) >= 30
    assert top_answer_share(gen)[0] <= 0.40


def test_type_claim_mentions_a_type():
    for q in samples(gen_by_name("veri_tipleri.type_claim"), 60):
        assert q["claim"].startswith("<class '") and "&lt;class" in q["text"]


def test_input_int_blank_uses_keyboard_input():
    kinds = set()
    for q in samples(gen_by_name("veri_tipleri.input_int_blank"), 80):
        assert q["stdin"] and "input()" in fill_in(q["code"], [a[0] for a in q["answer"]])
        assert q["stdin"] in q["text"]
        kinds.add(q["answer"][0][0])
    assert kinds == {"int", "float"}


def test_conv_direction_answers_vary():
    answers = {q["answer"][0][0] for q in samples(gen_by_name("veri_tipleri.conv_direction_blank"), 80)}
    assert answers == {"int", "str", "float"}


def test_mixed_conv_measures_type():
    """Tip ölçülür: 9.5 doğru, 9,5 kabul; 9.50 ve tam sayı karşılıkları kabul edilmez."""
    for q in samples(gen_by_name("veri_tipleri.mixed_conv"), 80):
        assert q["norm"] == "sayi" and len(q["whys"]) >= 2
        if "." in q["answer"]:
            assert qs.grade(q, q["answer"].replace(".", ","))[0]
            assert not qs.grade(q, q["answer"] + "0")[0]


def test_bool_arith_answers_are_numbers():
    for q in samples(gen_by_name("veri_tipleri.bool_arith"), 80):
        assert outcome(q["code"]).lstrip("-").isdigit() and len(q["whys"]) >= 2


# ---------------------------------------------------------------- write_text_sum
TSUM = code_q("text_sum", v1="a", v2="b", s1="7", s2="5")


@pytest.mark.parametrize("src", [
    'a = "7"\nb = "5"\nprint(int(a) + int(b))',
    'a = "7"\nb = "5"\nprint(int(b) + int(a))',
    'a = "7"\nb = "5"\na = int(a)\nb = int(b)\nprint(a + b)',
    'a = "7"\nb = "5"\ntoplam = int(a) + int(b)\nprint("Toplam:", toplam)',
    'a = "7"\nb = "5"\nprint(f"Toplam: {int(a) + int(b)}")',
    "a = '7'\nb = '5'\nx = int(a)\ny = int(b)\nprint(x + y)",
    'a, b = "7", "5"\nprint(int(a) + int(b))',
    'a = "7"\nb = "5"\nprint("Toplam = " + str(int(a) + int(b)))',
])
def test_text_sum_accepts(src):
    assert accepts(TSUM, src)


@pytest.mark.parametrize("src, reason", [
    ('a = "7"\nb = "5"\nprint(a + b)', "75"),
    ('a = "7"\nb = "5"\nprint(12)', "elle yazma"),
    ('a = "7"\nb = "5"\nprint(float(a) + float(b))', "float"),
    ("a = 7\nb = 5\nprint(a + b)", "tırnak"),
    ('a = "7"\nb = "5"\nprint(int(a + b))', "birleştirip"),
    ('a = "7"\nb = "5"\nprint(int(a) * int(b))', "toplam"),
    ('a = "7"\nb = "5"', "print"),
    ('a = "7"\nb = "5"\nprint(int(a), int(b), int(a) + int(b))', "Yalnızca"),
    ('a = "7"\nb = "5"\nsonuc = 12\nprint(sonuc)', "elle yazma"),
])
def test_text_sum_rejects(src, reason):
    assert rejects(TSUM, src, reason)


# ---------------------------------------------------------------- write_celsius
CELS = code_q("celsius", var="c", c=25)


@pytest.mark.parametrize("src", [
    "c = 25\nprint(c * 9 / 5 + 32)",
    "c = 25\nprint(1.8 * c + 32)",
    "c = 25\nprint((c * 9 / 5) + 32)",
    "c = 25\nprint(32 + c * 1.8)",
    "c = 25\nf = c * 9 / 5 + 32\nprint(f)",
    'c = 25\nprint("Fahrenheit:", c * 9 / 5 + 32)',
    'c = 25\nprint(f"{c * 9 / 5 + 32} F")',
    "c = 25\nfahrenheit = c * 1.8\nfahrenheit = fahrenheit + 32\nprint(fahrenheit)",
])
def test_celsius_accepts(src):
    assert accepts(CELS, src)


@pytest.mark.parametrize("src, reason", [
    ("c = 25\nprint(77)", "elle yazma"),
    ("c = 25\nprint(c * 9 / 5)", "32"),
    ("c = 25\nprint(c * 5 / 9 + 32)", "9 / 5"),
    ("c = 30\nprint(c * 9 / 5 + 32)", "<code>c</code> değişkenine"),
    ("c = 25\nprint(c * 9 / (5 + 32))", "işlem"),
    ("c = 25", "print"),
    ("c = 25\nprint(c, c * 9 / 5 + 32)", "Yalnızca"),
    ("c = 25\nf = 77\nprint(f)", "elle yazma"),
])
def test_celsius_rejects(src, reason):
    assert rejects(CELS, src, reason)


def test_celsius_float_answers_are_exact():
    for q in samples(gen_by_name("veri_tipleri.write_celsius"), 40):
        assert qs.grade(q, q["answer"])[0]
        assert json.dumps(q["check"])



# ---------------------------------------------------------------- uzman denetimi (aşama 3): haksız ret/kabul
def test_text_sum_accepts_sum_of_list():
    q = code_q("text_sum", v1="a", v2="b", s1="35", s2="12")
    assert accepts(q, 'a = "35"\nb = "12"\nprint(sum([int(a), int(b)]))')
    assert accepts(q, 'a = "35"\nb = "12"\nprint(sum((int(a), int(b))))')


def test_text_sum_mixed_types_named_as_type_error():
    q = code_q("text_sum", v1="a", v2="b", s1="35", s2="12")
    assert rejects(q, 'a = "35"\nb = "12"\nprint(int(a) + b)', "TypeError")
    assert rejects(q, 'a = "35"\nb = "12"\nprint(a + int(b))', "TypeError")


@pytest.mark.parametrize("src", [
    "c = 45\nprint(c * 9 // 5 + 32)",
    "c = 45\nprint(int(c * 9 / 5 + 32))",
])
def test_celsius_rejects_truncation_even_when_exact(src):
    """c = 45 iken // ve int() tesadüfen doğru sonuç verir; başka değerlerde kesir atılır."""
    q = code_q("celsius", var="c", c=45)
    assert rejects(q, src, "kesir")
