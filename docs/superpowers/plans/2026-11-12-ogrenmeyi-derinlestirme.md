# Öğrenmeyi Derinleştirme (Birinci Teslimat) Uygulama Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Pratik moduna ipucu, adım adım kod izleme, yanlışı tekrar çözdürme ve yanlışın nedenini
eklemek; kod izleme ve yanlışın nedenini sınav sonucunda ve öğretmen panelinde göstermek; ilk 4
ünitenin (30 şablon) içeriğini yazmak.

**Architecture:** Soru şablonları üç iç alan taşır: `hint`, `whys` ve `trace`. Bunlar öğrenciye
giden soruya hiç konmaz. Kod izleme, Flask'tan bağımsız `questions/tracer.py` modülüdür; yalnızca
sunucuda saklanan şablon kodunu `sys.settrace` ile çalıştırır. Rotalar bu alanları koşullara göre açar.
Tarayıcıda ortak `tracer.js` bileşeni üç sayfada kullanılır. Pratik ilerlemesi yalnızca tarayıcıdaki
`sessionStorage`'da tutulur.

**Tech Stack:** Python 3.9+, Flask 3, SQLite, pytest, düz JavaScript (derleme adımı yok), Playwright (elle doğrulama).

**Spec:** `docs/superpowers/specs/2026-11-11-ogrenmeyi-derinlestirme-design.md`

## Global Constraints

- Python 3.9 sözdizimi: `X | Y` tip yazımı, `match` ve f-string ifadesi içinde ters bölü kullanılmaz.
- Öğrenci kodu asla çalıştırılmaz. `tracer.trace()` yalnızca sunucuda saklanan sorunun `trace` alanını
  (veya eski kayıtlarda `code` alanını) çalıştırır; istekle gelen kod çalıştırılmaz.
- İz sınırları: en fazla 200 adım, en fazla 5000 karakter çıktı, değer gösterimi en fazla 60 karakter
  (fazlası `…`), önbellek `lru_cache(maxsize=512)`.
- `public_question()` çıktısında `hint`, `whys`, `trace`, `gen`, `unit`, `answer`, `solution`, `check`,
  `stdin` bulunmaz.
- CSP: satır içi `<script>`, `on*=` öznitelikleri ve `style="..."` yok; JS'te stil yalnızca CSSOM ile
  (`el.style.x = ...`) verilir.
- Arayüz metinleri Türkçe ve cümle düzeninde; BÜYÜK HARF etiket, `·` ile birleştirilmiş meta yazıları
  ve düğmede `→` yok. Renk ve ölçüler yalnızca `style.css` değişkenlerinden (`--marker`, `--pen` vb.).
- İnternetsiz çalışma: dış kaynak yüklenmez.
- Mevcut 253 test geçmeye devam eder; her görev sonunda `python -m pytest -q` yeşil olmalıdır.

## Review Focus

1. Klavye girdisi verilmeden `input()` içeren kod izlenirse uygulama çökmemeli; iz `EOFError` ile
   bitmeli. Test: Task 2, `test_input_without_stdin_ends_with_eoferror`.
2. Sonsuz döngülü kod (`while True:`) izlenirse istek askıda kalmamalı; iz 200 adımda kesilmeli.
   Test: Task 2, `test_infinite_loop_is_truncated`.
3. Öğrencinin cevabı HTML veya beklenmedik bir metin içerirse açıklama bulunamamalı (`None`) ve bu
   metin hiçbir yerde HTML olarak yorumlanmamalı. Test: Task 1, `test_why_for_unknown_answer_is_none`;
   arayüzde cevaplar `esc()` ile basılır (Task 6–7).
4. Pratikte ünitenin tüm şablonları `avoid` listesindeyse yine de soru gelmeli. Test: Task 3,
   `test_next_with_everything_avoided_still_returns_question`.
5. Sınav izinde soru numarası sayı değilse veya sınavda yoksa `500` değil `404` dönmeli. Test: Task 4,
   `test_exam_trace_bad_question_id_is_404`.

---

### Task 1: Soru içeriği veri yapısı (`Wrong`, `hint`, `whys`, `trace`)

**Files:**
- Modify: `pytest_pro/questions/helpers.py`
- Modify: `pytest_pro/questions/registry.py` (`Generator.__call__`)
- Modify: `pytest_pro/questions/__init__.py`
- Test: `tests/test_content.py` (yeni)

**Interfaces:**
- Produces:
  - `helpers.Wrong(NamedTuple)` alanları `value: str`, `why: str`.
  - `helpers.FILLER_WHY_NUMBER: str`, `helpers.FILLER_WHY_OTHER: str`. Metinler spec §2'den aynen alınır.
  - `helpers.unique_options(correct, wrongs, n=4) -> list[str]`. `wrongs` elemanları `str` veya `Wrong`
    olabilir; dönen seçenekler yine `str`'dir.
  - `helpers.whys_for_options(correct, wrongs, options) -> dict[str, str]`. Yalnızca `options` içindeki
    yanlış seçenekleri kapsar. Yedek çeldiriciye, sayısal mı değil mi olduğuna göre `FILLER_WHY_*`
    açıklaması verilir. `str` olarak verilen (açıklamasız) yanlışlar sözlüğe girmez.
  - `helpers.output_question(code, answer, solution, wrongs=None, text=None, stdin=None, hint=None, common_wrongs=None) -> dict`.
    Çıktıda `hint` (verildiyse) ve `whys` bulunur. Seçenekli sorularda `whys` `whys_for_options`'tan
    gelir. Kısa cevapta `common_wrongs` içindeki `Wrong` değerlerinden oluşur: `{w.value: w.why}`.
  - `helpers.tf_question(statements_true, statements_false, solution, code=None, hint=None) -> dict`.
  - `Generator.__call__` sonucunda her soruda `trace` anahtarı bulunur:
    - `verify` değeri `"output"` veya `"error"` ise ve `code` doluysa: `{"code": q["code"], "stdin": q.get("stdin", "")}`.
    - `type == "code"` ise: `{"code": q["answer"], "stdin": ""}`.
    - Diğer durumlarda `None`.
  - `questions.why_for(question: dict, answer: str) -> Optional[str]`:
    - `mc` ve `tf` sorularında `question.get("whys", {}).get(answer)`.
    - `short` sorularında `whys` anahtarları `_norm_short` ile karşılaştırılır.
    - `code` sorularında `None`.
  - `questions.trace_source(question: dict) -> Optional[dict]`:
    - `question.get("trace")` varsa onu döndürür.
    - `trace` anahtarı hiç yoksa (eski kayıt) ve tip `mc` ya da `short` ise ve `code` doluysa
      `{"code": code, "stdin": question.get("stdin", "")}` döndürür.
    - Diğer durumlarda `None`.
  - `questions.CONTENT_UNITS = ("temel", "veri_tipleri", "operatorler", "metinler")`.
  - `questions.PUBLIC_KEYS` değişmez.

- [ ] **Step 1: Write the failing tests in `tests/test_content.py`**

```python
from pytest_pro import questions as qs
from pytest_pro.questions.helpers import Wrong, output_question, FILLER_WHY_NUMBER

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
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_content.py -q`
Expected: FAIL (`ImportError: cannot import name 'Wrong'`)

- [ ] **Step 3: Implement the Produces block.** `unique_options` önce `Wrong` değerlerini `str`'ye
  çevirir. Seçenek sırası ve `_fillers` davranışı değişmez. `output_question` her zaman `whys` anahtarı
  üretir (boş sözlük olabilir).

- [ ] **Step 4: Run the new and existing tests**

Run: `python -m pytest -q`
Expected: tümü PASS

- [ ] **Step 5: Commit**

```bash
git add pytest_pro/questions tests/test_content.py
git commit -m "İçerik yapısı: Wrong, hint, whys, trace alanları"
```

---

### Task 2: Kod izleme motoru

**Files:**
- Create: `pytest_pro/questions/tracer.py`
- Test: `tests/test_tracer.py` (yeni)

**Interfaces:**
- Consumes: `questions.registry.all_generators()`, `Generator.verify`; Task 1'deki `trace` alanı.
- Produces:
  - `tracer.trace(code: str, stdin: str = "") -> dict`, spec §3'teki biçimde:
    `{"lines", "steps", "error", "truncated"}`. Her adım `{"line", "scope", "vars", "changed", "output"}` içerir.
  - Sabitler: `MAX_STEPS = 200`, `MAX_OUTPUT = 5000`, `MAX_REPR = 60`.
  - `trace` aynı `(code, stdin)` için önbellekten döner. Döndürülen sözlük paylaşılır; çağıran değiştirmez.

- [ ] **Step 1: Write the failing tests in `tests/test_tracer.py`**

```python
import random, pytest
from pytest_pro.questions.tracer import trace, MAX_STEPS
from pytest_pro.questions.registry import all_generators

def test_simple_assignment_steps():
    t = trace("a = 5\nb = a + 2\nprint(b)")
    assert [s["line"] for s in t["steps"]] == [1, 2, 3]
    assert t["steps"][1]["vars"] == {"a": "5"} and t["steps"][2]["changed"] == ["b"]
    assert t["steps"][-1]["output"] == "7\n" and t["error"] is None and t["truncated"] is False

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

@pytest.mark.parametrize("gen", [g for g in all_generators() if g.verify in ("output", "error")], ids=lambda g: g.name)
def test_trace_agrees_with_answer_key(gen):
    for seed in range(30):
        random.seed(seed)
        q = gen()
        t = trace(q["trace"]["code"], q["trace"]["stdin"])
        if gen.verify == "output":
            assert t["error"] is None and t["steps"][-1]["output"].rstrip("\n") == q["answer"]
        else:
            assert t["error"]["type"] in q["answer"]
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_tracer.py -q`
Expected: FAIL (`ModuleNotFoundError: pytest_pro.questions.tracer`)

- [ ] **Step 3: Implement `trace` in `pytest_pro/questions/tracer.py`**

Algoritma, testlerin belirlemediği kısımlar:
- `compile(code, "<soru>", "exec")`. Yerleşik fonksiyonlar `builtins.__dict__` kopyasından alınır;
  `open`, `eval`, `exec`, `compile`, `input`, `__import__` çıkarılır. Yerlerine iki fonksiyon konur:
  - `input`: `stdin` satırlarını sırayla döndürür ve girilen değeri çıktıya `değer + "\n"` olarak yazar;
    satırlar bitince `EOFError` fırlatır.
  - `__import__`: yalnızca `math` modülüne izin verir, diğerlerinde `ImportError` fırlatır.
- `print`, `io.StringIO`'ya yönlendirilir (`contextlib.redirect_stdout`).
- İzleyici `frame.f_code.co_filename == "<soru>"` olan çerçevelerde `line` olayını kaydeder; `return`
  olayında son durum güncellenir.
- 200 adım dolunca özel bir `_StopTrace` istisnası fırlatılır, `truncated=True` olur. Çıktı 5000
  karakteri aşarsa da aynı şekilde durdurulur.
- `vars` kaydı: Modül çerçevesinde `__` ile başlamayan ve modül olmayan adlar; fonksiyon çerçevesinde
  `f_locals`. `scope` değeri `f"{frame.f_code.co_name}() içinde"` veya `None`.
- Gösterim:
  - Fonksiyon → `"fonksiyon"`, sınıf → `"sınıf"`.
  - `__dict__` taşıyan kullanıcı nesnesi → `Ad(k=repr(v), …)`.
  - Diğer değerler `repr` ile yazılır; 60 karakteri aşanlar 59 karakter ve `…` olarak kısaltılır.
- `changed`: Önceki kayıtlı adımla aynı kapsamda gösterimi farklı olan adlar, kaynak koddaki
  sıralarıyla.
- Hata: İstisnanın son `<soru>` çerçevesindeki satır numarası `traceback`'ten alınır. Son adımın satırı
  bu değilse o satır için ek bir adım eklenir.
- `try/finally` içinde eski izleyici (`sys.gettrace()`) geri yüklenir. Sonuç `functools.lru_cache(512)`
  ile önbelleğe alınır.

- [ ] **Step 4: Run tests**

Run: `python -m pytest -q`
Expected: tümü PASS (`test_trace_agrees_with_answer_key` 75 şablonun izlenebilir olanlarının hepsinde)

- [ ] **Step 5: Commit**

```bash
git add pytest_pro/questions/tracer.py tests/test_tracer.py
git commit -m "Kod izleme motoru: satır satır değişkenler, çıktı ve hata"
```

---

### Task 3: Pratik API (ipucu, iz, tekrar, `why`)

**Files:**
- Modify: `pytest_pro/questions/__init__.py` (`generate_one`)
- Modify: `pytest_pro/routes/practice.py`
- Test: `tests/test_practice_api.py` (yeni; pratik testleri `tests/test_api.py`'den buraya taşınmaz, orada kalır)

**Interfaces:**
- Consumes: `qs.why_for`, `qs.trace_source` (Task 1), `tracer.trace` (Task 2), `PracticeStore`.
- Produces:
  - `questions.generate_one(unit_id: str, gen: Optional[str] = None, avoid: Iterable[str] = ()) -> dict`.
    - Bilinmeyen ünitede `KeyError`, üniteye ait olmayan `gen` için `ValueError` fırlatır.
    - `avoid` dikkate alınır, ama `random.random() < 0.2` ise göz ardı edilir. Kalan aday yoksa tüm
      şablonlar aday olur.
  - `POST /api/practice/next {unit, gen?, avoid?}` → `{token, unit, gen, topic, question}`.
    Bozuk `gen` için `400`. `avoid` liste değilse yok sayılır.
  - `POST /api/practice/hint {token}` → `{hint}`; ipucu yoksa veya anahtar bulunamazsa `404`.
  - `POST /api/practice/trace {token}` → `tracer.trace(...)` çıktısı; izlenecek kod yoksa `404`.
  - `POST /api/practice/check` yanıtı bugünkü alanlara ek olarak `why`, `gen` ve `has_trace` içerir.
    `why` için:
    - Doğru cevapta `None`.
    - `code` sorusunda `grade` notu.
    - Diğerlerinde `qs.why_for`.
  - Tüm uçlar pratik kapalıyken `403` döner (bugünkü `_closed()` kalıbı).

- [ ] **Step 1: Write the failing tests in `tests/test_practice_api.py`**

```python
import pytest
from conftest import TEACHER

@pytest.fixture
def open_client(client):
    client.put("/api/settings", json={"practice_open": True}, headers=TEACHER)
    return client

def nxt(c, **body):
    return c.post("/api/practice/next", json=body)

def test_hint_and_trace_flow(open_client, app):
    r = nxt(open_client, unit="temel", gen="temel.print_sep").get_json()
    assert r["gen"] == "temel.print_sep" and r["topic"] == "Print Parametreleri (sep)"
    assert "hint" not in r["question"] and "trace" not in r["question"]
    t = open_client.post("/api/practice/trace", json={"token": r["token"]}).get_json()
    assert t["steps"][-1]["output"].rstrip("\n") == app.extensions["pytest_pro_practice"].get(r["token"])["answer"]

def test_hint_404_when_template_has_no_hint(open_client):
    # Birinci teslimatta nesne ünitesinde ipucu yok; ikinci teslimatta bu test, ipucusuz bir
    # sahte şablonla (monkeypatch) yeniden yazılır.
    r = nxt(open_client, unit="nesne").get_json()
    assert open_client.post("/api/practice/hint", json={"token": r["token"]}).status_code == 404

def test_check_returns_why_for_wrong_option(open_client, app):
    r = nxt(open_client, unit="veri_tipleri", gen="veri_tipleri.str_concat").get_json()
    q = app.extensions["pytest_pro_practice"].get(r["token"])
    wrong = next(o for o in q["options"] if o != q["answer"])
    d = open_client.post("/api/practice/check", json={"token": r["token"], "answer": wrong}).get_json()
    assert d["correct"] is False and d["why"] == q["whys"][wrong] and d["has_trace"] is True and d["gen"] == r["gen"]
    ok = open_client.post("/api/practice/check", json={"token": r["token"], "answer": q["answer"]}).get_json()
    assert ok["why"] is None

def test_gen_from_other_unit_is_400(open_client):
    assert nxt(open_client, unit="temel", gen="metinler.indexing").status_code == 400

def test_next_with_everything_avoided_still_returns_question(open_client):
    from pytest_pro.questions import UNITS
    avoid = [g.name for g in UNITS["operatorler"].generators]
    assert nxt(open_client, unit="operatorler", avoid=avoid).status_code == 200

def test_avoid_is_respected(open_client, monkeypatch):
    import random
    monkeypatch.setattr(random, "random", lambda: 0.99)
    from pytest_pro.questions import UNITS
    names = [g.name for g in UNITS["metinler"].generators]
    for _ in range(20):
        assert nxt(open_client, unit="metinler", avoid=names[1:]).get_json()["gen"] == names[0]

def test_trace_404_for_true_false(open_client):
    r = nxt(open_client, unit="temel", gen="temel.input_type").get_json()
    assert open_client.post("/api/practice/trace", json={"token": r["token"]}).status_code == 404

def test_new_endpoints_closed_when_practice_closed(client):
    for path in ("/api/practice/hint", "/api/practice/trace"):
        assert client.post(path, json={"token": "x"}).status_code == 403
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_practice_api.py -q`
Expected: FAIL (`gen` anahtarı yok veya `404/405`)

- [ ] **Step 3: Implement the Produces block** in `questions/__init__.py` and `routes/practice.py`.

- [ ] **Step 4: Run tests**

Run: `python -m pytest -q`
Expected: tümü PASS

- [ ] **Step 5: Commit**

```bash
git add pytest_pro/questions/__init__.py pytest_pro/routes/practice.py tests/test_practice_api.py
git commit -m "Pratik API: ipucu, kod izi, aynı konudan yeni soru, yanlışın nedeni"
```

---

### Task 4: Sınav ve öğretmen API (iz, `why`, en sık yanlış)

**Files:**
- Modify: `pytest_pro/routes/student.py` (`submit`, yeni `exam_trace`)
- Modify: `pytest_pro/routes/teacher.py` (`result_detail`, yeni `result_trace`)
- Modify: `pytest_pro/exams.py` (`topic_stats`)
- Test: `tests/test_exam_learning.py` (yeni)

**Interfaces:**
- Consumes: `qs.why_for`, `qs.trace_source`, `tracer.trace`, `settings.get_settings`.
- Produces:
  - `submit` yanıtında, çözümler açıksa her ayrıntıya şu alanlar eklenir:
    - `why`: Doğruysa `None`, kod sorusunda `None` (not zaten `note` alanında), diğerlerinde `qs.why_for`.
    - `has_trace`: `bool`.
  - `POST /api/exam/trace {exam_id, question_id}` → iz.
    - Gönderilmemiş sınavda veya `show_solutions` kapalıysa `403`.
    - Sınav, soru veya izlenecek kod yoksa ve `question_id` sayıya çevrilemezse `404`.
  - `GET /api/results/<exam_id>/trace/<question_id>` (öğretmen şifresi gerekir) → iz.
    Gönderilmemiş sınavda `409`, diğer eksiklerde `404`.
  - Öğretmen ayrıntısında her soruya `why` ve `has_trace` alanları eklenir.
  - `exams.topic_stats(...)` her öğeye `common_wrong` alanını ekler:
    - Değer `{"answer": str, "share": int, "why": Optional[str]}` veya `None`.
    - Hesaba yalnızca `mc` ve `short` tipindeki, boş olmayan yanlış cevaplar girer.
    - Kısa cevaplar `_norm_short` ile gruplanır; gösterilen değer ilk görülen yazımdır.
    - `share = round(adet * 100 / o konudaki toplam cevap)`.
    - `why` değeri ilk eşleşen sorunun `qs.why_for` sonucudur.

- [ ] **Step 1: Write the failing tests in `tests/test_exam_learning.py`**

```python
from conftest import TEACHER

def setup_exam(client, **settings):
    client.put("/api/settings", json={"units": ["veri_tipleri"], "question_count": 5, **settings}, headers=TEACHER)
    d = client.post("/api/start", json={"name": "Ali", "no": "1"}).get_json()
    return d

def wrong_answers(secrets_of, exam_id):
    return {str(q["id"]): next(o for o in q["options"] if o != q["answer"])
            for q in secrets_of(exam_id) if q["type"] == "mc"}

def test_submit_includes_why_and_has_trace(client, secrets_of):
    d = setup_exam(client)
    res = client.post("/api/submit", json={"exam_id": d["exam_id"], "answers": wrong_answers(secrets_of, d["exam_id"])}).get_json()
    mc = [x for x in res["details"] if x["type"] == "mc"]
    assert mc and all(x["why"] for x in mc)            # veri_tipleri: tüm yanlışların açıklaması var
    assert all("has_trace" in x for x in res["details"])

def test_exam_trace_requires_submission_and_solutions(client):
    d = setup_exam(client)
    body = {"exam_id": d["exam_id"], "question_id": 1}
    assert client.post("/api/exam/trace", json=body).status_code == 403          # gönderilmedi
    client.post("/api/submit", json={"exam_id": d["exam_id"], "answers": {}})
    client.put("/api/settings", json={"show_solutions": False}, headers=TEACHER)
    assert client.post("/api/exam/trace", json=body).status_code == 403          # çözümler kapalı
    client.put("/api/settings", json={"show_solutions": True}, headers=TEACHER)
    traceable = next(i for i in range(1, 6) if client.post("/api/exam/trace", json={**body, "question_id": i}).status_code == 200)
    assert traceable

def test_exam_trace_bad_question_id_is_404(client):
    d = setup_exam(client)
    client.post("/api/submit", json={"exam_id": d["exam_id"], "answers": {}})
    for qid in ("abc", 999, None):
        assert client.post("/api/exam/trace", json={"exam_id": d["exam_id"], "question_id": qid}).status_code == 404

def test_teacher_trace_and_detail_why(client, secrets_of):
    d = setup_exam(client)
    client.post("/api/submit", json={"exam_id": d["exam_id"], "answers": wrong_answers(secrets_of, d["exam_id"])})
    det = client.get(f"/api/results/{d['exam_id']}", headers=TEACHER).get_json()
    assert any(q["why"] for q in det["details"])
    qid = next(q["id"] for q in det["details"] if q["has_trace"])
    assert client.get(f"/api/results/{d['exam_id']}/trace/{qid}", headers=TEACHER).status_code == 200
    assert client.get(f"/api/results/{d['exam_id']}/trace/{qid}").status_code == 401

def test_topic_stats_common_wrong(client, secrets_of):
    d = setup_exam(client)
    client.post("/api/submit", json={"exam_id": d["exam_id"], "answers": wrong_answers(secrets_of, d["exam_id"])})
    topics = client.get("/api/results", headers=TEACHER).get_json()["topics"]
    with_wrong = [t for t in topics if t["common_wrong"]]
    assert with_wrong and all(t["common_wrong"]["share"] == 100 and t["common_wrong"]["why"] for t in with_wrong)
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_exam_learning.py -q`
Expected: FAIL (`KeyError: 'why'`, `404`)

- [ ] **Step 3: Implement the Produces block.**

- [ ] **Step 4: Run tests**

Run: `python -m pytest -q`
Expected: tümü PASS. `test_submit_includes_why_and_has_trace` testi Task 8 tamamlanana kadar
`veri_tipleri` içeriği olmadığı için başarısız olur. Bu yüzden Task 4'ü Task 8'den sonra uygulayın
(bkz. sıra notu sonda).

- [ ] **Step 5: Commit**

```bash
git add pytest_pro/routes pytest_pro/exams.py tests/test_exam_learning.py
git commit -m "Sınav ve öğretmen API: kod izi, yanlışın nedeni, en sık yanlış cevap"
```

---

### Task 5: İz bileşeni (`tracer.js`) ve stilleri

**Files:**
- Create: `pytest_pro/static/js/tracer.js`
- Modify: `pytest_pro/static/css/style.css` (yeni bölüm `/* kod izi */`, `.why-note`)
- Modify: `pytest_pro/templates/index.html`, `practice.html`, `teacher.html` (`tracer.js`'i `common.js`'ten sonra, `defer` ile ekle)
- Modify: `tests/test_api.py::test_pages_and_security_headers` (`/static/js/tracer.js` ekle)

**Interfaces:**
- Consumes: Task 2 iz biçimi; `window.PyTest.esc`.
- Produces:
  - `window.PyTest.renderTrace(container: HTMLElement, trace: object) -> void`.
    - Container içine şunları çizer: kod satırları (`ol.trace-code`, o anki satır `li.now`), değişken
      tablosu (`table.trace-vars`, değişenler `tr.changed`), çıktı (`pre.trace-out`), kapsam adı,
      kontroller ve `aria-live` duyuru alanı.
    - Kontroller: "Önceki adım", "Sonraki adım", adım çubuğu (`input type=range`).
    - Klavye: Bileşen odaktayken ←/→ adım değiştirir.
    - Duyuru metni: `Adım ${i} / ${n}, satır ${line}`.
    - Hata: Hatalı son adımda `.trace-error` öğesinde `${type}: ${message} (satır ${line})` yazar.
    - Kesilen iz: `truncated` ise son adımda "İlk 200 adım gösteriliyor" notu çıkar.
  - `window.PyTest.whyNote(text: string) -> string`. Döndürdüğü HTML:
    `<div class="why-note"><b>Neden yanlış:</b> ${text}</div>`. `text` sunucudan gelen güvenli
    şablon HTML'idir.
  - `window.PyTest.traceToggle(button: HTMLElement, container: HTMLElement, fetchTrace: () => Promise<{ok, status, data}>) -> void`.
    - İlk tıklamada izi getirir ve çizer; sonraki tıklamalarda gizler ve gösterir.
    - Düğme metni "Kodu adım adım izle" ile "İzi gizle" arasında değişir.
    - Hata durumunda container'a `data.error` veya "İz alınamadı." yazar.
- Stil kuralları:
  - `li.now` arka planı `--marker`.
  - `.why-note` için `font-family: var(--font-hand)`, `color: var(--pen)`, `font-size: 1.35rem`.
  - Değişken tablosu `--rule` çizgili, kod için `--font-code`.
  - Telefonda (≤560px) kod, değişkenler ve çıktı tek sütunda.

- [ ] **Step 1: Add `/static/js/tracer.js` to the static asset list in `test_pages_and_security_headers`, run it**

Run: `python -m pytest tests/test_api.py::test_pages_and_security_headers -q`
Expected: FAIL (404)

- [ ] **Step 2: Implement `tracer.js`, CSS and template includes per Produces.**

- [ ] **Step 3: Run tests**

Run: `python -m pytest -q`
Expected: tümü PASS

- [ ] **Step 4: Commit**

```bash
git add pytest_pro/static pytest_pro/templates tests/test_api.py
git commit -m "Kod izi bileşeni ve 'neden yanlış' notu"
```

---

### Task 6: Pratik ekranı akışı

**Files:**
- Modify: `pytest_pro/static/js/practice.js`
- Modify: `pytest_pro/templates/practice.html`
- Modify: `pytest_pro/static/css/style.css` (`.topic-progress`, `.done-mark`)

**Interfaces:**
- Consumes: Task 3 uçları, Task 5'teki `renderTrace`, `whyNote` ve `traceToggle`.
- Produces (yalnızca tarayıcı davranışı; spec §4):
  - **İpucu:** Kontrolden önce görünen "İpucu" düğmesi `/hint`'i çağırır. İpucu `.exp` kutusunda
    gösterilir ve o soru için `usedHint = true` olur. `404` dönerse düğme gizlenir.
  - **Doğru cevap:**
    - Sonuç kutusunda "Doğru" yazar; ipucu alındıysa "Doğru (ipucuyla)".
    - Düğmeler: "Yeni soru" (birincil) ve "Kodu adım adım izle" (`has_trace` ise).
  - **Yanlış cevap:**
    - Sonuç kutusu sırasıyla `whyNote(why)` (varsa), doğru cevap ve çözümü gösterir.
    - Düğmeler: "Bu konudan yeni soru" (birincil; `/next` isteği `gen` ile), "Kodu adım adım izle",
      "Yeni soru".
  - **İlerleme kaydı:** `sessionStorage['pytest_pratik']` yapısı spec §4'teki gibidir:
    `{unit: {gen: {streak, done, topic}}}`.
    - İpucusuz doğru cevap `streak` değerini 1 artırır; yanlış cevap veya ipucu sıfırlar.
    - `streak >= 2` olunca `done = true` olur.
    - Okuma ve yazma `try/catch` içindedir; depolama yoksa bellekte tutulur.
  - **Soru seçimi:** "Yeni soru", `/next` isteğini `avoid` ile gönderir; liste o ünitede `done`
    olan şablonlardır.
  - **İçindekiler:** Her ünitenin altında `.topic-progress` alanında "X / Y konu tamamlandı" yazar.
    Konu sayısı `unit.topics`'ten gelir. Bir konu, o konuya ait ve görülmüş tüm şablonları `done`
    olduğunda tamamlanmış sayılır.
  - **Ünite bitince:** Ünitenin bütün konuları tamamlanınca soru alanının üstünde bir not çıkar:
    "Bu ünitedeki tüm konuları tamamladın. Sıradaki ünite: {başlık}". Not, ünite listesinde bir
    sonraki üniteyi açan bir düğme içerir.

- [ ] **Step 1: Implement per Produces.**

- [ ] **Step 2: Browser check (Playwright script in scratchpad, not committed)**

Pratik modunu öğretmen API'siyle açın. `temel` ünitesinde şunları doğrulayın:
- İpucu açılıyor.
- Yanlış şık seçilince "Neden yanlış" notu görünüyor.
- İz açılıyor ve → tuşu adımı ilerletiyor.
- "Bu konudan yeni soru" aynı konuyu getiriyor.
- Aynı şablonda iki ipucusuz doğru cevap sonrası içindekiler ilgili konuyu tamamlanmış sayıyor.
- Konsolda hata yok; 390 piksel genişlikte yatay taşma yok.

Expected: Betik tüm kontrollerde `OK` yazar.

- [ ] **Step 3: Run tests and commit**

```bash
python -m pytest -q
git add pytest_pro/static pytest_pro/templates
git commit -m "Pratik: ipucu, tekrar çözdürme, konu tamamlama, kod izi"
```

---

### Task 7: Sınav sonucu ve öğretmen ekranları

**Files:**
- Modify: `pytest_pro/static/js/student.js` (`showResult`)
- Modify: `pytest_pro/static/js/teacher.js` (`detail`, `renderTopics`)
- Modify: `pytest_pro/static/css/style.css` (`.common-wrong`)

**Interfaces:**
- Consumes: Task 4 alanları ve uçları, Task 5'teki `whyNote` ve `traceToggle`.
- Produces:
  - **Öğrenci sonucu:**
    - Yanlış sorularda "Senin cevabın" satırının ardından `whyNote(q.why)` gelir (varsa).
    - `has_trace` olan her soruda "Kodu adım adım izle" düğmesi bulunur. Düğme, yanlış sorularda
      `.btn sm`, doğru sorularda daha sade `.btn sm` biçimindedir. İz `/api/exam/trace` ile getirilir
      ve sorunun altındaki bir `div` içinde açılır.
  - **Öğretmen ayrıntısı:** Aynı "neden yanlış" notu ve iz düğmesi bulunur; iz
    `/api/results/<id>/trace/<qid>` ile şifre başlığıyla getirilir.
  - **Konu analizi:** `common_wrong` alanı olan satırların altında `.common-wrong` öğesi gösterilir.
    Metni: `%${share} "${esc(answer)}" cevabını verdi.` Ardından, açıklama varsa
    `whyNote(why)` gelir.

- [ ] **Step 1: Implement per Produces.**

- [ ] **Step 2: Browser check (scratchpad script)**

Kurulum: Öğretmen olarak `veri_tipleri` ünitesinden 5 soruluk bir sınav kurun, öğrenci olarak bütün
şıklara yanlış cevap verip gönderin.

Doğrulayın:
- **Öğrenci sonucu:** "Neden yanlış" notları görünüyor; bir iz açılıp kapanıyor.
- **Öğretmen ayrıntısı:** İz açılıyor.
- **Konu analizi:** "%100" ifadesi ve açıklama görünüyor.
- **Genel:** Konsolda hata yok.

Expected: Betik tüm kontrollerde `OK` yazar.

- [ ] **Step 3: Run tests and commit**

```bash
python -m pytest -q
git add pytest_pro/static
git commit -m "Sınav sonucu ve öğretmen paneli: neden yanlış, kod izi, en sık yanlış"
```

---

### Task 8: İçerik: Ünite 1–2 (16 şablon)

**Files:**
- Modify: `pytest_pro/questions/units/u01_temel.py`, `u02_veri_tipleri.py`
- Modify: `tests/test_content.py`

**Interfaces:**
- Consumes: Task 1 `Wrong`, `hint=`, `common_wrongs=`.
- Produces: Bu iki ünitenin her şablonunda `hint` bulunur. Her seçenekli şablonda açıklamasız yanlış
  şık kalmaz; yedek çeldiriciler hariç her yanlış `Wrong` olarak yazılır. Kısa cevaplı şablonlarda en
  az bir `common_wrongs` bulunur.

İçerik kuralları:
- **Ses:** İkinci tekil şahıs ve öğrencinin düşüncesini adlandıran cümleler kullanılır ("... diye
  düşünmüş olabilirsin, ama ..."). Açıklamalar 1–2 cümleyi geçmez ve suçlayıcı değildir.
- **İpucu:** Neye bakılacağını söyler, sonucu söylemez. Örneğin "Önce a ile b'nin tipine bak: tırnak
  içinde mi?"
- **Dinamik değerler:** Açıklamalar, şablonun ürettiği değerleri kullanabilir (f-string). HTML'e
  gömülen değerler `e()` ile kaçışlanır.
- **`var_name`:** Seçenekler değişken adı olduğu için her geçersiz ada neden geçersiz olduğunu söyleyen
  bir açıklama verilir. Örneğin `"2sayi"` → "Rakamla başlıyor".
- **`conversion_error`:** Yanlış seçenekler hata vermeyen ifadelerdir. Açıklama, ifadenin neden
  sorunsuz çalıştığını söyler.

- [ ] **Step 1: Write the failing content coverage test** in `tests/test_content.py`:

```python
import random, pytest
from pytest_pro import questions as qs
from pytest_pro.questions.helpers import FILLER_WHY_NUMBER, FILLER_WHY_OTHER
from pytest_pro.questions.registry import UNITS

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
```

Task 8 sırasında `CONTENT_UNITS` geçici olarak `("temel", "veri_tipleri")` olarak tutulur.

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_content.py -q`
Expected: FAIL (`ipucu yok`)

- [ ] **Step 3: Write the content for the 16 templates.**

- [ ] **Step 4: Run all tests**

Run: `python -m pytest -q`
Expected: tümü PASS

- [ ] **Step 5: Commit**

```bash
git add pytest_pro/questions/units/u01_temel.py pytest_pro/questions/units/u02_veri_tipleri.py pytest_pro/questions/__init__.py tests/test_content.py
git commit -m "İçerik: Ünite 1-2 ipuçları ve yanlış şık açıklamaları"
```

---

### Task 9: İçerik: Ünite 3–4 (14 şablon)

**Files:**
- Modify: `pytest_pro/questions/units/u03_operatorler.py`, `u04_metinler.py`
- Modify: `pytest_pro/questions/__init__.py` (`CONTENT_UNITS` son hâli: 4 ünite)

**Interfaces:**
- Consumes: Task 8'deki kurallar ve test.

- [ ] **Step 1:** `CONTENT_UNITS` listesine `"operatorler"` ve `"metinler"` eklenir.
  Run: `python -m pytest tests/test_content.py -q`. Expected: FAIL.
- [ ] **Step 2:** İçeriği yazın. Özel durumlar:
  - `precedence`, `logic` ve `augmented` gibi değeri hesaplanan şablonlarda yanlışlar ve açıklamaları,
    tipik yanılgı hesaplanarak üretilir. Örneğin soldan sağa hesaplanmış sonuç → "Çarpmayı toplamadan
    önce yapmadın".
  - Hesaplanan yanlış, doğru cevaba eşit çıkarsa listeye alınmaz.
- [ ] **Step 3:** Run: `python -m pytest -q`. Expected: tümü PASS.
- [ ] **Step 4: Commit**

```bash
git add pytest_pro/questions
git commit -m "İçerik: Ünite 3-4 ipuçları ve yanlış şık açıklamaları"
```

---

### Task 10: Belgeler ve uçtan uca doğrulama

**Files:**
- Modify: `docs/TASARIM.md` (bileşenler: "Kod izi", "Neden yanlış notu", "Konu ilerlemesi")
- Modify: `docs/GELISTIRME.md` (şablon yazımı: `Wrong`, `hint`, `common_wrongs`, içerik kuralları,
  `CONTENT_UNITS`)
- Modify: `docs/superpowers/specs/2026-11-11-ogrenmeyi-derinlestirme-design.md` (Durum: "Birinci teslimat uygulandı")
- Regenerate: `docs/MUFREDAT.md` (`python -m pytest_pro.questions.catalog > docs/MUFREDAT.md`)

- [ ] **Step 1:** Belgeleri güncelleyin.
- [ ] **Step 2: Doğrulama**
  - Run: `python -m pytest -q` ve `python -m pyflakes pytest_pro tests server.py`. Expected: tümü PASS,
    pyflakes çıktısı boş.
  - Task 6 ve 7'deki tarayıcı betiklerini birlikte çalıştırın. Expected: `OK`, konsol hatası yok.
- [ ] **Step 3: Commit and push**

```bash
git add docs
git commit -m "Belgeler: öğrenme yardımları"
git push -u origin ogrenme/derinlestirme
```

---

## Sıra notu

Görevleri şu sırayla uygulayın: **1 → 2 → 3 → 8 → 4 → 5 → 6 → 7 → 9 → 10**. Task 4'ün
`test_submit_includes_why_and_has_trace` ve `test_topic_stats_common_wrong` testleri `veri_tipleri`
içeriğine (Task 8) dayanır. Task 3'ün `test_check_returns_why_for_wrong_option` testi
`veri_tipleri.str_concat` içeriğine dayanır; Task 3'ü uygularken bu testi `xfail` yapın, Task 8
bitince işareti kaldırın.
