"""
PyTest Pro - soru üreteçleri ve puanlama.

Her üreteç (q_... fonksiyonu) bir sözlük döndürür:
    type      "mc" (çoktan seçmeli) | "tf" (doğru/yanlış) | "short" (kısa cevap) | "code" (kod yazma)
    topic     konu adı
    text      soru metni (sunucuda üretilen güvenli HTML)
    code      gösterilecek kod parçası ya da None
    options   yalnızca "mc" için seçenekler
    answer    doğru cevap (sınav sırasında öğrenciye gönderilmez)
    solution  açıklama (HTML)

Öğrenciye hiç gönderilmeyen isteğe bağlı iç alanlar:
    check     "code" soruları için denetim bilgisi
    stdin     kodun çalışırken klavyeden okuduğu girdi (testlerde kullanılır)
"""
import ast
import html
import random

MAX_CODE_LEN = 2000
ERROR = "Hata verir (TypeError)"
STR_VALUES = ["Python", "Kodlama", "Gelisim", "Yazilim", "Bilgisayar", "Algoritma"]
PEOPLE = ["Ali", "Ayşe", "Can", "Deniz", "Ece", "Elif", "Mert", "Zeynep"]
PUBLIC_KEYS = ("id", "type", "topic", "text", "code", "options")


def _e(value):
    return html.escape(str(value), quote=False)


def _shown(s):
    """Boşlukları görünür yapar: ' - ' -> '"␣-␣"', '' -> 'boş metin ("")'."""
    return '"' + s.replace(" ", "␣") + '"' if s else 'boş metin ("")'


def unique_options(correct, wrongs, n=4):
    """Doğru cevap + birbirinden farklı yanlışlar (en fazla n seçenek), karıştırılmış."""
    opts = [correct]
    for w in wrongs:
        if len(opts) == n:
            break
        if w not in opts:
            opts.append(w)
    random.shuffle(opts)
    return opts


# ======================================================================
# Soru şablonları
# ======================================================================
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
        "solution": f'<code>sep="{_e(sep)}"</code> parametresi, print\'e verilen değerlerin arasına '
                    f'"{_e(sep)}" koyar. Varsayılan ayırıcı tek boşluktur.',
    }


def q_print_end():
    w1, w2 = random.sample(STR_VALUES, 2)
    end = random.choice(["", " ", "-", "***", " | "])
    correct = f"{w1}{end}{w2}"
    return {
        "type": "mc",
        "topic": "Print Parametreleri (end)",
        "text": "Aşağıdaki kodun ekran çıktısı ne olur?",
        "code": f'print("{w1}", end="{end}")\nprint("{w2}")',
        "options": unique_options(correct, [
            f"{w1}\n{w2}", f"{w1} {w2}", f"{w1}{w2}", f"{w1}{end}\n{w2}", f"{w2}{end}{w1}",
        ]),
        "answer": correct,
        "solution": "<code>end</code> parametresi print'in sonuna eklenecek metni belirler; varsayılanı "
                    f"yeni satırdır (<code>\\n</code>). Burada sona {_e(_shown(end))} eklendiği için "
                    "ikinci print aynı satırdan devam eder.",
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
        "solution": f'<code>a</code> metin ("{n1}") olarak tanımlanmıştır. <code>int(a)</code> ile {n1} '
                    f"sayısına dönüşür; {n1} {op} {n2} = {res}.",
    }


def q_float_int():
    if random.random() < 0.5:
        whole, frac = random.randint(2, 20), random.randint(1, 9)
        return {
            "type": "short",
            "topic": "Tip Dönüşümleri (float/int)",
            "text": "Aşağıdaki kodun ekran çıktısını yazınız:",
            "code": f"x = {whole}.{frac}\nprint(int(x))",
            "answer": str(whole),
            "solution": f"<code>int()</code> ondalıklı sayının kesir kısmını atar (yuvarlamaz): "
                        f"int({whole}.{frac}) = {whole}.",
        }
    n = random.randint(2, 20)
    return {
        "type": "short",
        "topic": "Tip Dönüşümleri (float/int)",
        "text": "Aşağıdaki kodun ekran çıktısını yazınız:",
        "code": f'x = "{n}"\ny = float(x)\nprint(y)',
        "answer": f"{n}.0",
        "solution": f'<code>float("{n}")</code> metni ondalıklı sayıya çevirir; float değerler '
                    f"ekrana {n}.0 biçiminde yazılır.",
    }


def q_fstring():
    vname = random.choice(["ad", "kullanici", "isim"])
    val = random.choice(PEOPLE)
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
        "solution": "f-string içinde süslü parantez <code>{}</code> içindeki değişkenler kendi "
                    "değerleriyle değiştirilir.",
    }


def q_input_type():
    is_true = random.random() < 0.5
    text = (
        "Python'da <code>input()</code> fonksiyonu kullanıcıdan alınan veriyi her zaman "
        "<strong>str (metin)</strong> tipinde döndürür."
        if is_true else
        "Python'da <code>input()</code> fonksiyonu kullanıcı bir sayı girdiğinde bunu otomatik olarak "
        "<strong>int (tam sayı)</strong> tipine dönüştürür."
    )
    return {
        "type": "tf",
        "topic": "input() Veri Tipi",
        "text": text,
        "code": 'veri = input("Bir şey giriniz: ")',
        "answer": "True" if is_true else "False",
        "solution": "<code>input()</code> ile alınan her girdi str türündedir. Sayısal işlem için "
                    "<code>int()</code> veya <code>float()</code> dönüşümü gerekir.",
    }


def q_input_concat():
    n = random.randint(2, 9)
    k = random.choice([2, 3])
    correct = str(n) * k
    return {
        "type": "mc",
        "topic": "input() Veri Tipi",
        "text": f"Kod çalıştırıldığında kullanıcı klavyeden <strong>{n}</strong> yazıp Enter'a basıyor. "
                "Ekrana ne yazdırılır?",
        "code": f"sayi = input()\nprint(sayi * {k})",
        "stdin": str(n),
        "options": unique_options(correct, [str(n * k), ERROR, " ".join([str(n)] * k)]),
        "answer": correct,
        "solution": f'<code>input()</code> metin döndürür: sayi = "{n}". Metin * {k} işlemi metni {k} kez '
                    f"tekrarlar, bu yüzden sonuç {correct} olur. Sayı olarak çarpmak için "
                    "<code>int(input())</code> gerekir.",
    }


def q_str_concat():
    n1, n2 = random.randint(1, 9), random.randint(1, 9)
    correct = f"{n1}{n2}"
    return {
        "type": "mc",
        "topic": "Metin İşlemleri (str)",
        "text": "Aşağıdaki kodun ekran çıktısı ne olur?",
        "code": f'a = "{n1}"\nb = "{n2}"\nprint(a + b)',
        "options": unique_options(correct, [str(n1 + n2), f"{n1} {n2}", ERROR]),
        "answer": correct,
        "solution": "İki değişken de tırnak içinde olduğu için str tipindedir. Metinlerde <code>+</code> "
                    f"toplama değil birleştirme yapar: \"{n1}\" + \"{n2}\" = \"{correct}\".",
    }


def q_str_repeat():
    word = random.choice(["ab", "Py", "ha", "xo", "-*"])
    k = random.randint(2, 4)
    correct = word * k
    return {
        "type": "mc",
        "topic": "Metin İşlemleri (str)",
        "text": "Aşağıdaki kodun ekran çıktısı ne olur?",
        "code": f'kelime = "{word}"\nprint(kelime * {k})',
        "options": unique_options(correct, [f"{word}{k}", " ".join([word] * k), ERROR]),
        "answer": correct,
        "solution": f"Bir metni tam sayıyla çarpmak o metni art arda tekrarlar: "
                    f'"{_e(word)}" * {k} = "{_e(correct)}".',
    }


def q_int_div():
    a, b = random.randint(11, 40), random.randint(2, 7)
    op = random.choice(["//", "%"])
    res = a // b if op == "//" else a % b
    expl = (f"<code>//</code> tam sayı bölmesidir, bölümün yalnızca tam kısmını verir: {a} // {b} = {res}."
            if op == "//" else
            f"<code>%</code> (mod) bölme işleminden kalanı verir: {a} = {b} × {a // b} + {res}.")
    return {
        "type": "short",
        "topic": "Aritmetik Operatörler",
        "text": "Aşağıdaki kodun ekran çıktısını yazınız:",
        "code": f"a = {a}\nb = {b}\nprint(a {op} b)",
        "answer": str(res),
        "solution": expl,
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
        "solution": "Değişkenlere değer atanır, çarpım <code>*</code> operatörüyle yapılıp "
                    "<code>print()</code> ile yazdırılır.",
    }


def q_type_func():
    literal, typ = random.choice([
        ("3.14", "float"), ("0.0", "float"),
        ("42", "int"), ("-7", "int"),
        ('"100"', "str"), ('"3.14"', "str"), ('"True"', "str"),
        ("True", "bool"), ("False", "bool"),
    ])
    opts = ["<class 'int'>", "<class 'float'>", "<class 'str'>", "<class 'bool'>"]
    random.shuffle(opts)
    answer = f"<class '{typ}'>"
    note = " Tırnak içindeki her değer, içeriği ne olursa olsun metindir." if literal.startswith('"') else ""
    return {
        "type": "mc",
        "topic": "type() ve Veri Tipleri",
        "text": "Aşağıdaki kodun çıktısı ne olur?",
        "code": f"x = {literal}\nprint(type(x))",
        "options": opts,
        "answer": answer,
        "solution": f"<code>type()</code> değerin tipini döndürür. <code>{_e(literal)}</code> değeri "
                    f"{_e(answer)} tipindedir.{note}",
    }


def q_var_name():
    valid = random.choice(["ogrenci_no", "_sayac", "toplam2", "adSoyad", "yas_1", "not_ortalamasi"])
    invalid = random.sample(["2sayi", "ogrenci no", "ad-soyad", "class", "for", "toplam$", "1_deger", "if"], 3)
    return {
        "type": "mc",
        "topic": "Değişken Adlandırma",
        "text": "Aşağıdakilerden hangisi Python'da <strong>geçerli</strong> bir değişken adıdır?",
        "code": None,
        "options": unique_options(valid, invalid),
        "answer": valid,
        "solution": "Değişken adları harf veya alt çizgi (_) ile başlar; yalnızca harf, rakam ve _ "
                    "içerebilir. Boşluk, - ve $ gibi işaretler kullanılamaz; <code>class</code>, "
                    "<code>for</code>, <code>if</code> gibi anahtar kelimeler değişken adı olamaz.",
    }


def q_swap():
    x, y = random.sample(range(1, 20), 2)
    correct = f"{y} {x}"
    return {
        "type": "mc",
        "topic": "Çoklu Atama",
        "text": "Aşağıdaki kodun ekran çıktısı ne olur?",
        "code": f"a, b = {x}, {y}\na, b = b, a\nprint(a, b)",
        "options": unique_options(correct, [f"{x} {y}", f"{y} {y}", f"{x} {x}"]),
        "answer": correct,
        "solution": "<code>a, b = b, a</code> satırında önce sağ taraf hesaplanır, sonra değerler aynı "
                    f"anda atanır; böylece a ile b yer değiştirir: a = {y}, b = {x}.",
    }


GENERATORS = [
    q_print_sep, q_print_end, q_type_conversion, q_float_int, q_fstring,
    q_input_type, q_input_concat, q_str_concat, q_str_repeat, q_int_div,
    q_write_code, q_type_func, q_var_name, q_swap,
]


def generate_questions(count):
    """Her şablondan dengeli dağılım; şablon sayısı yetmezse tekrar eder. Sıra rastgeledir."""
    pool = []
    while len(pool) < count:
        batch = GENERATORS[:]
        random.shuffle(batch)
        pool.extend(batch)
    pool = pool[:count]
    random.shuffle(pool)
    return [{"id": i + 1, **gen()} for i, gen in enumerate(pool)]


def public_question(q):
    """Öğrenciye giden sürüm: cevap, çözüm ve denetim bilgisi içermez."""
    return {k: q.get(k) for k in PUBLIC_KEYS}


# ======================================================================
# Kod sorusu değerlendirme (AST ile - öğrenci kodu ASLA çalıştırılmaz)
# ======================================================================
def _is_mult_of(node, v1, v2):
    return (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult)
            and isinstance(node.left, ast.Name) and isinstance(node.right, ast.Name)
            and {node.left.id, node.right.id} == {v1, v2} and v1 != v2)


def _assignments(stmt):
    """Bir atama satırındaki (ad, değer) çiftleri: a = 5, a = b = 5, a, b = 5, 3, a: int = 5."""
    if isinstance(stmt, ast.Assign):
        for target in stmt.targets:
            if isinstance(target, ast.Name):
                yield target.id, stmt.value
            elif (isinstance(target, (ast.Tuple, ast.List)) and isinstance(stmt.value, (ast.Tuple, ast.List))
                  and len(target.elts) == len(stmt.value.elts)):
                for t, v in zip(target.elts, stmt.value.elts):
                    if isinstance(t, ast.Name):
                        yield t.id, v
    elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name) and stmt.value is not None:
        yield stmt.target.id, stmt.value


def check_code_answer(src, chk):
    """Kriterler: v1 = n1 ve v2 = n2 ataması, ardından print(v1 * v2) (ara değişkenle de olabilir)."""
    v1, v2, n1, n2 = chk["v1"], chk["v2"], chk["n1"], chk["n2"]
    if len(src) > MAX_CODE_LEN:
        return False, "Kod çok uzun."
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return False, "Kodda sözdizimi (syntax) hatası var."
    except (ValueError, RecursionError, MemoryError):
        return False, "Kod çözümlenemedi."

    values = {}        # değişken -> sabit sayı değeri
    mult_vars = set()  # doğru değerlerle v1*v2 sonucunu tutan değişkenler
    printed_ok = False

    def values_ok():
        return values.get(v1) == n1 and values.get(v2) == n2

    for stmt in tree.body:
        pairs = list(_assignments(stmt))
        if pairs:
            ok_before = values_ok()
            for name, val in pairs:
                if isinstance(val, ast.Constant) and type(val.value) in (int, float):
                    values[name] = val.value
                else:
                    values.pop(name, None)
                if _is_mult_of(val, v1, v2) and ok_before:
                    mult_vars.add(name)
                else:
                    mult_vars.discard(name)
        elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            call = stmt.value
            if isinstance(call.func, ast.Name) and call.func.id == "print" and call.args:
                arg = call.args[0]
                if _is_mult_of(arg, v1, v2) and values_ok():
                    printed_ok = True
                elif isinstance(arg, ast.Name) and arg.id in mult_vars:
                    printed_ok = True

    if printed_ok:
        return True, "Kod tüm kriterleri sağlıyor."
    if values.get(v1) != n1:
        return False, f"<code>{v1}</code> değişkenine {n1} atanmamış."
    if values.get(v2) != n2:
        return False, f"<code>{v2}</code> değişkenine {n2} atanmamış."
    return False, "Çarpım <code>print()</code> ile doğru şekilde (atamalardan sonra) yazdırılmamış."


def _norm_short(s):
    # "3,5" ve "3.5" aynı kabul edilir; boşluklar önemsenmez
    return "".join(str(s).split()).replace(",", ".")


def grade(question, user_ans):
    """(doğru_mu, not) döndürür. Not yalnızca kod sorularında doludur."""
    raw = "" if user_ans is None else str(user_ans)
    qtype = question["type"]
    if not raw.strip():
        return False, ("Boş bırakıldı." if qtype == "code" else None)
    if qtype == "code":
        return check_code_answer(raw.strip(), question["check"])
    if qtype == "short":
        return _norm_short(raw) == _norm_short(question["answer"]), None
    return raw == question["answer"], None
