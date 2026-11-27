"""Ünite 7 (Listeler) özel testleri."""
import pytest
from helpers import accepts, code_q, gen_by_name, outcome, rejects, samples

from pytest_pro.questions.fill import fill_in

# ---------------------------------------------------------------- write_max_loop (liste_en_buyuk)
MAX = code_q("liste_en_buyuk", var="sayilar", nums=[12, 45, 7, 33, 28])
L = "sayilar = [12, 45, 7, 33, 28]\n"


@pytest.mark.parametrize("src", [
    L + "en_buyuk = sayilar[0]\nfor s in sayilar:\n    if s > en_buyuk:\n        en_buyuk = s\nprint(en_buyuk)",
    L + "en_buyuk = sayilar[0]\nfor s in sayilar[1:]:\n    if s > en_buyuk:\n        en_buyuk = s\nprint(\"En büyük:\", en_buyuk)",
    L + "eb = sayilar[0]\nfor i in range(len(sayilar)):\n    if sayilar[i] > eb:\n        eb = sayilar[i]\nprint(eb)",
    L + "eb = sayilar[0]\ni = 1\nwhile i < len(sayilar):\n    if sayilar[i] >= eb:\n        eb = sayilar[i]\n    i += 1\nprint(eb)",
    L + "en_buyuk = None\nfor s in sayilar:\n    if en_buyuk is None or s > en_buyuk:\n        en_buyuk = s\nprint(en_buyuk)",
    L + "en_buyuk = sayilar[0]\nfor s in sayilar:\n    if en_buyuk < s:\n        en_buyuk = s\nprint(f\"Sonuç: {en_buyuk}\")",
])
def test_write_max_loop_accepts(src):
    assert accepts(MAX, src)


@pytest.mark.parametrize("src, reason", [
    (L + "print(max(sayilar))", "max()"),
    (L + "sayilar.sort()\nprint(sayilar[-1])", "sort"),
    (L + "print(sorted(sayilar)[-1])", "sorted"),
    (L + "print(45)", "döngü"),
    (L + "en_buyuk = 0\nfor s in sayilar:\n    if s > en_buyuk:\n        en_buyuk = s\nprint(en_buyuk)", "ilk eleman"),
    (L + "en_buyuk = sayilar[0]\nfor s in sayilar:\n    if s < en_buyuk:\n        en_buyuk = s\nprint(en_buyuk)", "karşılaştırma"),
    (L + "en_buyuk = sayilar[0]\nfor s in sayilar:\n    if s > en_buyuk:\n        en_buyuk = s\n    print(en_buyuk)", "bir kez"),
    (L + "en_buyuk = sayilar[0]\nfor s in sayilar:\n    if s > en_buyuk:\n        en_buyuk = s\n        break\nprint(en_buyuk)", "break"),
    ("sayilar = [12, 45, 7]\nen_buyuk = sayilar[0]\nfor s in sayilar:\n    if s > en_buyuk:\n        en_buyuk = s\nprint(en_buyuk)",
     "sayilar = [12, 45, 7, 33, 28]"),
    (L + "en_buyuk = sayilar[0]\nfor s in sayilar:\n    en_buyuk = s\nprint(en_buyuk)", "karşılaştır"),
])
def test_write_max_loop_rejects(src, reason):
    assert rejects(MAX, src, reason)


# ---------------------------------------------------------------- write_filter_even (liste_suzme)
EVEN = code_q("liste_suzme", var="sayilar", nums=[4, 7, 10, 3, 8, 15], res="ciftler", rule="even", k=2)
LE = "sayilar = [4, 7, 10, 3, 8, 15]\n"


@pytest.mark.parametrize("src", [
    LE + "ciftler = []\nfor s in sayilar:\n    if s % 2 == 0:\n        ciftler.append(s)\nprint(ciftler)",
    LE + "ciftler = [s for s in sayilar if s % 2 == 0]\nprint(ciftler)",
    LE + "ciftler = []\nfor i in range(len(sayilar)):\n    if sayilar[i] % 2 != 1:\n        ciftler.append(sayilar[i])\nprint(ciftler)",
    LE + "ciftler = []\nfor s in sayilar:\n    if not s % 2:\n        ciftler += [s]\nprint(ciftler)",
    LE + "ciftler = []\nfor s in sayilar:\n    if s % 2 == 0:\n        ciftler = ciftler + [s]\nprint(\"Çiftler:\", ciftler)",
    LE + "ciftler = list()\ni = 0\nwhile i < len(sayilar):\n    if sayilar[i] % 2 == 0:\n        ciftler.append(sayilar[i])\n    i += 1\nprint(ciftler)",
])
def test_write_filter_even_accepts(src):
    assert accepts(EVEN, src)


@pytest.mark.parametrize("src, reason", [
    (LE + "ciftler = [4, 10, 8]\nprint(ciftler)", "döngü"),
    (LE + "ciftler = []\nfor s in [4, 10, 8]:\n    ciftler.append(s)\nprint(ciftler)", "sayilar değişkenini"),
    (LE + "for s in sayilar:\n    if s % 2 == 1:\n        sayilar.remove(s)\nprint(sayilar)", "remove"),
    (LE + "ciftler = []\nfor s in sayilar:\n    if s % 2 == 0:\n        ciftler.append(s)\n        print(ciftler)", "bir kez"),
    (LE + "ciftler = []\nfor s in sayilar:\n    if s % 2 == 0:\n        ciftler.append(s)\nprint(sayilar)", "ciftler"),
    (LE + "ciftler = []\nfor s in sayilar:\n    if s % 2 == 1:\n        ciftler.append(s)\nprint(ciftler)", "koşul"),
    (LE + "ciftler = []\nfor s in sayilar:\n    if s % 2 == 0:\n        ciftler = [s]\nprint(ciftler)", "append"),
    (LE + "ciftler = []\nfor s in sayilar:\n    if s % 2 == 0:\n        ciftler.append(s)\n    else:\n        break\nprint(ciftler)", "break"),
    (LE + "for s in sayilar:\n    if s % 2 == 0:\n        print(s)", "ciftler"),
])
def test_write_filter_even_rejects(src, reason):
    assert rejects(EVEN, src, reason)


def test_filter_rules():
    big = code_q("liste_suzme", var="sayilar", nums=[4, 17, 10, 23], res="buyukler", rule="gt", k=10)
    assert accepts(big, "sayilar = [4, 17, 10, 23]\nbuyukler = [s for s in sayilar if s > 10]\nprint(buyukler)")
    assert rejects(big, "sayilar = [4, 17, 10, 23]\nbuyukler = [s for s in sayilar if s >= 10]\nprint(buyukler)", "koşul")
    div = code_q("liste_suzme", var="sayilar", nums=[9, 4, 12], res="ucler", rule="div", k=3)
    assert accepts(div, "sayilar = [9, 4, 12]\nucler = []\nfor s in sayilar:\n    if s % 3 == 0:\n        ucler.append(s)\nprint(ucler)")


# ---------------------------------------------------------------- şablonlar
def test_list_method_blank_has_single_method():
    methods = set()
    for q in samples(gen_by_name("listeler.list_method_blank"), 150):
        (alts,) = q["answer"]
        assert len(alts) == 1
        methods.add(alts[0])
    assert {"append", "remove", "pop", "insert", "sort", "reverse"} <= methods


def test_comp_blank_alternatives_all_work():
    for q in samples(gen_by_name("listeler.comp_blank"), 60):
        for alt in q["answer"][0]:
            assert outcome(fill_in(q["code"], [alt])) == q["expect"]


def test_nested_list_sometimes_raises_index_error():
    answers = [q["answer"] for q in samples(gen_by_name("listeler.nested_list"), 200)]
    share = sum(a == "Hata verir (IndexError)" for a in answers) / len(answers)
    assert 0.15 <= share <= 0.35


def test_list_copy_covers_every_copy_style():
    codes = " ".join(q["code"] for q in samples(gen_by_name("listeler.list_copy"), 200))
    for style in ("b = a\n", "b = a[:]", "b = a.copy()", "b = list(a)"):
        assert style in codes


def test_code_templates_model_answers_vary():
    for name in ("listeler.write_max_loop", "listeler.write_filter_even"):
        assert len({q["answer"] for q in samples(gen_by_name(name), 60)}) > 30



# ---------------------------------------------------------------- uzman denetimi (aşama 3)
def test_comp_blank_accepts_subtraction_when_same_decade():
    """range(25, 29) -> [5, 6, 7, 8]: "s - 20" de aynı listeyi verir ve kabul edilmeli."""
    import re
    seen = 0
    for q in samples(gen_by_name("listeler.comp_blank"), 400):
        alts = q["answer"][0]
        if not any("% 10" in a for a in alts):
            continue
        a, b = map(int, re.search(r"range\((\d+), (\d+)\)", q["code"]).groups())
        v = re.search(r"for (\w+) in", q["code"]).group(1)
        if a // 10 == (b - 1) // 10:
            seen += 1
            assert f"{v} - {a - a % 10}" in alts
            assert outcome(fill_in(q["code"], [f"{v} - {a - a % 10}"])) == q["expect"]
    assert seen



def test_filter_list_reset_inside_loop_is_named():
    """Liste döngü içinde boşaltılıyorsa "yeni bir listede tutulmalı" demek yanıltıcıdır."""
    src = ("sayilar = [4, 7, 10, 3, 8, 15]\nfor s in sayilar:\n    ciftler = []\n    if s % 2 == 0:\n"
           "        ciftler.append(s)\nprint(ciftler)")
    assert rejects(EVEN, src, "döngüden önce")
