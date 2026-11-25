"""Ünite 3 - Operatörler."""
import ast
import copy
import random

from ..codecheck import OK, checker, same_value
from ..helpers import Wrong, code_options_question, e, err, fill_question, output_question, tf_claim, tf_question
from ..registry import register_unit
from .u01_temel import print_numbers, straight_run

UNIT = register_unit(
    "operatorler", "Operatörler", "Başlangıç",
    "Aritmetik (+ - * / // % **), işlem önceliği, karşılaştırma, mantıksal (and/or/not) ve "
    "birleşik atama (+=, -=, *=) operatörleri.",
    order=3,
)
q = UNIT.question


def _distinct(answer, wrongs):
    """Doğru cevaba eşit çıkan hesaplanmış yanlışları atar."""
    return [w for w in wrongs if w.value != answer]


@q("Tam Bölme ve Mod", verify="output")
def int_div():
    a, b = random.randint(11, 40), random.randint(2, 7)
    op = random.choice(["//", "%"])
    res = a // b if op == "//" else a % b
    if op == "//":
        expl = f"<code>//</code> tam sayı bölmesidir, bölümün yalnızca tam kısmını verir: {a} // {b} = {res}."
        common = [Wrong(str(a % b), "Bu kalan; kalanı <code>%</code> verir. <code>//</code> bölümün tam kısmını verir."),
                  Wrong(str(a / b), "Bu <code>/</code> bölmesinin sonucu; <code>//</code> kesir kısmını atar.")]
    else:
        expl = f"<code>%</code> (mod) bölme işleminden kalanı verir: {a} = {b} × {a // b} + {res}."
        common = [Wrong(str(a // b), "Bu bölüm; bölümü <code>//</code> verir. <code>%</code> kalanı verir."),
                  Wrong(str(a / b), "Bu <code>/</code> bölmesinin sonucu; <code>%</code> yalnızca kalanı verir.")]
    return output_question(
        f"a = {a}\nb = {b}\nprint(a {op} b)", str(res), expl,
        common_wrongs=_distinct(str(res), common),
        hint="// ve % operatörlerinden hangisi bölümü, hangisi kalanı verir?",
    )


@q("Bölme Sonucunun Tipi", verify="output")
def true_division():
    b = random.randint(2, 6)
    a = b * random.randint(2, 9)
    return output_question(
        f"print({a} / {b})", f"{a // b}.0",
        f"<code>/</code> operatörü her zaman float döndürür; tam bölünse bile sonuç {a // b}.0 olur. "
        "Tam sayı sonuç için <code>//</code> kullanılır.",
        wrongs=[
            Wrong(str(a // b), "<code>/</code> her zaman float verir; tam bölünse bile sonuç .0 ile yazılır."),
            Wrong(f"{a // b},0", "Python ondalık ayırıcı olarak virgül değil nokta kullanır."),
            Wrong(f"{a}/{b}", "print işlemin kendisini değil, sonucunu yazar."),
        ],
        hint="/ operatörünün sonucu hangi tipte olur: int mi, float mı?",
    )


@q("İşlem Önceliği", verify="output")
def precedence():
    a, b, c = random.randint(2, 9), random.randint(2, 9), random.randint(2, 5)
    expr, why, wrong_expr, wrong_why = random.choice([
        (f"{a} + {b} * {c}", "Çarpma, toplamadan önce yapılır.",
         f"({a} + {b}) * {c}", "Soldan sağa hesapladın; ama çarpma toplamadan önce yapılır."),
        (f"({a} + {b}) * {c}", "Parantez içi önce hesaplanır.",
         f"{a} + {b} * {c}", "Parantezi atladın; parantez içi her zaman önce hesaplanır."),
        (f"{a} ** 2 - {b}", "Üs alma (**) en yüksek önceliğe sahiptir.",
         f"{a} * 2 - {b}", "** üs almadır (karesini alır), 2 ile çarpma değil."),
        (f"{a * c + b} - {b} // {c}", "Tam bölme (//), çıkarmadan önce yapılır.",
         f"({a * c + b} - {b}) // {c}", "Soldan sağa hesapladın; ama // çıkarmadan önce yapılır."),
        (f"2 * {a} % {c}", "* ve % aynı önceliktedir; soldan sağa hesaplanır.",
         f"2 * ({a} % {c})", "* ile % aynı önceliktedir; soldan sağa, yani önce çarpma yapılır."),
    ])
    res = eval(expr)  # noqa: S307 - yalnızca bizim ürettiğimiz sabit ifade
    wrong = eval(wrong_expr)  # noqa: S307
    return output_question(
        f"print({expr})", str(res), f"{why} Sonuç: <code>{expr} = {res}</code>.",
        common_wrongs=_distinct(str(res), [Wrong(str(wrong), wrong_why)]) or [Wrong(str(res + 1), "Hesabı adım adım tekrar et.")],
        hint="İşlem sırası: önce parantez, sonra **, sonra * / // %, en son + ve -.",
    )


def _logic_exprs(a, b, c):
    return [
        f"{a} > {b} and {b} > {c}", f"{a} > {b} or {b} > {c}", f"not {a} > {b}",
        f"{a} != {b} and {c} >= {a}", f"{a} < {c} or {b} == {c}", f"not ({a} < {b} or {c} < {a})",
        f"{b} >= {a} and not {c} > {b}", f"{c} > {a} or {c} > {b}",
    ]


@q("Karşılaştırma ve Mantıksal Operatörler", verify="output")
def logic():
    """İki mantıksal ifade birlikte yazdırılır; dört birleşimin hepsi anlamlı bir şıktır (K4)."""
    a, b, c = random.sample(range(1, 15), 3)
    exprs = _logic_exprs(a, b, c)
    by_value = {True: [x for x in exprs if eval(x)], False: [x for x in exprs if not eval(x)]}  # noqa: S307
    picks = []
    for _ in range(2):  # her ifadenin sonucu (True/False) eşit olasılıkla seçilir
        want = random.random() < 0.5
        pool = [x for x in by_value[want] if x not in picks] or [x for x in exprs if x not in picks]
        picks.append(random.choice(pool))
    e1, e2 = picks
    r1, r2 = eval(e1), eval(e2)  # noqa: S307 - yalnızca bizim ürettiğimiz sabit ifade
    rule = ("Her karşılaştırmayı ayrı ayrı hesaplayıp sonra and (ikisi de doğru olmalı), or (biri doğru yeter) ve "
            "not (tersine çevirir) kurallarını uygula.")
    wrongs = []
    for x in (True, False):
        for y in (True, False):
            if (x, y) == (r1, r2):
                continue
            if x != r1 and y != r2:
                why = f"İki sonucu da ters buldun. {rule}"
            elif x != r1:
                why = f"İlk ifade <code>{e1}</code> aslında {r1}. {rule}"
            else:
                why = f"İkinci ifade <code>{e2}</code> aslında {r2}. {rule}"
            wrongs.append(Wrong(f"{x} {y}", why))
    return output_question(
        f"print({e1}, {e2})", f"{r1} {r2}",
        "<code>and</code>: iki taraf da True ise True; <code>or</code>: en az biri True ise True; "
        "<code>not</code>: değeri tersine çevirir. Karşılaştırmalar mantıksal operatörlerden önce hesaplanır. "
        f"<code>{e1}</code> → {r1}, <code>{e2}</code> → {r2}.",
        wrongs=wrongs,
        hint="Önce her karşılaştırmanın doğru mu yanlış mı olduğuna karar ver, sonra and, or ve not'u uygula.",
    )


@q("Birleşik Atama Operatörleri", verify="output")
def augmented():
    x, a, b, c = random.randint(2, 9), random.randint(1, 9), random.randint(2, 3), random.randint(1, 5)
    res = ((x + a) * b) - c
    common = [
        Wrong(str(x + a * b - c), "Her satır x'in o anki değeriyle çalışır; işlemler sırayla birikir. "
                                  f"Önce x = {x + a} olur, sonra bu değer {b} ile çarpılır."),
        Wrong(str(x), "x += a gibi satırlar x'in değerini kalıcı olarak değiştirir."),
    ]
    return output_question(
        f"x = {x}\nx += {a}\nx *= {b}\nx -= {c}\nprint(x)", str(res),
        f"<code>x += {a}</code>, <code>x = x + {a}</code> demektir. Adım adım: {x} → {x + a} → "
        f"{(x + a) * b} → {res}.",
        common_wrongs=_distinct(str(res), common),
        hint="Her satırdan sonra x'in yeni değerini bir kenara yaz.",
    )


@q("Atama ve Karşılaştırma")
def assign_vs_equal():
    return tf_question(
        [("Python'da <code>=</code> atama, <code>==</code> ise eşitlik karşılaştırması için kullanılır.",
          "= sağdaki değeri değişkene atar; == iki değeri karşılaştırıp True/False verir."),
         ("<code>5 == 5.0</code> ifadesinin sonucu <code>True</code>'dur.",
          "Sayısal karşılaştırmada 5 ile 5.0 aynı değerdir; tiplerinin farklı olması sonucu değiştirmez."),
         ("<code>x = 3</code> satırından sonra <code>x == 3</code> ifadesi True verir.",
          "x'e 3 atandığı için x == 3 karşılaştırması doğrudur."),
         ("<code>10 / 2</code> ifadesinin sonucu float tipindedir (5.0).",
          "/ her zaman float verir; tam bölünse bile sonuç 5.0'dır."),
         ("<code>!=</code> operatörü 'eşit değil' anlamına gelir.",
          "!= iki değer farklıysa True, aynıysa False verir."),
         ("<code>\"3\" == 3</code> ifadesinin sonucu False'tur.",
          "Biri metin, diğeri sayı; Python bunları eşit saymaz.")],
        [("Python'da <code>==</code> operatörü bir değişkene değer atamak için kullanılır.",
          "== karşılaştırma yapar; atama tek eşittir (=) ile yapılır."),
         ("<code>10 / 2</code> ifadesinin sonucu int tipindedir.",
          "/ her zaman float verir (5.0); tam sayı sonuç için // kullanılır."),
         ("<code>\"3\" == 3</code> ifadesinin sonucu True'dur.",
          "Metin ile sayı birbirine eşit sayılmaz; sonuç False'tur."),
         ("<code>x == 5</code> satırı x değişkenine 5 değerini atar.",
          "x == 5 yalnızca karşılaştırır, x'i değiştirmez; atama için x = 5 yazılır."),
         ("<code>a = b = 0</code> yazımı Python'da hata verir.",
          "Python zincirleme atamaya izin verir; a ile b'nin ikisi de 0 olur."),
         ("<code>1 &lt; 5 &lt; 10</code> gibi zincirleme karşılaştırma Python'da hata verir.",
          "Python zincirleme karşılaştırmayı destekler; 1 < 5 < 10 ifadesi True'dur.")],
        "<code>=</code> sağdaki değeri soldaki değişkene atar; <code>==</code> iki değeri karşılaştırıp "
        "True/False döndürür. Sayısal karşılaştırmada 5 ile 5.0 eşittir. <code>/</code> her zaman float verir.",
        hint="= ile == farklı işler yapar; / operatörünün sonucunun tipini de hatırla.",
    )


# ================================================================= yeni şablonlar (ölçme raporu Ö3.1-Ö3.7)
@q("Operatör İddiası (Doğru/Yanlış)", verify="tf_output")
def op_claim():
    """Kazanım: //, %, / ve ** sonuçlarını ayırt eder · Bloom: U"""
    op = random.choice(["//", "%", "/", "**"])
    if op == "**":
        while True:
            a, b = random.randint(2, 9), random.randint(2, 3)
            if a ** b != b ** a:
                break
        result = a ** b
        wrongs = [Wrong(str(a * b), "<code>**</code> üs alır; çarpma değildir."),
                  Wrong(str(b ** a), "Taban ile üs yer değiştirmiş; soldaki sayı taban, sağdaki üstür."),
                  Wrong(str(a * a if b == 3 else a * a * a), f"Üs {b}; sayı kendisiyle {b} kez çarpılır.")]
    else:
        b = random.choice([2, 4, 5, 8])
        a = random.choice([n for n in range(11, 61) if n % b])
        result = {"//": a // b, "%": a % b, "/": a / b}[op]
        quotient, remainder = a // b, a % b
        if op == "//":
            wrongs = [Wrong(str(remainder), "Bu <code>%</code> sonucu (kalan); <code>//</code> bölümün tam "
                                                 "kısmını verir."),
                      Wrong(str(a / b), "Bu <code>/</code> sonucu; <code>//</code> kesir kısmını atar."),
                      Wrong(str(quotient + 1), "<code>//</code> yukarı yuvarlamaz; bölümün tam kısmını alır.")]
        elif op == "%":
            wrongs = [Wrong(str(quotient), "Bu <code>//</code> sonucu (bölüm); <code>%</code> kalanı verir."),
                      Wrong(str(a / b), "Bu <code>/</code> sonucu; <code>%</code> yalnızca kalanı verir."),
                      Wrong(str(round(a / b - quotient, 4)), "Bu, bölümün kesir kısmı; <code>%</code> ise tam sayı "
                                                             "olan kalanı verir.")]
        else:
            wrongs = [Wrong(str(quotient), "<code>/</code> kesir kısmını atmaz; bu <code>//</code> sonucu."),
                      Wrong(str(remainder), "Bu <code>%</code> sonucu (kalan); <code>/</code> bölümün tamamını verir."),
                      Wrong(f"{quotient}.0", "<code>/</code> kesir kısmını atmaz; sonuç tam bölünmüyorsa ondalık "
                                             "kısmı da yazılır.")]
    return tf_claim(
        f"print({a} {op} {b})", str(result), wrongs,
        "<code>//</code> bölümün tam kısmını, <code>%</code> kalanı, <code>/</code> ondalıklı bölümü, "
        "<code>**</code> üs almayı verir.",
        hint="// bölümün tam kısmı, % kalan, / ondalıklı bölüm, ** üs almadır. Bu kodda hangisi var?",
    )


MISSING_OPS = ["+", "-", "*", "/", "//", "%", "**"]


def _apply(a, op, b):
    return {"+": a + b, "-": a - b, "*": a * b, "/": a / b, "//": a // b, "%": a % b, "**": a ** b}[op]


@q("Eksik Operatör (Boşluk Doldurma)", verify="fill")
def missing_op_blank():
    """Kazanım: sonuçtan geriye giderek operatörü belirler · Bloom: An"""
    op = random.choice(MISSING_OPS)
    while True:
        a = random.randint(5, 30) if op != "**" else random.randint(2, 6)
        b = random.choice([2, 4, 5, 8]) if op == "/" else random.randint(2, 9 if op != "**" else 4)
        results = {o: str(_apply(a, o, b)) for o in MISSING_OPS}
        if list(results.values()).count(results[op]) == 1 and len(results["/"]) <= 6:
            break
    expect = results[op]
    wrongs = [Wrong(o, f"<code>{a} {o} {b}</code> işleminin sonucu {results[o]} olur; istenen {expect}.")
              for o in MISSING_OPS if o != op]
    return fill_question(
        f"print({a} ____ {b})", [[op]], expect,
        f"Aşağıdaki kod ekrana <code>{expect}</code> yazmalı. Boşluğa gereken <strong>operatörü</strong> yazın.",
        f"<code>{a} {op} {b}</code> = {expect}. Diğer operatörlerin hiçbiri bu sonucu vermez: <code>//</code> "
        "bölümün tam kısmı, <code>%</code> kalan, <code>/</code> ondalıklı bölüm, <code>**</code> üs almadır.",
        hint="Her operatörü sırayla dene: hangisi tam olarak bu sonucu verir?",
        wrongs=[wrongs],
    )


def _aug_run(x, steps, swap=None):
    """Birleşik atama adımlarını uygular. swap: bir operatörü yanılgıdaki karşılığıyla değiştirir."""
    for op, k in steps:
        op = (swap or {}).get(op, op)
        x = {"//=": lambda v: v // k, "%=": lambda v: v % k, "**=": lambda v: v ** k, "*=": lambda v: v * k,
             "/=": lambda v: v / k}[op](x)
    return x


@q("Birleşik Atama Zinciri", verify="output")
def augmented2():
    """Kazanım: //=, **= ve %= operatörlerini izler · Bloom: U"""
    while True:  # sonuç 0 ya da 1'e yığılmasın; en az iki farklı yaygın yanlış kalsın
        x = random.randint(10, 30)
        steps = [("//=", random.randint(2, 7)), ("**=", 2), ("%=", random.randint(3, 13))]
        random.shuffle(steps)
        result = _aug_run(x, steps)
        common = [Wrong(str(_aug_run(x, steps[:2])), f"Son satırı atladın; o satırdan sonra x = {result} olur."),
                  Wrong(str(_aug_run(x, steps, {"**=": "*="})), "<code>**=</code> üs alır; <code>x **= 2</code> "
                                                                 "x'in karesidir, iki katı değil."),
                  Wrong(str(_aug_run(x, steps, {"%=": "//="})), "<code>%=</code> bölümü değil, kalanı verir.")]
        with_div = _aug_run(x, steps, {"//=": "/="})
        if len(str(with_div)) <= 8:
            common.append(Wrong(str(with_div), "<code>//=</code> tam bölmedir; kesir kısmı atılır."))
        if result > 1 and len({w.value for w in common} - {str(result)}) >= 2:
            break
    trace, value = [str(x)], x
    for step in steps:
        value = _aug_run(value, [step])
        trace.append(str(value))
    return output_question(
        f"x = {x}\n" + "\n".join(f"x {op} {k}" for op, k in steps) + "\nprint(x)", str(result),
        "<code>x //= k</code>, <code>x = x // k</code> demektir; <code>**=</code> ve <code>%=</code> da aynı "
        f"biçimde çalışır. Adım adım: {' → '.join(trace)}.",
        common_wrongs=common, norm="sayi",
        hint="Her satırdan sonra x'in yeni değerini bir kenara yaz.",
    )


@q("Bölünebilme Koşulu", verify="code_one")
def divisible_expr():
    """Kazanım: tam bölünebilmeyi ve tek/çift olmayı doğru ifade eder · Bloom: An/D"""
    v = random.choice(["sayi", "n", "x"])
    mode = random.choices(["div", "odd", "even"], weights=[6, 2, 2])[0]
    if mode == "div":
        d = random.randint(3, 9)
        task = f"<code>{v}</code> değişkeninin {d} ile tam bölünüp bölünmediğini"
        correct, check = f"{v} % {d} == 0", (lambda i: i % d == 0)
        wrongs = [Wrong(f"{v} / {d} == 0", f"Bölüm yalnızca {v} 0 iken 0 olur; diğer katlar için False verir."),
                  Wrong(f"{v} // {d} == 0", f"Yalnızca 0 ile {d - 1} arasındaki sayılar için True olur."),
                  Wrong(f"{v} % {d} == 1", "Kalanın 1 olması tam bölünmediğini gösterir."),
                  Wrong(f"{v} % 2 == 0", f"Bu ifade 2 ile bölünebilmeyi denetler; {d} ile değil.")]
        wrongs = random.sample(wrongs, 3)
    elif mode == "odd":
        task = f"<code>{v}</code> değişkeninin <strong>tek</strong> sayı olup olmadığını"
        correct, check = random.choice([f"{v} % 2 == 1", f"{v} % 2 != 0"]), (lambda i: i % 2 == 1)
        wrongs = [Wrong(f"{v} / 2 == 1", f"Yalnızca {v} 2 iken True olur."),
                  Wrong(f"{v} // 2 == 1", "Yalnızca 2 ve 3 için True olur."),
                  Wrong(f"{v} % 2 == 0", "Kalan 0 ise sayı çifttir; bu ifade çiftliği denetler.")]
    else:
        task = f"<code>{v}</code> değişkeninin <strong>çift</strong> sayı olup olmadığını"
        correct, check = f"{v} % 2 == 0", (lambda i: i % 2 == 0)
        wrongs = [Wrong(f"{v} / 2 == 0", f"Bölüm yalnızca {v} 0 iken 0 olur."),
                  Wrong(f"{v} // 2 == 0", "Yalnızca 0 ve 1 için True olur."),
                  Wrong(f"{v} % 2", "Bu ifade kalanın kendisini (0 ya da 1) verir; True/False değil ve tek "
                                    "sayılarda 1 olur.")]
    return code_options_question(
        f"Aşağıdaki ifadelerden hangisi {task} <strong>her tam sayı için</strong> doğru kontrol eder?",
        correct, wrongs,
        cases=[{"setup": f"{v} = {i}", "expect": str(check(i))} for i in range(-20, 21)],
        solution="Tam bölünen bir sayının kalanı 0'dır; kalanı <code>%</code> verir. Bu yüzden bölünebilme "
                 "<code>% ... == 0</code> ile, tek sayı kalanın 1 olmasıyla denetlenir.",
        hint="Tam bölünen bir sayının kalanı kaçtır? Hangi operatör kalanı verir?",
        harness="print({option})",
    )


@q("Kısa Devre Değerlendirme", verify="outcome")
def short_circuit():
    """Kazanım: and/or operatörlerinin ikinci tarafı ne zaman hesaplamadığını bilir · Bloom: An"""
    family = random.choice(["div", "list"])
    risky = random.random() < 0.6  # riskli işlem yapılamaz durumda mı (x = 0, liste boş)
    form = random.choice(["and_safe", "or_safe", "and_unsafe", "or_unsafe"])
    if family == "div":
        x = 0 if risky else random.randint(1, 19)
        setup, error = f"x = {x}", "ZeroDivisionError"
        guard_and, guard_or, risky_part = "x != 0", "x == 0", "10 / x > 1"
        right = (10 / x > 1) if x else None
        danger, why_safe = "bölme", "x sıfır olmadığı için"
    else:
        lst = [] if risky else random.sample(range(2, 10), random.randint(1, 3))
        setup, error = f"liste = {lst}", "IndexError"
        guard_and, guard_or, risky_part = "len(liste) > 0", "len(liste) == 0", "liste[0] > 5"
        right = (lst[0] > 5) if lst else None
        danger, why_safe = "<code>liste[0]</code>", "liste boş olmadığı için"
    unsafe = form.endswith("unsafe")
    word = form.split("_")[0]
    expr = {"and_safe": f"{guard_and} and {risky_part}", "or_safe": f"{guard_or} or {risky_part}",
            "and_unsafe": f"{risky_part} and {guard_and}", "or_unsafe": f"{risky_part} or {guard_or}"}[form]
    if not risky:
        answer = str(right)
        expl = (f"{why_safe} iki taraf da sorunsuz hesaplanabilir: <code>{e(risky_part)}</code> {right} olur; "
                f"sonuç {answer}.")
    elif unsafe:
        answer = err(error)
        expl = (f"{word} önce soldaki <code>{e(risky_part)}</code> ifadesini hesaplar; burada {danger} yapılamaz ve "
                f"{error} oluşur. Denetim sağda kaldığı için koruma işe yaramaz.")
    elif word == "and":
        answer = "False"
        expl = (f"Sol taraf (<code>{e(guard_and)}</code>) False olduğu için and sağ tarafa hiç bakmaz; "
                f"{danger} yapılmaz "
                "ve sonuç False olur.")
    else:
        answer = "True"
        expl = (f"Sol taraf (<code>{e(guard_or)}</code>) True olduğu için or sağ tarafa hiç bakmaz; {danger} yapılmaz "
                "ve sonuç True olur.")
    both = "Sonucu iki tarafa birden bakarak bulmalısın; and için iki taraf da True olmalı, or için biri yeter."
    pool = {
        "True": both, "False": both,
        err(error): ("Sol taraf sonucu belirlediğinde sağ taraf hiç hesaplanmaz; riskli işlem yapılmaz."
                     if risky else f"Bu durumda {danger} sorunsuz yapılır; hata oluşmaz."),
        "None": "and ve or burada karşılaştırma sonuçlarını döndürür; çıktı True ya da False olur.",
    }
    if risky and unsafe:
        stop = (f"Sağdaki koruma hiç çalışmaz; {word} önce soldaki <code>{e(risky_part)}</code> ifadesini hesaplar ve "
                "hata oluşur.")
        pool["True"] = pool["False"] = stop
    wrongs = [Wrong(value, why) for value, why in pool.items() if value != answer]
    return output_question(
        f"{setup}\nprint({expr})", answer, expl, wrongs=wrongs,
        hint="and ile or soldan sağa çalışır. Sol taraf sonucu tek başına belirliyorsa sağ tarafa bakmaya "
             "gerek var mı? "
             "Riskli işlem hangi tarafta?",
    )


DIVMOD_VARS = ["toplam", "saniye", "sure"]


@q("Saniyeyi Dakikaya Çevir (Kod Yazma)")
def write_divmod():
    """Kazanım: // ve % ile birim çevirir · Bloom: O"""
    var = random.choice(DIVMOD_VARS)
    while True:
        total = random.randint(61, 3599)
        if total % 60 and total // 60 != total % 60:
            break
    return {
        "type": "code",
        "text": (
            f"<code>{var}</code> değişkenine <strong>{total}</strong> atayın. Bu süreyi <strong>dakika</strong> ve "
            f"<strong>saniye</strong> olarak, önce dakika sonra saniye gelecek biçimde tek satırda yazdırın "
            f"({total} için çıktı: <code>{total // 60} {total % 60}</code>). Değerleri <code>//</code> ve "
            "<code>%</code> ile hesaplayın; elle yazmayın."
        ),
        "code": None,
        "check": {"kind": "divmod_time", "var": var, "total": total},
        "answer": f"{var} = {total}\nprint({var} // 60, {var} % 60)",
        "hint": "Dakika için hangi operatör, kalan saniye için hangisi kullanılır?",
        "solution": "Bir dakika 60 saniyedir. Tam dakika sayısı <code>// 60</code>, geriye kalan saniye "
                    "<code>% 60</code> ile bulunur.",
    }


AVG_NAMES = [("n1", "n2", "n3"), ("not1", "not2", "not3"), ("a", "b", "c")]


@q("Üç Notun Ortalaması (Kod Yazma)")
def write_average():
    """Kazanım: işlem önceliğini doğru kullanarak ortalama hesaplar · Bloom: O"""
    names = list(random.choice(AVG_NAMES))
    values = [random.randint(40, 100) for _ in range(3)]
    avg = sum(values) / 3
    shown_avg = f"{avg:.2f}".rstrip("0").rstrip(".")
    assigns = ", ".join(f"<code>{n} = {v}</code>" for n, v in zip(names, values))
    return {
        "type": "code",
        "text": (
            f"{assigns} atamalarını yapın. Ardından bu üç notun <strong>ortalamasını</strong> hesaplayıp yazdırın "
            f"(yaklaşık {shown_avg}). Sonucu elle yazmayın; değişkenleri kullanın."
        ),
        "code": None,
        "check": {"kind": "average3", "names": names, "values": values},
        "answer": "\n".join(f"{n} = {v}" for n, v in zip(names, values))
                  + f"\nprint(({names[0]} + {names[1]} + {names[2]}) / 3)",
        "hint": "Önce toplam, sonra bölme. Python hangisini önce yapar?",
        "solution": "Ortalama, toplamın not sayısına bölümüdür: <code>(n1 + n2 + n3) / 3</code>. Parantez olmazsa "
                    "yalnızca son not 3'e bölünür, çünkü bölme toplamadan önce yapılır.",
    }


# ================================================================= denetleyiciler
class _Divmod(ast.NodeTransformer):
    """divmod(a, b) çağrısını (a // b, a % b) demetine çevirir (yalnızca okunur, çalıştırılmaz)."""

    def visit_Call(self, node):
        self.generic_visit(node)
        if (isinstance(node.func, ast.Name) and node.func.id == "divmod" and len(node.args) == 2
                and not node.keywords):
            a, b = node.args
            return ast.Tuple(elts=[ast.BinOp(left=a, op=ast.FloorDiv(), right=b),
                                   ast.BinOp(left=copy.deepcopy(a), op=ast.Mod(), right=copy.deepcopy(b))],
                             ctx=ast.Load())
        return node


def _number_lines(tree, overrides=None):
    prints, firsts = straight_run(tree, overrides)
    return [vals for vals in (print_numbers(call, tr) for call, tr in prints) if vals], firsts


@checker("divmod_time")
def check_divmod_time(tree, p):
    """var = total; aynı satırda önce total // 60, sonra total % 60 yazdırılır."""
    var, total = p["var"], p["total"]
    tree = _Divmod().visit(copy.deepcopy(tree))
    lines, firsts = _number_lines(tree)
    if not same_value(firsts.get(var), total):
        return False, f"<code>{var}</code> değişkenine {total} atanmamış."
    if not lines:
        return False, "Dakika ve saniyeyi <code>print()</code> ile yazdır."
    dk, sn = total // 60, total % 60

    def matches(vals, a, b):
        return len(vals) == 2 and same_value(vals[0], a) and same_value(vals[1], b)

    good = [i for i, vals in enumerate(lines) if matches(vals, dk, sn)]
    if good:
        alt = 3725
        alt_lines, _ = _number_lines(tree, {var: alt})
        if not (len(alt_lines) > good[0] and matches(alt_lines[good[0]], alt // 60, alt % 60)):
            return False, (f"Değerleri elle yazma; <code>{var}</code> değişkeninden hesapla. Süre değişince sonuç da "
                           "değişmeli.")
        return True, OK
    flat = [v for vals in lines for v in vals]
    if any(same_value(v, total / 60) for v in flat):
        return False, "<code>/</code> ondalıklı sonuç verir; tam dakika sayısı için <code>//</code> kullan."
    if len(lines) > 1 and matches(flat, dk, sn):
        return False, "Dakika ve saniyeyi aynı satırda (tek bir print ile) yazdır."
    if any(matches(vals, sn, dk) for vals in lines):
        return False, "Önce dakika, sonra saniye yazdırılmalı."
    if any(len(vals) > 2 and any(same_value(v, dk) for v in vals) and any(same_value(v, sn) for v in vals)
           for vals in lines):
        return False, "Yalnızca dakika ve saniyeyi yazdır (yanlarına açıklama metni ekleyebilirsin)."
    return False, "Yazdırılan değerler beklenen dakika ve saniyeyi vermiyor; işlemleri kontrol et."


AVG_TOLERANCE = 0.051  # round(..., 1) ve :.2f gibi yuvarlanmış yazımlar kabul edilir


@checker("average3")
def check_average3(tree, p):
    """Üç değişkene notlar atanır; (a + b + c) / 3 yazdırılır (yuvarlama serbest)."""
    names, values = p["names"], p["values"]
    lines, firsts = _number_lines(tree)
    if not all(same_value(firsts.get(n), v) for n, v in zip(names, values)):
        listed = ", ".join(f"<code>{n}</code>" for n in names)
        return False, f"{listed} değişkenlerine istenen notlar atanmamış."
    if not lines:
        return False, "Ortalamayı <code>print()</code> ile yazdır."
    flat = [v for vals in lines for v in vals]
    if len(flat) > 1:
        return False, "Yalnızca ortalamayı yazdır (yanına açıklama metni ekleyebilirsin)."
    value = flat[0]
    a, b, c = values

    def close(x, want):
        return isinstance(x, (int, float)) and not isinstance(x, bool) and abs(x - want) <= AVG_TOLERANCE

    if not close(value, (a + b + c) / 3):
        if close(value, a + b + c / 3):
            return False, "Yalnızca son not 3'e bölündü; bölme toplamadan önce yapılır. Toplamı paranteze al."
        if close(value, a + b + c):
            return False, "Toplamı not sayısına bölmeyi unutma."
        if close(value, (a + b + c) // 3):
            return False, "<code>//</code> tam bölmedir ve kesir kısmını atar; ortalama için <code>/</code> kullan."
        return False, "Yazdırılan değer üç notun ortalaması değil; formülü kontrol et."
    shifted = [v + d for v, d in zip(values, (7, 11, 4))]
    alt_lines, _ = _number_lines(tree, dict(zip(names, shifted)))
    alt_flat = [v for vals in alt_lines for v in vals]
    if len(alt_flat) != 1 or not close(alt_flat[0], sum(shifted) / 3):
        return False, "Sonucu elle yazma; değişkenleri kullan. Notlar değişince ortalama da değişmeli."
    return True, OK
