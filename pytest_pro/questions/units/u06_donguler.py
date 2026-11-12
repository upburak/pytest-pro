"""Ünite 6 - Döngüler."""
import random

from ..helpers import Wrong, output_question
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
    near = list(eval(f"range({form})"))  # noqa: S307 - yalnızca bizim ürettiğimiz sabit ifade
    step = s if form.count(",") == 2 else 1
    return output_question(
        f"print(list(range({form})))", str(near),
        "<code>range(başlangıç, bitiş, adım)</code>: başlangıç dahil, <strong>bitiş dahil değildir</strong>. "
        "Tek parametre verilirse başlangıç 0, adım verilmezse 1 kabul edilir.",
        wrongs=[
            Wrong(str(near + [near[-1] + step]), "Bitiş değerini de dahil ettin; range bitiş değerini üretmez."),
            Wrong(str(near[1:]), "Başlangıç değeri dahildir; liste onunla başlar."),
            Wrong(str([x + 1 for x in near]), "Tek parametreli range 0'dan başlar; her değeri 1 kaydırdın."
                  if "," not in form else "Değerler başlangıçtan başlar, 1 fazlasından değil."),
        ],
        hint="range başlangıcı dahil eder mi, bitişi dahil eder mi? Parametre sayısı neyi değiştirir?",
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
        common_wrongs=[
            Wrong(str(total - n), f"range({start}, {n + 1}) son değer olarak {n}'i de üretir; bitiş ({n + 1}) "
                                  "hariçtir ama ondan önceki sayı dahildir."),
            Wrong(str(total + n + 1), f"Bitiş değeri {n + 1} dahil değildir."),
        ],
        hint="i hangi değerleri alır? İlkini ve sonuncusunu yaz, sonra topla.",
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
    one_less = f"Koşul her turdan önce kontrol edilir; x < {limit} hâlâ doğruyken bir tur daha çalışır."
    one_more = f"x, {limit} değerine ulaşınca ya da geçince koşul yanlış olur ve döngü hemen biter."
    return output_question(
        f"x = {x}\nadim = 0\nwhile x < {limit}:\n    x *= {k}\n    adim += 1\nprint(x, adim)", f"{v} {count}",
        f"Koşul (x < {limit}) her turdan önce kontrol edilir. x değerleri {x}'den başlayıp {k} ile çarpılarak "
        f"{v} olunca döngü biter; döngü {count} kez çalışır.",
        wrongs=[Wrong(f"{v // k} {count - 1}", one_less), Wrong(f"{v} {count + 1}", one_more),
                Wrong(f"{v * k} {count + 1}", one_more)],
        hint="Her turdan önce koşulu kontrol et ve x ile adim değerlerini bir tabloya yaz.",
    )


@q("break ve continue", verify="output")
def break_continue():
    n = random.randint(6, 9)
    if random.random() < 0.5:
        stop = random.randint(3, n - 1)
        out = [str(i) for i in range(1, n) if i < stop]
        code = f"for i in range(1, {n}):\n    if i == {stop}:\n        break\n    print(i, end=\" \")"
        why = f"<code>break</code> döngüyü tamamen sonlandırır; i = {stop} olduğunda döngüden çıkılır."
        wrongs = [
            Wrong(" ".join(out + [str(stop)]), f"break, print'ten önce çalışır; i = {stop} yazdırılmadan çıkılır."),
            Wrong(" ".join(str(i) for i in range(1, n) if i != stop),
                  "break döngüyü tamamen bitirir; continue gibi yalnızca o turu atlamaz."),
            Wrong(" ".join(out[:-1]), f"i = {stop} olana kadar her tur yazdırılır."),
        ]
        hint = "break çalıştığında döngüye ne olur? i'nin hangi değerinde çalışıyor?"
    else:
        skip = random.randint(2, n - 2)
        out = [str(i) for i in range(1, n) if i != skip]
        code = f"for i in range(1, {n}):\n    if i == {skip}:\n        continue\n    print(i, end=\" \")"
        why = f"<code>continue</code> yalnızca o turu atlar; i = {skip} yazdırılmaz ama döngü devam eder."
        wrongs = [
            Wrong(" ".join(str(i) for i in range(1, skip)), "continue döngüyü bitirmez; yalnızca o turu atlar."),
            Wrong(" ".join(str(i) for i in range(1, n)), f"continue, i = {skip} olduğunda print'e ulaşmadan sonraki "
                                                         "tura geçer."),
            Wrong(" ".join(str(i) for i in range(1, n + 1) if i != skip), f"range(1, {n}) bitiş değerini ({n}) "
                                                                         "üretmez."),
        ]
        hint = "continue çalıştığında o turun geri kalanına ne olur? Döngü bitiyor mu?"
    res = " ".join(out) + " "
    return output_question(code, res, why, wrongs=[Wrong(w.value + " ", w.why) for w in wrongs], hint=hint)


@q("İç İçe Döngüler", verify="output")
def nested():
    a, b = random.randint(2, 6), random.randint(2, 6)
    if random.random() < 0.5:
        return output_question(
            f"sayac = 0\nfor i in range({a}):\n    for j in range({b}):\n        sayac += 1\nprint(sayac)", str(a * b),
            f"Dış döngü {a} kez döner; her turda iç döngü {b} kez çalışır. Toplam {a} × {b} = {a * b} tekrar.",
            wrongs=[
                Wrong(str(a + b), "İç döngü dış döngünün HER turunda baştan çalışır; tekrarlar toplanmaz, çarpılır."),
                Wrong(str(a), "İç döngüyü de saymalısın; sayac en içte artıyor."),
                Wrong(str(b), "İç döngü yalnızca bir kez değil, dış döngünün her turunda çalışır."),
            ],
            hint="Dış döngünün her turunda iç döngü kaç kez çalışır?",
        )
    total = a * (a - 1) // 2
    return output_question(
        f"sayac = 0\nfor i in range({a}):\n    for j in range(i):\n        sayac += 1\nprint(sayac)", str(total),
        f"İç döngü range(i) kadar döner: i = 0, 1, ..., {a - 1} için 0 + 1 + ... + {a - 1} = {total}.",
        wrongs=[
            Wrong(str(a * a), "İç döngünün tur sayısı sabit değil; range(i) her dış turda i kadar döner."),
            Wrong(str(total + a), f"range(i), i'yi dahil etmez; i = {a - 1} iken iç döngü {a - 1} kez döner."),
            Wrong(str(a), "İç döngüyü de saymalısın; sayac en içte artıyor."),
        ],
        hint="i'nin her değeri için iç döngü kaç kez çalışır? Bunları topla.",
    )


@q("Metin Üzerinde Döngü", verify="output")
def loop_string():
    word = random.choice(["Python", "kalem", "Ankara", "bilgisayar", "programlama", "elma", "Antalya"])
    letter = random.choice(sorted(set(word)))
    count = word.count(letter)
    return output_question(
        f'metin = "{word}"\nsayac = 0\nfor harf in metin:\n    if harf == "{letter}":\n        sayac += 1\nprint(sayac)',
        str(count),
        f"for döngüsü metnin her karakterini sırayla <code>harf</code> değişkenine verir. "
        f"\"{letter}\" harfi \"{word}\" içinde {count} kez geçer.",
        wrongs=[
            Wrong(str(count + 1), "sayac 0'dan başlar ve yalnızca eşleşen her harfte 1 artar."),
            Wrong(str(len(word)), "sayac her karakterde değil, yalnızca harf eşleşince artar."),
            Wrong("0" if count else "1", "for döngüsü metnin her karakterini dolaşır; eşleşmeleri tek tek say. "
                                         "Büyük/küçük harfe dikkat et."),
        ],
        hint=f"Metindeki her harfi sırayla \"{letter}\" ile karşılaştır.",
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
        "hint": "range() bitiş değerini dahil etmez; bitişe ne yazman gerektiğini düşün.",
        "solution": f"<code>range(1, {n + 1})</code> 1'den {n}'e kadar sayıları üretir; bitiş değeri dahil "
                    "olmadığı için bir fazlası yazılır.",
    }
