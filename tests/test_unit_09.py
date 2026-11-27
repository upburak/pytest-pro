"""Ünite 9 (Fonksiyonlar ve Modüller) özel testleri."""
import json

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
from pytest_pro.questions.fill import fill_in

NEW = ["print_return_claim", "call_args_blank", "global_blank", "keyword_args", "func_compose", "which_function",
       "write_is_even", "write_mean_func", "write_factorial"]


@pytest.mark.parametrize("name", NEW)
def test_new_templates_are_varied(name):
    gen = gen_by_name(f"fonksiyonlar.{name}")
    assert variety(gen) >= 30
    assert top_answer_share(gen)[0] <= 0.40


# ---------------------------------------------------------------- bool_func (write_is_even)
EVEN = code_q("bool_func", name="cift_mi", pred="cift")


@pytest.mark.parametrize("src", [
    "def cift_mi(n):\n    return n % 2 == 0",
    "def cift_mi(sayi):\n    if sayi % 2 == 0:\n        return True\n    else:\n        return False",
    "def cift_mi(n):\n    if n % 2 == 0:\n        return True\n    return False",
    "def cift_mi(x):\n    kalan = x % 2\n    sonuc = kalan == 0\n    return sonuc",
    "def cift_mi(n):\n    return n % 2 != 1",
    "def cift_mi(n):\n    # çift sayıların kalanı 0'dır\n    if n % 2 == 1:\n        return False\n    else:\n        return True",
    "def cift_mi(n):\n    return not n % 2",
    "def cift_mi(n):\n    if n % 2 == 0:\n        cevap = True\n    else:\n        cevap = False\n    return cevap",
])
def test_bool_func_accepts(src):
    assert accepts(EVEN, src)


@pytest.mark.parametrize("src, reason", [
    ("def cift_mi(n):\n    print(n % 2 == 0)", "return"),
    ("def cift_mi(n):\n    return n % 2", "True ya da False"),
    ("def cift_mi(n):\n    return n % 2 == 1", "yanlış sonuç"),
    ("def cift_mi(n):\n    if n % 2 == 0:\n        return True", "None"),
    ("def cift(n):\n    return n % 2 == 0", "tanımlanmamış"),
    ("def cift_mi(a, b):\n    return a % 2 == 0", "bir parametre"),
    ("def cift_mi(n):\n    return True", "yanlış sonuç"),
    ("def cift_mi(n):\n    if n % 2 == 0:\n        return \"True\"\n    return \"False\"", "True ya da False"),
])
def test_bool_func_rejects(src, reason):
    assert rejects(EVEN, src, reason)


def test_bool_func_other_predicates():
    pos = code_q("bool_func", name="pozitif_mi", pred="pozitif")
    assert accepts(pos, "def pozitif_mi(n):\n    return n > 0")
    assert rejects(pos, "def pozitif_mi(n):\n    return n >= 0", "yanlış sonuç")
    five = code_q("bool_func", name="bese_bolunur_mu", pred="bes")
    assert accepts(five, "def bese_bolunur_mu(n):\n    if n % 5 == 0:\n        return True\n    return False")
    assert rejects(five, "def bese_bolunur_mu(n):\n    return n // 5 == 0", "yanlış sonuç")


# ---------------------------------------------------------------- mean_func (write_mean_func)
MEAN = code_q("mean_func", name="ortalama")


@pytest.mark.parametrize("src", [
    "def ortalama(liste):\n    return sum(liste) / len(liste)",
    "def ortalama(sayilar):\n    toplam = sum(sayilar)\n    adet = len(sayilar)\n    return toplam / adet",
    "def ortalama(liste):\n    toplam = 0\n    for x in liste:\n        toplam += x\n    return toplam / len(liste)",
    ("def ortalama(liste):\n    toplam = 0\n    sayac = 0\n    for s in liste:\n        toplam = toplam + s\n"
    "        sayac += 1\n    return toplam / sayac"),
    ("def ortalama(liste):\n    toplam = 0\n    for i in range(len(liste)):\n        toplam += liste[i]\n"
    "    return toplam / len(liste)"),
    "def ortalama(notlar):\n    ort = sum(notlar) / len(notlar)\n    return ort",
    "def ortalama(liste):\n    \"\"\"Listenin ortalaması.\"\"\"\n    return round(sum(liste) / len(liste), 2)",
])
def test_mean_func_accepts(src):
    assert accepts(MEAN, src)


@pytest.mark.parametrize("src, reason", [
    ("def ortalama(liste):\n    return sum(liste) // len(liste)", "//"),
    ("def ortalama(liste):\n    print(sum(liste) / len(liste))", "return"),
    ("def ortalama(liste):\n    return sum(liste) / 3", "ortalama değil"),
    ("def ortalama(liste):\n    return sum(liste)", "ortalama değil"),
    (("def ortalama(liste):\n    toplam = 0\n    for x in liste:\n        toplam += x\n        break\n"
     "    return toplam / len(liste)"), "break"),
    ("def ortalama(liste):\n    toplam = 1\n    for x in liste:\n        toplam += x\n    return toplam / len(liste)",
     "ortalama değil"),
    ("def ort(liste):\n    return sum(liste) / len(liste)", "tanımlanmamış"),
    (("def ortalama(liste):\n    toplam = 0\n    for x in liste:\n        toplam += x\n"
     "        return toplam / len(liste)"), "return"),
])
def test_mean_func_rejects(src, reason):
    assert rejects(MEAN, src, reason)


# ---------------------------------------------------------------- factorial (write_factorial)
FACT = code_q("factorial", name="faktoriyel", method=None)
FACT_LOOP = code_q("factorial", name="faktoriyel", method="dongu")
FACT_REC = code_q("factorial", name="faktoriyel", method="ozyineleme")


@pytest.mark.parametrize("src", [
    "def faktoriyel(n):\n    sonuc = 1\n    for i in range(1, n + 1):\n        sonuc *= i\n    return sonuc",
    "def faktoriyel(n):\n    carpim = 1\n    for i in range(2, n + 1):\n        carpim = carpim * i\n    return carpim",
    "def faktoriyel(n):\n    sonuc = 1\n    while n > 1:\n        sonuc *= n\n        n -= 1\n    return sonuc",
    "def faktoriyel(n):\n    if n <= 1:\n        return 1\n    return n * faktoriyel(n - 1)",
    "def faktoriyel(n):\n    if n == 0:\n        return 1\n    else:\n        return faktoriyel(n - 1) * n",
    "def faktoriyel(sayi):\n    if sayi < 2:\n        return 1\n    onceki = faktoriyel(sayi - 1)\n    return sayi * onceki",
    "def faktoriyel(n):\n    sonuc = 1\n    for i in range(n, 0, -1):\n        sonuc = i * sonuc\n    return sonuc",
])
def test_factorial_accepts(src):
    assert accepts(FACT, src)


def test_factorial_method_requirement_accepts():
    loop = "def faktoriyel(n):\n    sonuc = 1\n    for i in range(1, n + 1):\n        sonuc *= i\n    return sonuc"
    rec = "def faktoriyel(n):\n    if n <= 1:\n        return 1\n    return n * faktoriyel(n - 1)"
    assert accepts(FACT_LOOP, loop) and accepts(FACT_REC, rec)
    assert rejects(FACT_LOOP, rec, "döngü") and rejects(FACT_REC, loop, "kendini çağırarak")


@pytest.mark.parametrize("src, reason", [
    ("import math\n\ndef faktoriyel(n):\n    return math.factorial(n)", "kendin yaz"),
    ("def faktoriyel(n):\n    sonuc = 1\n    for i in range(1, n):\n        sonuc *= i\n    return sonuc", "döndürmeli"),
    ("def faktoriyel(n):\n    if n == 1:\n        return 1\n    return n * faktoriyel(n - 1)", "durma koşul"),
    ("def faktoriyel(n):\n    sonuc = 0\n    for i in range(1, n + 1):\n        sonuc *= i\n    return sonuc",
     "döndürmeli"),
    ("def faktoriyel(n):\n    sonuc = 1\n    for i in range(1, n + 1):\n        sonuc *= i\n    print(sonuc)",
     "return"),
    ("def faktoriyel(n):\n    if n <= 1:\n        return 1\n    return n * faktoriyel(n)", "durma koşul"),
    ("def faktoriyel(n):\n    sonuc = 1\n    while n > 1:\n        sonuc *= n\n    return sonuc", "bitmiyor"),
    (("def faktoriyel(n):\n    sonuc = 1\n    for i in range(1, n + 1):\n        sonuc *= i\n        break\n"
     "    return sonuc"), "break"),
])
def test_factorial_rejects(src, reason):
    assert rejects(FACT, src, reason)


# ---------------------------------------------------------------- şablona özel
def test_call_args_blank_accepts_every_call_with_the_target_output():
    """Kabul listesi kaba kuvvetle üretilir: her kabul ortak testte çalıştırılır; burada ilk cevabın
    soruda istenen biçim olduğu ve konumsal/isimli biçimlerin birlikte bulunduğu denetlenir."""
    for q in samples(gen_by_name("fonksiyonlar.call_args_blank"), 60):
        alts = q["answer"][0]
        assert any("=" in a for a in alts) and any("=" not in a for a in alts), alts
        assert qs.grade(q, json.dumps([alts[0]]))[0]


def test_global_blank_operator_is_unique():
    for q in samples(gen_by_name("fonksiyonlar.global_blank"), 60):
        ok = [op for op in ("+=", "-=", "*=", "//=", "=")
              if outcome(fill_in(q["code"], ["global", op])) == q["expect"]]
        assert ok == q["answer"][1], (q["code"], ok)


def test_print_return_claim_has_error_and_output_variants():
    outputs = {q["output"].startswith("Hata verir") for q in samples(gen_by_name("fonksiyonlar.print_return_claim"))}
    assert outputs == {True, False}



# ---------------------------------------------------------------- uzman denetimi (aşama 3)
def test_function_names_do_not_contradict_their_body():
    """iki_kat(x) içinde x * 5, artir() içinde skor -= 4 gibi yanıltıcı adlar olmamalı."""
    import re
    for q in samples(gen_by_name("fonksiyonlar.print_return_claim"), 400):
        m = re.search(r"def iki_kat\((\w+)\):\n.*?\1 ([*+]) (\d+)", q["code"], re.S)
        if m:
            assert m.group(2) == "*" and m.group(3) == "2", q["code"]
        m = re.search(r"def artir\((\w+)\):\n.*?\1 ([*+]) (\d+)", q["code"], re.S)
        if m:
            assert m.group(2) == "+", q["code"]
    for q in samples(gen_by_name("fonksiyonlar.global_blank"), 400):
        if "def artir()" in q["code"]:
            assert q["answer"][1] == ["+="], q["code"]



@pytest.mark.parametrize("src", [
    "def fakt(n):\n    return 1 if n == 0 else n * fakt(n - 1)",
    "def fakt(n):\n    return n * fakt(n - 1) if n > 1 else 1",
])
def test_factorial_recursive_conditional_expression_accepted(src):
    """Koşul ifadesinde (x if k else y) yalnızca seçilen dal hesaplanmalı; fakt(-1) erken çağrılmamalı."""
    q = code_q("factorial", name="fakt", method="ozyineleme")
    assert accepts(q, src)


def test_factorial_base_case_one_names_zero():
    """if n == 1 durma koşulu fakt(0) için bitmez; not 0! durumunu işaret etmeli."""
    q = code_q("factorial", name="fakt", method="ozyineleme")
    assert rejects(q, "def fakt(n):\n    if n == 1:\n        return 1\n    return n * fakt(n - 1)", "fakt(0)")
