"""Soru üreteçleri ve puanlama testleri."""
import builtins
import contextlib
import io
import keyword
import random

import pytest

import questions as qs

# Cevabı kodun gerçek çıktısı olan şablonlar: kodu çalıştırıp cevabı doğrularız
OUTPUT_GENERATORS = [
    qs.q_print_sep, qs.q_print_end, qs.q_type_conversion, qs.q_float_int, qs.q_fstring,
    qs.q_input_concat, qs.q_str_concat, qs.q_str_repeat, qs.q_int_div, qs.q_type_func, qs.q_swap,
]
OTHER_GENERATORS = [qs.q_input_type, qs.q_write_code, qs.q_var_name]
SEEDS = range(150)


def run(code, stdin=""):
    out = io.StringIO()
    lines = iter(stdin.splitlines())
    original = builtins.input
    builtins.input = lambda prompt="": next(lines)
    try:
        with contextlib.redirect_stdout(out):
            exec(code, {})  # noqa: S102 - yalnızca bizim ürettiğimiz kod
    finally:
        builtins.input = original
    return out.getvalue()


def test_every_generator_is_covered():
    assert set(qs.GENERATORS) == set(OUTPUT_GENERATORS) | set(OTHER_GENERATORS)


@pytest.mark.parametrize("gen", qs.GENERATORS, ids=lambda g: g.__name__)
def test_structure(gen):
    for seed in SEEDS:
        random.seed(seed)
        q = gen()
        assert q["type"] in ("mc", "tf", "short", "code")
        assert q["topic"] and q["text"] and q["solution"] and q["answer"]
        if q["type"] == "mc":
            assert q["answer"] in q["options"]
            assert len(q["options"]) == len(set(q["options"])) == 4
        if q["type"] == "tf":
            assert q["answer"] in ("True", "False")


@pytest.mark.parametrize("gen", OUTPUT_GENERATORS, ids=lambda g: g.__name__)
def test_answer_matches_real_output(gen):
    for seed in SEEDS:
        random.seed(seed)
        q = gen()
        output = run(q["code"], q.get("stdin", ""))
        assert output.rstrip("\n") == q["answer"], q["code"]


def test_var_name_answers():
    for seed in SEEDS:
        random.seed(seed)
        q = qs.q_var_name()
        for opt in q["options"]:
            valid = opt.isidentifier() and not keyword.iskeyword(opt)
            assert valid == (opt == q["answer"]), opt


def test_model_code_answer_is_accepted_and_correct():
    for seed in SEEDS:
        random.seed(seed)
        q = qs.q_write_code()
        assert qs.grade(q, q["answer"]) == (True, "Kod tüm kriterleri sağlıyor.")
        c = q["check"]
        assert run(q["answer"]).strip() == str(c["n1"] * c["n2"])


def test_generate_questions_balanced_and_numbered():
    qlist = qs.generate_questions(len(qs.GENERATORS))
    assert [q["id"] for q in qlist] == list(range(1, len(qs.GENERATORS) + 1))
    assert len({q["topic"] + q["type"] for q in qlist}) > 1
    assert len(qs.generate_questions(20)) == 20


def test_public_question_hides_answers():
    for q in qs.generate_questions(20):
        pub = qs.public_question(q)
        assert set(pub) == set(qs.PUBLIC_KEYS)
        for secret in ("answer", "solution", "check", "stdin"):
            assert secret not in pub


# ---------------------------------------------------------------- kod sorusu
CHK = {"type": "code", "check": {"v1": "a", "v2": "b", "n1": 7, "n2": 3}}


@pytest.mark.parametrize("src", [
    "a = 7\nb = 3\nprint(a * b)",
    "a = 7\nb = 3\nprint(b * a)",
    "b = 3\na = 7\nsonuc = a * b\nprint(sonuc)",
    "a, b = 7, 3\nprint(a * b)",
    "# yorum\na = 7  # yedi\nb: int = 3\n\nprint(a * b, end='')",
    "a = 7\nb = 3\nprint(a * b)\na = 1",
])
def test_code_accepts_valid_variants(src):
    assert qs.grade(CHK, src)[0] is True


@pytest.mark.parametrize("src, reason", [
    ("a = 8\nb = 3\nprint(a * b)", "<code>a</code>"),
    ("a = 7\nb = 4\nprint(a * b)", "<code>b</code>"),
    ("a = 7\nb = 3\nprint(a + b)", "print"),
    ("a = 7\nb = 3", "print"),
    ("print(a * b)\na = 7\nb = 3", "print"),
    ("c = a * b\na = 7\nb = 3\nprint(c)", "print"),
    ("a = 7\nb = 3\nprint(21)", "print"),
    ('a = "7"\nb = 3\nprint(a * b)', "<code>a</code>"),
    ("a = 7\nb = 3\nprint(a * b", "sözdizimi"),
])
def test_code_rejects_wrong_answers(src, reason):
    ok, note = qs.grade(CHK, src)
    assert ok is False and reason in note


@pytest.mark.parametrize("src", ["(" * 5000, "a = 7\x00", "x" * 5000, "   "])
def test_code_hostile_input_does_not_crash(src):
    assert qs.grade(CHK, src)[0] is False


# ---------------------------------------------------------------- diğer tipler
def test_short_answer_normalization():
    q = {"type": "short", "answer": "3.5"}
    assert qs.grade(q, " 3.5 ")[0]
    assert qs.grade(q, "3,5")[0]
    assert not qs.grade(q, "35")[0]
    assert qs.grade(q, "") == (False, None)


def test_choice_answers_are_exact():
    q = {"type": "mc", "answer": "Python Kodlama"}
    assert qs.grade(q, "Python Kodlama")[0]
    assert not qs.grade(q, "PythonKodlama")[0]
    assert not qs.grade(q, None)[0]
