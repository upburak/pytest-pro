"""Ünite 9 - Fonksiyonlar ve Modüller."""
import math
import random

from ..helpers import err, output_question, tf_question
from ..registry import register_unit

UNIT = register_unit(
    "fonksiyonlar", "Fonksiyonlar ve Modüller", "Orta",
    "def ile fonksiyon tanımlama, parametre ve return, varsayılan parametre, yerel/global kapsam, "
    "birden fazla değer döndürme, özyineleme, import ve math modülü.",
    order=9,
)
q = UNIT.question


@q("Fonksiyon ve return", verify="output")
def call_return():
    a, b = random.randint(2, 9), random.randint(2, 9)
    return output_question(
        f"def hesapla(x, y):\n    return x * 2 + y\n\nprint(hesapla({a}, {b}))", str(a * 2 + b),
        f"Çağrıda x = {a}, y = {b} olur; fonksiyon {a} * 2 + {b} = {a * 2 + b} değerini döndürür.",
        wrongs=[str((a + b) * 2), str(b * 2 + a), "None"],
    )


@q("Varsayılan Parametre", verify="output")
def default_param():
    base = random.randint(2, 5)
    exp = random.randint(2, 3)
    other = random.randint(2, 4)
    if random.random() < 0.5:
        call, res = f"us({base})", base ** 2
        why = "Üs verilmediği için varsayılan değer (2) kullanılır"
    else:
        call, res = f"us({base}, {other})", base ** other
        why = f"Üs açıkça {other} verildiği için varsayılan değer kullanılmaz"
    return output_question(
        f"def us(taban, kuvvet=2):\n    return taban ** kuvvet\n\nprint({call})", str(res),
        f"{why}: sonuç {res}.",
        wrongs=[str(base * 2), str(base ** exp + 1), err("TypeError")],
    )


@q("return Olmayan Fonksiyon", verify="output")
def return_none():
    name = random.choice(["Ali", "Ece", "Can"])
    return output_question(
        f"def selamla(ad):\n    print(\"Merhaba\", ad)\n\nsonuc = selamla(\"{name}\")\nprint(sonuc)",
        f"Merhaba {name}\nNone",
        "Fonksiyon ekrana yazar ama <code>return</code> içermez; bu yüzden çağrının değeri <strong>None</strong>'dır. "
        "Önce fonksiyon içindeki print çalışır, sonra None yazdırılır.",
        wrongs=[f"Merhaba {name}", f"Merhaba {name}\nMerhaba {name}", "None"],
    )


@q("Yerel ve Global Değişkenler", verify="output")
def scope():
    x, y = random.sample(range(1, 20), 2)
    return output_question(
        f"x = {x}\n\ndef degistir():\n    x = {y}\n    return x\n\ndegistir()\nprint(x)", str(x),
        f"Fonksiyon içindeki <code>x = {y}</code> yeni bir <strong>yerel</strong> değişken oluşturur; dışarıdaki "
        f"(global) x değişmez ve {x} kalır.",
        wrongs=[str(y), "None", err("NameError")],
    )


@q("Birden Fazla Değer Döndürme", verify="output")
def multi_return():
    a, b = random.sample(range(10, 40), 2)
    lo, hi = min(a, b), max(a, b)
    return output_question(
        f"def kucuk_buyuk(a, b):\n    return min(a, b), max(a, b)\n\nk, b = kucuk_buyuk({a}, {b})\nprint(b - k)",
        str(hi - lo),
        "<code>return x, y</code> bir demet döndürür; demet açma ile iki değişkene atanır. "
        f"k = {lo}, b = {hi}, fark {hi - lo}.",
        wrongs=[str(lo - hi), str(hi + lo), err("TypeError")],
    )


@q("Özyineleme", verify="output")
def recursion():
    n = random.randint(3, 6)
    if random.random() < 0.5:
        return output_question(
            f"def faktoriyel(n):\n    if n <= 1:\n        return 1\n    return n * faktoriyel(n - 1)\n\n"
            f"print(faktoriyel({n}))", str(math.factorial(n)),
            f"Fonksiyon kendini n - 1 ile çağırır ve n <= 1 olunca durur: {n}! = "
            + " × ".join(str(i) for i in range(n, 0, -1)) + f" = {math.factorial(n)}.",
            wrongs=[str(math.factorial(n - 1)), str(n * (n + 1) // 2), str(math.factorial(n + 1))],
        )
    return output_question(
        f"def topla(n):\n    if n == 0:\n        return 0\n    return n + topla(n - 1)\n\nprint(topla({n}))",
        str(n * (n + 1) // 2),
        f"topla({n}) = {n} + topla({n - 1}) = ... = {n * (n + 1) // 2}. n == 0 durma koşuludur.",
        wrongs=[str(n * (n - 1) // 2), str(math.factorial(n)), str(n)],
    )


@q("math Modülü", verify="output")
def math_module():
    x = random.choice([16, 25, 36, 49, 81])
    y = round(random.uniform(2, 9), 1)
    if y == int(y):
        y += 0.3
    code, res, why = random.choice([
        (f"import math\nprint(math.sqrt({x}))", str(math.sqrt(x)), "math.sqrt() karekök alır ve float döndürür"),
        (f"import math\nprint(math.ceil({y}))", str(math.ceil(y)), "math.ceil() yukarı yuvarlar"),
        (f"import math\nprint(math.floor({y}))", str(math.floor(y)), "math.floor() aşağı yuvarlar"),
        ("from math import pi\nprint(round(pi, 2))", "3.14", "round(sayı, 2) virgülden sonra 2 basamağa yuvarlar"),
    ])
    return output_question(
        code, res,
        f"{why}. <code>import math</code> modülü yükler; fonksiyonlara <code>math.ad</code> ile ulaşılır.",
        wrongs=[str(int(float(res))) if "." in res else res + ".0", str(round(y)), err("NameError"), "3.1416"],
    )


@q("Fonksiyon Kavramları")
def concepts():
    return tf_question(
        ["Bir fonksiyon <code>return</code> satırına ulaştığında çalışmasını hemen bitirir.",
         "Fonksiyon tanımlamak (def) onu çalıştırmaz; fonksiyon çağrıldığında çalışır."],
        ["<code>return</code> ile <code>print</code> aynı işi yapar; ikisi de değeri çağırana döndürür.",
         "Bir fonksiyon en fazla bir parametre alabilir."],
        "<code>print</code> değeri yalnızca ekrana yazar; <code>return</code> ise değeri çağıran koda geri "
        "verir ve fonksiyonu sonlandırır. Fonksiyonlar istenen sayıda parametre alabilir.",
    )


@q("Fonksiyon Yazma (Kod Yazma)")
def write_square_func():
    name = random.choice(["kare", "karesi", "kare_al"])
    return {
        "type": "code",
        "text": f"<code>{name}</code> adında, bir sayı parametresi alıp o sayının <strong>karesini döndüren</strong> "
                "(<code>return</code>) bir fonksiyon yazınız. Fonksiyonu çağırmanız gerekmez.",
        "code": None,
        "check": {"kind": "square_func", "name": name},
        "answer": f"def {name}(sayi):\n    return sayi * sayi",
        "solution": f"<code>def {name}(sayi):</code> ile fonksiyon tanımlanır; <code>return sayi * sayi</code> "
                    "(veya <code>sayi ** 2</code>) sonucu çağırana geri verir.",
    }
