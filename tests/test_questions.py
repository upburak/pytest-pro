"""
Soru bankası testleri.

Her şablon birçok rastgele tohumla üretilir ve `verify` türüne göre cevap anahtarı
gerçekten Python çalıştırılarak doğrulanır. Yeni bir şablon eklendiğinde ayrıca test
yazmaya gerek yoktur.
"""
import json
import keyword

import pytest
from helpers import outcome, passing_options, run, samples

from pytest_pro import questions as qs
from pytest_pro.questions.fill import BLANK, blank_count, fill_in
from pytest_pro.questions.registry import UNITS, all_generators

GENERATORS = all_generators()


# ---------------------------------------------------------------- müfredat
def test_curriculum_is_complete():
    assert len(UNITS) >= 11
    for unit in UNITS.values():
        assert len(unit.generators) >= 4, unit.id
        assert unit.title and unit.description
    orders = [u.order for u in UNITS.values()]
    assert len(orders) == len(set(orders))
    assert len({g.name for g in GENERATORS}) == len(GENERATORS)


def test_every_unit_has_auto_verified_questions():
    for unit in UNITS.values():
        verified = [g for g in unit.generators if g.verify]
        assert len(verified) >= len(unit.generators) // 2, unit.id


# ---------------------------------------------------------------- yapı
@pytest.mark.parametrize("gen", GENERATORS, ids=lambda g: g.name)
def test_structure(gen):
    for q in samples(gen):
        assert q["type"] in ("mc", "tf", "short", "code", "fill")
        assert q["topic"] and q["text"] and q["solution"] and q["answer"]
        assert q["unit"] == gen.unit and q["gen"] == gen.name
        if q["type"] == "mc":
            assert q["answer"] in q["options"]
            assert len(q["options"]) == len(set(q["options"])) == 4, q["options"]
            assert all(str(o).strip() for o in q["options"])
        if q["type"] == "tf":
            assert q["answer"] in ("True", "False")
        if q["type"] == "short":
            assert "\n" not in q["answer"]
            assert qs.grade(q, q["answer"])[0] and all(qs.grade(q, a)[0] for a in q.get("accept", []))
            assert not any(qs.grade(q, w)[0] for w in q.get("whys", {})), "sık yanlış doğru sayılıyor"
        if q["type"] == "code":
            assert q["check"]["kind"] in qs.codecheck.CHECKS
        if q["type"] == "fill":
            assert gen.verify == "fill", "boşluk doldurma şablonu doldurulmuş kodla doğrulanmalı"
            assert blank_count(q["code"]) == len(q["answer"]) >= 1
            for alts in q["answer"]:
                assert alts and all(isinstance(a, str) and a.strip() and "\n" not in a for a in alts), alts


# ---------------------------------------------------------------- cevap anahtarı
def _by(kind):
    return [g for g in GENERATORS if g.verify == kind]


@pytest.mark.parametrize("gen", _by("output"), ids=lambda g: g.name)
def test_output_answers_match_real_output(gen):
    for q in samples(gen):
        assert run(q["code"], q.get("stdin", "")).rstrip("\n") == q["answer"], q["code"]


@pytest.mark.parametrize("gen", _by("error"), ids=lambda g: g.name)
def test_error_answers_match_real_error(gen):
    for q in samples(gen):
        with pytest.raises(Exception) as info:
            run(q["code"], q.get("stdin", ""))
        assert type(info.value).__name__ in q["answer"], q["code"]


@pytest.mark.parametrize("gen", _by("outcome"), ids=lambda g: g.name)
def test_outcome_answers_match_real_result(gen):
    """Cevap, kodun gerçek çıktısı ya da hata veriyorsa 'Hata verir (TürAdı)' olmalı."""
    for q in samples(gen):
        assert outcome(q["code"], q.get("stdin", "")) == q["answer"], q["code"]


@pytest.mark.parametrize("gen", _by("tf_output"), ids=lambda g: g.name)
def test_tf_claims_match_real_result(gen):
    """Hesaplanan D/Y: 'output' gerçek sonuç olmalı; cevap ancak iddia gerçek sonuçsa True olmalı."""
    answers = set()
    for q in samples(gen):
        assert q["type"] == "tf" and q["code"]
        real = outcome(q["code"], q.get("stdin", ""))
        assert real == q["output"], q["code"]
        assert (q["claim"] == real) == (q["answer"] == "True"), (q["code"], q["claim"])
        answers.add(q["answer"])
    assert answers == {"True", "False"}


@pytest.mark.parametrize("gen", _by("fill"), ids=lambda g: g.name)
def test_filled_code_gives_expected_output(gen):
    """Her boşluğun her kabul edilen cevabı (diğerleri ilk cevapla) ya da her cevap takımı yerleştirilince kod
    beklenen çıktıyı vermeli; açıklamalı yaygın yanlışlar ise farklı sonuç vermeli."""
    for q in samples(gen):
        stdin = q.get("stdin", "")
        first = [alts[0] for alts in q["answer"]]
        assert run(fill_in(q["code"], first), stdin).rstrip("\n") == q["expect"], q["code"]
        if q.get("answer_sets"):
            for combo in q["answer_sets"]:
                assert run(fill_in(q["code"], combo), stdin).rstrip("\n") == q["expect"], (q["code"], combo)
                assert qs.grade(q, json.dumps(combo))[0]
        else:
            for i, alts in enumerate(q["answer"]):
                for alt in alts[1:]:
                    values = first[:i] + [alt] + first[i + 1:]
                    assert run(fill_in(q["code"], values), stdin).rstrip("\n") == q["expect"], (q["code"], values)
        for i, whys in enumerate(q.get("blank_whys") or []):
            for wrong in whys:
                values = first[:i] + [wrong] + first[i + 1:]
                assert outcome(fill_in(q["code"], values), stdin) != q["expect"], ("yanlış doğru çıkıyor", values)
                assert not qs.grade(q, json.dumps(values))[0]
        assert qs.grade(q, json.dumps(first))[0]
        with pytest.raises(Exception):  # boşluklu kod tek başına çalışmamalı (gerçekten eksik)
            run(q["code"].replace(BLANK, "__bos__"), stdin)


@pytest.mark.parametrize("gen", _by("code_one"), ids=lambda g: g.name)
def test_only_answer_option_gives_expected_results(gen):
    """Seçenekleri kod olan ÇS: yalnızca doğru seçenek her durumda (case) beklenen sonucu vermeli."""
    for q in samples(gen, 40):
        assert passing_options(q) == [q["answer"]], (q["options"], q["cases"])


@pytest.mark.parametrize("gen", _by("raises_one"), ids=lambda g: g.name)
def test_only_answer_raises(gen):
    for q in samples(gen):
        for opt in q["options"]:
            try:
                eval(opt, {})  # noqa: S307
                raised = False
            except Exception:
                raised = True
            assert raised == (opt == q["answer"]), opt


@pytest.mark.parametrize("gen", _by("identifier"), ids=lambda g: g.name)
def test_only_answer_is_valid_identifier(gen):
    for q in samples(gen):
        for opt in q["options"]:
            valid = opt.isidentifier() and not keyword.iskeyword(opt)
            assert valid == (opt == q["answer"]), opt


@pytest.mark.parametrize("gen", [g for g in GENERATORS if g.func().get("type") == "code"], ids=lambda g: g.name)
def test_model_code_answers_pass_their_checker(gen):
    for q in samples(gen):
        assert qs.grade(q, q["answer"]) == (True, "Kod tüm kriterleri sağlıyor."), q["answer"]
        run(q["answer"])  # örnek çözüm gerçekten çalışmalı


# ---------------------------------------------------------------- üretim
def test_generate_questions_is_balanced_across_units():
    units = ["temel", "donguler", "nesne"]
    qlist = qs.generate_questions(9, units)
    assert [q["id"] for q in qlist] == list(range(1, 10))
    assert sorted(q["unit"] for q in qlist) == sorted(units * 3)
    orders = [UNITS[q["unit"]].order for q in qlist]
    assert orders == sorted(orders)  # müfredat sırasında


def test_generate_questions_no_repeat_within_unit_when_possible():
    unit = UNITS["temel"]
    qlist = qs.generate_questions(len(unit.generators), ["temel"])
    assert len({q["gen"] for q in qlist}) == len(unit.generators)


def test_generate_questions_ignores_unknown_units():
    qlist = qs.generate_questions(5, ["yok", "metinler"])
    assert {q["unit"] for q in qlist} == {"metinler"}
    assert {q["unit"] for q in qs.generate_questions(4, ["yok"])} <= set(qs.DEFAULT_UNITS)


def test_public_question_hides_answers():
    for q in qs.generate_questions(30, list(UNITS)):
        pub = qs.public_question(q)
        assert set(pub) == set(qs.PUBLIC_KEYS)
        for secret in ("answer", "solution", "check", "stdin", "gen", "unit"):
            assert secret not in pub


# ---------------------------------------------------------------- puanlama
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


def test_legacy_code_question_without_kind():
    q = {"type": "code", "check": {"v1": "a", "v2": "b", "n1": 7, "n2": 3}}
    assert qs.grade(q, "a = 7\nb = 3\nprint(a * b)")[0]


def test_curriculum_doc_is_up_to_date():
    """Ünite/şablon eklenince docs/MUFREDAT.md yeniden üretilmeli (komut dosyanın başında yazar)."""
    from pathlib import Path

    from pytest_pro.questions.mufredat import render
    doc = Path(__file__).resolve().parent.parent / "docs" / "MUFREDAT.md"
    assert doc.read_text(encoding="utf-8") == render()
