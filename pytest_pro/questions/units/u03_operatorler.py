"""Ünite 3 - Operatörler."""
import random

from ..helpers import Wrong, output_question, tf_question
from ..registry import register_unit

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


@q("Karşılaştırma ve Mantıksal Operatörler", verify="output")
def logic():
    a, b, c = random.sample(range(1, 15), 3)
    expr = random.choice([
        f"{a} > {b} and {b} > {c}", f"{a} > {b} or {b} > {c}", f"not {a} > {b}",
        f"{a} != {b} and {c} >= {a}", f"{a} == {a} or {b} < {c}", f"not ({a} < {b} or {c} < {a})",
    ])
    res = str(eval(expr))  # noqa: S307
    first = expr.split()[0]
    return output_question(
        f"print({expr})", res,
        "<code>and</code>: iki taraf da True ise True; <code>or</code>: en az biri True ise True; "
        "<code>not</code>: değeri tersine çevirir. Karşılaştırmalar mantıksal operatörlerden önce hesaplanır.",
        wrongs=[
            Wrong("False" if res == "True" else "True",
                  "Her karşılaştırmayı ayrı ayrı hesaplayıp sonra and (ikisi de doğru olmalı), or (biri doğru "
                  "yeter) ve not (tersine çevirir) kurallarını uygula."),
            Wrong("None", "Karşılaştırmalar ve mantıksal işlemler her zaman True ya da False verir."),
            Wrong(first, "print ifadenin sonucunu yazar; ifadenin bir parçasını değil."),
        ],
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
