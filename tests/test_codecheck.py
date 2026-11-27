"""Kod yazma sorusu denetleyicilerinin testleri (öğrenci kodu çalıştırılmaz)."""
import ast
import time

import pytest
from helpers import OK, code_q

from pytest_pro.questions import codecheck as cc
from pytest_pro.questions import grade

MULT = code_q("mult", v1="a", v2="b", n1=7, n2=3)
RANGE = code_q("range_print", start=1, stop=5)
SQUARE = code_q("square_func", name="kare")


# ---------------------------------------------------------------- mult
@pytest.mark.parametrize("src", [
    "a = 7\nb = 3\nprint(a * b)",
    "a = 7\nb = 3\nprint(b * a)",
    "b = 3\na = 7\nsonuc = a * b\nprint(sonuc)",
    "a, b = 7, 3\nprint(a * b)",
    "# yorum\na = 7  # yedi\nb: int = 3\n\nprint(a * b, end='')",
    "a = 7\nb = 3\nprint(a * b)\na = 1",
    'a = 7\nb = 3\nprint("Sonuç:", a * b)',
    'a = 7\nb = 3\nprint(f"{a * b}")',
    'a = 7\nb = 3\nprint(f"Çarpım: {a * b}")',
    "a = int(7)\nb = int(3)\nprint(a * b)",
    'a = 7\nb = 3\nprint("Sonuç: " + str(a * b))',
    "a = 7\nb = 3\nc = a\nprint(c * b)",
    "a = 7\nb = 3\nprint((a) * (b))",
    'a = 7\nb = 3\nprint("Çarpım hesaplanıyor")\nprint(a * b)',
])
def test_mult_accepts(src):
    assert grade(MULT, src) == (True, OK)


@pytest.mark.parametrize("src, reason", [
    ("a = 8\nb = 3\nprint(a * b)", "<code>a</code>"),
    ("a = 7\nb = 4\nprint(a * b)", "<code>b</code>"),
    ("a = 7\nb = 3\nprint(a + b)", "print"),
    ("a = 7\nb = 3", "print"),
    ("print(a * b)\na = 7\nb = 3", "print"),
    ("c = a * b\na = 7\nb = 3\nprint(c)", "print"),
    ("a = 7\nb = 3\nprint(21)", "değişken"),
    ('a = 7\nb = 3\nprint(f"{21}")', "değişken"),
    ('a = "7"\nb = 3\nprint(a * b)', "<code>a</code>"),
    ("a = 7\nb = 3\nprint(a * b", "sözdizimi"),
    ("a = 7\nb = 3\nprint(a, b, a * b)", "yalnızca çarpımı"),
    ("a = 7\nb = 3\nprint(a * b + 1)", "print"),
    ("a = 7\nb = 3\nprint(a * a)", "print"),
])
def test_mult_rejects(src, reason):
    ok, note = grade(MULT, src)
    assert ok is False and reason in note, note


# ---------------------------------------------------------------- range_print
@pytest.mark.parametrize("src", [
    "for i in range(1, 6):\n    print(i)",
    "for sayi in range(1, 6, 1):\n    print(sayi)",
    "for i in range(5):\n    print(i + 1)",
    "for i in range(1, 6):\n    print(i, end='\\n')",
    "n = 5\nfor i in range(1, n + 1):\n    print(i)",
    "n = 6\nfor i in range(1, n):\n    print(i)",
    "for i in range(1, 6):\n    print(str(i))",
    'for i in range(1, 6):\n    print(f"{i}")',
    "for i in range(1, 6):\n    if i > 0:\n        print(i)",
    'print("Sayılar:")\nfor i in range(1, 6):\n    print(i)',
    "if True:\n    for i in range(1, 6):\n        print(i)",
    "def yaz():\n    for i in range(1, 6):\n        print(i)\n\nyaz()",
    "for i in range(0, 5):\n    print(1 + i)",
    'for i in range(1, 6):\n    print("Sayı:", i)',
    "for i in range(1, 6):\n    kare = i * i\n    print(i)",
])
def test_range_print_accepts(src):
    assert grade(RANGE, src) == (True, OK)


@pytest.mark.parametrize("src, reason", [
    ("print(1)\nprint(2)", "for"),
    ("x = 1\nwhile x <= 5:\n    print(x)\n    x += 1", "for"),
    ("for i in range(1, 5):\n    print(i)", "dahil"),
    ("for i in range(1, 6):\n    print(i, end=' ')", "alt alta"),
    ("for i in range(1, 6):\n    toplam = i", "print"),
    ("for i in range(1, 6):\n    print(i)\n    break", "break"),
    ("for i in range(1, 6):\n    if i == 3:\n        continue\n    print(i)", "continue"),
    ("for i in range(1, 6):\n    i = 99\n    print(i)", "döngü değişkeni"),
    ("for i in range(1, 6):\n    print(i)\n    print(i)", "bir kez"),
    ("for i in range(1, 6):\n    if i < 3:\n        print(i)", "yazdırmıyor"),
    ("for i in range(1, 6):\n    print(5)", "yazdırmıyor"),
    ("def yaz():\n    for i in range(1, 6):\n        print(i)", "çağır"),
    ("for i in range(1, 6):\n    print(i)\nprint(5)", "dışında"),
    ("for i in [1, 2, 3, 4, 5]:\n    print(i)", "range"),
    ("for i in range(1, 6):\n    print(i, i * 2)", "bir sayı"),
])
def test_range_print_rejects(src, reason):
    ok, note = grade(RANGE, src)
    assert ok is False and reason in note, note


# ---------------------------------------------------------------- square_func
@pytest.mark.parametrize("src", [
    "def kare(x):\n    return x * x",
    "def kare(sayi):\n    return sayi ** 2",
    "def kare(n):\n    sonuc = n * n\n    return sonuc",
    "def kare(n):\n    return pow(n, 2)\n\nprint(kare(4))",
    "def kare(x):\n    return x ** 2.0",
    "def kare(x):\n    y = x\n    return y * y",
    "def kare(x):\n    x = x * x\n    return x",
    "def kare(x):\n    return (x) * (x)",
    "def kare(x):\n    sonuc = x ** 2\n    print(sonuc)\n    return sonuc",
    "def kare(x):\n    if x < 0:\n        return (-x) * (-x)\n    return x * x",
])
def test_square_func_accepts(src):
    assert grade(SQUARE, src) == (True, OK)


@pytest.mark.parametrize("src, reason", [
    ("def karesi(x):\n    return x * x", "adında"),
    ("def kare(x, y):\n    return x * x", "bir parametre"),
    ("def kare(x):\n    print(x * x)", "return"),
    ("def kare(x):\n    return x * 2", "karesini"),
    ("def kare(x):\n    pass", "return"),
    ("def kare(x):\n    x = 3\n    return x * x", "parametre"),
    ("def kare(x):\n    return 9", "parametre"),
    ("def kare(x):\n    return x * x * x", "karesini"),
    ("def kare(x):\n    return", "return"),
    ("def kare(x):\n    y = 5\n    return y * y", "parametre"),
])
def test_square_func_rejects(src, reason):
    ok, note = grade(SQUARE, src)
    assert ok is False and reason in note, note


# ---------------------------------------------------------------- dayanıklılık
@pytest.mark.parametrize("q", [MULT, RANGE, SQUARE])
@pytest.mark.parametrize("src", ["(" * 5000, "a = 7\x00", "x" * 5000, "   ", "for i in range(10**9):\n print(i)",
                                 "a = 7\nb = 3\nprint(a ** 10 ** 10 ** 10)", "x = 'a' * 10 ** 9\nprint(x)",
                                 "def kare(x):\n    return x ** 99999999", "print(" + "-" * 900 + "1)"])
def test_hostile_input_does_not_crash(q, src):
    start = time.perf_counter()
    assert grade(q, src)[0] is False
    assert time.perf_counter() - start < 1


def test_huge_range_is_not_expanded():
    assert grade(RANGE, "for i in range(1, 99999999):\n    print(i)")[0] is False


def test_unknown_check_kind():
    assert grade({"type": "code", "check": {"kind": "yok"}}, "print(1)") == (False, "Bu soru türü değerlendirilemiyor.")


def test_legacy_question_without_kind_is_mult():
    assert grade({"type": "code", "check": {"v1": "a", "v2": "b", "n1": 7, "n2": 3}}, "a = 7\nb = 3\nprint(a * b)")[0]


# ---------------------------------------------------------------- kayıt
def test_checker_registration_and_duplicates():
    @cc.checker("_test_tur")
    def check_test(tree, p):
        return True, OK

    try:
        assert grade(code_q("_test_tur"), "print(1)") == (True, OK)
        with pytest.raises(ValueError, match="_test_tur"):
            @cc.checker("_test_tur")
            def again(tree, p):
                return True, OK
        with pytest.raises(ValueError):
            cc.checker("mult")(lambda tree, p: (True, OK))
    finally:
        del cc.CHECKS["_test_tur"]


def test_every_code_question_uses_a_registered_checker():
    from helpers import gens, samples
    for gen in gens():
        for q in samples(gen, 5):
            if q["type"] == "code":
                assert q["check"]["kind"] in cc.CHECKS, gen.name


# ---------------------------------------------------------------- ortak AST yardımcıları
def expr(src):
    return ast.parse(src, mode="eval").body


@pytest.mark.parametrize("src, env, value", [
    ("2 + 3 * 4", {}, 14),
    ("(a + b) / 2", {"a": 3, "b": 4}, 3.5),
    ("int(7) + float(2)", {}, 9.0),
    ("str(5) + 'x'", {}, "5x"),
    ("a // 60, a % 60", {"a": 135}, None),  # demet desteklenmez
    ("-x ** 2", {"x": 3}, -9),
    ("x > 2 and x < 5", {"x": 3}, True),
    ("f'{x:.2f}'", {"x": 2.5}, "2.50"),
    ("round(2.567, 2)", {}, 2.57),
    ("max(a, b) - min(a, b)", {"a": 3, "b": 9}, 6),
    ("abs(-4) + len('abc')", {}, 7),
    ("'ab' * 3", {}, "ababab"),
    ("10 if x else 20", {"x": 0}, 20),
])
def test_safe_eval(src, env, value):
    if value is None:
        with pytest.raises(cc.Unknown):
            cc.safe_eval(expr(src), env)
    else:
        assert cc.safe_eval(expr(src), env) == value


@pytest.mark.parametrize("src", ["10 ** 10 ** 10", "'a' * 10 ** 9", "y + 1", "open('x')", "1 / 0", "print(1)",
                                 "[1, 2]", "x.upper()", "f'{x:999999}'", "int('9' * 5000)", "int = 3"])
def test_safe_eval_refuses_unknown_or_dangerous(src):
    with pytest.raises((cc.Unknown, SyntaxError)):
        cc.safe_eval(expr(src), {"x": "a"})


def test_print_parts_and_keywords():
    call = expr('print("Sonuç:", a * b, f"= {c}", sep="", end="!")')
    values = [ast.unparse(v) for v in cc.print_values(call)]
    assert values == ["a * b", "c"]
    assert cc.print_texts(call) == ["Sonuç:", "= "]
    assert cc.print_keyword(call, "end") == "!" and cc.print_keyword(call, "sep") == ""
    assert cc.print_keyword(expr("print(1)"), "end") == "\n"
    assert [ast.unparse(v) for v in cc.print_values(expr('print("x" + str(y))'))] == ["y"]
    assert cc.is_print(expr("print()")) and not cc.is_print(expr("input()"))
    tree = ast.parse("if a:\n    print(1)\nprint(2)")
    assert len(cc.find_prints(tree)) == 2


def test_tracker_follows_straight_line_code():
    tree = ast.parse("a = 7\nb = int(3)\nc = a * b\na, b = b, a\nd = c\nd += 1\nfor i in range(3):\n    e = 1")
    tr = cc.Tracker()
    for stmt in tr.run(tree.body):
        pass
    assert tr.values == {"a": 3, "b": 7, "c": 21, "d": 22}
    assert ast.unparse(tr.inline(expr("d"))) == "7 * int(3) + 1"
    assert "e" not in tr.values and "i" not in tr.values


def test_tracker_keep_names_stay_symbolic():
    tree = ast.parse("a = 7\nb = 3\nc = a\nd = c * b")
    tr = cc.Tracker(keep={"a", "b"})
    for _ in tr.run(tree.body):
        pass
    assert ast.unparse(tr.inline(expr("d"))) == "a * b" and tr.values["d"] == 21


def test_computes_and_shortcuts():
    assert cc.is_product_of(expr("b * a"), ["a", "b"])
    assert cc.is_product_of(expr("a * b * 1"), ["a", "b"])
    assert not cc.is_product_of(expr("a + b"), ["a", "b"])
    assert not cc.is_product_of(expr("21"), ["a", "b"])
    assert cc.is_sum_of(expr("b + a"), ["a", "b"])
    assert cc.computes(expr("(a + b + c) / 3"), ["a", "b", "c"], lambda a, b, c: (a + b + c) / 3)
    assert not cc.computes(expr("a + b + c / 3"), ["a", "b", "c"], lambda a, b, c: (a + b + c) / 3)
    assert cc.computes(expr("x * 9 / 5 + 32"), ["x"], lambda x: x * 1.8 + 32)
    assert cc.computes(expr("y"), ["x"], lambda x: x * x, defs={"y": expr("x * x")})


def test_assigned_names_and_loop_problems():
    tree = ast.parse("for i in range(3):\n    i += 1\n    t = i\n    if t:\n        break")
    loop = tree.body[0]
    assert cc.assigned_names(loop.body[0]) == {"i"}
    assert "break" in cc.loop_problems(loop)
    assert cc.loop_problems(ast.parse("for i in range(3):\n    print(i)").body[0]) is None
    assert "döngü değişkeni" in cc.loop_problems(ast.parse("for i in range(3):\n    i = 2").body[0])


def test_function_helpers():
    tree = ast.parse("def f(a, b=2):\n    return a\n\ndef g(*x):\n    pass\n\nf(1)")
    assert cc.find_function(tree, "f").name == "f" and cc.find_function(tree, "yok") is None
    assert cc.function_params(cc.find_function(tree, "f")) == ["a", "b"]
    assert cc.function_params(cc.find_function(tree, "g")) is None
    assert cc.is_called(tree, "f") and not cc.is_called(tree, "g")
    assert cc.range_values(expr("range(1, n + 1)"), {"n": 4}) == [1, 2, 3, 4]
    assert cc.range_values(expr("range(1, 10 ** 9)"), {}) is None
    assert cc.uses_name(expr("a * (b + 1)"), "b") and not cc.uses_name(expr("a"), "b")



# ---------------------------------------------------------------- uzman denetimi (aşama 3)
@pytest.mark.parametrize("src, env, value", [
    ("sum([a, b, c]) / 3", {"a": 3, "b": 4, "c": 5}, 4.0),
    ("sum((a, b))", {"a": 3, "b": 4}, 7),
    ("max([a, b, 9])", {"a": 3, "b": 4}, 9),
    ("min((a, b))", {"a": 3, "b": 4}, 3),
])
def test_safe_eval_sum_min_max_over_literal_list(src, env, value):
    assert cc.safe_eval(ast.parse(src, mode="eval"), env) == value


@pytest.mark.parametrize("src", ["sum(x)", "sum([a, 'b'])", "sum([*x])", "sum([])", "sum([1, 2], 5)"])
def test_safe_eval_sum_refuses_non_literal_or_text(src):
    with pytest.raises(cc.Unknown):
        cc.safe_eval(ast.parse(src, mode="eval"), {"a": 1, "x": 5})
