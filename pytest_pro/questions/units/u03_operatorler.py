"""Ünite 3 - Operatörler."""
import random

from ..helpers import output_question, tf_question
from ..registry import register_unit

UNIT = register_unit(
    "operatorler", "Operatörler", "Başlangıç",
    "Aritmetik (+ - * / // % **), işlem önceliği, karşılaştırma, mantıksal (and/or/not) ve "
    "birleşik atama (+=, -=, *=) operatörleri.",
    order=3,
)
q = UNIT.question


@q("Tam Bölme ve Mod", verify="output")
def int_div():
    a, b = random.randint(11, 40), random.randint(2, 7)
    op = random.choice(["//", "%"])
    res = a // b if op == "//" else a % b
    expl = (f"<code>//</code> tam sayı bölmesidir, bölümün yalnızca tam kısmını verir: {a} // {b} = {res}."
            if op == "//" else
            f"<code>%</code> (mod) bölme işleminden kalanı verir: {a} = {b} × {a // b} + {res}.")
    return output_question(f"a = {a}\nb = {b}\nprint(a {op} b)", str(res), expl)


@q("Bölme Sonucunun Tipi", verify="output")
def true_division():
    b = random.randint(2, 6)
    a = b * random.randint(2, 9)
    return output_question(
        f"print({a} / {b})", f"{a // b}.0",
        f"<code>/</code> operatörü her zaman float döndürür; tam bölünse bile sonuç {a // b}.0 olur. "
        "Tam sayı sonuç için <code>//</code> kullanılır.",
        wrongs=[str(a // b), f"{a // b},0", f"{a}/{b}"],
    )


@q("İşlem Önceliği", verify="output")
def precedence():
    a, b, c = random.randint(2, 9), random.randint(2, 9), random.randint(2, 5)
    expr, why = random.choice([
        (f"{a} + {b} * {c}", "Çarpma, toplamadan önce yapılır."),
        (f"({a} + {b}) * {c}", "Parantez içi önce hesaplanır."),
        (f"{a} ** 2 - {b}", "Üs alma (**) en yüksek önceliğe sahiptir."),
        (f"{a * c + b} - {b} // {c}", "Tam bölme (//), çıkarmadan önce yapılır."),
        (f"2 * {a} % {c}", "* ve % aynı önceliktedir; soldan sağa hesaplanır."),
    ])
    res = eval(expr)  # noqa: S307 - yalnızca bizim ürettiğimiz sabit ifade
    return output_question(f"print({expr})", str(res),
                           f"{why} Sonuç: <code>{expr} = {res}</code>.")


@q("Karşılaştırma ve Mantıksal Operatörler", verify="output")
def logic():
    a, b, c = random.sample(range(1, 15), 3)
    expr = random.choice([
        f"{a} > {b} and {b} > {c}", f"{a} > {b} or {b} > {c}", f"not {a} > {b}",
        f"{a} != {b} and {c} >= {a}", f"{a} == {a} or {b} < {c}", f"not ({a} < {b} or {c} < {a})",
    ])
    res = str(eval(expr))  # noqa: S307
    return output_question(
        f"print({expr})", res,
        "<code>and</code>: iki taraf da True ise True; <code>or</code>: en az biri True ise True; "
        "<code>not</code>: değeri tersine çevirir. Karşılaştırmalar mantıksal operatörlerden önce hesaplanır.",
        wrongs=["False" if res == "True" else "True", "None", expr.split()[0]],
    )


@q("Birleşik Atama Operatörleri", verify="output")
def augmented():
    x, a, b, c = random.randint(2, 9), random.randint(1, 9), random.randint(2, 3), random.randint(1, 5)
    res = ((x + a) * b) - c
    return output_question(
        f"x = {x}\nx += {a}\nx *= {b}\nx -= {c}\nprint(x)", str(res),
        f"<code>x += {a}</code>, <code>x = x + {a}</code> demektir. Adım adım: {x} → {x + a} → "
        f"{(x + a) * b} → {res}.",
    )


@q("Atama ve Karşılaştırma")
def assign_vs_equal():
    return tf_question(
        ["Python'da <code>=</code> atama, <code>==</code> ise eşitlik karşılaştırması için kullanılır.",
         "<code>5 == 5.0</code> ifadesinin sonucu <code>True</code>'dur."],
        ["Python'da <code>==</code> operatörü bir değişkene değer atamak için kullanılır.",
         "<code>10 / 2</code> ifadesinin sonucu int tipindedir."],
        "<code>=</code> sağdaki değeri soldaki değişkene atar; <code>==</code> iki değeri karşılaştırıp "
        "True/False döndürür. Sayısal karşılaştırmada 5 ile 5.0 eşittir. <code>/</code> her zaman float verir.",
    )
