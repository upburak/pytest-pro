"""
PyTest Pro v2 - Python Giriş Dinamik Ölçme ve Değerlendirme Sistemi
Çalıştırma:  python server.py
Öğrenciler : http://<IP>:5000
Öğretmen   : http://<IP>:5000/ogretmen   (şifre konsolda yazar)
"""
import ast
import csv
import io
import json
import os
import random
import secrets
import socket
import sqlite3
import time
import uuid
from datetime import datetime
from functools import wraps

from flask import Flask, Response, g, jsonify, render_template, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("PYTEST_DB", os.path.join(BASE_DIR, "results.db"))
PORT = int(os.environ.get("PYTEST_PORT", "5000"))
EXAM_SECONDS = int(os.environ.get("PYTEST_SURE", "900"))  # 15 dk
GRACE_SECONDS = 30  # ağ gecikmesi toleransı
TEACHER_KEY = os.environ.get("PYTEST_SIFRE") or f"{secrets.randbelow(900000) + 100000}"

app = Flask(__name__)


# ======================================================================
# Veritabanı
# ======================================================================
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DB_PATH) as db:
        db.execute(
            """CREATE TABLE IF NOT EXISTS exams (
                id TEXT PRIMARY KEY,
                no TEXT NOT NULL,
                name TEXT NOT NULL,
                questions TEXT NOT NULL,
                answers TEXT,
                started_at REAL NOT NULL,
                submitted_at REAL,
                correct INTEGER,
                wrong INTEGER,
                score INTEGER
            )"""
        )


# ======================================================================
# Dinamik soru üreteçleri (cevaplar SADECE sunucuda kalır)
# ======================================================================
STR_VALUES = ["Python", "Kodlama", "Gelisim", "Yazilim", "Bilgisayar", "Algoritma"]


def unique_options(correct, wrongs):
    """Doğru cevap + birbirinden farklı yanlışlar, karıştırılmış."""
    opts = [correct]
    for w in wrongs:
        if w not in opts:
            opts.append(w)
    random.shuffle(opts)
    return opts


def q_print_sep():
    w1, w2 = random.sample(STR_VALUES, 2)
    sep = random.choice(["-", "*", "#", "...", "/", "_"])
    correct = f"{w1}{sep}{w2}"
    return {
        "type": "mc",
        "topic": "Print Parametreleri (sep)",
        "text": "Aşağıda verilen Python kodunun ekran çıktısı ne olur?",
        "code": f'print("{w1}", "{w2}", sep="{sep}")',
        "options": unique_options(correct, [f"{w1} {w2}", f"{w1}{w2}{sep}", f"{w1} {sep} {w2}"]),
        "answer": correct,
        "solution": f'<code>sep="{sep}"</code> parametresi, print\'e verilen değerlerin arasına "{sep}" koyar. Varsayılan ayırıcı tek boşluktur.',
    }


def q_type_conversion():
    n1, n2 = random.randint(2, 9), random.randint(10, 50)
    op = random.choice(["+", "*"])
    res = n1 + n2 if op == "+" else n1 * n2
    return {
        "type": "short",
        "topic": "Tip Dönüşümleri (int/str)",
        "text": "Aşağıdaki kod çalıştırıldığında ekrana yazdırılacak <strong>sayısal değeri</strong> giriniz:",
        "code": f'a = "{n1}"\nb = {n2}\nsonuc = int(a) {op} b\nprint(sonuc)',
        "answer": str(res),
        "solution": f'<code>a</code> metin ("{n1}") olarak tanımlanmıştır. <code>int(a)</code> ile {n1} sayısına dönüşür; {n1} {op} {n2} = {res}.',
    }


def q_fstring():
    vname = random.choice(["ad", "kullanici", "isim"])
    val = random.choice(["Ali", "Ayşe", "Can", "Deniz", "Ece"])
    age = random.randint(14, 18)
    correct = f"Merhaba {val}, yasiniz: {age}"
    return {
        "type": "mc",
        "topic": "f-string Kullanımı",
        "text": "Aşağıdaki f-string kodunun ekran çıktısı aşağıdakilerden hangisidir?",
        "code": f'{vname} = "{val}"\nyas = {age}\nprint(f"Merhaba {{{vname}}}, yasiniz: {{yas}}")',
        "options": unique_options(correct, [
            f"Merhaba {{{vname}}}, yasiniz: {{yas}}",
            f"Merhaba {vname}, yasiniz: yas",
            f'f"Merhaba {val}, yasiniz: {age}"',
        ]),
        "answer": correct,
        "solution": "f-string içinde süslü parantez <code>{}</code> içindeki değişkenler kendi değerleriyle değiştirilir.",
    }


def q_input_type():
    is_true = random.random() < 0.5
    text = (
        "Python'da <code>input()</code> fonksiyonu kullanıcıdan alınan veriyi her zaman <strong>str (metin)</strong> tipinde döndürür."
        if is_true else
        "Python'da <code>input()</code> fonksiyonu kullanıcı bir sayı girdiğinde bunu otomatik olarak <strong>int (tam sayı)</strong> tipine dönüştürür."
    )
    return {
        "type": "tf",
        "topic": "input() Veri Tipi",
        "text": text,
        "code": 'veri = input("Bir şey giriniz: ")',
        "answer": "True" if is_true else "False",
        "solution": "<code>input()</code> ile alınan her girdi str türündedir. Sayısal işlem için <code>int()</code> veya <code>float()</code> dönüşümü gerekir.",
    }


def q_write_code():
    v1 = random.choice(["sayi1", "a", "x"])
    v2 = random.choice(["sayi2", "b", "y"])
    n1, n2 = random.randint(5, 20), random.randint(2, 5)
    return {
        "type": "code",
        "topic": "Değişken & Aritmetik",
        "text": (
            "Şu adımları gerçekleştiren Python kodunu yazınız:<br>"
            f"1. <code>{v1}</code> adında bir değişken tanımlayıp <strong>{n1}</strong> değerini atayın.<br>"
            f"2. <code>{v2}</code> adında bir değişken tanımlayıp <strong>{n2}</strong> değerini atayın.<br>"
            "3. Bu iki değişkenin çarpımını <code>print()</code> ile ekrana yazdırın."
        ),
        "code": None,
        "check": {"v1": v1, "v2": v2, "n1": n1, "n2": n2},
        "answer": f"{v1} = {n1}\n{v2} = {n2}\nprint({v1} * {v2})",
        "solution": "Değişkenlere değer atanır, çarpım <code>*</code> operatörüyle yapılıp <code>print()</code> ile yazdırılır.",
    }


def q_type_func():
    sel = random.choice([
        ("3.14", "<class 'float'>"),
        ("42", "<class 'int'>"),
        ('"100"', "<class 'str'>"),
        ("True", "<class 'bool'>"),
    ])
    opts = ["<class 'int'>", "<class 'float'>", "<class 'str'>", "<class 'bool'>"]
    random.shuffle(opts)
    return {
        "type": "mc",
        "topic": "type() ve Veri Tipleri",
        "text": "Aşağıdaki kodun çıktısı ne olur?",
        "code": f"x = {sel[0]}\nprint(type(x))",
        "options": opts,
        "answer": sel[1],
        "solution": f"<code>type()</code> değerin tipini döndürür. <code>{sel[0]}</code> değeri {sel[1].replace('<', '&lt;').replace('>', '&gt;')} tipindedir.",
    }


def q_print_end():
    is_true = random.random() < 0.5
    symbol = random.choice([" ", " - ", "***"])
    shown = symbol.replace(" ", "␣")
    text = (
        f'<code>print("Merhaba", end="{shown}")</code> kullanımı, yazdırmadan sonra alt satıra geçmek yerine sona "{shown}" ekler.'
        if is_true else
        f'<code>print("Merhaba", end="{shown}")</code> kullanımı bir sonraki print komutunu siler ve çalıştırmaz.'
    )
    return {
        "type": "tf",
        "topic": "Print Parametreleri (end)",
        "text": text + ' <span class="hint">(␣ = boşluk)</span>' if " " in symbol else text,
        "code": f'print("Merhaba", end="{symbol}")\nprint("Dünya")',
        "answer": "True" if is_true else "False",
        "solution": "<code>end</code> parametresi, print'in sonuna varsayılan olarak eklenen yeni satır (\\n) karakterinin yerine geçer.",
    }


GENERATORS = [q_print_sep, q_type_conversion, q_fstring, q_input_type,
              q_write_code, q_type_func, q_print_end]


def generate_questions(count):
    # Her şablondan dengeli dağılım + gerçek rastgele sıra
    pool = []
    while len(pool) < count:
        batch = GENERATORS[:]
        random.shuffle(batch)
        pool.extend(batch)
    pool = pool[:count]
    random.shuffle(pool)
    return [{"id": i + 1, **gen()} for i, gen in enumerate(pool)]


# ======================================================================
# Kod sorusu değerlendirme (AST ile - öğrenci kodu ÇALIŞTIRILMAZ)
# ======================================================================
def _is_mult_of(node, v1, v2):
    return (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult)
            and isinstance(node.left, ast.Name) and isinstance(node.right, ast.Name)
            and {node.left.id, node.right.id} == {v1, v2} and v1 != v2)


def check_code_answer(src, chk):
    """Kriterler: v1 = n1, v2 = n2 ataması ve print(v1*v2) (veya ara değişkenle)."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return False, "Kodda sözdizimi (syntax) hatası var."

    assigns = {}
    mult_vars = set()
    printed_ok = False
    for stmt in tree.body:
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
            name, val = stmt.targets[0].id, stmt.value
            if isinstance(val, ast.Constant) and type(val.value) in (int, float):
                assigns[name] = val.value
            if _is_mult_of(val, chk["v1"], chk["v2"]):
                mult_vars.add(name)
        elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            call = stmt.value
            if isinstance(call.func, ast.Name) and call.func.id == "print" and call.args:
                arg = call.args[0]
                if _is_mult_of(arg, chk["v1"], chk["v2"]) or (isinstance(arg, ast.Name) and arg.id in mult_vars):
                    # print'ten önce atamaların yapılmış olması gerekir
                    if assigns.get(chk["v1"]) == chk["n1"] and assigns.get(chk["v2"]) == chk["n2"]:
                        printed_ok = True

    if assigns.get(chk["v1"]) != chk["n1"]:
        return False, f"<code>{chk['v1']}</code> değişkenine {chk['n1']} atanmamış."
    if assigns.get(chk["v2"]) != chk["n2"]:
        return False, f"<code>{chk['v2']}</code> değişkenine {chk['n2']} atanmamış."
    if not printed_ok:
        return False, "Çarpım <code>print()</code> ile doğru şekilde yazdırılmamış."
    return True, "Kod tüm kriterleri sağlıyor."


def grade(question, user_ans):
    user_ans = (user_ans or "").strip()
    if question["type"] == "code":
        return check_code_answer(user_ans, question["check"]) if user_ans else (False, "Boş bırakıldı.")
    if question["type"] == "short":
        return user_ans.replace(" ", "") == question["answer"], None
    return user_ans == question["answer"], None


def public_question(q):
    """Öğrenciye giden sürüm: cevap/çözüm/kontrol bilgisi yok."""
    return {k: q.get(k) for k in ("id", "type", "topic", "text", "code", "options")}


# ======================================================================
# Yardımcılar
# ======================================================================
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))  # paket gönderilmez, internet gerekmez
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def teacher_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        key = request.headers.get("X-Ogretmen-Sifre") or request.args.get("sifre")
        if not key or not secrets.compare_digest(key, TEACHER_KEY):
            return jsonify({"error": "Yetkisiz. Öğretmen şifresi hatalı."}), 401
        return f(*args, **kwargs)
    return wrapper


def clean(s, n):
    return " ".join(str(s or "").split())[:n]


# ======================================================================
# Sayfalar
# ======================================================================
@app.route("/")
def student_page():
    return render_template("index.html")


@app.route("/ogretmen")
def teacher_page():
    return render_template("teacher.html")


# ======================================================================
# Öğrenci API
# ======================================================================
@app.post("/api/start")
def api_start():
    data = request.get_json(silent=True) or {}
    name, no = clean(data.get("name"), 60), clean(data.get("no"), 20)
    try:
        count = int(data.get("count", 10))
    except (TypeError, ValueError):
        count = 10
    if count not in (5, 10, 15):
        count = 10
    if not name or not no:
        return jsonify({"error": "Ad Soyad ve Okul No zorunludur."}), 400

    exam_id = uuid.uuid4().hex
    questions = generate_questions(count)
    db = get_db()
    db.execute(
        "INSERT INTO exams (id, no, name, questions, started_at) VALUES (?,?,?,?,?)",
        (exam_id, no, name, json.dumps(questions, ensure_ascii=False), time.time()),
    )
    db.commit()
    return jsonify({
        "exam_id": exam_id,
        "duration": EXAM_SECONDS,
        "questions": [public_question(q) for q in questions],
    })


@app.post("/api/submit")
def api_submit():
    data = request.get_json(silent=True) or {}
    exam_id = str(data.get("exam_id", ""))
    answers = data.get("answers") or {}
    if not isinstance(answers, dict):
        answers = {}

    db = get_db()
    row = db.execute("SELECT * FROM exams WHERE id = ?", (exam_id,)).fetchone()
    if row is None:
        return jsonify({"error": "Sınav bulunamadı."}), 404
    if row["submitted_at"] is not None:
        return jsonify({"error": "Bu sınav zaten gönderildi."}), 409

    now = time.time()
    late = now - row["started_at"] > EXAM_SECONDS + GRACE_SECONDS
    questions = json.loads(row["questions"])

    correct = 0
    details = []
    for q in questions:
        ua = "" if late else str(answers.get(str(q["id"]), ""))[:2000]
        ok, note = grade(q, ua)
        correct += ok
        details.append({
            "id": q["id"], "topic": q["topic"], "text": q["text"], "code": q.get("code"),
            "type": q["type"], "user_answer": ua, "answer": q["answer"],
            "correct": ok, "note": note, "solution": q["solution"],
        })

    total = len(questions)
    wrong = total - correct
    score = round(correct * 100 / total)
    db.execute(
        "UPDATE exams SET answers=?, submitted_at=?, correct=?, wrong=?, score=? WHERE id=? AND submitted_at IS NULL",
        (json.dumps(answers, ensure_ascii=False), now, correct, wrong, score, exam_id),
    )
    db.commit()
    return jsonify({"correct": correct, "wrong": wrong, "score": score,
                    "percent": score, "late": late, "details": details})


# ======================================================================
# Öğretmen API (şifreli)
# ======================================================================
@app.get("/api/info")
@teacher_required
def api_info():
    return jsonify({"url": f"http://{get_local_ip()}:{PORT}", "duration": EXAM_SECONDS})


@app.get("/api/qr.svg")
def api_qr():
    import qrcode
    import qrcode.image.svg
    url = f"http://{get_local_ip()}:{PORT}"
    img = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, box_size=10, border=2)
    buf = io.BytesIO()
    img.save(buf)
    return Response(buf.getvalue(), mimetype="image/svg+xml")


@app.get("/api/results")
@teacher_required
def api_results():
    db = get_db()
    rows = db.execute(
        "SELECT id, no, name, started_at, submitted_at, correct, wrong, score FROM exams ORDER BY started_at"
    ).fetchall()
    attempts = {}
    out = []
    for r in rows:
        attempts[r["no"]] = attempts.get(r["no"], 0) + 1
        out.append({
            "id": r["id"], "no": r["no"], "name": r["name"], "attempt": attempts[r["no"]],
            "started": datetime.fromtimestamp(r["started_at"]).strftime("%d.%m.%Y %H:%M:%S"),
            "submitted": datetime.fromtimestamp(r["submitted_at"]).strftime("%H:%M:%S") if r["submitted_at"] else None,
            "correct": r["correct"], "wrong": r["wrong"], "score": r["score"],
            "status": "bitti" if r["submitted_at"] else (
                "sure_doldu" if time.time() - r["started_at"] > EXAM_SECONDS + GRACE_SECONDS else "sinavda"),
        })
    out.reverse()
    return jsonify(out)


@app.get("/api/results/<exam_id>")
@teacher_required
def api_result_detail(exam_id):
    row = get_db().execute("SELECT * FROM exams WHERE id = ?", (exam_id,)).fetchone()
    if row is None:
        return jsonify({"error": "Bulunamadı"}), 404
    questions = json.loads(row["questions"])
    answers = json.loads(row["answers"] or "{}")
    details = []
    for q in questions:
        ua = str(answers.get(str(q["id"]), ""))
        ok, note = grade(q, ua)
        details.append({"id": q["id"], "topic": q["topic"], "text": q["text"], "code": q.get("code"),
                        "user_answer": ua, "answer": q["answer"], "correct": ok, "note": note})
    return jsonify({"name": row["name"], "no": row["no"], "score": row["score"], "details": details})


@app.delete("/api/results")
@teacher_required
def api_clear():
    db = get_db()
    db.execute("DELETE FROM exams")
    db.commit()
    return jsonify({"status": "ok"})


@app.get("/api/results.csv")
@teacher_required
def api_csv():
    rows = get_db().execute(
        "SELECT no, name, started_at, submitted_at, correct, wrong, score FROM exams "
        "WHERE submitted_at IS NOT NULL ORDER BY CAST(no AS INTEGER), no"
    ).fetchall()
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";")  # Türkçe Excel ; ayırıcı kullanır
    w.writerow(["Okul No", "Ad Soyad", "Başlama", "Bitiş", "Doğru", "Yanlış", "Puan"])
    for r in rows:
        w.writerow([
            r["no"], r["name"],
            datetime.fromtimestamp(r["started_at"]).strftime("%d.%m.%Y %H:%M"),
            datetime.fromtimestamp(r["submitted_at"]).strftime("%H:%M"),
            r["correct"], r["wrong"], r["score"],
        ])
    data = "﻿" + buf.getvalue()  # BOM: Excel'de Türkçe karakterler bozulmaz
    fname = f"python_sinav_{datetime.now():%Y%m%d_%H%M}.csv"
    return Response(data.encode("utf-8"), mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment; filename={fname}"})


init_db()

# ======================================================================
if __name__ == "__main__":
    ip = get_local_ip()
    print("\n" + "=" * 52)
    print("  PYTEST PRO - ÖĞRETMEN SUNUCUSU AKTİF")
    print(f"  Öğrenci adresi : http://{ip}:{PORT}")
    print(f"  Öğretmen paneli: http://{ip}:{PORT}/ogretmen")
    print(f"  Öğretmen şifresi: {TEACHER_KEY}")
    print("=" * 52 + "\n")
    app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)
