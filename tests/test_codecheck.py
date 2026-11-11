"""Kod yazma sorusu denetleyicilerinin testleri (öğrenci kodu çalıştırılmaz)."""
import pytest

from pytest_pro.questions import grade

MULT = {"type": "code", "check": {"kind": "mult", "v1": "a", "v2": "b", "n1": 7, "n2": 3}}
RANGE = {"type": "code", "check": {"kind": "range_print", "start": 1, "stop": 5}}
SQUARE = {"type": "code", "check": {"kind": "square_func", "name": "kare"}}


@pytest.mark.parametrize("q, src", [
    (MULT, "a = 7\nb = 3\nprint(a * b)"),
    (MULT, "a = 7\nb = 3\nprint(b * a)"),
    (MULT, "b = 3\na = 7\nsonuc = a * b\nprint(sonuc)"),
    (MULT, "a, b = 7, 3\nprint(a * b)"),
    (MULT, "# yorum\na = 7  # yedi\nb: int = 3\n\nprint(a * b, end='')"),
    (MULT, "a = 7\nb = 3\nprint(a * b)\na = 1"),
    (RANGE, "for i in range(1, 6):\n    print(i)"),
    (RANGE, "for sayi in range(1, 6, 1):\n    print(sayi)"),
    (RANGE, "for i in range(5):\n    print(i + 1)"),
    (RANGE, "for i in range(1, 6):\n    print(i, end='\\n')"),
    (SQUARE, "def kare(x):\n    return x * x"),
    (SQUARE, "def kare(sayi):\n    return sayi ** 2"),
    (SQUARE, "def kare(n):\n    sonuc = n * n\n    return sonuc"),
    (SQUARE, "def kare(n):\n    return pow(n, 2)\n\nprint(kare(4))"),
])
def test_accepts_valid_variants(q, src):
    assert grade(q, src) == (True, "Kod tüm kriterleri sağlıyor.")


@pytest.mark.parametrize("q, src, reason", [
    (MULT, "a = 8\nb = 3\nprint(a * b)", "<code>a</code>"),
    (MULT, "a = 7\nb = 4\nprint(a * b)", "<code>b</code>"),
    (MULT, "a = 7\nb = 3\nprint(a + b)", "print"),
    (MULT, "a = 7\nb = 3", "print"),
    (MULT, "print(a * b)\na = 7\nb = 3", "print"),
    (MULT, "c = a * b\na = 7\nb = 3\nprint(c)", "print"),
    (MULT, "a = 7\nb = 3\nprint(21)", "print"),
    (MULT, 'a = "7"\nb = 3\nprint(a * b)', "<code>a</code>"),
    (MULT, "a = 7\nb = 3\nprint(a * b", "sözdizimi"),
    (RANGE, "print(1)\nprint(2)", "for"),
    (RANGE, "for i in range(1, 5):\n    print(i)", "dahil"),
    (RANGE, "for i in range(1, 6):\n    print(i, end=' ')", "alt alta"),
    (RANGE, "for i in range(1, 6):\n    toplam = i", "print"),
    (RANGE, "n = 6\nfor i in range(1, n):\n    print(i)", "sabit"),
    (SQUARE, "def karesi(x):\n    return x * x", "adında"),
    (SQUARE, "def kare(x, y):\n    return x * x", "bir parametre"),
    (SQUARE, "def kare(x):\n    print(x * x)", "return"),
    (SQUARE, "def kare(x):\n    return x * 2", "karesini"),
    (SQUARE, "def kare(x):\n    pass", "return"),
])
def test_rejects_wrong_answers(q, src, reason):
    ok, note = grade(q, src)
    assert ok is False and reason in note, note


@pytest.mark.parametrize("q", [MULT, RANGE, SQUARE])
@pytest.mark.parametrize("src", ["(" * 5000, "a = 7\x00", "x" * 5000, "   ", "for i in range(10**9):\n print(i)"])
def test_hostile_input_does_not_crash(q, src):
    assert grade(q, src)[0] is False


def test_huge_range_is_not_expanded():
    q = {"type": "code", "check": {"kind": "range_print", "start": 1, "stop": 5}}
    assert grade(q, "for i in range(1, 99999999):\n    print(i)")[0] is False


def test_unknown_check_kind():
    assert grade({"type": "code", "check": {"kind": "yok"}}, "print(1)") == (False, "Bu soru türü değerlendirilemiyor.")
