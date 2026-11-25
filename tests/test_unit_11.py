"""Ünite 11 (Nesne Yönelimli Programlama) özel testleri."""
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

from pytest_pro.questions.fill import fill_in

NEW = ["attr_shadow_claim", "self_blank", "super_blank", "account_trace", "isinstance_check", "object_list",
       "write_rect_class", "write_counter_class"]


@pytest.mark.parametrize("name", NEW)
def test_new_templates_are_varied(name):
    gen = gen_by_name(f"nesne.{name}")
    assert variety(gen) >= 30
    assert top_answer_share(gen)[0] <= 0.40


def test_isinstance_options_are_all_four_combinations():
    for q in samples(gen_by_name("nesne.isinstance_check"), 60):
        assert sorted(q["options"]) == ["False False", "False True", "True False", "True True"]
        assert outcome(q["code"]) == q["answer"]


def test_self_blank_needs_self_in_definition():
    for q in samples(gen_by_name("nesne.self_blank"), 40):
        attr = q["answer"][1][0]
        assert outcome(fill_in(q["code"], ["bu", attr])) != q["expect"]


# ---------------------------------------------------------------- class_method (write_rect_class)
RECT = code_q("class_method", cls="Dikdortgen", params=["en", "boy"], method="alan", formula="dikdortgen_alan")

RECT_OK = ("class Dikdortgen:\n    def __init__(self, en, boy):\n        self.en = en\n        self.boy = boy\n\n"
           "    def alan(self):\n        return self.en * self.boy")


@pytest.mark.parametrize("src", [
    RECT_OK,
    ("class Dikdortgen:\n    def __init__(self, a, b):\n        self.a = a\n        self.b = b\n\n"
    "    def alan(self):\n        return self.b * self.a"),
    ("class Dikdortgen:\n    def __init__(self, en, boy):\n        self.genislik = en\n        self.yukseklik = boy\n\n"
    "    def alan(self):\n        sonuc = self.genislik * self.yukseklik\n        return sonuc"),
    ("class Dikdortgen:\n    \"\"\"Dikdörtgen.\"\"\"\n\n    def __init__(self, en, boy):\n        self.en = en\n"
    "        self.boy = boy\n        self.renk = \"mavi\"\n\n    def alan(self):\n        return self.en * self.boy\n\n"
    "    def cevre(self):\n        return 2 * (self.en + self.boy)"),
    RECT_OK + "\n\nd = Dikdortgen(3, 4)\nprint(d.alan())",
    ("class Dikdortgen:\n    def __init__(s, en, boy):\n        s.en = en\n        s.boy = boy\n\n"
    "    def alan(s):\n        return s.en * s.boy"),
    ("class Dikdortgen():\n    def __init__(self, en, boy):\n        self.en, self.boy = en, boy\n\n"
    "    def alan(self):\n        return (self.en) * (self.boy)"),
])
def test_class_method_accepts(src):
    assert accepts(RECT, src)


@pytest.mark.parametrize("src, reason", [
    (RECT_OK.replace("return self.en * self.boy", "print(self.en * self.boy)"), "return"),
    (RECT_OK.replace("def alan(self):", "def alan():"), "self"),
    (RECT_OK.replace("return self.en * self.boy", "return en * boy"), "self.en"),
    (("class Dikdortgen:\n    def __init__(self, en, boy):\n        self.en = en\n        self.boy = boy\n"
     "        self.sonuc = en * boy\n\n    def alan(self):\n        return self.sonuc"), "metodun içinde"),
    (RECT_OK.replace("return self.en * self.boy", "return self.en + self.boy"), "formülü"),
    (RECT_OK.replace("class Dikdortgen:", "class Dortgen:"), "tanımlanmamış"),
    (RECT_OK.replace("        self.boy = boy\n", ""), "saklamalı"),
    (RECT_OK.replace("def alan(self):", "def hesapla(self):"), "alan"),
    (RECT_OK.replace("def __init__(self, en, boy):", "def __init__(self, en):"), "parametre"),
])
def test_class_method_rejects(src, reason):
    assert rejects(RECT, src, reason)


def test_class_method_other_shapes():
    square = code_q("class_method", cls="Kare", params=["kenar"], method="cevre", formula="kare_cevre")
    assert accepts(square, "class Kare:\n    def __init__(self, kenar):\n        self.kenar = kenar\n\n"
                           "    def cevre(self):\n        return 4 * self.kenar")
    assert rejects(square, "class Kare:\n    def __init__(self, kenar):\n        self.kenar = kenar\n\n"
                           "    def cevre(self):\n        return self.kenar * self.kenar", "formülü")


# ---------------------------------------------------------------- counter_class (write_counter_class)
COUNTER = code_q("counter_class", cls="Sayac", attr="deger", inc="arttir", other="sifirla", other_kind="sifirla")
COUNTER_OK = ("class Sayac:\n    def __init__(self):\n        self.deger = 0\n\n    def arttir(self):\n"
              "        self.deger += 1\n\n    def sifirla(self):\n        self.deger = 0")


@pytest.mark.parametrize("src", [
    COUNTER_OK,
    COUNTER_OK.replace("self.deger += 1", "self.deger = self.deger + 1"),
    COUNTER_OK.replace("self.deger += 1", "self.deger = 1 + self.deger"),
    COUNTER_OK.replace("self.deger += 1", "yeni = self.deger + 1\n        self.deger = yeni"),
    COUNTER_OK + "\n\n    def goster(self):\n        print(self.deger)",
    COUNTER_OK.replace("self.deger += 1", "self.deger += 1\n        print(\"Arttı\")"),
    COUNTER_OK + "\n\ns = Sayac()\ns.arttir()\ns.arttir()\nprint(s.deger)",
    ("class Sayac:\n    \"\"\"Basit sayaç.\"\"\"\n    def __init__(sayac):\n        sayac.deger = 0\n\n    def arttir(sayac):\n"
    "        sayac.deger += 1\n\n    def sifirla(sayac):\n        sayac.deger = 0"),
])
def test_counter_class_accepts(src):
    assert accepts(COUNTER, src)


def test_counter_class_decrement_variant():
    dec = code_q("counter_class", cls="Sayac", attr="deger", inc="arttir", other="azalt", other_kind="azalt")
    src = COUNTER_OK.replace("def sifirla(self):\n        self.deger = 0", "def azalt(self):\n        self.deger -= 1")
    assert accepts(dec, src)
    assert rejects(dec, COUNTER_OK.replace("def sifirla", "def azalt"), "azalt")


@pytest.mark.parametrize("src, reason", [
    (COUNTER_OK.replace("self.deger += 1", "Sayac.deger += 1"), "her nesneye"),
    (("class Sayac:\n    deger = 0\n\n    def arttir(self):\n        self.deger += 1\n\n    def sifirla(self):\n"
     "        self.deger = 0"), "__init__"),
    (COUNTER_OK.replace("self.deger += 1", "deger = self.deger\n        deger += 1"), "değiştirmeli"),
    (COUNTER_OK.replace("self.deger += 1", "return self.deger + 1"), "değiştirmeli"),
    (COUNTER_OK.replace("def sifirla(self):\n        self.deger = 0", "def sifirla(self):\n        self.deger = 1"),
     "sifirla"),
    (COUNTER_OK.replace("def __init__(self):\n        self.deger = 0", "def __init__(self):\n        self.deger = 1"),
     "0"),
    (COUNTER_OK.replace("self.deger += 1", "self.deger += 2"), "arttir"),
    (COUNTER_OK.replace("\n\n    def sifirla(self):\n        self.deger = 0", ""), "sifirla"),
    (COUNTER_OK.replace("def arttir(self):", "def arttir():"), "self"),
])
def test_counter_class_rejects(src, reason):
    assert rejects(COUNTER, src, reason)
