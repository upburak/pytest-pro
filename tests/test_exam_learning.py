"""Sınav sonucu ve öğretmen paneli: kod izi, yanlışın nedeni, en sık yanlış cevap."""
from conftest import TEACHER


def setup_exam(client, **settings):
    client.put("/api/settings", json={"units": ["veri_tipleri"], "question_count": 5, **settings}, headers=TEACHER)
    return client.post("/api/start", json={"name": "Ali", "no": "1"}).get_json()


def wrong_answers(secrets_of, exam_id):
    return {str(q["id"]): next(o for o in q["options"] if o != q["answer"])
            for q in secrets_of(exam_id) if q["type"] == "mc"}


def test_submit_includes_why_and_has_trace(client, secrets_of):
    d = setup_exam(client)
    res = client.post("/api/submit", json={"exam_id": d["exam_id"], "answers": wrong_answers(secrets_of, d["exam_id"])}).get_json()
    mc = [x for x in res["details"] if x["type"] == "mc"]
    assert mc and all(x["why"] for x in mc)  # veri_tipleri: tüm yanlışların açıklaması var
    assert all("has_trace" in x for x in res["details"])


def test_submit_hides_why_when_solutions_hidden(client, secrets_of):
    d = setup_exam(client, show_solutions=False)
    res = client.post("/api/submit", json={"exam_id": d["exam_id"], "answers": wrong_answers(secrets_of, d["exam_id"])}).get_json()
    assert all("why" not in x and "has_trace" not in x for x in res["details"])


def test_exam_trace_requires_submission_and_solutions(client):
    d = setup_exam(client)
    body = {"exam_id": d["exam_id"], "question_id": 1}
    assert client.post("/api/exam/trace", json=body).status_code == 403  # gönderilmedi
    client.post("/api/submit", json={"exam_id": d["exam_id"], "answers": {}})
    client.put("/api/settings", json={"show_solutions": False}, headers=TEACHER)
    assert client.post("/api/exam/trace", json=body).status_code == 403  # çözümler kapalı
    client.put("/api/settings", json={"show_solutions": True}, headers=TEACHER)
    codes = [client.post("/api/exam/trace", json={**body, "question_id": i}).status_code for i in range(1, 6)]
    assert 200 in codes and set(codes) <= {200, 404}


def test_exam_trace_bad_question_id_is_404(client):
    d = setup_exam(client)
    client.post("/api/submit", json={"exam_id": d["exam_id"], "answers": {}})
    for qid in ("abc", 999, None):
        r = client.post("/api/exam/trace", json={"exam_id": d["exam_id"], "question_id": qid})
        assert r.status_code == 404 and r.is_json
    assert client.post("/api/exam/trace", json={"exam_id": "yok", "question_id": 1}).status_code == 404


def test_teacher_trace_and_detail_why(client, secrets_of):
    d = setup_exam(client)
    client.post("/api/submit", json={"exam_id": d["exam_id"], "answers": wrong_answers(secrets_of, d["exam_id"])})
    det = client.get(f"/api/results/{d['exam_id']}", headers=TEACHER).get_json()
    assert any(q["why"] for q in det["details"])
    qid = next(q["id"] for q in det["details"] if q["has_trace"])
    assert client.get(f"/api/results/{d['exam_id']}/trace/{qid}", headers=TEACHER).status_code == 200
    assert client.get(f"/api/results/{d['exam_id']}/trace/{qid}").status_code == 401


def test_teacher_trace_unfinished_exam_is_409(client):
    d = setup_exam(client)
    assert client.get(f"/api/results/{d['exam_id']}/trace/1", headers=TEACHER).status_code == 409


def test_topic_stats_common_wrong(client, secrets_of):
    d = setup_exam(client)
    client.post("/api/submit", json={"exam_id": d["exam_id"], "answers": wrong_answers(secrets_of, d["exam_id"])})
    topics = client.get("/api/results", headers=TEACHER).get_json()["topics"]
    with_wrong = [t for t in topics if t["common_wrong"]]
    assert with_wrong and all(t["common_wrong"]["share"] >= 50 and t["common_wrong"]["why"] for t in with_wrong)
    assert all(t["common_wrong"] is None for t in topics if t not in with_wrong)
