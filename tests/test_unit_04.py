"""Ünite 4 (Metinler) özel testleri."""
import json

import pytest
from helpers import accepts, code_q, gen_by_name, outcome, rejects, samples, top_answer_share, variety

from pytest_pro import questions as qs
from pytest_pro.questions.fill import fill_in

NEW = ["metinler.index_claim", "metinler.slice_blank", "metinler.method_blank", "metinler.find_index",
       "metinler.str_immutable", "metinler.str_method_claim", "metinler.write_reverse", "metinler.write_vowels"]


@pytest.mark.parametrize("name", NEW)
def test_new_templates_are_varied(name):
    gen = gen_by_name(name)
    assert variety(gen) >= 30
    assert top_answer_share(gen)[0] <= 0.40


def test_slice_blank_accepts_equivalent_slices():
    """Kabul listesi kaba kuvvetle bulunur: hedefi veren her a:b biçimi (negatif ve boş dahil) kabul edilir."""
    for q in samples(gen_by_name("metinler.slice_blank"), 60):
        word = q["code"].split('"')[1]
        alts = q["answer"][0]
        assert any(a.startswith("-") or ":-" in a for a in alts), alts
        for a in alts:
            assert outcome(fill_in(q["code"], [a])) == q["expect"]
        n = len(word)
        for s in [""] + list(range(-n, n + 1)):
            for t in [""] + list(range(-n, n + 1)):
                got = word[(None if s == "" else s):(None if t == "" else t)]
                assert (got == q["expect"]) == (f"{s}:{t}" in alts), (s, t)


def test_method_blank_single_method():
    methods = ["upper", "lower", "title", "capitalize", "strip", "lstrip", "rstrip", "swapcase"]
    for q in samples(gen_by_name("metinler.method_blank"), 80):
        hits = [m for m in methods if outcome(fill_in(q["code"], [m])) == q["expect"]]
        assert hits == q["answer"][0], (q["code"], hits)


def test_find_index_accepts_unicode_minus():
    for q in samples(gen_by_name("metinler.find_index"), 80):
        assert q["norm"] == "sayi" and q["whys"]
        if q["answer"] == "-1":
            assert qs.grade(q, "−1")[0] and not qs.grade(q, "None")[0]


def test_str_immutable_mixes_error_and_output():
    answers = [q["answer"] for q in samples(gen_by_name("metinler.str_immutable"), 200)]
    errors = sum(a.startswith("Hata verir") for a in answers)
    assert 0.2 <= errors / len(answers) <= 0.5


# ---------------------------------------------------------------- write_reverse
REV = code_q("reverse_text", var="kelime", word="kalem")


@pytest.mark.parametrize("src", [
    'kelime = "kalem"\nprint(kelime[::-1])',
    'kelime = "kalem"\nters = kelime[::-1]\nprint(ters)',
    'kelime = "kalem"\nprint("".join(reversed(kelime)))',
    'kelime = "kalem"\nters = ""\nfor h in kelime:\n    ters = h + ters\nprint(ters)',
    'kelime = "kalem"\nters = ""\nfor i in range(len(kelime) - 1, -1, -1):\n    ters += kelime[i]\nprint(ters)',
    'kelime = "kalem"\nters = ""\nfor i in range(len(kelime)):\n    ters = kelime[i] + ters\nprint(ters)',
    'kelime = "kalem"\nprint("Ters:", kelime[::-1])',
    "kelime = 'kalem'\nsonuc = ''\nfor harf in kelime:\n    sonuc = harf + sonuc\nprint(f\"{sonuc}\")",
])
def test_reverse_accepts(src):
    assert accepts(REV, src)


@pytest.mark.parametrize("src, reason", [
    ('kelime = "kalem"\nprint("melak")', "elle yazma"),
    ('kelime = "kalem"\nprint(kelime)', "ters çevrilmeden"),
    ('kelime = "kalem"\nters = ""\nfor h in kelime:\n    ters = ters + h\nprint(ters)', "başına"),
    ('kelime = "kalem"\nters = ""\nfor h in kelime:\n    ters = h + ters\n    print(ters)', "döngü bittikten"),
    ('kelime = "kalem"\nprint(reversed(kelime))', "join"),
    ('kelime = "kitap"\nprint(kelime[::-1])', "<code>kelime</code> değişkenine"),
    ('kelime = "kalem"\nprint(kelime[::1])', "tersi değil"),
    ('kelime = "kalem"\nters = ""\nfor h in kelime:\n    ters = h + ters\n    break\nprint(ters)', "break"),
    ('kelime = "kalem"', "print"),
    ('kelime = "kalem"\nfor i in range(len(kelime) - 1, 0, -1):\n    print(kelime[i], end="")', "döngü bittikten"),
])
def test_reverse_rejects(src, reason):
    assert rejects(REV, src, reason)


# ---------------------------------------------------------------- write_vowels
VOW = code_q("count_vowels", var="metin", word="bilgisayar")
LOOP = 'metin = "bilgisayar"\nsayac = 0\nfor h in metin:\n    if h in {vowels}:\n        sayac += 1\nprint(sayac)'


@pytest.mark.parametrize("src", [
    LOOP.format(vowels='"aeıioöuü"'),
    'metin = "bilgisayar"\nsesliler = "aeıioöuü"\nsayac = 0\nfor h in metin:\n    if h in sesliler:\n'
    '        sayac = sayac + 1\nprint(sayac)',
    LOOP.format(vowels='["a", "e", "ı", "i", "o", "ö", "u", "ü"]'),
    LOOP.format(vowels='"aeıioöuüAEIİOÖUÜ"'),
    'metin = "bilgisayar"\nprint(metin.count("a") + metin.count("e") + metin.count("ı") + metin.count("i") + '
    'metin.count("o") + metin.count("ö") + metin.count("u") + metin.count("ü"))',
    'metin = "bilgisayar"\nsayac = 0\nfor h in metin:\n    if h == "a" or h == "e" or h == "ı" or h == "i" or '
    'h == "o" or h == "ö" or h == "u" or h == "ü":\n        sayac += 1\nprint(sayac)',
    'metin = "bilgisayar"\nprint(sum(1 for h in metin if h in "aeıioöuü"))',
    'metin = "bilgisayar"\nsayac = 0\nfor h in metin:\n    if h in "aeıioöuü":\n        sayac += 1\n'
    'print("Sesli harf sayısı:", sayac)',
])
def test_vowels_accepts(src):
    assert accepts(VOW, src)


@pytest.mark.parametrize("src, reason", [
    ('metin = "bilgisayar"\nprint(4)', "elle yazma"),
    (LOOP.format(vowels='"aeiou"'), "ı"),
    ('metin = "bilgisayar"\nsayac = 0\nfor h in metin:\n    if h in "aeıioöuü":\n        sayac += 1\n'
     '        print(sayac)', "döngü bittikten"),
    ('metin = "bilgisayar"\nsayac = 0\nfor h in metin:\n    if h in "aeıioöuü":\n        sayac += 1\n'
     '        break\nprint(sayac)', "break"),
    ('metin = "bilgisayar"\nprint(len(metin))', "sesli"),
    ('metin = "bilgisayar"\nfor h in metin:\n    if h in "aeıioöuü":\n        sayac += 1\nprint(sayac)', "0 ile"),
    ('metin = "bilgisayar"\nsayac = 0\nfor h in metin:\n    sayac += 1\nprint(sayac)', "if"),
    (LOOP.format(vowels='"aeıioöuüb"'), "sesli olmayan"),
    ('metin = "bilgisayar"\nsayac = 0\nfor h in metin:\n    if h in "aeıioöuü":\n        sayac += 1', "print"),
    ('metin = "okul"\nsayac = 0\nfor h in metin:\n    if h in "aeıioöuü":\n        sayac += 1\nprint(sayac)',
     "<code>metin</code> değişkenine"),
])
def test_vowels_rejects(src, reason):
    assert rejects(VOW, src, reason)


def test_vowel_model_answers_count_correctly():
    for q in samples(gen_by_name("metinler.write_vowels"), 40):
        word = q["check"]["word"]
        assert str(sum(ch in "aeıioöuü" for ch in word)) in q["text"]
        assert json.dumps(q["check"], ensure_ascii=False)
