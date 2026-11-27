"""Ünite 1 (Temel Giriş/Çıkış ve Değişkenler) özel testleri."""
import json

import pytest
from helpers import accepts, code_q, gen_by_name, outcome, rejects, samples, top_answer_share, variety

from pytest_pro import questions as qs
from pytest_pro.questions.fill import fill_in

NEW = ["temel.comments", "temel.sep_end_claim", "temel.fstring_blank", "temel.swap_blank", "temel.write_greet",
       "temel.write_rect", "temel.which_print"]


@pytest.mark.parametrize("name", NEW)
def test_new_templates_are_varied(name):
    gen = gen_by_name(name)
    assert variety(gen) >= 30
    assert top_answer_share(gen)[0] <= 0.40


# ---------------------------------------------------------------- yorum satırları
def test_comments_answer_is_the_only_running_print():
    for q in samples(gen_by_name("temel.comments"), 80):
        assert outcome(q["code"]) == q["answer"]
        assert q["code"].count("print(") == 4 and q["code"].count("#") >= 3
        assert qs.grade(q, f'"{q["answer"]}"')[0]  # tırnaklı yazım da kabul
        assert not qs.grade(q, q["answer"].lower() + "x")[0]


# ---------------------------------------------------------------- f-string ve takas boşlukları
def test_fstring_blank_accepts_both_prefix_cases():
    seen = set()
    for q in samples(gen_by_name("temel.fstring_blank"), 80):
        if q["answer"] == [["f", "F"]]:
            seen.add("prefix")
            assert qs.grade(q, '["F"]')[0] and not qs.grade(q, '["str"]')[0]
        else:
            seen.add("names")
            assert len(q["answer"]) == 2
            first, second = q["answer"][0][0], q["answer"][1][0]
            assert qs.grade(q, json.dumps([first, second]))[0]
            assert not qs.grade(q, json.dumps([f'"{first}"', second]))[0]  # tırnaklı ad metin olarak yazılır
    assert seen == {"prefix", "names"}


def test_swap_blank_accepts_tuple_and_list_forms():
    for q in samples(gen_by_name("temel.swap_blank"), 60):
        alts = q["answer"][0]
        assert any(a.startswith("(") for a in alts) and any(a.startswith("[") for a in alts)
        expect_values = q["expect"].split()
        constants = ", ".join(expect_values)
        assert outcome(fill_in(q["code"], [constants])) == q["expect"]  # sabitler aynı çıktıyı verir...
        assert not qs.grade(q, json.dumps([constants]))[0]  # ...ama kabul edilmez (değişken adı istenir)


# ---------------------------------------------------------------- write_greet
GREET = code_q("greet_var", var="ad", name="Ece", greet="Merhaba")


@pytest.mark.parametrize("src", [
    'ad = "Ece"\nprint("Merhaba", ad)',
    'ad = "Ece"\nprint("Merhaba " + ad)',
    'ad = "Ece"\nprint(f"Merhaba {ad}")',
    'ad = "Ece"\nprint(f"Merhaba, {ad}!")',
    'ad = "Ece"\nmesaj = "Merhaba " + ad\nprint(mesaj)',
    "# selamlama\nad = 'Ece'\nprint('Merhaba', ad, sep=' ')",
    'ad = "Ece"\nselam = "Merhaba"\nprint(selam, ad)',
    'ad = "Ece"\nprint("Program başladı")\nprint("Merhaba", ad + "!")',
    'ad = "Ece"\nprint("merhaba", ad)',
    'ad = "Ece"\nprint("Merhaba  " + ad)',
])
def test_greet_accepts(src):
    assert accepts(GREET, src)


@pytest.mark.parametrize("src, reason", [
    ('isim = "Ece"\nprint("Merhaba", isim)', "<code>ad</code> değişkenine"),
    ('ad = "Ece"', "print"),
    ('ad = "Ece"\nprint("Merhaba Ece")', "değişken"),
    ('ad = "Ece"\nprint("Merhaba ad")', "tırnak"),
    ('ad = "Ece"\nprint("Merhaba" + ad)', "boşluk"),
    ('ad = "Ece"\nprint("Selam", ad)', "Merhaba"),
    ('ad = "Ece"\nprint(ad)', "Merhaba"),
    ('print("Merhaba", ad)\nad = "Ece"', "print"),
    ('ad = "Ece"\nprint("Merhaba", "Ece")', "değişken"),
    ('ad = "Ece"\nprint("Merhaba", ad', "sözdizimi"),
])
def test_greet_rejects(src, reason):
    assert rejects(GREET, src, reason)


def test_greet_two_word_greeting():
    q = code_q("greet_var", var="isim", name="Mert", greet="Hoş geldin")
    assert accepts(q, 'isim = "Mert"\nprint("Hoş geldin", isim)')
    assert accepts(q, 'isim = "Mert"\nprint(f"Hoş geldin, {isim}!")')
    assert rejects(q, 'isim = "Mert"\nprint("Merhaba", isim)', "Hoş geldin")


# ---------------------------------------------------------------- write_rect
RECT = code_q("rect_area", en_ad="en", boy_ad="boy", en=7, boy=4)


@pytest.mark.parametrize("src", [
    "en = 7\nboy = 4\nprint(en * boy)\nprint(2 * (en + boy))",
    'en = 7\nboy = 4\nprint("Alan:", en * boy)\nprint("Çevre:", 2 * en + 2 * boy)',
    'en = 7\nboy = 4\nprint(f"Alan: {en * boy}")\nprint(f"Çevre: {(en + boy) * 2}")',
    "en = 7\nboy = 4\nalan = en * boy\ncevre = 2 * (en + boy)\nprint(alan)\nprint(cevre)",
    "en, boy = 7, 4\nprint(boy * en)\nprint(en + en + boy + boy)",
    "en = int(7)\nboy = int(4)\nprint(en * boy)\nprint(2 * (boy + en))",
    '# dikdörtgen\nen = 7\nboy = 4\nprint("Hesaplanıyor")\nprint("Alan = " + str(en * boy))\nprint(2 * (en + boy))',
])
def test_rect_accepts(src):
    assert accepts(RECT, src)


@pytest.mark.parametrize("src, reason", [
    ("en = 7\nboy = 4\nprint(28)\nprint(22)", "elle yazma"),
    ("en = 7\nboy = 4\nprint(en * boy)\nprint(en + boy * 2)", "parantez"),
    ("en = 8\nboy = 4\nprint(en * boy)\nprint(2 * (en + boy))", "istenen değerler"),
    ("en = 7\nboy = 4\nprint(en * boy, 2 * (en + boy))", "ayrı satırlarda"),
    ("en = 7\nboy = 4\nprint(2 * (en + boy))\nprint(en * boy)", "Sıra ters"),
    ("en = 7\nboy = 4\nprint(en * boy)", "iki değer"),
    ("en = 7\nboy = 4\nprint(en + boy)\nprint(2 * (en + boy))", "Alan"),
    ("en = 7\nboy = 4\nprint(en * boy)\nprint(en + boy)", "iki katı"),
    ("en = 7\nboy = 4\nalan = 28\nprint(alan)\nprint(2 * (en + boy))", "elle yazma"),
    ("en = 7\nboy = 4", "print"),
])
def test_rect_rejects(src, reason):
    assert rejects(RECT, src, reason)


# ---------------------------------------------------------------- uzman denetimi (aşama 3): haksız ret/kabul
@pytest.mark.parametrize("src", [
    'ad = "Ece"\nprint("Merhaba {}".format(ad))',
    'ad = "Ece"\nprint("Merhaba {0}".format(ad))',
    'ad = "Ece"\nprint("Merhaba %s" % ad)',
])
def test_greet_accepts_format_and_percent(src):
    assert accepts(GREET, src)


def test_greet_format_with_constant_name_still_rejected():
    assert rejects(GREET, 'ad = "Ece"\nprint("Merhaba {}".format("Ece"))', "değişken")
    assert rejects(GREET, 'ad = "Ece"\nprint("Merhaba {0.upper}".format(ad))', "")


def test_rect_accepts_one_print_with_newline_sep():
    assert accepts(RECT, 'en = 7\nboy = 4\nprint(en * boy, 2 * (en + boy), sep="\\n")')
    assert rejects(RECT, 'en = 7\nboy = 4\nprint(28, 22, sep="\\n")', "elle yazma")
