"""Ünite 6 (Döngüler) özel testleri."""
import pytest
from helpers import accepts, code_q, gen_by_name, outcome, rejects, samples

from pytest_pro.questions.fill import fill_in
from pytest_pro.questions.helpers import LOOP_OUTCOME

# ---------------------------------------------------------------- write_sum_loop (dongu_toplam)
SUM = code_q("dongu_toplam", var="n", n=10, loop=None)
SUM_FOR = code_q("dongu_toplam", var="n", n=10, loop="for")
SUM_WHILE = code_q("dongu_toplam", var="n", n=10, loop="while")


@pytest.mark.parametrize("src", [
    "n = 10\ntoplam = 0\nfor i in range(1, n + 1):\n    toplam += i\nprint(toplam)",
    "n = 10\ntoplam = 0\nfor i in range(n + 1):\n    toplam = toplam + i\nprint(toplam)",
    "n = 10\ntoplam = 0\ni = 1\nwhile i <= n:\n    toplam += i\n    i += 1\nprint(toplam)",
    "n = 10\nt = 0\nfor sayi in range(n, 0, -1):\n    t += sayi\nprint(\"Toplam:\", t)",
    "n = 10\ntoplam = 0\nfor i in range(1, n + 1):\n    toplam += i\nprint(f\"1'den {n}'e kadar toplam: {toplam}\")",
    "n = 10\ntoplam = 0\nsayac = n\nwhile sayac > 0:\n    toplam += sayac\n    sayac -= 1\nprint(toplam)",
    "# toplam\nn = 10\ntoplam = 0\nfor i in range(1, n + 1):\n    toplam += i\n    sonuc = toplam\nprint(sonuc)",
])
def test_write_sum_loop_accepts(src):
    assert accepts(SUM, src)


@pytest.mark.parametrize("src, reason", [
    ("n = 10\nprint(55)", "döngü"),
    ("n = 10\nprint(sum(range(1, n + 1)))", "sum()"),
    ("n = 10\ntoplam = 0\nfor i in range(1, n):\n    toplam += i\nprint(toplam)", "bitiş"),
    ("n = 10\ntoplam = 0\nfor i in range(1, n + 1):\n    toplam += i\n    print(toplam)", "Ara toplam"),
    ("n = 10\ntoplam = 0\nfor i in range(1, n + 1):\n    toplam = i\nprint(toplam)", "toplam"),
    ("n = 10\ntoplam = 0\nfor i in range(1, n + 1):\n    toplam += i\n    break\nprint(toplam)", "break"),
    ("n = 10\ntoplam = 0\ni = 1\nwhile i <= n:\n    toplam += i\nprint(toplam)", "sonsuz"),
    ("n = 7\ntoplam = 0\nfor i in range(1, n + 1):\n    toplam += i\nprint(toplam)", "n = 10"),
    ("n = 10\ntoplam = 0\nfor i in range(1, 11):\n    toplam += i\nprint(toplam)", "n değişkenini"),
])
def test_write_sum_loop_rejects(src, reason):
    assert rejects(SUM, src, reason)


def test_write_sum_loop_kind_requirement():
    for_src = "n = 10\ntoplam = 0\nfor i in range(1, n + 1):\n    toplam += i\nprint(toplam)"
    while_src = "n = 10\ntoplam = 0\ni = 1\nwhile i <= n:\n    toplam += i\n    i += 1\nprint(toplam)"
    assert accepts(SUM_FOR, for_src) and rejects(SUM_FOR, while_src, "for")
    assert accepts(SUM_WHILE, while_src) and rejects(SUM_WHILE, for_src, "while")


# ---------------------------------------------------------------- write_times_table (dongu_carpim)
TABLE = code_q("dongu_carpim", var="n", n=7, stop=5)


@pytest.mark.parametrize("src", [
    "n = 7\nfor i in range(1, 6):\n    print(n, \"x\", i, \"=\", n * i)",
    "n = 7\nfor i in range(1, 6):\n    print(f\"{n} x {i} = {n * i}\")",
    "n = 7\nfor i in range(1, 6):\n    print(str(n) + \" * \" + str(i) + \" = \" + str(i * n))",
    "n = 7\ni = 1\nwhile i <= 5:\n    print(n, \"X\", i, \"=\", n * i)\n    i += 1",
    "n = 7\nfor carpan in range(1, 6):\n    sonuc = n * carpan\n    print(n, 'x', carpan, '=', sonuc)",
    "n = 7\nfor i in range(5):\n    print(f\"{n}x{i + 1}={n * (i + 1)}\")",
])
def test_write_times_table_accepts(src):
    assert accepts(TABLE, src)


@pytest.mark.parametrize("src, reason", [
    ("n = 7\nprint(\"7 x 1 = 7\")\nprint(\"7 x 2 = 14\")\nprint(\"7 x 3 = 21\")\nprint(\"7 x 4 = 28\")\n"
     "print(\"7 x 5 = 35\")", "döngü"),
    ("n = 7\nfor i in range(1, 5):\n    print(n, \"x\", i, \"=\", n * i)", "satır"),
    ("n = 7\nfor i in range(0, 6):\n    print(n, \"x\", i, \"=\", n * i)", "satır"),
    ("n = 7\nfor i in range(1, 6):\n    print(n, \"x\", i, \"=\", n + i)", "sonuç"),
    ("n = 7\nfor i in range(1, 6):\n    print(7, \"x\", i, \"=\", 7 * i)", "n değişkenini"),
    ("n = 7\nfor i in range(1, 6):\n    print(n * i)", "üç sayı"),
    ("n = 7\nfor i in range(1, 6):\n    print(n, \"x\", i, \"=\", n * i, end=\" \")", "alt alta"),
    ("n = 9\nfor i in range(1, 6):\n    print(n, \"x\", i, \"=\", n * i)", "n = 7"),
])
def test_write_times_table_rejects(src, reason):
    assert rejects(TABLE, src, reason)


# ---------------------------------------------------------------- şablonlar
def test_range_blank_accepts_every_equivalent_range():
    for q in samples(gen_by_name("donguler.range_blank"), 80):
        (alts,) = q["answer"]
        for alt in alts:
            assert outcome(fill_in(q["code"], [alt])) == q["expect"], alt
        assert len(alts) >= 1


def test_while_blank_accepts_exactly_the_working_operators():
    ops = ["<", "<=", "!=", ">", ">=", "=="]
    for q in samples(gen_by_name("donguler.while_blank"), 80):
        (alts,) = q["answer"]
        for op in ops:
            assert (outcome(fill_in(q["code"], [op])) == q["expect"]) == (op in alts), (q["code"], op)


def test_infinite_loop_has_exactly_one_infinite_option():
    for q in samples(gen_by_name("donguler.infinite_loop"), 60):
        results = [outcome(opt) for opt in q["options"]]
        assert results.count(LOOP_OUTCOME) == 1
        assert outcome(q["answer"]) == LOOP_OUTCOME


def test_loop_count_claim_covers_negative_step_and_while():
    codes = [q["code"] for q in samples(gen_by_name("donguler.loop_count_claim"), 200)]
    assert any("-" in c.split("range(")[-1].split(")")[0] for c in codes if "range(" in c)
    assert any("while" in c for c in codes)


def test_sentinel_break_answers_vary_and_include_negatives():
    answers = {q["answer"] for q in samples(gen_by_name("donguler.sentinel_break"), 200)}
    assert any(a.startswith("-") for a in answers) and len(answers) > 15


def test_code_templates_model_answers_vary():
    for name in ("donguler.write_sum_loop", "donguler.write_times_table"):
        assert len({q["answer"] for q in samples(gen_by_name(name), 60)}) > 20
