"""Ünite 5 (Koşullu İfadeler) özel testleri."""
import ast

import pytest
from helpers import accepts, code_q, gen_by_name, outcome, rejects, samples

from pytest_pro.questions.codecheck import Unknown
from pytest_pro.questions.fill import fill_in
from pytest_pro.questions.units.u05_kosullar import Crash, Halt, Sim, fold


# ---------------------------------------------------------------- sınırlı izleyici (öğrenci kodu çalıştırılmaz)
def _sim(src, **overrides):
    sim = Sim(overrides)
    sim.run(ast.parse(src).body, top=True)
    return sim


def test_sim_follows_if_loops_lists_and_dicts():
    src = ("t = 0\nfor i in range(1, 5):\n    if i % 2 == 0:\n        continue\n    t += i\n"
           "d = {}\nfor h in 'kek':\n    d[h] = d.get(h, 0) + 1\nl = []\nl.append(t)\nprint(t, d, l, sep='|')")
    assert _sim(src).lines() == ["4|{'k': 2, 'e': 1}|[4]"]
    assert _sim("x = 3\nwhile True:\n    x -= 1\n    if x < 0:\n        break\nprint(f'son: {x}')").lines() == ["son: -1"]


def test_sim_override_replaces_first_assignment_and_remembers_given_value():
    sim = _sim("n = 7\nprint(n * 2)", n=10)
    assert sim.lines() == ["20"] and sim.given == {"n": 7}


def test_sim_reports_crash_and_infinite_loop():
    with pytest.raises(Crash) as info:
        _sim("d = {}\nprint(d['a'])")
    assert info.value.name == "KeyError"
    with pytest.raises(Crash):
        _sim("x = '5'\nif x > 3:\n    print(x)")
    with pytest.raises(Halt):
        _sim("i = 0\nwhile i < 5:\n    print(i)")


def test_sim_refuses_unsupported_code():
    for src in ("import os\nos.system('x')", "def f():\n    pass", "x = open('a')", "x = 2 ** 10000",
                "x = 'a' * 5000", "x = [1] * 5000", "print(__import__('os'))"):
        with pytest.raises(Unknown):
            _sim(src)


def test_fold_ignores_case_and_turkish_letters():
    assert fold("ÇİFT") == fold("cift") == fold(" Çift. ") == fold("çift")
    assert fold("Tek sayı") == fold("tek  sayi")


# ---------------------------------------------------------------- write_even_odd (kosul_tek_cift)
EVEN_ODD = code_q("kosul_tek_cift", var="sayi", n=17, even="Çift", odd="Tek")


@pytest.mark.parametrize("src", [
    'sayi = 17\nif sayi % 2 == 0:\n    print("Çift")\nelse:\n    print("Tek")',
    'sayi = 17\nif sayi % 2 == 1:\n    print("Tek")\nelse:\n    print("Çift")',
    'sayi = 17\nif sayi % 2 != 0:\n    print("tek")\nelse:\n    print("çift")',
    'sayi = 17\nif sayi % 2:\n    print("Tek")\nelse:\n    print("Cift")',
    'sayi = 17\nif not sayi % 2:\n    print("Çift")\nelse:\n    print("Tek")',
    'sayi = 17\nkalan = sayi % 2\nif kalan == 0:\n    print("Çift")\nif kalan == 1:\n    print("Tek")',
    'sayi = 17\nif sayi % 2 == 0:\n    sonuc = "Çift"\nelse:\n    sonuc = "Tek"\nprint(sonuc)',
    'sayi = 17\nprint("Çift" if sayi % 2 == 0 else "Tek")',
    '# tek mi çift mi\nsayi = 17\nif sayi % 2 == 0:\n    print("ÇİFT")\nelif sayi % 2 == 1:\n    print("TEK")',
])
def test_write_even_odd_accepts(src):
    assert accepts(EVEN_ODD, src)


@pytest.mark.parametrize("src, reason", [
    ('sayi = 17\nprint("Tek")', "if"),
    ('sayi = 17\nif sayi % 2 == 0:\n    print("Tek")\nelse:\n    print("Çift")', "Koşul doğruyken"),
    ('sayi = 17\nif sayi % 2 == 0:\n    print("Çift")', "hiçbir şey"),
    ('sayi = 17\nif sayi % 2 == 0:\n    print("Çift")\nprint("Tek")', "iki satır"),
    ('sayi = 17\nif sayi > 10:\n    print("Tek")\nelse:\n    print("Çift")', "Koşul doğruyken"),
    ('if sayi % 2 == 0:\n    print("Çift")\nelse:\n    print("Tek")', "sayi = 17"),
    ('sayi = 18\nif sayi % 2 == 0:\n    print("Çift")\nelse:\n    print("Tek")', "sayi = 17"),
    ('sayi = 17\nif sayi % 2 == 0:\n    print("Çift sayı")\nelse:\n    print("Tek sayı")', "Çift"),
    ('sayi = 17\nif sayi % 2 = 0:\n    print("Çift")', "sözdizimi"),
    ('sayi = 17\nif sayi % 3 == 0:\n    print("Çift")\nelse:\n    print("Tek")', "Koşul doğruyken"),
])
def test_write_even_odd_rejects(src, reason):
    assert rejects(EVEN_ODD, src, reason)


# ---------------------------------------------------------------- write_grade_ladder (kosul_not_harfi)
LADDER = code_q("kosul_not_harfi", var="puan", n=77, limits=[[85, "A"], [70, "B"], [50, "C"]], low="F")
GOOD_LADDER = 'puan = 77\nif puan >= 85:\n    print("A")\nelif puan >= 70:\n    print("B")\nelif puan >= 50:\n    print("C")\nelse:\n    print("F")'


@pytest.mark.parametrize("src", [
    GOOD_LADDER,
    'puan = 77\nif puan < 50:\n    print("F")\nelif puan < 70:\n    print("C")\nelif puan < 85:\n    print("B")\nelse:\n    print("A")',
    'puan = 77\nif puan >= 85:\n    print("A")\nif 70 <= puan < 85:\n    print("B")\nif 50 <= puan < 70:\n    print("C")\nif puan < 50:\n    print("F")',
    'puan = 77\nif puan > 84:\n    harf = "A"\nelif puan > 69:\n    harf = "B"\nelif puan > 49:\n    harf = "C"\nelse:\n    harf = "F"\nprint(harf)',
    'puan = 77\nif puan >= 85:\n    print("Harf: A")\nelif puan >= 70 and puan < 85:\n    print("Harf: B")\nelif puan >= 50:\n    print("Harf: C")\nelse:\n    print("Harf: F")'.replace("Harf: ", ""),
    'puan = 77\nif puan >= 70:\n    if puan >= 85:\n        print("A")\n    else:\n        print("B")\nelse:\n    if puan >= 50:\n        print("C")\n    else:\n        print("F")',
    'puan = 77\nharf = "F"\nif puan >= 50:\n    harf = "C"\nif puan >= 70:\n    harf = "B"\nif puan >= 85:\n    harf = "A"\nprint(harf)',
])
def test_write_grade_ladder_accepts(src):
    assert accepts(LADDER, src)


@pytest.mark.parametrize("src, reason", [
    ('puan = 77\nprint("B")', "if"),
    ('puan = 77\nif puan >= 50:\n    print("C")\nelif puan >= 70:\n    print("B")\nelif puan >= 85:\n    print("A")\nelse:\n    print("F")', "sırasını"),
    ('puan = 77\nif puan > 85:\n    print("A")\nelif puan > 70:\n    print("B")\nelif puan > 50:\n    print("C")\nelse:\n    print("F")', "Sınır"),
    ('puan = 77\nif puan >= 85:\n    print("A")\nif puan >= 70:\n    print("B")\nif puan >= 50:\n    print("C")\nelse:\n    print("F")', "birden fazla"),
    ('puan = 77\nif puan >= 85:\n    print("A")\nelif puan >= 70:\n    print("B")\nelif puan >= 50:\n    print("C")', "hiçbir şey"),
    ('puan = 70\nif puan >= 85:\n    print("A")\nelif puan >= 70:\n    print("B")\nelif puan >= 50:\n    print("C")\nelse:\n    print("F")', "puan = 77"),
    ('puan = 77\nif puan >= 85:\n    print("A")\nelif puan >= 70:\n    print("B")\nelif puan >= 50:\n    print("D")\nelse:\n    print("F")', "C"),
])
def test_write_grade_ladder_rejects(src, reason):
    assert rejects(LADDER, src, reason)


# ---------------------------------------------------------------- şablonlar
def test_model_answers_of_code_templates_differ_and_pass():
    for name in ("kosullar.write_even_odd", "kosullar.write_grade_ladder"):
        answers = {q["answer"] for q in samples(gen_by_name(name), 60)}
        assert len(answers) > 20, name


def test_nested_if_covers_every_branch_and_dangling_else():
    answers, codes = set(), []
    for q in samples(gen_by_name("kosullar.nested_if"), 200):
        answers.add(q["answer"].split("\n")[0])
        codes.append(q["code"])
    assert any("Bitti" in c for c in codes) and any("Bitti" not in c for c in codes)
    assert len(answers) >= 6


def test_cond_blank_accepts_only_the_operator_that_matches_the_rule():
    """Tek boşluk, tek işleç: kuralı her sayı için karşılayan başka bir işleç yoktur (sınırda ya da içeride ayrışır)."""
    ops = ["<", "<=", ">", ">=", "==", "!="]
    seen = set()
    for q in samples(gen_by_name("kosullar.cond_blank"), 150):
        (alts,) = q["answer"]
        assert len(alts) == 1
        seen.add(alts[0])
        t = int(q["code"].split("\n")[1].split()[-1].rstrip(":"))
        for op in ops:
            if op != alts[0]:
                assert any(eval(f"{v} {op} {t}") != eval(f"{v} {alts[0]} {t}") for v in (t - 1, t, t + 1))
    assert seen == set(ops)


def test_tie_max_often_has_ties_and_answers_vary():
    ties = 0
    answers = set()
    for q in samples(gen_by_name("kosullar.tie_max"), 200):
        first = q["code"].split("\n")[0]
        vals = [int(v) for v in first.split("=")[1].split(",")]
        ties += len(set(vals)) < 3
        answers.add(q["answer"])
        assert outcome(q["code"]) == q["answer"]
    assert ties >= 100 and len(answers) >= 6


def test_cond_claim_includes_input_type_error():
    outputs = {q["output"] for q in samples(gen_by_name("kosullar.cond_claim"), 200)}
    assert "Hata verir (TypeError)" in outputs and len(outputs) > 6


def test_ladder_order_bug_answer_is_not_always_lowest_grade():
    answers = {q["answer"] for q in samples(gen_by_name("kosullar.ladder_order_bug"), 200)}
    assert len(answers) >= 8


def test_which_condition_has_three_purposes():
    kinds = set()
    for q in samples(gen_by_name("kosullar.which_condition"), 120):
        kinds.add("aralık" if "arasındaysa" in q["text"] else "işaret" if "Pozitif" in q["text"] else "not")
        assert all("\n" in opt for opt in q["options"])  # seçenekler tam kod
    assert kinds == {"aralık", "işaret", "not"}


def test_cond_blank_filled_code_runs():
    for q in samples(gen_by_name("kosullar.cond_blank"), 40):
        assert outcome(fill_in(q["code"], [q["answer"][0][0]])) == q["expect"]



# ---------------------------------------------------------------- uzman denetimi (aşama 3)
def test_cond_blank_text_has_no_double_degilse():
    """"hiz 62 değilse Ceza, değilse Uygun" bozuk cümledir; else kısmı "aksi hâlde" ile yazılır."""
    for q in samples(gen_by_name("kosullar.cond_blank"), 300):
        assert q["text"].count("değilse") <= 1, q["text"]
        assert "aksi hâlde" in q["text"]
