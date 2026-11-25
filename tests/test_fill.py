"""Boşluk doldurma (fill) soru tipi: puanlama, gizlilik, kod izi, sınav ve pratik akışı, gösterim."""
import json
import random
import shutil
import subprocess
from pathlib import Path

import pytest
from conftest import TEACHER

from pytest_pro import questions as qs
from pytest_pro.questions.fill import BLANK, blank_count, fill_in
from pytest_pro.questions.helpers import fill_question
from pytest_pro.questions.registry import UNITS, all_generators

FILL_GENS = [g for g in all_generators() if g.func().get("type") == "fill"]


def make(answer=None, code=None):
    return {"type": "fill", "code": code or "for i in ____(____, ____):\n    print(i)",
            "answer": answer or [["range"], ["1"], ["6"]], "expect": "1\n2\n3\n4\n5"}


def ans(*values):
    return json.dumps(list(values), ensure_ascii=False)


# ---------------------------------------------------------------- yardımcılar
def test_fill_in_places_values_in_order():
    assert BLANK == "____"
    assert fill_in("a = ____ + ____", ["1", "2"]) == "a = 1 + 2"
    assert blank_count("print(____, ____)\n____") == 3


def test_fill_question_checks_blank_count():
    q = fill_question("print(____)", [["1"]], "1", "Doldur.", "Açıklama", hint="İpucu")
    assert q["type"] == "fill" and q["answer"] == [["1"]] and q["expect"] == "1" and q["hint"] == "İpucu"
    with pytest.raises(ValueError):
        fill_question("print(____)", [["1"], ["2"]], "1", "Doldur.", "Açıklama")


# ---------------------------------------------------------------- puanlama
def test_all_blanks_correct():
    assert qs.grade(make(), ans("range", "1", "6")) == (True, "3 boşluktan 3'ü doğru.")


def test_partially_correct_is_wrong_with_count_note():
    assert qs.grade(make(), ans("range", "1", "5")) == (False, "3 boşluktan 2'si doğru.")
    assert qs.grade(make(), ans("list", "0", "5")) == (False, "3 boşluktan 0'ı doğru.")
    assert qs.grade(make(), ans("range", "", "")) == (False, "3 boşluktan 1'i doğru.")


def test_empty_answers():
    assert qs.grade(make(), "") == (False, "Boş bırakıldı.")
    assert qs.grade(make(), None) == (False, "Boş bırakıldı.")
    assert qs.grade(make(), ans("", " ", "")) == (False, "Boş bırakıldı.")


def test_whitespace_and_quotes_are_equivalent():
    q = make([['"-"'], ["a + b"], ["sep"]], code="____ ____ ____")
    assert qs.grade(q, ans("'-'", " a+b ", "  sep"))[0]
    assert qs.grade(q, ans('"-"', "a  +  b", "sep"))[0]
    # metnin içindeki boşluk önemlidir; anahtar kelimeler arasındaki boşluk kaldırılamaz
    assert not qs.grade(q, ans('" - "', "a + b", "sep"))[0]
    q2 = make([["is not"]], code="x ____ None")
    assert qs.grade(q2, ans("is   not"))[0]
    assert not qs.grade(q2, ans("isnot"))[0]


def test_alternatives_are_accepted():
    q = make([["range"], ["0"], ["10", "11"]])
    assert qs.grade(q, ans("range", "0", "11"))[0]
    assert qs.grade(q, ans("range", "0", "10"))[0]


def test_broken_or_wrong_shaped_json():
    for raw in ("range", "[bozuk", '{"a": 1}', '"range"', "[[1]]"):
        ok, note = qs.grade(make(), raw)
        assert ok is False and note == "Cevap okunamadı.", raw
    # eksik boşluk boş sayılır, sayılar metne çevrilir
    assert qs.grade(make(), ans("range", "1")) == (False, "3 boşluktan 2'si doğru.")
    assert qs.grade(make(), json.dumps(["range", 1, 6])) == (True, "3 boşluktan 3'ü doğru.")


def test_why_for_fill_is_none():
    assert qs.why_for(make(), ans("range", "1", "5")) is None


def test_fill_marks_per_blank():
    assert qs.fill_marks(make(), ans("range", "2", " 6 ")) == [True, False, True]
    assert qs.fill_marks(make(), "bozuk") == [False, False, False]
    assert qs.fill_marks({"type": "mc", "answer": "x"}, "x") is None


# ---------------------------------------------------------------- gizlilik ve kod izi
def test_public_question_does_not_leak_answer():
    for gen in FILL_GENS:
        for seed in range(20):
            random.seed(seed)
            q = gen()
            pub = qs.public_question(q)
            assert pub["type"] == "fill" and BLANK in pub["code"]
            assert not {"answer", "expect", "trace", "solution", "hint"} & set(pub)


def test_trace_source_is_filled_code():
    for gen in FILL_GENS:
        random.seed(1)
        q = gen()
        src = qs.trace_source(q)
        assert BLANK not in src["code"]
        assert src["code"] == fill_in(q["code"], [a[0] for a in q["answer"]])
    legacy = make()
    assert qs.trace_source(legacy)["code"] == "for i in range(1, 6):\n    print(i)"


# ---------------------------------------------------------------- şablonlar
def test_at_least_three_fill_templates_in_different_units():
    assert len(FILL_GENS) >= 3
    assert {"temel", "donguler", "fonksiyonlar"} <= {g.unit for g in FILL_GENS}
    assert all(g.verify == "fill" for g in FILL_GENS)


def test_curriculum_doc_names_fill_type():
    # catalog alt modülü burada içe aktarılmaz: qs.catalog fonksiyonunun üstüne yazılırdı.
    # Belgenin koddan üretildiği test_curriculum_doc_is_up_to_date ile denetlenir.
    doc = Path(__file__).resolve().parent.parent / "docs" / "MUFREDAT.md"
    assert doc.read_text(encoding="utf-8").count("Boşluk doldurma") >= 3


# ---------------------------------------------------------------- sınav akışı
def test_exam_flow_with_fill_question(client, secrets_of):
    from pytest_pro.settings import COUNT_CHOICES
    count = min(c for c in COUNT_CHOICES if c >= len(UNITS["donguler"].generators))  # her şablon en az bir kez
    r = client.put("/api/settings", json={"units": ["donguler"], "question_count": count}, headers=TEACHER)
    assert r.status_code == 200
    d = client.post("/api/start", json={"name": "Ece Kaya", "no": "77"}).get_json()
    pub = next(q for q in d["questions"] if q["type"] == "fill")
    assert "answer" not in pub and BLANK in pub["code"]
    secret = next(q for q in secrets_of(d["exam_id"]) if q["id"] == pub["id"])
    right = ans(*[a[0] for a in secret["answer"]])

    assert client.post("/api/save", json={"exam_id": d["exam_id"], "answers": {str(pub["id"]): right}}).status_code == 200
    resumed = client.post("/api/resume", json={"exam_id": d["exam_id"]}).get_json()
    assert resumed["answers"][str(pub["id"])] == right

    res = client.post("/api/submit", json={"exam_id": d["exam_id"], "answers": {str(pub["id"]): right}}).get_json()
    item = next(x for x in res["details"] if x["id"] == pub["id"])
    assert item["correct"] is True and item["type"] == "fill" and item["user_answer"] == right
    assert item["answer"] == secret["answer"] and item["has_trace"] is True
    assert item["note"] == qs.grade(secret, right)[1]
    tr = client.post("/api/exam/trace", json={"exam_id": d["exam_id"], "question_id": pub["id"]}).get_json()
    assert tr["steps"][-1]["output"].rstrip("\n") == secret["expect"]

    # ikinci öğrenci: son boşluk yanlış
    d2 = client.post("/api/start", json={"name": "Can Ak", "no": "78"}).get_json()
    pub2 = next(q for q in d2["questions"] if q["type"] == "fill" and q["topic"] == pub["topic"])
    secret2 = next(q for q in secrets_of(d2["exam_id"]) if q["id"] == pub2["id"])
    wrong = ans(*([a[0] for a in secret2["answer"]][:-1] + ["yanlış"]))
    n = len(secret2["answer"])
    res2 = client.post("/api/submit", json={"exam_id": d2["exam_id"], "answers": {str(pub2["id"]): wrong}}).get_json()
    item2 = next(x for x in res2["details"] if x["id"] == pub2["id"])
    assert item2["correct"] is False and item2["note"].startswith(f"{n} boşluktan {n - 1}")
    detail = client.get(f"/api/results/{d2['exam_id']}", headers=TEACHER).get_json()
    row = next(x for x in detail["details"] if x["id"] == pub2["id"])
    assert row["type"] == "fill" and row["user_answer"] == wrong and row["correct"] is False


def test_fill_answer_survives_sanitize():
    from pytest_pro import exams
    questions = [{"id": 1}]
    raw = ans("range", "1", "6")
    assert exams.sanitize_answers({"1": raw}, questions) == {"1": raw}


# ---------------------------------------------------------------- pratik akışı
def test_practice_check_with_fill(client, app):
    client.put("/api/settings", json={"practice_open": True}, headers=TEACHER)
    gen = next(g for g in FILL_GENS if g.unit == "fonksiyonlar")
    r = client.post("/api/practice/next", json={"unit": "fonksiyonlar", "gen": gen.name}).get_json()
    assert r["question"]["type"] == "fill" and "answer" not in r["question"]
    secret = app.extensions["pytest_pro_practice"].get(r["token"])
    values = [a[0] for a in secret["answer"]]
    n = len(values)

    bad = client.post("/api/practice/check", json={"token": r["token"], "answer": ans(*(["x"] + values[1:]))}).get_json()
    assert bad["correct"] is False and bad["type"] == "fill" and bad["answer"] == secret["answer"]
    assert bad["note"].startswith(f"{n} boşluktan {n - 1}'") and bad["note"].endswith(" doğru.")
    assert bad["blanks"] == [False] + [True] * (n - 1) and bad["why"] is None and bad["has_trace"] is True

    good = client.post("/api/practice/check", json={"token": r["token"], "answer": ans(*values)}).get_json()
    assert good["correct"] is True and good["blanks"] == [True] * n
    t = client.post("/api/practice/trace", json={"token": r["token"]}).get_json()
    assert t["steps"][-1]["output"].rstrip("\n") == secret["expect"]


# ---------------------------------------------------------------- gösterim (common.js)
COMMON_JS = Path(__file__).resolve().parent.parent / "pytest_pro" / "static" / "js" / "common.js"


@pytest.mark.skipif(shutil.which("node") is None, reason="node yok")
def test_fmt_answer_for_fill():
    script = (
        "const vm=require('vm');const fs=require('fs');const ctx={window:{},document:{}};"
        f"vm.runInNewContext(fs.readFileSync({json.dumps(str(COMMON_JS))},'utf8'),ctx);"
        "const f=ctx.window.PyTest.fmtAnswer;"
        "console.log(JSON.stringify([f('fill',[['range'],['1'],['6','7']]),f('fill','[\"range\",\"\",\"6\"]'),"
        "f('fill','bozuk'),f('tf','True'),f('short','5')]));"
    )
    out = json.loads(subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True).stdout)
    sp = " "
    assert out == [f"1) range{sp}2) 1{sp}3) 6", f"1) range{sp}2) (boş){sp}3) 6", "bozuk", "Doğru (True)", "5"]
