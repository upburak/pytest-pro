"""Ünite 9 - Fonksiyonlar ve Modüller."""
import math
import random

from ..helpers import PEOPLE, Wrong, err, output_question, tf_question
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
        wrongs=[
            Wrong(str((a + b) * 2), "İşlem önceliği: önce x * 2 hesaplanır, sonra y eklenir."),
            Wrong(str(b * 2 + a), f"Argümanlar sırayla eşleşir: x = {a}, y = {b}."),
            Wrong("None", "Fonksiyon return ile bir değer döndürüyor; None değil."),
        ],
        hint="Çağrıdaki değerler hangi parametrelere gider? Sonra return satırını hesapla.",
    )


@q("Varsayılan Parametre", verify="output")
def default_param():
    base = random.randint(2, 5)
    other = random.randint(3, 4)
    if random.random() < 0.5:
        call, res = f"us({base})", base ** 2
        why = "Kuvvet verilmediği için varsayılan değer (2) kullanılır"
        wrongs = [Wrong(str(base), "Kuvvet verilmeyince varsayılan değer 2 kullanılır; 1 ya da 0 değil."),
                  Wrong(err("TypeError"), "Varsayılanı olan parametre çağrıda verilmeyebilir; hata oluşmaz.")]
    else:
        call, res = f"us({base}, {other})", base ** other
        why = f"Kuvvet açıkça {other} verildiği için varsayılan değer kullanılmaz"
        wrongs = [Wrong(str(base ** 2), "Açıkça verilen değer, varsayılanın yerine geçer."),
                  Wrong(err("TypeError"), "Fonksiyon iki parametre alıyor; iki argüman vermek geçerlidir.")]
    wrongs.insert(0, Wrong(str(base * 2), "** üs almadır, 2 ile çarpma değil."))
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
    x, y = random.sample(range(1, 20), 2)
    return output_question(
        f"x = {x}\n\ndef degistir():\n    x = {y}\n    return x\n\ndegistir()\nprint(x)", str(x),
        f"Fonksiyon içindeki <code>x = {y}</code> yeni bir <strong>yerel</strong> değişken oluşturur; dışarıdaki "
        f"(global) x değişmez ve {x} kalır.",
        wrongs=[
            Wrong(str(y), "Fonksiyon içindeki x yerel bir değişkendir; dışarıdaki x'i değiştirmez."),
            Wrong("None", "print(x) dışarıdaki x'i yazar; fonksiyonun dönüş değerini değil."),
            Wrong(err("NameError"), "x dışarıda tanımlı; hata oluşmaz."),
        ],
        hint="Fonksiyon içindeki x ile dışarıdaki x aynı değişken mi?",
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
        wrongs=[
            Wrong(str(lo - hi), "k küçük, b büyük değeri alır; b - k pozitiftir."),
            Wrong(str(hi + lo), "Kod iki değerin farkını yazdırıyor, toplamını değil."),
            Wrong(err("TypeError"), "return a, b bir demet döndürür; iki değişkene açılabilir."),
        ],
        hint="Fonksiyon hangi iki değeri hangi sırayla döndürür? k ve b neye eşit olur?",
    )


@q("Özyineleme", verify="output")
def recursion():
    n = random.randint(3, 8)
    if random.random() < 0.5:
        return output_question(
            f"def faktoriyel(n):\n    if n <= 1:\n        return 1\n    return n * faktoriyel(n - 1)\n\n"
            f"print(faktoriyel({n}))", str(math.factorial(n)),
            f"Fonksiyon kendini n - 1 ile çağırır ve n <= 1 olunca durur: {n}! = "
            + " × ".join(str(i) for i in range(n, 0, -1)) + f" = {math.factorial(n)}.",
            wrongs=[
                Wrong(str(math.factorial(n - 1)), f"faktoriyel({n}) {n}'den 1'e kadar tüm sayıların çarpımıdır; {n} de "
                                                  "dahil."),
                Wrong(str(n * (n + 1) // 2), "Bu toplama; fonksiyon sayıları çarpıyor."),
                Wrong(str(math.factorial(n + 1)), f"Çağrı {n} ile başlar ve küçülerek 1'e iner; {n + 1} hiç çarpılmaz."),
            ],
            hint="faktoriyel(n), n * faktoriyel(n - 1) demektir. n = 1'e inene kadar aç.",
        )
    return output_question(
        f"def topla(n):\n    if n == 0:\n        return 0\n    return n + topla(n - 1)\n\nprint(topla({n}))",
        str(n * (n + 1) // 2),
        f"topla({n}) = {n} + topla({n - 1}) = ... = {n * (n + 1) // 2}. n == 0 durma koşuludur.",
        wrongs=[
            Wrong(str(n * (n - 1) // 2), f"topla({n}) {n}'i de toplar; {n} + {n - 1} + ... + 1."),
            Wrong(str(math.factorial(n)), "Bu çarpım; fonksiyon sayıları topluyor."),
            Wrong(str(n), "Fonksiyon kendini çağırarak 0'a kadar tüm sayıları ekler."),
        ],
        hint="topla(n), n + topla(n - 1) demektir. n = 0'a inene kadar aç.",
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
                  Wrong(str(x / 2), "Karekök, sayının yarısı değildir.")]
    elif variant == "ceil":
        code, res = f"import math\nprint(math.ceil({y}))", str(math.ceil(y))
        why = "math.ceil() yukarı yuvarlar"
        wrongs = [Wrong(str(math.floor(y)), "ceil her zaman yukarı yuvarlar; aşağı yuvarlayan floor'dur."),
                  Wrong(str(y), "ceil kesirli kısmı atıp tam sayıya yuvarlar.")]
    elif variant == "floor":
        code, res = f"import math\nprint(math.floor({y}))", str(math.floor(y))
        why = "math.floor() aşağı yuvarlar"
        wrongs = [Wrong(str(math.ceil(y)), "floor her zaman aşağı yuvarlar; yukarı yuvarlayan ceil'dir."),
                  Wrong(str(y), "floor kesirli kısmı atıp tam sayıya yuvarlar.")]
    else:
        digits = random.choice([2, 3])
        code, res = f"from math import pi\nprint(round(pi, {digits}))", str(round(math.pi, digits))
        why = f"round(sayı, {digits}) virgülden sonra {digits} basamağa yuvarlar"
        wrongs = [Wrong(str(round(math.pi, 5 - digits)), f"round'un ikinci parametresi basamak sayısıdır: {digits}."),
                  Wrong("3", "İkinci parametre verildiği için tam sayıya değil, ondalık basamaklara yuvarlanır.")]
    wrongs.append(Wrong(err("NameError"), "Modül ya da ad içe aktarıldığı için tanımlıdır; hata oluşmaz."))
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
