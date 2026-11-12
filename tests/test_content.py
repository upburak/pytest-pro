"""Soru içeriği: ipucu, yanlış şık açıklamaları ve izlenecek kod."""
from pytest_pro import questions as qs
from pytest_pro.questions.helpers import FILLER_WHY_NUMBER, Wrong, output_question


def test_wrong_reasons_become_whys_for_shown_options_only():
    q = output_question("print(1)", "1", "s", wrongs=[Wrong("2", "neden2"), "3", Wrong("4", "neden4")], hint="h")
    assert q["hint"] == "h"
    assert q["whys"] == {"2": "neden2", "4": "neden4"}
    assert set(q["whys"]) <= set(q["options"]) and "1" not in q["whys"]


def test_filler_options_get_generic_why():
    q = output_question("print(10)", "10", "s", wrongs=[Wrong("11", "x")])  # 2 yedek çeldirici eklenir
    fillers = [o for o in q["options"] if o not in ("10", "11")]
    assert fillers and all(q["whys"][f] == FILLER_WHY_NUMBER for f in fillers)


def test_short_answer_common_wrongs():
    q = output_question("print(int(7.9))", "7", "s", common_wrongs=[Wrong("8", "yuvarlamaz")])
    assert q["type"] == "short"
    assert qs.why_for(q, " 8 ") == "yuvarlamaz" and qs.why_for(q, "9") is None


def test_why_for_unknown_answer_is_none():
    q = output_question("print(1)", "1", "s", wrongs=[Wrong("2", "n")])
    assert qs.why_for(q, "<b>x</b>") is None and qs.why_for(q, "") is None


def test_trace_field_is_filled_by_generator():
    from pytest_pro.questions.registry import UNITS
    by_name = {g.name: g for u in UNITS.values() for g in u.generators}
    assert by_name["temel.print_sep"]()["trace"]["code"].startswith("print(")
    q = by_name["temel.write_mult"]()
    assert q["trace"] == {"code": q["answer"], "stdin": ""}
    assert by_name["temel.input_type"]()["trace"] is None
    assert by_name["veri_tipleri.input_concat"]()["trace"]["stdin"]


def test_trace_source_legacy_and_none():
    assert qs.trace_source({"type": "mc", "code": "print(1)"}) == {"code": "print(1)", "stdin": ""}
    assert qs.trace_source({"type": "tf", "code": "x = 1"}) is None
    assert qs.trace_source({"type": "mc", "code": None, "trace": None}) is None


def test_public_question_hides_new_fields():
    for q in qs.generate_questions(20, list(qs.UNITS)):
        pub = qs.public_question(q)
        assert not {"hint", "whys", "trace", "gen", "unit"} & set(pub)


# ---------------------------------------------------------------- içerik kapsamı
import random  # noqa: E402

import pytest  # noqa: E402

from pytest_pro.questions.registry import UNITS  # noqa: E402

COVERED = [g for u in qs.CONTENT_UNITS for g in UNITS[u].generators]


@pytest.mark.parametrize("gen", COVERED, ids=lambda g: g.name)
def test_content_complete(gen):
    for seed in range(40):
        random.seed(seed)
        q = gen()
        assert q.get("hint"), "ipucu yok"
        if len(q["answer"]) > 3:
            assert q["answer"] not in q["hint"], "ipucu cevabı içeriyor"
        assert q["answer"] not in q.get("whys", {})
        if q["type"] == "mc":
            for opt in q["options"]:
                if opt != q["answer"]:
                    assert q["whys"].get(opt), f"açıklamasız şık: {opt!r}"
        if q["type"] == "short":
            assert q["whys"], "sık yanlış yok"
