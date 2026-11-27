"""Ünite 8 (Sözlük, Demet ve Küme) özel testleri."""
import pytest
from helpers import accepts, code_q, gen_by_name, outcome, rejects, samples

from pytest_pro.questions.fill import fill_in

# ---------------------------------------------------------------- write_dict_max (sozluk_en_yuksek)
BEST = code_q("sozluk_en_yuksek", var="notlar", data={"Ali": 72, "Ece": 91, "Can": 65})
D = 'notlar = {"Ali": 72, "Ece": 91, "Can": 65}\n'


@pytest.mark.parametrize("src", [
    D + 'en_iyi = ""\nen_yuksek = -1\nfor ad, puan in notlar.items():\n    if puan > en_yuksek:\n        en_yuksek = puan\n        en_iyi = ad\nprint(en_iyi)',
    D + "en_iyi = None\nfor ad in notlar:\n    if en_iyi is None or notlar[ad] > notlar[en_iyi]:\n        en_iyi = ad\nprint(en_iyi)",
    D + "print(max(notlar, key=notlar.get))",
    D + 'ilk = list(notlar.keys())[0]\nen_iyi = ilk\nfor ad in notlar.keys():\n    if notlar[ad] > notlar[en_iyi]:\n        en_iyi = ad\nprint("En yüksek not:", en_iyi)',
    D + "en_yuksek = 0\nen_iyi = ''\nfor ad, puan in notlar.items():\n    if puan >= en_yuksek:\n        en_yuksek = puan\n        en_iyi = ad\nprint(f'Birinci: {en_iyi}')",
    D + "en_yuksek = max(notlar.values())\nfor ad, puan in notlar.items():\n    if puan == en_yuksek:\n        print(ad)",
])
def test_write_dict_max_accepts(src):
    assert accepts(BEST, src)


@pytest.mark.parametrize("src, reason", [
    (D + 'print("Ece")', "döngü"),
    (D + "en_yuksek = -1\nfor ad, puan in notlar.items():\n    if puan > en_yuksek:\n        en_yuksek = puan\nprint(en_yuksek)", "adını"),
    (D + "print(max(notlar.values()))", "adını"),
    (D + "print(max(notlar))", "harf sırasına"),
    (D + "en_iyi = ''\nen_yuksek = -1\nfor ad, puan in notlar.items():\n    if puan < en_yuksek:\n        en_yuksek = puan\n        en_iyi = ad\nprint(en_iyi)", "karşılaştır"),
    (D + "en_iyi = ''\nen_yuksek = -1\nfor ad, puan in notlar.items():\n    if puan > en_yuksek:\n        en_yuksek = puan\n        en_iyi = ad\n    print(en_iyi)", "bir kez"),
    (D + "en_iyi = ''\nen_yuksek = -1\nfor ad, puan in notlar.items():\n    en_yuksek = puan\n    en_iyi = ad\nprint(en_iyi)", "karşılaştır"),
    ('notlar = {"Ali": 72, "Ece": 91}\nprint(max(notlar, key=notlar.get))', "notlar = "),
    (D + 'for ad in ["Ece"]:\n    print(ad)', "notlar değişkenini"),
])
def test_write_dict_max_rejects(src, reason):
    assert rejects(BEST, src, reason)


# ---------------------------------------------------------------- write_freq (sozluk_sayim)
FREQ = code_q("sozluk_sayim", var="meyveler", items=["elma", "armut", "elma", "kiraz", "elma", "armut"], res="sayim")
M = 'meyveler = ["elma", "armut", "elma", "kiraz", "elma", "armut"]\n'


@pytest.mark.parametrize("src", [
    M + "sayim = {}\nfor m in meyveler:\n    sayim[m] = sayim.get(m, 0) + 1\nprint(sayim)",
    M + "sayim = {}\nfor m in meyveler:\n    if m in sayim:\n        sayim[m] += 1\n    else:\n        sayim[m] = 1\nprint(sayim)",
    M + "sayim = {}\nfor m in meyveler:\n    if m not in sayim:\n        sayim[m] = 0\n    sayim[m] = sayim[m] + 1\nprint(sayim)",
    M + "sayim = dict()\nfor meyve in meyveler:\n    sayim[meyve] = meyveler.count(meyve)\nprint(sayim)",
    M + "sayim = {}\nfor i in range(len(meyveler)):\n    m = meyveler[i]\n    sayim[m] = sayim.get(m, 0) + 1\nprint(\"Sayım:\", sayim)",
    M + "sayim = {}\nfor m in meyveler:\n    if m in sayim.keys():\n        sayim[m] += 1\n    else:\n        sayim[m] = 1\nprint(sayim)",
])
def test_write_freq_accepts(src):
    assert accepts(FREQ, src)


@pytest.mark.parametrize("src, reason", [
    (M + "sayim = {'elma': 3, 'armut': 2, 'kiraz': 1}\nprint(sayim)", "döngü"),
    (M + "sayim = {}\nfor m in meyveler:\n    sayim[m] += 1\nprint(sayim)", "KeyError"),
    (M + "sayim = {}\nfor m in meyveler:\n    sayim[m] = 1\nprint(sayim)", "1 ekle"),
    (M + "sayim = {}\nfor m in meyveler:\n    sayim[m] = sayim.get(m, 0) + 1\n    print(sayim)", "bir kez"),
    (M + "from collections import Counter\nsayim = Counter(meyveler)\nprint(sayim)", "hazır"),
    (M + "sayim = {}\nfor m in meyveler:\n    sayim[m] = sayim.get(m, 1) + 1\nprint(sayim)", "get"),
    (M + "sayim = {}\nfor m in ['elma', 'armut', 'elma', 'kiraz', 'elma', 'armut']:\n    sayim[m] = sayim.get(m, 0) + 1\nprint(sayim)", "meyveler değişkenini"),
    (M + "sayim = {}\nfor m in meyveler:\n    sayim[m] = sayim.get(m, 0) + 1\nprint(meyveler)", "sayim"),
])
def test_write_freq_rejects(src, reason):
    assert rejects(FREQ, src, reason)


# ---------------------------------------------------------------- şablonlar
def test_dict_view_blank_methods_vary():
    seen = set()
    for q in samples(gen_by_name("koleksiyonlar.dict_view_blank"), 120):
        (alts,) = q["answer"]
        assert len(alts) == 1
        seen.add(alts[0])
        for other in {"keys", "values", "items"} - set(alts):
            assert outcome(fill_in(q["code"], [other])) != q["expect"]
    assert seen == {"keys", "values", "items"}


def test_dict_in_claim_covers_keys_values_and_missing():
    codes = " ".join(q["code"] for q in samples(gen_by_name("koleksiyonlar.dict_in_claim"), 200))
    assert ".values()" in codes and "in notlar)" in codes


def test_set_claim_covers_single_element_tuple():
    codes = [q["code"] for q in samples(gen_by_name("koleksiyonlar.set_claim"), 200)]
    assert any("type(" in c for c in codes) and any(".add(" in c for c in codes)


def test_dict_size_ops_answers_vary():
    answers = {q["answer"] for q in samples(gen_by_name("koleksiyonlar.dict_size_ops"), 200)}
    assert len(answers) >= 5


def test_dict_dup_key_error_option_is_not_always_shown():
    shown = sum(any(o.startswith("Hata verir") for o in q["options"])
                for q in samples(gen_by_name("koleksiyonlar.dict_dup_key"), 200))
    assert shown <= 120


def test_code_templates_model_answers_vary():
    for name in ("koleksiyonlar.write_dict_max", "koleksiyonlar.write_freq"):
        assert len({q["answer"] for q in samples(gen_by_name(name), 60)}) > 30



# ---------------------------------------------------------------- uzman denetimi (aşama 3)
def test_dict_max_last_student_named_even_when_last_is_lowest():
    """Ad döngüden sonra atanırsa kod hep son öğrenciyi yazar; son öğrenci tesadüfen en düşük notlu olsa da
    teşhis "son öğrenci" olmalı."""
    q = code_q("sozluk_en_yuksek", var="notlar", data={"Deniz": 75, "Mert": 97, "Ali": 64})
    src = ("notlar = {'Deniz': 75, 'Mert': 97, 'Ali': 64}\nen_iyi = ''\nen_yuksek = -1\n"
           "for ad, puan in notlar.items():\n    if puan > en_yuksek:\n        en_yuksek = puan\nen_iyi = ad\n"
           "print(en_iyi)")
    assert rejects(q, src, "son öğrenciyi")


def test_freq_dict_reset_inside_loop_is_named():
    src = ("meyveler = ['elma', 'armut', 'elma', 'kiraz', 'elma', 'armut']\nfor m in meyveler:\n    sayim = {}\n"
           "    sayim[m] = sayim.get(m, 0) + 1\nprint(sayim)")
    assert rejects(FREQ, src, "döngüden önce")
