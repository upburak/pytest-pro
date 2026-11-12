"""Kod izleme motoru testleri."""
import random

import pytest

from pytest_pro.questions.registry import all_generators
from pytest_pro.questions.tracer import MAX_STEPS, trace


def test_simple_assignment_steps():
    t = trace("a = 5\nb = a + 2\nprint(b)")
    assert [s["line"] for s in t["steps"]] == [1, 2, 3]
    assert t["steps"][1]["vars"] == {"a": "5"} and t["steps"][2]["changed"] == ["b"]
    assert t["steps"][-1]["output"] == "7\n" and t["error"] is None and t["truncated"] is False
    assert t["lines"] == ["a = 5", "b = a + 2", "print(b)"]


def test_string_values_show_quotes():
    assert trace('a = "3"\nprint(a)')["steps"][-1]["vars"] == {"a": "'3'"}


def test_function_scope_and_locals():
    t = trace("def kare(x):\n    y = x * x\n    return y\n\nprint(kare(4))")
    inner = [s for s in t["steps"] if s["scope"] == "kare() içinde"]
    assert inner and inner[-1]["vars"]["y"] == "16"
    assert t["steps"][0]["vars"] == {} and t["steps"][-1]["output"] == "16\n"
    assert any(s["vars"].get("kare") == "fonksiyon" for s in t["steps"])


def test_object_repr():
    t = trace("class A:\n    def __init__(self):\n        self.ad = 'Ali'\n\na = A()\nprint(a.ad)")
    assert t["steps"][-1]["vars"]["a"] == "A(ad='Ali')" and t["steps"][-1]["vars"]["A"] == "sınıf"


def test_input_echo():
    assert trace("s = input()\nprint(s * 2)", "4")["steps"][-1]["output"] == "4\n44\n"


def test_input_without_stdin_ends_with_eoferror():
    t = trace("s = input()\nprint(s)")
    assert t["error"]["type"] == "EOFError" and t["error"]["line"] == 1


def test_error_line_and_type():
    t = trace('yas = 15\nprint("Yaş " + yas)')
    assert t["error"]["type"] == "TypeError" and t["error"]["line"] == 2 and t["steps"][-1]["line"] == 2


def test_infinite_loop_is_truncated():
    t = trace("while True:\n    x = 1")
    assert t["truncated"] is True and len(t["steps"]) == MAX_STEPS


def test_long_values_are_shortened():
    assert len(trace("x = 'a' * 500\ny = 1")["steps"][-1]["vars"]["x"]) <= 61


@pytest.mark.parametrize("code", ["open('x.txt', 'w')", "import os", "eval('1')", "__import__('os')"])
def test_forbidden_operations_error(code):
    assert trace(code)["error"] is not None


def test_math_import_allowed():
    assert trace("import math\nprint(math.sqrt(16))")["steps"][-1]["output"] == "4.0\n"


def test_error_inside_function_ends_on_error_line():
    t = trace("def f(x):\n    return 10 / x\n\nprint(f(0))")
    assert t["error"]["type"] == "ZeroDivisionError" and t["error"]["line"] == 2
    assert t["steps"][-1]["line"] == 2 and t["steps"][-1]["scope"] == "f() içinde"


def test_tracer_does_not_touch_real_stdout(capsys):
    trace("print('gizli')")
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("gen", [g for g in all_generators() if g.verify in ("output", "error")], ids=lambda g: g.name)
def test_trace_agrees_with_answer_key(gen):
    for seed in range(30):
        random.seed(seed)
        q = gen()
        t = trace(q["trace"]["code"], q["trace"]["stdin"])
        if gen.verify == "output":
            echo = "".join(line + "\n" for line in q["trace"]["stdin"].splitlines())  # input() girdisi ekranda görünür
            assert t["error"] is None and t["steps"][-1]["output"].rstrip("\n") == echo + q["answer"]
        else:
            assert t["error"]["type"] in q["answer"]


def test_output_cap_holds_for_single_print():
    from pytest_pro.questions.tracer import MAX_OUTPUT
    t = trace("print('a' * 100000)")
    assert len(t["steps"][-1]["output"]) <= MAX_OUTPUT + 1


def test_trace_result_is_not_shared_between_callers():
    first = trace("a = 1\nprint(a)")
    first["steps"].clear()
    assert len(trace("a = 1\nprint(a)")["steps"]) == 2
