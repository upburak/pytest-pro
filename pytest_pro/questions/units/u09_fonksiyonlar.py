"""Ünite 9 - Fonksiyonlar ve Modüller."""
import ast
import copy
import math
import random

from ..codecheck import (
    OK,
    Unknown,
    assigned_names,
    checker,
    find_loops,
    find_prints,
    function_params,
    function_returns,
    is_print,
    loop_problems,
    safe_eval,
    same_value,
)
from ..helpers import (
    PEOPLE,
    Wrong,
    code_options_question,
    e,
    err,
    fill_question,
    output_question,
    tf_claim,
    tf_question,
)
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
    a, b = random.sample(range(2, 10), 2)  # a ≠ b: aksi hâlde "argüman sırası" şıkkı doğru cevaba eşit olur (Y1)
    return output_question(
        f"def hesapla(x, y):\n    return x * 2 + y\n\nprint(hesapla({a}, {b}))", str(a * 2 + b),
        f"Çağrıda x = {a}, y = {b} olur; fonksiyon {a} * 2 + {b} = {a * 2 + b} değerini döndürür.",
        wrongs=[
            Wrong(str((a + b) * 2), "İşlem önceliği: önce x * 2 hesaplanır, sonra y eklenir."),
            Wrong(str(b * 2 + a), f"Argümanlar sırayla eşleşir: x = {a}, y = {b}."),
            Wrong("None", "Fonksiyon return ile bir değer döndürüyor; None değil."),
        ],
        hint="Çağrıdaki değerler hangi parametrelere gider? Sonra return satırını hesapla.",
    )


@q("Varsayılan Parametre", verify="output")
def default_param():
    """Taban 3, 5, 6 ya da 7: 2 * 2 = 2 ** 2 ve 4 ** 2 = 2 ** 4 çakışmaları olmaz (Y1)."""
    base = random.choice([3, 5, 6, 7])
    type_error = random.random() < 0.4  # hata şıkkı her soruda görünmesin (O8)
    if random.random() < 0.5:
        call, res = f"us({base})", base ** 2
        why = "Kuvvet verilmediği için varsayılan değer (2) kullanılır"
        wrongs = [Wrong(str(base * 2), "** üs almadır, 2 ile çarpma değil."),
                  Wrong(str(base), "Kuvvet verilmeyince varsayılan değer 2 kullanılır; 1 ya da 0 değil."),
                  Wrong(str(2 ** base), "İlk parametre taban, ikincisi kuvvettir: taban ** kuvvet.")]
        if type_error:
            wrongs.insert(1, Wrong(err("TypeError"), "Varsayılanı olan parametre çağrıda verilmeyebilir; hata oluşmaz."))
    else:
        other = random.choice([k for k in (3, 4) if k != base])
        call, res = f"us({base}, {other})", base ** other
        why = f"Kuvvet açıkça {other} verildiği için varsayılan değer kullanılmaz"
        wrongs = [Wrong(str(base ** 2), "Açıkça verilen değer, varsayılanın yerine geçer."),
                  Wrong(str(base * other), "** üs almadır, çarpma değil."),
                  Wrong(str(other ** base), "İlk argüman tabana, ikincisi kuvvete gider: taban ** kuvvet.")]
        if type_error:
            wrongs.insert(1, Wrong(err("TypeError"), "Fonksiyon iki parametre alıyor; iki argüman vermek geçerlidir."))
    return output_question(
        f"def us(taban, kuvvet=2):\n    return taban ** kuvvet\n\nprint({call})", str(res),
        f"{why}: sonuç {res}.",
        wrongs=wrongs,
        hint="Çağrıda kaç argüman verilmiş? Verilmeyen parametre hangi değeri alır?",
    )


@q("return Olmayan Fonksiyon", verify="output")
def return_none():
    name = random.choice(PEOPLE)
    greet = random.choice(["Merhaba", "Selam", "Günaydın"])
    func = random.choice(["selamla", "karsila"])
    return output_question(
        f"def {func}(ad):\n    print(\"{greet}\", ad)\n\nsonuc = {func}(\"{name}\")\nprint(sonuc)",
        f"{greet} {name}\nNone",
        "Fonksiyon ekrana yazar ama <code>return</code> içermez; bu yüzden çağrının değeri <strong>None</strong>'dır. "
        "Önce fonksiyon içindeki print çalışır, sonra None yazdırılır.",
        wrongs=[
            Wrong(f"{greet} {name}", "print(sonuc) da çalışır; fonksiyon return içermediği için sonuc None'dır ve "
                                     "None yazılır."),
            Wrong(f"{greet} {name}\n{greet} {name}", "Fonksiyon bir kez çağrılır; ikinci satır sonucun değerini "
                                                     "(None) yazar."),
            Wrong("None", "Fonksiyon çağrılınca içindeki print önce çalışır ve selamı yazar."),
        ],
        hint="Fonksiyon bir değer döndürüyor mu? return yoksa çağrının değeri nedir?",
    )


@q("Yerel ve Global Değişkenler", verify="output")
def scope():
    """Yerel atama, global bildirimi ve dönüş değeriyle birlikte yazdırma değişkeleri (O8: NameError şıkkı
    her soruda görünmez)."""
    x, y = random.sample(range(1, 20), 2)
    func = random.choice(["degistir", "guncelle", "ayarla"])
    variant = random.choice(["local", "local", "global", "both"])
    name_error = Wrong(err("NameError"), "x dışarıda tanımlı; hata oluşmaz.")
    if variant == "local":
        code = f"x = {x}\n\ndef {func}():\n    x = {y}\n    return x\n\n{func}()\nprint(x)"
        res = str(x)
        expl = (f"Fonksiyon içindeki <code>x = {y}</code> yeni bir <strong>yerel</strong> değişken oluşturur; dışarıdaki "
                f"(global) x değişmez ve {x} kalır.")
        wrongs = [Wrong(str(y), "Fonksiyon içindeki x yerel bir değişkendir; dışarıdaki x'i değiştirmez."),
                  Wrong("None", "print(x) dışarıdaki x'i yazar; fonksiyonun dönüş değerini değil."),
                  Wrong(f"{x}\n{y}", "Fonksiyonun döndürdüğü değer bir yere yazdırılmıyor; yalnızca print(x) çalışır."),
                  name_error]
    elif variant == "global":
        code = f"x = {x}\n\ndef {func}():\n    global x\n    x = {y}\n\n{func}()\nprint(x)"
        res = str(y)
        expl = (f"<code>global x</code> bildirimi, fonksiyondaki x'in dışarıdaki x olduğunu söyler; atama dışarıdaki x'i "
                f"{y} yapar.")
        wrongs = [Wrong(str(x), "global bildirimi sayesinde fonksiyon dışarıdaki x'i değiştirir."),
                  Wrong("None", "print(x) x'in değerini yazar; fonksiyonun dönüş değerini değil."),
                  Wrong(f"{x}\n{y}", "print yalnızca bir kez, fonksiyon çağrıldıktan sonra çalışır."),
                  name_error]
    else:
        code = f"x = {x}\n\ndef {func}():\n    x = {y}\n    return x\n\nprint({func}(), x)"
        res = f"{y} {x}"
        expl = (f"Fonksiyon yerel x'i ({y}) döndürür; dışarıdaki x değişmez ({x}). print ikisini aralarında boşlukla "
                "yazar.")
        wrongs = [Wrong(f"{y} {y}", "Fonksiyon içindeki x yereldir; dışarıdaki x değişmez."),
                  Wrong(f"{x} {x}", "Fonksiyon return ile kendi yerel x'ini döndürür."),
                  Wrong(f"None {x}", "Fonksiyon return ile bir değer döndürüyor; None değil.")]
    if variant != "both":
        if random.random() < 0.5:
            wrongs.remove(name_error)
        random.shuffle(wrongs)
    return output_question(
        code, res, expl, wrongs=wrongs,
        hint="Fonksiyon içindeki x ile dışarıdaki x aynı değişken mi? global yazılmış mı?",
    )


@q("Birden Fazla Değer Döndürme", verify="output")
def multi_return():
    a, b = random.sample(range(10, 40), 2)
    lo, hi = min(a, b), max(a, b)
    return output_question(
        f"def kucuk_buyuk(a, b):\n    return min(a, b), max(a, b)\n\nkucuk, buyuk = kucuk_buyuk({a}, {b})\n"
        "print(buyuk - kucuk)",
        str(hi - lo),
        "<code>return x, y</code> bir demet döndürür; demet açma ile iki değişkene atanır. "
        f"kucuk = {lo}, buyuk = {hi}, fark {hi - lo}.",
        wrongs=[
            Wrong(str(lo - hi), "kucuk küçük, buyuk büyük değeri alır; buyuk - kucuk pozitiftir."),
            Wrong(str(hi + lo), "Kod iki değerin farkını yazdırıyor, toplamını değil."),
            Wrong(str(hi), "Fonksiyon iki değer döndürür ve ikisi de kullanılır; kod farklarını yazdırıyor."),
        ],
        hint="Fonksiyon hangi iki değeri hangi sırayla döndürür? kucuk ve buyuk neye eşit olur?",
    )


@q("Özyineleme", verify="output")
def recursion():
    """n en az 4: 3! = 1 + 2 + 3 gibi çakışmalar olmaz (Y1)."""
    n = random.randint(4, 8)
    p = random.choice(["n", "sayi", "k"])
    if random.random() < 0.5:
        func = random.choice(["faktoriyel", "carpim"])
        return output_question(
            f"def {func}({p}):\n    if {p} <= 1:\n        return 1\n    return {p} * {func}({p} - 1)\n\n"
            f"print({func}({n}))", str(math.factorial(n)),
            f"Fonksiyon kendini {p} - 1 ile çağırır ve {p} <= 1 olunca durur: {n}! = "
            + " × ".join(str(i) for i in range(n, 0, -1)) + f" = {math.factorial(n)}.",
            wrongs=[
                Wrong(str(math.factorial(n - 1)), f"{func}({n}), {n}'den 1'e kadar tüm sayıların çarpımıdır; {n} de "
                                                  "dahil."),
                Wrong(str(n * (n + 1) // 2), "Bu toplama; fonksiyon sayıları çarpıyor."),
                Wrong(str(math.factorial(n + 1)), f"Çağrı {n} ile başlar ve küçülerek 1'e iner; {n + 1} hiç çarpılmaz."),
            ],
            hint=f"{func}({p}), {p} * {func}({p} - 1) demektir. 1'e inene kadar aç.",
        )
    func = random.choice(["topla", "toplam"])
    return output_question(
        f"def {func}({p}):\n    if {p} == 0:\n        return 0\n    return {p} + {func}({p} - 1)\n\nprint({func}({n}))",
        str(n * (n + 1) // 2),
        f"{func}({n}) = {n} + {func}({n - 1}) = ... = {n * (n + 1) // 2}. {p} == 0 durma koşuludur.",
        wrongs=[
            Wrong(str(n * (n - 1) // 2), f"{func}({n}) {n}'i de toplar; {n} + {n - 1} + ... + 1."),
            Wrong(str(math.factorial(n)), "Bu çarpım; fonksiyon sayıları topluyor."),
            Wrong(str(n), "Fonksiyon kendini çağırarak 0'a kadar tüm sayıları ekler."),
        ],
        hint=f"{func}({p}), {p} + {func}({p} - 1) demektir. 0'a inene kadar aç.",
    )


@q("math Modülü", verify="output")
def math_module():
    x = random.choice([16, 25, 36, 49, 64, 81, 100])
    y = round(random.randint(20, 89) / 10 + 0.05, 2)
    variant = random.choice(["sqrt", "ceil", "floor", "pi"])
    if variant == "sqrt":
        code, res = f"import math\nprint(math.sqrt({x}))", str(math.sqrt(x))
        why = "math.sqrt() karekök alır ve float döndürür"
        wrongs = [Wrong(str(int(math.sqrt(x))), "math.sqrt() sonucu float'tur; tam kare olsa da .0 ile yazılır."),
                  Wrong(str(x / 2), "Karekök, sayının yarısı değildir."),
                  Wrong(str(x * x), "sqrt karekök alır; sayının karesini değil.")]
    elif variant == "ceil":
        code, res = f"import math\nprint(math.ceil({y}))", str(math.ceil(y))
        why = "math.ceil() yukarı yuvarlar"
        wrongs = [Wrong(str(math.floor(y)), "ceil her zaman yukarı yuvarlar; aşağı yuvarlayan floor'dur."),
                  Wrong(str(y), "ceil kesirli kısmı atıp tam sayıya yuvarlar."),
                  Wrong(f"{math.ceil(y)}.0", "math.ceil() tam sayı (int) döndürür; sonuç .0 ile yazılmaz.")]
    elif variant == "floor":
        code, res = f"import math\nprint(math.floor({y}))", str(math.floor(y))
        why = "math.floor() aşağı yuvarlar"
        wrongs = [Wrong(str(math.ceil(y)), "floor her zaman aşağı yuvarlar; yukarı yuvarlayan ceil'dir."),
                  Wrong(str(y), "floor kesirli kısmı atıp tam sayıya yuvarlar."),
                  Wrong(f"{math.floor(y)}.0", "math.floor() tam sayı (int) döndürür; sonuç .0 ile yazılmaz.")]
    else:
        digits = random.choice([2, 3])
        code, res = f"from math import pi\nprint(round(pi, {digits}))", str(round(math.pi, digits))
        why = f"round(sayı, {digits}) virgülden sonra {digits} basamağa yuvarlar"
        wrongs = [Wrong(str(round(math.pi, 5 - digits)), f"round'un ikinci parametresi basamak sayısıdır: {digits}."),
                  Wrong("3", "İkinci parametre verildiği için tam sayıya değil, ondalık basamaklara yuvarlanır."),
                  Wrong(str(math.pi), "round() sayıyı istenen basamağa yuvarlar; pi'nin tamamı yazılmaz.")]
    return output_question(
        code, res,
        f"{why}. <code>import math</code> modülü yükler; fonksiyonlara <code>math.ad</code> ile ulaşılır.",
        wrongs=wrongs,
        hint="Kullanılan fonksiyon ne yapar: karekök mü, yukarı mı, aşağı mı yuvarlama?",
    )


@q("Fonksiyon Kavramları")
def concepts():
    return tf_question(
        [("Bir fonksiyon <code>return</code> satırına ulaştığında çalışmasını hemen bitirir.",
          "return değeri döndürür ve fonksiyondan çıkar; sonraki satırlar çalışmaz."),
         ("Fonksiyon tanımlamak (def) onu çalıştırmaz; fonksiyon çağrıldığında çalışır.",
          "def yalnızca tanımlar; fonksiyonun gövdesi ad(...) ile çağrıldığında çalışır."),
         ("Bir fonksiyon birden fazla parametre alabilir.",
          "Parametre sayısında sınır yoktur: def f(a, b, c) geçerlidir."),
         ("<code>return</code> içermeyen bir fonksiyon çağrıldığında None döndürür.",
          "return yoksa ya da değersizse fonksiyonun dönüş değeri None olur."),
         ("Fonksiyon içinde tanımlanan bir değişken, fonksiyon dışından doğrudan kullanılamaz.",
          "Fonksiyon içindeki değişkenler yereldir; dışarıda tanımlı değildir."),
         ("Bir fonksiyon başka bir fonksiyonu çağırabilir, hatta kendini de çağırabilir (özyineleme).",
          "Fonksiyonlar iç içe çağrılabilir; kendini çağırmaya özyineleme denir.")],
        [("<code>return</code> ile <code>print</code> aynı işi yapar; ikisi de değeri çağırana döndürür.",
          "print değeri yalnızca ekrana yazar; return ise değeri çağıran koda geri verir."),
         ("Bir fonksiyon en fazla bir parametre alabilir.",
          "Fonksiyonlar istenen sayıda parametre alabilir."),
         ("Fonksiyon tanımlandığı (def) anda gövdesindeki kodlar çalışır.",
          "def yalnızca fonksiyonu tanımlar; gövde çağrılana kadar çalışmaz."),
         ("Bir fonksiyon yalnızca bir kez çağrılabilir.",
          "Fonksiyonlar istenildiği kadar çağrılabilir; tekrar kullanım asıl amaçlarıdır."),
         ("Varsayılan değeri olan parametre çağrıda mutlaka verilmelidir.",
          "Varsayılan değeri olan parametre çağrıda verilmezse varsayılan değeri kullanılır."),
         ("Fonksiyon içinde <code>x = 5</code> yazmak, dışarıdaki x değişkenini her zaman değiştirir.",
          "Fonksiyon içindeki atama yeni bir yerel değişken oluşturur; dışarıdaki x değişmez.")],
        "<code>print</code> değeri yalnızca ekrana yazar; <code>return</code> ise değeri çağıran koda geri "
        "verir ve fonksiyonu sonlandırır. Fonksiyonlar istenen sayıda parametre alabilir ve istenildiği kadar "
        "çağrılabilir.",
        hint="Fonksiyon ne zaman çalışır, return ne yapar, parametreler nasıl eşleşir?",
    )


@q("Fonksiyon Yazma (Kod Yazma)")
def write_square_func():
    name = random.choice(["kare", "karesi", "kare_al", "karesini_bul", "kare_hesapla", "sayinin_karesi"])
    param = random.choice(["sayi", "x", "n"])
    return {
        "type": "code",
        "text": f"<code>{name}</code> adında, bir sayı parametresi alıp o sayının <strong>karesini döndüren</strong> "
                "(<code>return</code>) bir fonksiyon yazınız. Fonksiyonu çağırmanız gerekmez.",
        "code": None,
        "check": {"kind": "square_func", "name": name},
        "answer": f"def {name}({param}):\n    return {param} * {param}",
        "hint": "def ile tanımla; sonucu print ile yazdırma, return ile geri ver.",
        "solution": f"<code>def {name}({param}):</code> ile fonksiyon tanımlanır; <code>return {param} * {param}</code> "
                    f"(veya <code>{param} ** 2</code>) sonucu çağırana geri verir.",
    }


FILL_FUNCS = [("kare", "x * x"), ("kup", "x * x * x"), ("iki_kati", "2 * x"), ("bir_fazlasi", "x + 1"),
              ("yarisi", "x // 2"), ("on_kati", "x * 10")]


@q("def ve return (Boşluk Doldurma)", verify="fill",
   exempt={"top_answer": "Ölçülen şey def ve return anahtar sözcüklerinin yeri; cevap doğası gereği sabit, "
                         "çeşitlilik fonksiyon gövdesi ve çağrıdan gelir."})
def fill_def_return():
    name, expr = random.choice(FILL_FUNCS)
    arg = random.randint(2, 9)
    result = eval(expr, {"x": arg})  # noqa: S307 - yalnızca bizim ürettiğimiz sabit ifade
    call = random.choice([f"print({name}({arg}))", f"sonuc = {name}({arg})\nprint(sonuc)"])
    return fill_question(
        f"____ {name}(x):\n    ____ {expr}\n\n{call}",
        [["def"], ["return"]],
        str(result),
        f"Aşağıdaki kod <code>{name}</code> adında bir fonksiyon tanımlayıp ekrana <code>{result}</code> "
        "yazdırmalı. Boşluklara gereken anahtar kelimeleri yazın.",
        "Fonksiyon <code>def</code> anahtar kelimesiyle tanımlanır. <code>return</code>, hesaplanan değeri "
        f"fonksiyonun çağrıldığı yere geri gönderir; böylece <code>{name}({arg})</code> çağrısı {result} olur "
        "ve print bunu yazar.",
        hint="Fonksiyon tanımlayan satır hangi anahtar kelimeyle başlar? Bulunan değeri çağrıldığı yere geri "
             "göndermek için hangisi kullanılır?",
    )


# ================================================================= yeni şablonlar (ölçme raporu Ö9.1-Ö9.9)
@q("print mi return mü? (Doğru/Yanlış)", verify="tf_output")
def print_return_claim():
    """Kazanım: return ile print farkının çıktıya etkisini izler · Bloom: An"""
    name = random.choice(["iki_kat", "hesapla", "islem", "donustur", "artir"])
    p = random.choice(["x", "n", "sayi"])
    op, k = random.choice(["*", "+"]), random.randint(2, 5)
    a, c = random.randint(2, 9), random.randint(1, 9)
    val = a * k if op == "*" else a + k
    expr = f"{p} {op} {k}"
    variant = random.choice(["return_expr", "print_expr", "print_call", "both"])
    if variant == "return_expr":
        code = f"def {name}({p}):\n    return {expr}\n\nsonuc = {name}({a}) + {c}\nprint(sonuc)"
        output = str(val + c)
        wrongs = [Wrong(err("TypeError"), f"Fonksiyon return ile bir sayı döndürüyor; {name}({a}) + {c} hata vermez."),
                  Wrong(str(val), f"Fonksiyonun döndürdüğü {val} değerine {c} de eklenir."),
                  Wrong(f"{val}\n{val + c}", "Fonksiyonun içinde print yok; ekrana yalnızca sonuc yazılır.")]
        solution = f"Fonksiyon {val} değerini <strong>döndürür</strong>; sonuc = {val} + {c} = {val + c} olur."
    elif variant == "print_expr":
        code = f"def {name}({p}):\n    print({expr})\n\nsonuc = {name}({a}) + {c}\nprint(sonuc)"
        output = err("TypeError")
        wrongs = [Wrong(str(val + c), f"Fonksiyon değeri yalnızca ekrana yazar, döndürmez; {name}({a}) None olur ve "
                                      f"None + {c} hata verir."),
                  Wrong(f"{val}\n{val + c}", f"Önce {val} yazılır; ama fonksiyon None döndürdüğü için None + {c} "
                                             f"TypeError verir ve {val + c} hiç yazılmaz.")]
        solution = (f"Fonksiyon {val} değerini yalnızca ekrana yazar; <code>return</code> olmadığı için çağrının değeri "
                    f"<strong>None</strong> olur. <code>None + {c}</code> işlemi TypeError verir.")
    elif variant == "print_call":
        code = f"def {name}({p}):\n    print({expr})\n\nprint({name}({a}))"
        output = f"{val}\nNone"
        wrongs = [Wrong(str(val), "Dıştaki print, fonksiyonun döndürdüğü değeri de yazar; return olmadığı için bu "
                                  "değer None'dır."),
                  Wrong("None", f"Fonksiyon çağrılınca içindeki print önce çalışır ve {val} yazar."),
                  Wrong(err("TypeError"), "None değerini yazdırmak hata vermez; ekrana None yazılır.")]
        solution = (f"Önce fonksiyon içindeki print {val} yazar. Fonksiyon <code>return</code> içermediği için "
                    "None döndürür; dıştaki print bunu yazar.")
    else:
        code = f"def {name}({p}):\n    print({p})\n    return {expr}\n\nprint({name}({a}) + {c})"
        output = f"{a}\n{val + c}"
        wrongs = [Wrong(str(val + c), f"Fonksiyon içindeki print({p}) de çalışır; önce {a} yazılır."),
                  Wrong(f"{a}\n{val}", f"return edilen {val} değerine {c} eklenip öyle yazdırılır."),
                  Wrong(f"{val + c}\n{a}", "Önce fonksiyon çalışır ve içindeki print yazar; toplam daha sonra "
                                           "yazdırılır.")]
        solution = (f"Fonksiyon önce {a} yazar, sonra {val} değerini döndürür; dıştaki print {val} + {c} = "
                    f"{val + c} yazar.")
    return tf_claim(code, output, wrongs, solution,
                    hint="Fonksiyon bir değer döndürüyor mu, yoksa yalnızca ekrana mı yazıyor?")


def _call_forms(names, values, defaults):
    """Parametrelere values değerlerini bağlayan bütün çağrı biçimleri (konumsal, isimli, karışık; varsayılanı
    olan son parametre, değeri varsayılana eşitse yazılmayabilir)."""
    first, second = names
    v1, v2 = values
    forms = [f"{v1}, {v2}", f"{v1}, {second}={v2}", f"{first}={v1}, {second}={v2}", f"{second}={v2}, {first}={v1}"]
    if defaults.get(second) == v2:
        forms += [f"{v1}", f"{first}={v1}"]
    return forms


@q("Argümanlarla Çağrı (Boşluk Doldurma)", verify="fill")
def call_args_blank():
    """Kazanım: konumsal ve isimli argümanlarla çağrı kurar · Bloom: U/An"""
    kind = random.choice(["us", "tekrar", "selam"])
    if kind == "us":
        a, b = random.choice([2, 3, 4, 5, 6, 7]), random.choice([2, 3, 4])
        target = a ** b
        pairs = [(t, k) for t in range(-100, 101) for k in range(9) if t ** k == target]
        pairs.sort(key=lambda tk: (tk != (a, b), tk))
        alts = [f for t, k in pairs for f in _call_forms(("taban", "kuvvet"), (t, k), {"kuvvet": 2})]
        code = "def us(taban, kuvvet=2):\n    return taban ** kuvvet\n\nprint(us(____))"
        shown_target = str(target)
        wrongs = [Wrong(str(target), "Boşluğa sonucu değil, fonksiyona verilecek argümanları yazmalısın."),
                  Wrong(f"{b}, {a}", "Konumsal argümanlar sırayla eşleşir: ilk değer tabana, ikincisi kuvvete gider."),
                  Wrong(f"kuvvet={b}, {a}", "İsimli argümandan sonra konumsal argüman yazılamaz; sözdizimi hatası "
                                            "oluşur.")]
        if b != 2:
            wrongs.append(Wrong(str(a), "Kuvvet verilmezse varsayılan değer 2 kullanılır."))
        extra = " Tam sayı argümanlar kullanınız."
        hint = f"Hangi taban hangi kuvvetle {target} eder? Verilmeyen parametre hangi değeri alır?"
        solution = (f"<code>us({a}, {b})</code> çağrısında taban = {a}, kuvvet = {b} olur: {a} ** {b} = {target}. "
                    f"Aynı çağrı isimli argümanlarla <code>us(taban={a}, kuvvet={b})</code> ya da "
                    f"<code>us(kuvvet={b}, taban={a})</code> diye de yazılabilir; isimli argümanlarda sıra önemsizdir.")
    elif kind == "tekrar":
        word, k = random.choice(["ha", "na", "la", "tik", "pat", "ab", "cik"]), random.randint(2, 4)
        target = word * k
        alts = []
        for kk in range(1, len(target) + 1):
            if len(target) % kk == 0 and target[:len(target) // kk] * kk == target:
                s = target[:len(target) // kk]
                alts += _call_forms(("metin", "kez"), (f'"{s}"', kk), {"kez": 2})
                alts.append(f'{kk}, "{s}"')  # sayı * metin de aynı sonucu verir
        alts.sort(key=lambda f: f != f'"{word}", {k}')
        code = "def tekrar(metin, kez=2):\n    return metin * kez\n\nprint(tekrar(____))"
        shown_target = target
        wrongs = [Wrong(f'"{target}"', "Kez verilmezse varsayılan değer 2 kullanılır; metin iki kez tekrarlanır."),
                  Wrong(f"{word}, {k}", "Metin değerleri tırnak içinde yazılır; tırnaksız yazılınca bir değişken adı "
                                        "sanılır."),
                  Wrong(f'kez={k}, "{word}"', "İsimli argümandan sonra konumsal argüman yazılamaz; sözdizimi hatası "
                                              "oluşur.")]
        extra = ""
        hint = "Hangi metin kaç kez tekrarlanınca bu sonuç çıkar? Verilmeyen parametre hangi değeri alır?"
        solution = (f'<code>tekrar("{word}", {k})</code> çağrısında metin = "{word}", kez = {k} olur. Aynı çağrı '
                    f'<code>tekrar(kez={k}, metin="{word}")</code> diye de yazılabilir; isimli argümanlarda sıra '
                    "önemsizdir.")
    else:
        ad, unvan = random.choice(PEOPLE), random.choice(["Doktor", "Öğretmen", "Mühendis", "Sayın", "Avukat"])
        target = f"{unvan} {ad}"
        alts = _call_forms(("ad", "unvan"), (f'"{ad}"', f'"{unvan}"'), {"unvan": '"Sayın"'})
        code = "def selam(ad, unvan=\"Sayın\"):\n    return unvan + \" \" + ad\n\nprint(selam(____))"
        shown_target = target
        wrongs = [Wrong(f'"{unvan}", "{ad}"', "Konumsal argümanlar sırayla eşleşir: ilk değer ad parametresine gider."),
                  Wrong(f'unvan="{unvan}", "{ad}"', "İsimli argümandan sonra konumsal argüman yazılamaz; sözdizimi "
                                                    "hatası oluşur.")]
        if unvan != "Sayın":
            wrongs.append(Wrong(f'"{ad}"', 'Unvan verilmezse varsayılan değer "Sayın" kullanılır.'))
        extra = ""
        hint = "Fonksiyon unvanı ve adı hangi sırayla birleştiriyor? İlk konumsal argüman hangi parametreye gider?"
        solution = (f'<code>selam("{ad}", "{unvan}")</code> çağrısında ad = "{ad}", unvan = "{unvan}" olur. Aynı '
                    f'çağrı <code>selam(unvan="{unvan}", ad="{ad}")</code> diye de yazılabilir; isimli argümanlarda '
                    "sıra önemsizdir.")
    return fill_question(
        code, [list(dict.fromkeys(alts))], shown_target,
        f"Kod ekrana <code>{e(shown_target)}</code> yazmalı. Boşluğa fonksiyonun alacağı argümanları yazınız "
        f"(konumsal ya da isimli).{extra}",
        solution, hint=hint, wrongs=[wrongs],
    )


GLOBAL_OPS = ("+=", "-=", "*=", "//=")


def _apply(op, start, d, calls):
    value = start
    for _ in range(calls):
        value = {"+=": value + d, "-=": value - d, "*=": value * d, "//=": value // d, "=": d}[op]
    return value


@q("global Anahtar Sözcüğü (Boşluk Doldurma)", verify="fill")
def global_blank():
    """Kazanım: fonksiyon içinden global değişkeni değiştirmenin yolunu bilir · Bloom: H/A"""
    var = random.choice(["sayac", "puan", "toplam", "skor"])
    func = random.choice(["artir", "guncelle", "degistir", "isle"])
    while True:
        start, d, calls = random.randint(20, 60), random.randint(2, 4), random.randint(2, 3)
        results = {op: _apply(op, start, d, calls) for op in GLOBAL_OPS + ("=",)}
        if len(set(results.values()) | {start}) == len(results) + 1:
            break
    op = random.choice(GLOBAL_OPS)
    expect = results[op]
    code = (f"{var} = {start}\n\ndef {func}():\n    ____ {var}\n    {var} ____ {d}\n\n" + f"{func}()\n" * calls
            + f"print({var})")
    op_wrongs = [Wrong(o, f"<code>{o}</code> ile sonuç {results[o]} olur; beklenen {expect}.") for o in GLOBAL_OPS
                 if o != op]
    op_wrongs.append(Wrong("=", f"<code>=</code> her çağrıda değeri {d} yapar; önceki değer kullanılmaz."))
    return fill_question(
        code, [["global"], [op]], str(expect),
        f"<code>{func}()</code> her çağrıldığında dışarıdaki <code>{var}</code> değişkenini değiştirmeli ve kod "
        f"ekrana <code>{expect}</code> yazmalı. Boşlukları doldurunuz.",
        f"<code>global {var}</code> bildirimi, fonksiyondaki {var} adının dışarıdaki değişken olduğunu söyler. Bu "
        f"satır olmasaydı <code>{var} {op} {d}</code> yerel bir değişkeni değiştirmeye çalışır ve UnboundLocalError "
        f"verirdi. {calls} çağrıdan sonra {var} = {expect} olur.",
        hint="Fonksiyon içinden dışarıdaki bir değişkeni değiştirmek için Python'a ne söylemelisin? Değer her çağrıda "
             "nasıl değişmeli?",
        wrongs=[[Wrong("return", "return değer döndürür ve fonksiyonu bitirir; dışarıdaki değişkeni bağlamaz. Sonraki "
                                 "satır hiç çalışmaz."),
                 Wrong("Global", "Python büyük/küçük harfe duyarlıdır; anahtar sözcükler küçük harfle yazılır."),
                 Wrong("local", "Python'da local diye bir anahtar sözcük yoktur; fonksiyondaki değişkenler zaten "
                                "yereldir.")],
                op_wrongs],
    )


KEYWORD_FUNCS = [
    ("bolme", ("bolunen", "bolen"), "//"),
    ("fark", ("buyuk", "kucuk"), "-"),
    ("kalan", ("sayi", "bolen"), "%"),
]


@q("İsimli Argümanlar")
def keyword_args():
    """Kazanım: isimli argümanların sırayı değiştirdiğini bilir · Bloom: U"""
    if random.random() < 0.25:
        x, y, z = random.sample(range(2, 10), 3)
        code = f"def hesap(a, b, c):\n    return a * b - c\n\nprint(hesap(c={z}, a={x}, b={y}))"
        res = x * y - z
        wrongs = [Wrong(str(z * x - y), "İsimli argümanlar adlarına göre eşleşir, yazılış sırasına göre değil: "
                                        f"a = {x}, b = {y}, c = {z}."),
                  Wrong(str(x * y), "Fonksiyon çarpımdan c'yi çıkarıyor."),
                  Wrong(str(x * (y - z)), "Çarpma çıkarmadan önce yapılır: a * b - c.")]
        solution = f"İsimli argümanlar adlarıyla eşleşir: a = {x}, b = {y}, c = {z}; {x} * {y} - {z} = {res}."
    else:
        name, (p1, p2), op = random.choice(KEYWORD_FUNCS)
        big, small = random.randint(20, 60), random.randint(2, 9)
        while op != "-" and big % small == 0:  # tam bölünürse // ile / sonucu aynı görünür
            big, small = random.randint(20, 60), random.randint(2, 9)
        res = {"//": big // small, "-": big - small, "%": big % small}[op]
        swapped = {"//": small // big, "-": small - big, "%": small % big}[op]
        code = f"def {name}({p1}, {p2}):\n    return {p1} {op} {p2}\n\nprint({name}({p2}={small}, {p1}={big}))"
        wrongs = [Wrong(str(swapped), f"İsimli argümanlar adlarına göre eşleşir: {p1} = {big}, {p2} = {small}. "
                                      "Yazılış sırası önemli değildir.")]
        if op == "//":
            wrongs += [Wrong(str(big % small), "// bölümü verir; kalanı veren % operatörüdür.")]
            if (big * 100) % small == 0:  # öğrencinin yazabileceği kısa bir ondalık
                wrongs.append(Wrong(str(big / small), "// tam bölmedir; sonucun kesir kısmı atılır."))
        elif op == "%":
            wrongs += [Wrong(str(big // small), "% kalanı verir; bölümü veren // operatörüdür.")]
        else:
            wrongs += [Wrong(str(big + small), "Fonksiyon iki değerin farkını döndürüyor.")]
        solution = (f"İsimli argümanlar adlarıyla eşleşir: {p1} = {big}, {p2} = {small}. Fonksiyon {big} {op} {small} "
                    f"= {res} döndürür.")
    return output_question(code, str(res), solution, common_wrongs=wrongs, norm="sayi",
                           hint="Çağrıdaki her değer hangi parametreye gidiyor? İsimli argümanda sıra önemli mi?")


@q("Fonksiyon İçinde Fonksiyon")
def func_compose():
    """Kazanım: iç içe fonksiyon çağrılarını izler · Bloom: U"""
    f_name, g_name = random.choice([("f", "g"), ("ic", "dis"), ("ekle", "hesapla"), ("yardimci", "ana")])
    f_op, k1 = random.choice(["+", "*", "-"]), random.randint(2, 6)
    k2, n = random.randint(2, 5), random.randint(2, 9)

    def f(x):
        return {"+": x + k1, "*": x * k1, "-": x - k1}[f_op]

    g_kind = random.choice(["mul", "add", "inner"])
    if g_kind == "mul":
        g_body, g, reverse = f"{f_name}(x) * {k2}", (lambda x: f(x) * k2), f(n * k2)
    elif g_kind == "add":
        g_body, g, reverse = f"{f_name}(x) + {k2}", (lambda x: f(x) + k2), f(n + k2)
    else:
        g_body, g, reverse = f"{f_name}(x * {k2})", (lambda x: f(x * k2)), f(n) * k2
    nested = random.random() < 0.3
    if nested:
        call, res = f"{f_name}({g_name}({n}))", f(g(n))
        order = (f"önce içteki <code>{g_name}({n})</code> hesaplanır ({g(n)}), sonra sonuç <code>{f_name}</code> "
                 f"fonksiyonuna verilir")
        partial = Wrong(str(g(n)), f"{g_name}({n}) = {g(n)} yalnızca içteki çağrının sonucu; dıştaki {f_name} de "
                                   "uygulanır.")
    else:
        call, res = f"{g_name}({n})", g(n)
        order = f"<code>{g_name}</code> çalışırken içinde <code>{f_name}</code> çağrılır ve sonucu kullanılır"
        partial = Wrong(str(n * k2 if g_kind != "add" else n + k2),
                        f"{g_name} içindeki {f_name} çağrısı da hesaplanmalı; {f_name} fonksiyonunun işlemi "
                        "atlanmış.")
    code = f"def {f_name}(x):\n    return x {f_op} {k1}\n\ndef {g_name}(x):\n    return {g_body}\n\nprint({call})"
    wrongs = [Wrong(str(reverse), "İşlemlerin sırasına dikkat et: hangi fonksiyonun sonucu hangisine veriliyor?"),
              Wrong(str(f(n)), f"Yalnızca {f_name}({n}) hesaplanmış; {g_name} fonksiyonunun kendi işlemi "
                                       "de uygulanır."),
              partial]
    return output_question(
        code, str(res),
        f"İç içe çağrıda {order}. Sonuç {res}.",
        common_wrongs=wrongs, norm="sayi",
        hint=f"Önce hangi çağrı hesaplanır? {g_name} çalışırken {f_name} hangi değerle çağrılır?",
    )


def _function_options(purpose):
    name_pool, p_pool = {
        "mutlak": (["mutlak", "mutlak_deger", "pozitif_yap", "uzaklik"], ["x", "n", "sayi"]),
        "cift": (["cift_mi", "cift", "cift_sayi_mi", "ciftse"], ["x", "n", "sayi"]),
        "buyuk": (["buyuk", "en_buyuk", "buyugu", "buyugunu_bul"], [("a", "b"), ("x", "y"), ("s1", "s2")]),
    }[purpose]
    name, p = random.choice(name_pool), random.choice(p_pool)
    if purpose == "mutlak":
        text = "Hangi fonksiyon verilen sayının mutlak değerini <strong>döndürür</strong>?"
        correct = f"def {name}({p}):\n    if {p} < 0:\n        return -{p}\n    return {p}"
        wrongs = [Wrong(f"def {name}({p}):\n    if {p} < 0:\n        print(-{p})\n    else:\n        print({p})",
                        "Sonucu ekrana yazar ama döndürmez; fonksiyonun değeri None olur."),
                  Wrong(f"def {name}({p}):\n    return -{p}", "Pozitif sayıları negatife çevirir."),
                  Wrong(f"def {name}({p}):\n    if {p} < 0:\n        {p} = -{p}",
                        "return yok; fonksiyon her durumda None döndürür."),
                  Wrong(f"def {name}({p}):\n    if {p} > 0:\n        return -{p}\n    return {p}",
                        "Koşul ters: pozitif sayıyı negatife çevirir, negatifi olduğu gibi bırakır.")]
        cases = [{"setup": f"deger = {v}", "expect": str(abs(v))} for v in (-5, 0, 7, -12, 3)]
        harness = "{option}\n" + f"print({name}(deger))"
        hint = "Her seçeneği -5 ve 7 ile dene; sonucu yazıyor mu, döndürüyor mu?"
        solution = ("Negatif sayıda <code>-x</code>, diğerlerinde <code>x</code> döndürülür. print kullanan fonksiyon "
                    "sonucu döndürmez (None); return'ü olmayan fonksiyon da None döndürür.")
    elif purpose == "cift":
        text = "Hangi fonksiyon sayı çiftse <code>True</code>, tekse <code>False</code> <strong>döndürür</strong>?"
        correct = f"def {name}({p}):\n    return {p} % 2 == 0"
        wrongs = [Wrong(f"def {name}({p}):\n    print({p} % 2 == 0)",
                        "Sonucu ekrana yazar ama döndürmez; fonksiyonun değeri None olur."),
                  Wrong(f"def {name}({p}):\n    return {p} % 2 == 1", "Tek sayılar için True döndürür."),
                  Wrong(f"def {name}({p}):\n    if {p} % 2 == 0:\n        return True",
                        "Tek sayıda hiçbir return çalışmaz; False yerine None döner."),
                  Wrong(f"def {name}({p}):\n    return {p} / 2 == 0", "Yalnızca 0 için True olur; kalan % ile bulunur.")]
        cases = [{"setup": f"deger = {v}", "expect": str(v % 2 == 0)} for v in (4, 7, 0, -3, 10)]
        harness = "{option}\n" + f"print({name}(deger))"
        hint = "Her seçeneği bir tek ve bir çift sayıyla dene; sonuç döndürülüyor mu?"
        solution = ("<code>x % 2 == 0</code> karşılaştırması zaten True ya da False verir; return ile döndürülür. "
                    "Koşulu yalnızca bir dalda döndüren fonksiyon tek sayıda None döndürür.")
    else:
        a, b = p
        text = "Hangi fonksiyon iki sayıdan büyük olanı <strong>döndürür</strong>?"
        correct = f"def {name}({a}, {b}):\n    if {a} > {b}:\n        return {a}\n    return {b}"
        wrongs = [Wrong(f"def {name}({a}, {b}):\n    if {a} > {b}:\n        print({a})\n    else:\n        print({b})",
                        "Sonucu ekrana yazar ama döndürmez; fonksiyonun değeri None olur."),
                  Wrong(f"def {name}({a}, {b}):\n    if {a} > {b}:\n        return {b}\n    return {a}",
                        "Dönüş değerleri ters: küçük olanı döndürür."),
                  Wrong(f"def {name}({a}, {b}):\n    if {a} > {b}:\n        return {a}",
                        f"{b} büyükse hiçbir return çalışmaz; fonksiyon None döndürür."),
                  Wrong(f"def {name}({a}, {b}):\n    return {a} > {b}", "Sayıyı değil, karşılaştırmanın sonucunu "
                                                                       "(True/False) döndürür.")]
        cases = [{"setup": f"s_1 = {x}\ns_2 = {y}", "expect": str(max(x, y))}
                 for x, y in ((3, 8), (9, 2), (5, 5), (-1, -4))]
        harness = "{option}\n" + f"print({name}(s_1, s_2))"
        hint = "Her seçeneği önce büyük, sonra küçük sayı vererek dene; her durumda bir değer döndürülüyor mu?"
        solution = ("Büyük olan döndürülmeli: koşul sağlanırsa ilk sayı, sağlanmazsa ikinci sayı. Yalnızca bir dalda "
                    "return olan fonksiyon diğer durumda None döndürür.")
    random.shuffle(wrongs)
    return text, correct, wrongs[:3], cases, harness, hint, solution


@q("Hangi Fonksiyon Doğru?", verify="code_one")
def which_function():
    """Kazanım: fonksiyon tanımlarını doğruluk açısından değerlendirir · Bloom: D"""
    text, correct, wrongs, cases, harness, hint, solution = _function_options(
        random.choice(["mutlak", "cift", "buyuk"]))
    return code_options_question(text, correct, wrongs, cases, solution, hint=hint, harness=harness)


BOOL_PREDS = {
    "cift": (["cift_mi", "cift", "cift_sayi_mi"], "sayı çiftse <code>True</code>, değilse <code>False</code>",
             "{p} % 2 == 0", lambda n: n % 2 == 0),
    "pozitif": (["pozitif_mi", "pozitif", "arti_mi"],
                "sayı sıfırdan büyükse <code>True</code>, değilse <code>False</code>", "{p} > 0", lambda n: n > 0),
    "bes": (["bese_bolunur_mu", "bes_kati_mi", "bes_ile_bolunur"],
            "sayı 5 ile tam bölünüyorsa <code>True</code>, bölünmüyorsa <code>False</code>", "{p} % 5 == 0",
            lambda n: n % 5 == 0),
}


@q("True/False Döndüren Fonksiyon (Kod Yazma)")
def write_is_even():
    """Kazanım: bool döndüren fonksiyon yazar · Bloom: O"""
    pred = random.choice(list(BOOL_PREDS))
    names, desc, expr, func = BOOL_PREDS[pred]
    name, p = random.choice(names), random.choice(["n", "sayi", "x"])
    ex = random.choice([v for v in range(-9, 31) if v])
    return {
        "type": "code",
        "text": f"<code>{name}</code> adında, bir sayı alıp {desc} <strong>döndüren</strong> (<code>return</code>) "
                f"bir fonksiyon yazınız. Fonksiyonu çağırmanız gerekmez. (Örnek: <code>{name}({ex})</code> → "
                f"<code>{func(ex)}</code>)",
        "code": None,
        "check": {"kind": "bool_func", "name": name, "pred": pred},
        "answer": f"def {name}({p}):\n    return {expr.format(p=p)}",
        "hint": "Bir karşılaştırma ifadesi zaten True ya da False verir; sonucu yazdırma, döndür.",
        "solution": f"<code>{e(expr.format(p=p))}</code> karşılaştırması True ya da False verir; "
                    "<code>return</code> ile doğrudan döndürülebilir. <code>if ... return True / else: return False"
                    "</code> biçimi de doğrudur.",
    }


@q("Liste Ortalaması Fonksiyonu (Kod Yazma)")
def write_mean_func():
    """Kazanım: liste parametresi alan ve hesap döndüren fonksiyon yazar · Bloom: O"""
    name = random.choice(["ortalama", "ort", "ortalama_bul", "ortalama_hesapla"])
    p = random.choice(["liste", "sayilar", "notlar"])
    while True:  # örnek ortalama tam sayı ya da kısa ondalık (.25, .5, .75) olsun
        nums = random.sample(range(10, 100, 5), random.randint(3, 4))
        if (sum(nums) * 4) % len(nums) == 0:
            break
    mean = sum(nums) / len(nums)
    shown_mean = int(mean) if mean == int(mean) else mean
    return {
        "type": "code",
        "text": f"<code>{name}</code> adında, bir sayı listesi alıp listenin ortalamasını <strong>döndüren</strong> "
                f"bir fonksiyon yazınız (liste boş olmayacak). Örnek: <code>{name}({nums})</code> → "
                f"<code>{shown_mean}</code>",
        "code": None,
        "check": {"kind": "mean_func", "name": name},
        "answer": f"def {name}({p}):\n    return sum({p}) / len({p})",
        "hint": "Ortalama için hangi iki değere ihtiyacın var? Sonucu print ile değil, return ile ver.",
        "solution": f"<code>sum({p})</code> elemanların toplamını, <code>len({p})</code> eleman sayısını verir; "
                    "ortalama toplamın eleman sayısına bölümüdür. Toplam bir döngüyle de bulunabilir. "
                    "<code>//</code> kesir kısmını atacağı için <code>/</code> kullanılır.",
    }


@q("Faktöriyel Fonksiyonu (Kod Yazma)")
def write_factorial():
    """Kazanım: döngüyle ya da özyinelemeyle faktöriyel hesaplar · Bloom: O"""
    name = random.choice(["faktoriyel", "fakt", "faktoriyel_hesapla"])
    method = random.choice([None, "dongu", "ozyineleme"])
    k = random.randint(3, 8)
    how = {None: "", "dongu": "<strong>döngü kullanarak</strong> ",
           "ozyineleme": "<strong>özyinelemeyle (fonksiyon kendini çağırarak)</strong> "}[method]
    if method == "ozyineleme" or (method is None and random.random() < 0.5):
        answer = f"def {name}(n):\n    if n <= 1:\n        return 1\n    return n * {name}(n - 1)"
    else:
        answer = f"def {name}(n):\n    sonuc = 1\n    for i in range(1, n + 1):\n        sonuc *= i\n    return sonuc"
    return {
        "type": "code",
        "text": f"<code>{name}(n)</code> fonksiyonunu {how}yazınız: n! değerini <strong>döndürsün</strong>. "
                f"<code>{name}({k})</code> {math.factorial(k)}, <code>{name}(0)</code> 1 döndürmeli.",
        "code": None,
        "check": {"kind": "factorial", "name": name, "method": method},
        "answer": answer,
        "hint": "0! = 1 ve n! = n × (n-1)! olduğunu hatırla. Çarpımın başlangıç değeri ne olmalı?",
        "solution": "Döngüyle: <code>sonuc = 1</code> ile başlanır ve 1'den n'ye kadar her sayı çarpılır "
                    "(<code>range(1, n + 1)</code>). Özyinelemeyle: <code>n <= 1</code> durma koşulunda 1 döndürülür, "
                    "diğer durumda <code>n * fonksiyon(n - 1)</code> döndürülür.",
    }


# ================================================================= kod yazma denetleyicileri
# FuncSim, öğrencinin fonksiyonunu somut parametre değerleriyle AST üzerinde izler. Öğrenci kodu Python'a
# çalıştırılmaz: her ifade codecheck.safe_eval ile (yalnızca sayı/metin işlemleri) hesaplanır; listeye ait
# sum/len/indeks ve fonksiyonun kendini çağırması önceden sabit değere çevrilir. Adım ve döngü sayısı sınırlıdır.
MAX_SIM_STEPS = 3000
MAX_SIM_TURNS = 500


class Endless(Unknown):
    """Döngü sınırı aşıldı (büyük olasılıkla bitmeyen döngü)."""


class NoBase(Unknown):
    """Özyinelemeli çağrı küçülerek durma koşuluna ulaşmıyor."""


class _Return(Exception):
    def __init__(self, value):
        super().__init__()
        self.value = value


class _Break(Exception):
    pass


class _Continue(Exception):
    pass


class FuncSim:
    """Desteklenen satırlar: ad atama (a = ..., a, b = ..., ...), +=, if/elif/else, for (range ya da liste
    üzerinde), while, break, continue, return, pass, print (sayılır ama hesaplanmaz) ve belge metni.
    self_call: fonksiyon kendini çağırdığında argüman listesiyle çağrılır ve dönüş değerini verir.
    Desteklenmeyen her yapı Unknown fırlatır (check_code öğrenciye 'değerlendiremedim' notu verir)."""

    def __init__(self, func, self_call=None):
        self.func = func
        self.params = function_params(func) or []
        self.self_call = self_call
        self.steps = 0
        self.prints = 0

    def call(self, *args):
        self.steps = 0
        env = dict(zip(self.params, args))
        try:
            self._block(self.func.body, env)
        except _Return as ret:
            return ret.value
        except (_Break, _Continue):
            raise Unknown("döngü dışında break") from None
        return None

    # ---- ifadeler
    def value(self, node, env):
        scalars = {k: v for k, v in env.items() if not isinstance(v, list)}
        return safe_eval(self._reduce(node, env), scalars)

    def _reduce(self, node, env):
        sim = self

        class Reducer(ast.NodeTransformer):
            def visit_Call(self, n):
                f = n.func
                if isinstance(f, ast.Name) and not n.keywords:
                    if (f.id in ("sum", "len") and len(n.args) == 1 and isinstance(n.args[0], ast.Name)
                            and isinstance(env.get(n.args[0].id), list)):
                        seq = env[n.args[0].id]
                        return ast.Constant(sum(seq) if f.id == "sum" else len(seq))
                    if f.id == sim.func.name and sim.self_call is not None:
                        return ast.Constant(sim.self_call([sim.value(a, env) for a in n.args]))
                self.generic_visit(n)
                return n

            def visit_Subscript(self, n):
                if isinstance(n.value, ast.Name) and isinstance(env.get(n.value.id), list):
                    if isinstance(n.slice, ast.Slice):
                        raise Unknown("dilim")
                    seq, idx = env[n.value.id], sim.value(n.slice, env)
                    if not isinstance(idx, int) or isinstance(idx, bool) or not -len(seq) <= idx < len(seq):
                        raise Unknown("indeks")
                    return ast.Constant(seq[idx])
                self.generic_visit(n)
                return n

        return Reducer().visit(copy.deepcopy(node))

    def _iter(self, node, env):
        if isinstance(node, ast.Name) and isinstance(env.get(node.id), list):
            return list(env[node.id])
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "range"
                and 1 <= len(node.args) <= 3 and not node.keywords):
            args = [self.value(a, env) for a in node.args]
            if any(not isinstance(a, int) or isinstance(a, bool) for a in args) or (len(args) == 3 and not args[2]):
                raise Unknown("range")
            r = range(*args)
            if len(r) > MAX_SIM_TURNS:
                raise Endless("range çok uzun")
            return list(r)
        raise Unknown("desteklenmeyen döngü")

    # ---- satırlar
    def _block(self, stmts, env):
        for stmt in stmts:
            self._stmt(stmt, env)

    def _loop_body(self, body, env):
        """Döngü gövdesini bir tur izler; break olursa True."""
        try:
            self._block(body, env)
        except _Break:
            return True
        except _Continue:
            pass
        return False

    def _stmt(self, stmt, env):
        self.steps += 1
        if self.steps > MAX_SIM_STEPS:
            raise Endless("çok fazla adım")
        if isinstance(stmt, ast.Return):
            raise _Return(None if stmt.value is None else self.value(stmt.value, env))
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1:
            target = stmt.targets[0]
            if isinstance(target, ast.Name):
                env[target.id] = self.value(stmt.value, env)
                return
            if (isinstance(target, ast.Tuple) and isinstance(stmt.value, ast.Tuple)
                    and len(target.elts) == len(stmt.value.elts) and all(isinstance(t, ast.Name) for t in target.elts)):
                values = [self.value(v, env) for v in stmt.value.elts]
                for t, v in zip(target.elts, values):
                    env[t.id] = v
                return
        elif isinstance(stmt, ast.AugAssign) and isinstance(stmt.target, ast.Name):
            name = stmt.target.id
            if name not in env or isinstance(env[name], list):
                raise Unknown(f"{name} değeri bilinmiyor")
            right = self.value(stmt.value, env)
            node = ast.BinOp(left=ast.Name(id="sol_", ctx=ast.Load()), op=stmt.op,
                             right=ast.Name(id="sag_", ctx=ast.Load()))
            env[name] = safe_eval(node, {"sol_": env[name], "sag_": right})
            return
        elif isinstance(stmt, ast.If):
            self._block(stmt.body if self.value(stmt.test, env) else stmt.orelse, env)
            return
        elif isinstance(stmt, ast.For) and not stmt.orelse and isinstance(stmt.target, ast.Name):
            for item in self._iter(stmt.iter, env):
                env[stmt.target.id] = item
                if self._loop_body(stmt.body, env):
                    break
            return
        elif isinstance(stmt, ast.While) and not stmt.orelse:
            tested = {n.id for n in ast.walk(stmt.test) if isinstance(n, ast.Name)}
            changed = set().union(*(assigned_names(s) for s in stmt.body))
            if not tested & changed and not any(isinstance(n, (ast.Break, ast.Return)) for n in ast.walk(stmt)):
                raise Endless("koşuldaki değişken değişmiyor")
            turns = 0
            while self.value(stmt.test, env):
                turns += 1
                if turns > MAX_SIM_TURNS:
                    raise Endless("döngü bitmiyor")
                if self._loop_body(stmt.body, env):
                    break
            return
        elif isinstance(stmt, ast.Break):
            raise _Break
        elif isinstance(stmt, ast.Continue):
            raise _Continue
        elif isinstance(stmt, ast.Pass):
            return
        elif isinstance(stmt, ast.Expr):
            if is_print(stmt):
                self.prints += 1
                return
            if isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                return
        raise Unknown(f"{type(stmt).__name__} izlenemiyor")


PARAM_COUNT = {1: "bir", 2: "iki", 3: "üç"}


def find_def(tree, name, count):
    """Üst düzeydeki fonksiyon tanımı: (fonksiyon, None) ya da (None, öğrenciye not)."""
    funcs = [s for s in tree.body if isinstance(s, ast.FunctionDef) and s.name == name]
    if not funcs:
        return None, f"<code>{name}</code> adında bir fonksiyon tanımlanmamış (<code>def {name}(...):</code>)."
    func = funcs[-1]
    params = function_params(func)
    if params is None or len(params) != count:
        return None, f"Fonksiyon tam olarak {PARAM_COUNT[count]} parametre almalı."
    return func, None


def return_note(func):
    """Fonksiyonda return yoksa öğrenciye not; varsa None."""
    if function_returns(func):
        return None
    if find_prints(func):
        return "Fonksiyon sonucu <code>print</code> ile yazdırmak yerine <code>return</code> ile döndürmeli."
    return "Fonksiyonda <code>return</code> yok; sonucu <code>return</code> ile döndürmelisin."


def loops_note(func):
    """for döngülerinde break/continue/return ya da döngü değişkenine atama varsa öğrenciye not."""
    for loop in find_loops(func):
        note = loop_problems(loop)
        if note:
            return note
    return None


NO_VALUE = ("Bazı durumlarda fonksiyon hiçbir değer döndürmüyor (None). Her durumda bir <code>return</code> satırı "
            "çalışmalı.")
BOOL_TRIALS = (4, 7, 0, -3, 10, 15, -6, 1, 25, -10, 13, 30)


@checker("bool_func")
def check_bool_func(tree, p):
    """Tek parametreli, verilen yüklemi (BOOL_PREDS) True/False olarak döndüren fonksiyon."""
    name = p["name"]
    want = BOOL_PREDS[p["pred"]][3]
    func, note = find_def(tree, name, 1)
    note = note or return_note(func)
    if note:
        return False, note
    sim = FuncSim(func)
    for v in BOOL_TRIALS:
        got = sim.call(v)
        if got is None:
            return False, NO_VALUE
        if not isinstance(got, bool):
            return False, "Fonksiyon True ya da False döndürmeli; 0/1 ya da metin değil."
        if got != want(v):
            return False, f"Fonksiyon <code>{name}({v})</code> için yanlış sonuç döndürüyor; koşulu kontrol et."
    return True, OK


MEAN_TRIALS = ([70, 80, 90], [5], [1, 2], [3, 4, 8], [-2, 2, 6, 1])


@checker("mean_func")
def check_mean_func(tree, p):
    """Liste alıp ortalamasını döndüren fonksiyon (sum/len, döngüyle toplama, sayaç, indeksle gezme)."""
    name = p["name"]
    func, note = find_def(tree, name, 1)
    note = note or return_note(func) or loops_note(func)
    if note:
        return False, note
    if any(isinstance(n, ast.FloorDiv) for n in ast.walk(func)):
        return False, "<code>//</code> kesir kısmını atar; ortalama için <code>/</code> kullan."
    sim = FuncSim(func)
    for nums in MEAN_TRIALS:
        got = sim.call(list(nums))
        if got is None:
            return False, NO_VALUE
        if isinstance(got, bool) or not same_value(got, sum(nums) / len(nums)):
            return False, ("Fonksiyonun döndürdüğü değer ortalama değil; toplamı ve eleman sayısını nasıl bulduğunu "
                           "kontrol et.")
    return True, OK


@checker("factorial")
def check_factorial(tree, p):
    """n! döndüren fonksiyon: döngüyle (for/while) ya da özyinelemeyle. method: None, "dongu", "ozyineleme".
    Özyineleme tümevarımla denetlenir: daha küçük n için doğru sonuç varsayılır, durma koşulu ayrıca denenir."""
    name, method = p["name"], p.get("method")
    if any((isinstance(n, ast.Attribute) and n.attr == "factorial") or (isinstance(n, ast.Name) and n.id == "factorial")
           or (isinstance(n, ast.alias) and n.name == "factorial") for n in ast.walk(tree)):
        return False, "Fonksiyonu kendin yaz; hazır <code>math.factorial</code> fonksiyonunu kullanma."
    func, note = find_def(tree, name, 1)
    note = note or return_note(func) or loops_note(func)
    if note:
        return False, note
    recursive = any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == name
                    for n in ast.walk(func))
    has_loop = bool(find_loops(func) or find_loops(func, ast.While))
    if method == "ozyineleme" and not recursive:
        return False, "Soru fonksiyonu özyinelemeyle (kendini çağırarak) yazmanı istiyor."
    if method == "dongu" and (recursive or not has_loop):
        return False, "Soru döngü kullanmanı istiyor; fonksiyonu for ya da while ile, kendini çağırmadan yaz."
    current = [0]

    def assumed(args):
        """Tümevarım: daha küçük (ve negatif olmayan) bir n için fonksiyonun doğru sonuç verdiği varsayılır."""
        if len(args) != 1 or not isinstance(args[0], int) or isinstance(args[0], bool):
            raise Unknown("özyineleme argümanı")
        if not 0 <= args[0] < current[0]:
            raise NoBase("küçülmüyor")
        return math.factorial(args[0])

    sim = FuncSim(func, self_call=assumed)
    for k in (0, 1, 2, 3, 5, 7):
        current[0] = k
        try:
            got = sim.call(k)
        except NoBase:
            return False, ("Fonksiyon kendini çağırırken sayı küçülerek durma koşuluna ulaşmıyor; durma koşulunu ve "
                           "çağrıdaki değeri kontrol et.")
        except Endless:
            return False, "Döngü bitmiyor gibi görünüyor; döngü koşulundaki değişkenin değiştiğini kontrol et."
        if got is None:
            return False, NO_VALUE
        if isinstance(got, bool) or not same_value(got, math.factorial(k)):
            return False, (f"<code>{name}({k})</code> {math.factorial(k)} döndürmeli; başlangıç değerini ve döngü "
                           "sınırlarını (ya da durma koşulunu) kontrol et.")
    return True, OK
