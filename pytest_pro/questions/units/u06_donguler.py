"""Ünite 6 - Döngüler."""
import random

from ..helpers import output_question
from ..registry import register_unit

UNIT = register_unit(
    "donguler", "Döngüler", "Orta",
    "for döngüsü ve range(), while döngüsü, sayaç ve toplam değişkenleri, break, continue, iç içe döngüler.",
    order=6,
)
q = UNIT.question


@q("range() Fonksiyonu", verify="output")
def range_list():
    a = random.randint(0, 5)
    b = a + random.randint(4, 9)
    s = random.choice([1, 2, 3])
    form = random.choice([f"{b}", f"{a}, {b}", f"{a}, {b}, {s}"])
    res = str(list(eval(f"range({form})")))  # noqa: S307
    near = list(eval(f"range({form})"))  # noqa: S307
    return output_question(
        f"print(list(range({form})))", res,
        "<code>range(başlangıç, bitiş, adım)</code>: başlangıç dahil, <strong>bitiş dahil değildir</strong>. "
        "Tek parametre verilirse başlangıç 0, adım verilmezse 1 kabul edilir.",
        wrongs=[str(near + [near[-1] + (s if "," in form and form.count(",") == 2 else 1)]),
                str(near[1:]), str([x + 1 for x in near])],
    )


@q("for ile Toplam", verify="output")
def for_sum():
    n = random.randint(3, 10)
    start = random.choice([0, 1])
    total = sum(range(start, n + 1))
    return output_question(
        f"toplam = 0\nfor i in range({start}, {n + 1}):\n    toplam += i\nprint(toplam)", str(total),
        f"Döngü i = {start}, ..., {n} değerlerini alır (bitiş {n + 1} dahil değil). Her adımda i toplama eklenir: "
        f"toplam = {total}.",
    )


@q("while Döngüsü", verify="output")
def while_count():
    x = random.randint(1, 4)
    limit = random.randint(20, 60)
    k = random.choice([2, 3])
    count, v = 0, x
    while v < limit:
        v *= k
        count += 1
    return output_question(
        f"x = {x}\nadim = 0\nwhile x < {limit}:\n    x *= {k}\n    adim += 1\nprint(x, adim)", f"{v} {count}",
        f"Koşul (x < {limit}) her turdan önce kontrol edilir. x değerleri {x}'den başlayıp {k} ile çarpılarak "
        f"{v} olunca döngü biter; döngü {count} kez çalışır.",
        wrongs=[f"{v // k} {count - 1}", f"{v} {count + 1}", f"{v * k} {count + 1}"],
    )


@q("break ve continue", verify="output")
def break_continue():
    n = random.randint(6, 9)
    if random.random() < 0.5:
        stop = random.randint(3, n - 1)
        out = [str(i) for i in range(1, n) if i < stop]
        code = f"for i in range(1, {n}):\n    if i == {stop}:\n        break\n    print(i, end=\" \")"
        why = f"<code>break</code> döngüyü tamamen sonlandırır; i = {stop} olduğunda döngüden çıkılır."
        wrongs = [" ".join(out + [str(stop)]), " ".join(str(i) for i in range(1, n) if i != stop), " ".join(out[:-1])]
    else:
        skip = random.randint(2, n - 2)
        out = [str(i) for i in range(1, n) if i != skip]
        code = f"for i in range(1, {n}):\n    if i == {skip}:\n        continue\n    print(i, end=\" \")"
        why = f"<code>continue</code> yalnızca o turu atlar; i = {skip} yazdırılmaz ama döngü devam eder."
        wrongs = [" ".join(str(i) for i in range(1, skip)), " ".join(str(i) for i in range(1, n)),
                  " ".join(str(i) for i in range(1, n + 1) if i != skip)]
    res = " ".join(out) + " "
    return output_question(code, res, why, wrongs=[w + " " for w in wrongs])


@q("İç İçe Döngüler", verify="output")
def nested():
    a, b = random.randint(2, 4), random.randint(2, 4)
    return output_question(
        f"sayac = 0\nfor i in range({a}):\n    for j in range({b}):\n        sayac += 1\nprint(sayac)", str(a * b),
        f"Dış döngü {a} kez döner; her turda iç döngü {b} kez çalışır. Toplam {a} × {b} = {a * b} tekrar.",
        wrongs=[str(a + b), str(a), str(b)],
    )


@q("Metin Üzerinde Döngü", verify="output")
def loop_string():
    word = random.choice(["Python", "kalem", "Ankara", "bilgisayar"])
    letter = random.choice(sorted(set(word)))
    count = word.count(letter)
    return output_question(
        f'metin = "{word}"\nsayac = 0\nfor harf in metin:\n    if harf == "{letter}":\n        sayac += 1\nprint(sayac)',
        str(count),
        f"for döngüsü metnin her karakterini sırayla <code>harf</code> değişkenine verir. "
        f"\"{letter}\" harfi \"{word}\" içinde {count} kez geçer.",
        wrongs=[str(count + 1), str(len(word)), "0" if count else "1"],
    )


@q("for Döngüsü (Kod Yazma)")
def write_range_print():
    n = random.randint(4, 9)
    var = random.choice(["i", "sayi", "x"])
    return {
        "type": "code",
        "text": f"1'den {n}'e kadar (ikisi de dahil) sayıları <code>for</code> döngüsü ve <code>range()</code> "
                "kullanarak <strong>alt alta</strong> ekrana yazdıran kodu yazınız.",
        "code": None,
        "check": {"kind": "range_print", "start": 1, "stop": n},
        "answer": f"for {var} in range(1, {n + 1}):\n    print({var})",
        "solution": f"<code>range(1, {n + 1})</code> 1'den {n}'e kadar sayıları üretir; bitiş değeri dahil "
                    "olmadığı için bir fazlası yazılır.",
    }
