"""Ünite 10 (Hata Yönetimi) özel testleri."""
import pytest
from helpers import (
    accepts,
    code_q,
    gen_by_name,
    outcome,
    rejects,
    samples,
    top_answer_share,
    variety,
)

from pytest_pro import questions as qs
from pytest_pro.questions.helpers import ERROR_PREFIX

NEW = ["error_claim", "except_blank", "multi_except", "retry_loop", "error_propagation", "concepts2",
       "write_safe_div", "write_parse_guard"]


@pytest.mark.parametrize("name", NEW)
def test_new_templates_are_varied(name):
    gen = gen_by_name(f"hatalar.{name}")
    assert variety(gen) >= 30
    assert top_answer_share(gen)[0] <= 0.40


def test_error_answers_appear_naturally():
    """'Hata verir' doğru cevabı hem çıktı hem hata sonuçlu değişkelerle birlikte bulunmalı."""
    answers = [q["answer"] for q in samples(gen_by_name("hatalar.error_propagation"), 200)]
    share = sum(a.startswith(ERROR_PREFIX) for a in answers) / len(answers)
    assert 0.15 <= share <= 0.5
    outputs = {q["output"].startswith(ERROR_PREFIX) for q in samples(gen_by_name("hatalar.error_claim"))}
    assert outputs == {True, False}


def test_except_blank_answer_is_the_raised_error():
    for q in samples(gen_by_name("hatalar.except_blank"), 60):
        raised = outcome(q["code"].replace("____", "ArithmeticError"))  # yakalanmayan hata türü görünür
        assert q["answer"][0][0] in raised or q["answer"][0][0] == "ZeroDivisionError", (q["code"], raised)


def test_concepts2_pool_is_large():
    texts = {q["text"] for q in samples(gen_by_name("hatalar.concepts2"), 600)}
    assert len(texts) >= 30


# ---------------------------------------------------------------- safe_div (write_safe_div)
DIV = code_q("safe_div", name="guvenli_bol", fallback="None")
DIV_TEXT = code_q("safe_div", name="guvenli_bol", fallback='"Tanımsız"')
DIV_ZERO = code_q("safe_div", name="guvenli_bol", fallback="0")


@pytest.mark.parametrize("src", [
    "def guvenli_bol(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        return None",
    ("def guvenli_bol(x, y):\n    try:\n        sonuc = x / y\n    except ZeroDivisionError:\n        return None\n"
    "    return sonuc"),
    ("def guvenli_bol(a, b):\n    try:\n        sonuc = a / b\n    except ZeroDivisionError:\n        sonuc = None\n"
    "    return sonuc"),
    ("def guvenli_bol(a, b):\n    try:\n        bolum = a / b\n    except ZeroDivisionError:\n        return None\n"
    "    else:\n        return bolum"),
    "def guvenli_bol(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        return",
    ("def guvenli_bol(a, b):\n    # sıfıra bölmeyi yakala\n    try:\n        return a / b\n"
    "    except (ZeroDivisionError, TypeError):\n        return None"),
])
def test_safe_div_accepts(src):
    assert accepts(DIV, src)


def test_safe_div_other_fallbacks():
    assert accepts(DIV_TEXT, "def guvenli_bol(a, b):\n    try:\n        return a / b\n"
                             "    except ZeroDivisionError:\n        return \"Tanımsız\"")
    assert accepts(DIV_ZERO, "def guvenli_bol(a, b):\n    try:\n        return a / b\n"
                             "    except ZeroDivisionError:\n        return 0")
    assert rejects(DIV_ZERO, "def guvenli_bol(a, b):\n    try:\n        return a / b\n"
                             "    except ZeroDivisionError:\n        return None", "0")


def test_safe_div_broad_except_is_accepted_with_note():
    ok, note = qs.grade(DIV, "def guvenli_bol(a, b):\n    try:\n        return a / b\n    except:\n        return None")
    assert ok and "ZeroDivisionError" in note
    ok, note = qs.grade(DIV, "def guvenli_bol(a, b):\n    try:\n        return a / b\n"
                             "    except Exception:\n        return None")
    assert ok and "daha iyi" in note


@pytest.mark.parametrize("src, reason", [
    ("def guvenli_bol(a, b):\n    if b == 0:\n        return None\n    return a / b", "try"),
    ("def guvenli_bol(a, b):\n    try:\n        return a / b\n    except ValueError:\n        return None",
     "ZeroDivisionError"),
    ("def guvenli_bol(a, b):\n    try:\n        print(a / b)\n    except ZeroDivisionError:\n        print(None)", "return"),
    ("def guvenli_bol(a, b):\n    try:\n        return a // b\n    except ZeroDivisionError:\n        return None",
     "a / b"),
    ("def guvenli_bol(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        print(\"Hata\")",
     "sıfır olduğunda"),
    (("def guvenli_bol(a, b):\n    sonuc = a / b\n    try:\n        return sonuc\n    except ZeroDivisionError:\n"
     "        return None"), "try bloğunun içinde"),
    ("def guvenli_bol(a, b):\n    try:\n        return b / a\n    except ZeroDivisionError:\n        return None", "a / b"),
    ("def bol(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        return None", "tanımlanmamış"),
    ("def guvenli_bol(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        return 0",
     "sıfır olduğunda"),
])
def test_safe_div_rejects(src, reason):
    assert rejects(DIV, src, reason)


# ---------------------------------------------------------------- parse_guard (write_parse_guard)
GUARD = code_q("parse_guard", var="veri", factor=2, msg="Geçersiz")


@pytest.mark.parametrize("src", [
    'veri = "12"\ntry:\n    sayi = int(veri)\n    print(sayi * 2)\nexcept ValueError:\n    print("Geçersiz")',
    'veri = "12"\ntry:\n    sayi = int(veri)\nexcept ValueError:\n    print("Geçersiz")\nelse:\n    print(2 * sayi)',
    'veri = "12"\ntry:\n    print(int(veri) * 2)\nexcept ValueError:\n    print("Geçersiz")',
    ('veri = "abc"\ntry:\n    n = int(veri)\n    sonuc = n + n\n    print("Sonuç:", sonuc)\nexcept ValueError:\n'
    '    print("Geçersiz giriş")'),
    ('veri = "12"\ntry:\n    sayi = int(veri)\n    print(f"İki katı: {sayi * 2}")\nexcept ValueError:\n'
    '    print("geçersiz")'),
    ('veri = "12"\n# dönüşümü dene\ntry:\n    sayi = int(veri)\n    print(sayi * 2)\nexcept ValueError:\n'
    '    print("GECERSIZ")'),
    ('veri = "12"\ntry:\n    sayi = int(veri)\n    print(sayi * 2)\nexcept (ValueError, TypeError):\n'
    '    print("Geçersiz")'),
])
def test_parse_guard_accepts(src):
    assert accepts(GUARD, src)


def test_parse_guard_broad_except_is_accepted_with_note():
    ok, note = qs.grade(GUARD, 'veri = "12"\ntry:\n    print(int(veri) * 2)\nexcept:\n    print("Geçersiz")')
    assert ok and "ValueError" in note


@pytest.mark.parametrize("src, reason", [
    ('veri = "12"\nif veri.isdigit():\n    print(int(veri) * 2)\nelse:\n    print("Geçersiz")', "try"),
    ('veri = "12"\nsayi = int(veri)\ntry:\n    print(sayi * 2)\nexcept ValueError:\n    print("Geçersiz")',
     "try bloğunun içinde"),
    ('veri = "12"\ntry:\n    sayi = int(veri)\nexcept ValueError:\n    print("Geçersiz")\nprint(sayi * 2)', "try"),
    ('veri = "12"\ntry:\n    sayi = int(veri)\n    print(sayi * 2)\nexcept TypeError:\n    print("Geçersiz")',
     "ValueError"),
    ('veri = "12"\ntry:\n    sayi = int(veri)\n    print(sayi * 2)\nexcept ValueError:\n    print("Hata")', "Geçersiz"),
    ('veri = "12"\ntry:\n    sayi = int(veri)\n    print(24)\nexcept ValueError:\n    print("Geçersiz")', "katını"),
    ('veri = "12"\ntry:\n    sayi = float(veri)\n    print(sayi * 2)\nexcept ValueError:\n    print("Geçersiz")', "int"),
    ('veri = "12"\ntry:\n    sayi = int(veri)\n    print(sayi * 3)\nexcept ValueError:\n    print("Geçersiz")', "katını"),
    ('sayi = int("12")\ntry:\n    print(sayi * 2)\nexcept ValueError:\n    print("Geçersiz")', "veri"),
])
def test_parse_guard_rejects(src, reason):
    assert rejects(GUARD, src, reason)



# ---------------------------------------------------------------- uzman denetimi (aşama 3)
def test_safe_div_wrong_fallback_value_not_called_printing():
    """except bloğu return ile farklı bir değer döndürüyorsa "ekrana yazdırma" demek yanlış teşhis olur."""
    src = 'def guvenli_bol(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        return "tanımsız"'
    ok, note = qs.grade(DIV_TEXT, src)
    assert not ok and "yazdırma" not in note and "Tanımsız" in note
    src = 'def guvenli_bol(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        print("Tanımsız")'
    assert rejects(DIV_TEXT, src, "yazdırma")
