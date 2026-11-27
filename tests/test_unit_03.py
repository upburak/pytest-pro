"""Ünite 3 (Operatörler) özel testleri."""
import pytest
from helpers import accepts, code_q, gen_by_name, outcome, passing_options, rejects, samples, top_answer_share, variety

from pytest_pro.questions.helpers import ERROR_PREFIX

NEW = ["operatorler.op_claim", "operatorler.missing_op_blank", "operatorler.augmented2",
       "operatorler.divisible_expr", "operatorler.short_circuit", "operatorler.write_divmod",
       "operatorler.write_average"]
OPS = ["+", "-", "*", "/", "//", "%", "**"]


@pytest.mark.parametrize("name", NEW)
def test_new_templates_are_varied(name):
    gen = gen_by_name(name)
    assert variety(gen) >= 30
    assert top_answer_share(gen)[0] <= 0.40


def test_missing_op_has_single_answer():
    """Hedef sonucu yedi operatörden yalnızca biri vermeli."""
    for q in samples(gen_by_name("operatorler.missing_op_blank"), 80):
        hits = [op for op in OPS if outcome(q["code"].replace("____", op)) == q["expect"]]
        assert hits == q["answer"][0], (q["code"], q["expect"], hits)


def test_augmented2_uses_new_operators():
    for q in samples(gen_by_name("operatorler.augmented2"), 60):
        assert all(op in q["code"] for op in ("//=", "**=", "%="))
        assert q["norm"] == "sayi" and len(q["whys"]) >= 2


def test_divisible_expr_single_option():
    for q in samples(gen_by_name("operatorler.divisible_expr"), 60):
        assert passing_options(q) == [q["answer"]]


def test_short_circuit_has_error_and_plain_answers():
    answers = {q["answer"] for q in samples(gen_by_name("operatorler.short_circuit"), 200)}
    assert {"True", "False"} <= answers
    assert any(a.startswith(ERROR_PREFIX) for a in answers)


# ---------------------------------------------------------------- write_divmod
DIVMOD = code_q("divmod_time", var="toplam", total=135)


@pytest.mark.parametrize("src", [
    "toplam = 135\nprint(toplam // 60, toplam % 60)",
    "toplam = 135\ndk = toplam // 60\nsn = toplam % 60\nprint(dk, sn)",
    'toplam = 135\nprint(f"{toplam // 60}:{toplam % 60}")',
    'toplam = 135\nprint(toplam // 60, "dakika", toplam % 60, "saniye")',
    "toplam = 135\ndk, sn = divmod(toplam, 60)\nprint(dk, sn)",
    'toplam = 135\nprint(str(toplam // 60) + ":" + str(toplam % 60))',
    "toplam = 135\nprint(int(toplam / 60), toplam % 60)",
    "toplam = 135\ndakika = toplam // 60\nsaniye = toplam - dakika * 60\nprint(dakika, saniye)",
])
def test_divmod_accepts(src):
    assert accepts(DIVMOD, src)


@pytest.mark.parametrize("src, reason", [
    ("toplam = 135\nprint(2, 15)", "elle yazma"),
    ("toplam = 135\nprint(toplam / 60, toplam % 60)", "//"),
    ("toplam = 135\nprint(toplam // 60)\nprint(toplam % 60)", "aynı satırda"),
    ("toplam = 135\nprint(toplam % 60, toplam // 60)", "Önce dakika"),
    ("toplam = 100\nprint(toplam // 60, toplam % 60)", "<code>toplam</code> değişkenine"),
    ("toplam = 135\nprint(toplam // 60, toplam // 60)", "kontrol et"),
    ("toplam = 135", "print"),
    ("toplam = 135\nprint(toplam, toplam // 60, toplam % 60)", "Yalnızca"),
    ("toplam = 135\ndk = 2\nsn = 15\nprint(dk, sn)", "elle yazma"),
])
def test_divmod_rejects(src, reason):
    assert rejects(DIVMOD, src, reason)


# ---------------------------------------------------------------- write_average
AVG = code_q("average3", names=["n1", "n2", "n3"], values=[70, 85, 90])
HEAD = "n1 = 70\nn2 = 85\nn3 = 90\n"


@pytest.mark.parametrize("src", [
    HEAD + "print((n1 + n2 + n3) / 3)",
    HEAD + "ort = (n1 + n2 + n3) / 3\nprint(ort)",
    HEAD + "print(round((n1 + n2 + n3) / 3, 2))",
    HEAD + 'print(f"Ortalama: {(n1 + n2 + n3) / 3:.2f}")',
    HEAD + "toplam = n1 + n2 + n3\nprint(toplam / 3)",
    "n1, n2, n3 = 70, 85, 90\nprint(n1 / 3 + n2 / 3 + n3 / 3)",
    HEAD + 'print("Ortalama:", (n3 + n2 + n1) / 3)',
    HEAD + "ort = (n1 + n2 + n3) / 3\nprint(round(ort, 1))",
])
def test_average_accepts(src):
    assert accepts(AVG, src)


@pytest.mark.parametrize("src, reason", [
    (HEAD + "print(81.67)", "elle yazma"),
    (HEAD + "print(n1 + n2 + n3 / 3)", "paranteze"),
    (HEAD + "print(n1 + n2 + n3)", "bölmeyi"),
    (HEAD + "print((n1 + n2 + n3) // 3)", "//"),
    ("n1 = 75\nn2 = 85\nn3 = 90\nprint((n1 + n2 + n3) / 3)", "atanmamış"),
    (HEAD, "print"),
    (HEAD + "ort = (n1 + n2 + n3) / 3\nprint(n1, n2, n3, ort)", "Yalnızca"),
    (HEAD + "ort = 81.67\nprint(ort)", "elle yazma"),
    (HEAD + "print((n1 + n2) / 2)", "üç notun"),
])
def test_average_rejects(src, reason):
    assert rejects(AVG, src, reason)



# ---------------------------------------------------------------- uzman denetimi (aşama 3): haksız ret/kabul
def test_average_accepts_sum_of_list():
    assert accepts(AVG, "n1 = 70\nn2 = 85\nn3 = 90\nprint(sum([n1, n2, n3]) / 3)")


@pytest.mark.parametrize("src", [
    "n1 = 70\nn2 = 85\nn3 = 90\nprint((n1 + n2 + n3) // 3)",
    "n1 = 70\nn2 = 85\nn3 = 90\nprint(int((n1 + n2 + n3) / 3))",
])
def test_average_truncation_named_even_when_sum_divisible(src):
    """70 + 85 + 90 = 245 3'e bölünmez; 69 + 84 + 90 = 243 bölünür: // tesadüfen doğru değer verir."""
    exact = code_q("average3", names=["n1", "n2", "n3"], values=[69, 84, 90])
    assert rejects(exact, src.replace("70", "69").replace("85", "84"), "//")


def test_average_text_says_exact_when_divisible():
    import random
    for seed in range(300):
        random.seed(seed)
        q = gen_by_name("operatorler.write_average")()
        total = sum(q["check"]["values"])
        if total % 3 == 0:
            assert "yaklaşık" not in q["text"] and f"{total // 3}.0" in q["text"]
        else:
            assert "yaklaşık" in q["text"]
