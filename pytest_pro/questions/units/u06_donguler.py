"""Ünite 6 - Döngüler."""
import random

from ..helpers import Wrong, fill_question, output_question
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
    s = random.choice([2, 3])
    form = random.choice([f"{b}", f"{a}, {b}", f"{a}, {b}, {s}"])
    near = list(eval(f"range({form})"))  # noqa: S307 - yalnızca bizim ürettiğimiz sabit ifade
    start, step = (0, 1) if "," not in form else (a, s if form.count(",") == 2 else 1)
    wrongs = []
    if step == 1:
        wrongs.append(Wrong(str(near + [b]), "Bitiş değerini de dahil ettin; range bitiş değerini üretmez."))
    else:
        if (b - start) % step == 0:  # bitiş adımlarla tam yakalanıyor: onu eklemek bitişi dahil etmektir (Y5)
            wrongs.append(Wrong(str(near + [b]), f"Bitiş değerini ({b}) de dahil ettin; range bitiş değerini üretmez."))
        wrongs.append(Wrong(str(list(range(start, b))), f"Üçüncü parametre ({step}) adımdır; sayılar {step}'er {step}'er "
                                                        "artar."))
    wrongs.append(Wrong(str(near[1:]), "Başlangıç değeri dahildir; liste onunla başlar."))
    wrongs.append(Wrong(str([x + 1 for x in near]), "Tek parametreli range 0'dan başlar; her değeri 1 kaydırdın."
                        if "," not in form else "Değerler başlangıçtan başlar, 1 fazlasından değil."))
    return output_question(
        f"print(list(range({form})))", str(near),
        "<code>range(başlangıç, bitiş, adım)</code>: başlangıç dahil, <strong>bitiş dahil değildir</strong>. "
        "Tek parametre verilirse başlangıç 0, adım verilmezse 1 kabul edilir.",
        wrongs=wrongs,
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
        stop = random.randint(3, n - 2)  # stop = n - 1 iken "continue sandın" şıkkı doğru cevaba eşit olur
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
    a, b = random.sample(range(2, 8), 2)  # a ≠ b: aksi hâlde "a" ve "b" şıkları aynı olur (Y1)
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
    a = random.randint(4, 8)  # a = 3 iken toplam (0 + 1 + 2) a'ya eşit olur
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


LOOP_WORDS = ["bilgisayar", "programlama", "Antalya", "Ankara", "kelebek", "karakalem", "anahtar", "tencere",
              "papatya", "çekirdek", "öğretmen", "Kastamonu", "matematik", "Edirne", "kitaplık"]
VOWELS = "aeıioöuü"


@q("Metin Üzerinde Döngü", verify="output")
def loop_string():
    """Sayılan harf, harfin metinde geçme sayısıyla ağırlıklı seçilir; ayrıca sesli harf sayımı değişkesi
    vardır. Böylece doğru cevap 1'e yığılmaz (K4)."""
    word = random.choice(LOOP_WORDS)
    var = random.choice(["sayac", "adet", "toplam"])
    if random.random() < 0.4:
        count = sum(ch in VOWELS for ch in word)
        upper_vowels = sum(ch.lower() in VOWELS and ch not in VOWELS for ch in word)
        code = (f'metin = "{word}"\n{var} = 0\nfor harf in metin:\n    if harf in "{VOWELS}":\n'
                f"        {var} += 1\nprint({var})")
        expl = (f"Döngü her karakteri <code>harf</code> değişkenine verir; harf \"{VOWELS}\" içindeyse {var} 1 artar. "
                f"\"{word}\" içinde {count} küçük sesli harf vardır.")
        wrongs = [Wrong(str(len(word) - count), "Sesli harfleri değil, sessizleri saydın; koşul harfin "
                                                f"\"{VOWELS}\" içinde olmasıdır.")]
        if upper_vowels:
            wrongs.append(Wrong(str(count + upper_vowels), "Büyük harfle yazılan sesli harf \"aeıioöuü\" içinde yoktur; "
                                                           "in büyük/küçük harfe duyarlıdır."))
        wrongs += [Wrong(str(len(word)), f"{var} her karakterde değil, yalnızca koşul sağlanınca artar."),
                   Wrong(str(count - 1), "Sesli harfleri tek tek yeniden say; ilk harf de döngüye girer."),
                   Wrong(str(count + 1), f"{var} 0'dan başlar; yalnızca sesli harflerde 1 artar.")]
        hint = "Metindeki her harf için koşulun doğru olup olmadığına bak; kaç kez doğru oluyor?"
    else:
        letters = sorted(set(word))
        weights = [word.count(ch) ** 2 for ch in letters]
        letter = random.choices(letters, weights=weights)[0]
        count = word.count(letter)
        code = (f'metin = "{word}"\n{var} = 0\nfor harf in metin:\n    if harf == "{letter}":\n        {var} += 1\n'
                f"print({var})")
        expl = (f"for döngüsü metnin her karakterini sırayla <code>harf</code> değişkenine verir. "
                f"\"{letter}\" harfi \"{word}\" içinde {count} kez geçer.")
        wrongs = []
        other_case = letter.upper() if letter.islower() else letter.lower()
        if other_case in word:
            wrongs.append(Wrong(str(count + word.count(other_case)), "Büyük ve küçük harf farklı karakterlerdir; == "
                                                                     "yalnızca aynısını sayar."))
        wrongs += [Wrong(str(len(word)), f"{var} her karakterde değil, yalnızca harf eşleşince artar."),
                   Wrong(str(count + 1), f"{var} 0'dan başlar ve yalnızca eşleşen her harfte 1 artar."),
                   Wrong(str(count - 1) if count > 1 else "0", "Döngü metnin ilk karakterinden başlar; eşleşmeleri tek "
                                                               "tek, ilki de dahil say.")]
        hint = f"Metindeki her harfi sırayla \"{letter}\" ile karşılaştır."
    return output_question(code, str(count), expl, wrongs=wrongs, hint=hint)


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


@q("range() ile Döngü (Boşluk Doldurma)", verify="fill")
def fill_range_loop():
    var = random.choice(["i", "sayi", "x", "n"])
    step = random.choice([1, 1, 2, 3])
    start = random.randint(0, 6)
    nums = [start + k * step for k in range(random.randint(3, 6))]
    last = nums[-1]
    stops = [str(last + d) for d in range(1, step + 1)]  # son sayıdan büyük, bir sonrakinden küçük her bitiş olur
    step_part = f", {step}" if step > 1 else ""
    if step == 1:
        stop_note = f"bitiş dahil olmadığı için son sayının bir fazlası, yani {stops[0]} yazılır."
    else:
        stop_note = (f"bitiş dahil olmadığı için {last} sayısından büyük, {last + step} sayısından küçük ya da ona "
                     f"eşit bir bitiş gerekir ({' veya '.join(stops)}).")
    return fill_question(
        f"for {var} in ____(____, ____{step_part}):\n    print({var})",
        [["range"], [str(start)], stops],
        "\n".join(map(str, nums)),
        f"Aşağıdaki kod ekrana <code>{', '.join(map(str, nums))}</code> sayılarını alt alta (her satıra bir sayı) "
        "yazdırmalı. Boşlukları doldurun.",
        f"<code>range(başlangıç, bitiş{', adım' if step > 1 else ''})</code> başlangıcı dahil eder, bitişi dahil "
        f"etmez. İlk sayı {start} olduğu için başlangıç {start}; {stop_note}",
        hint="Döngünün sayacağı sayıları üreten hazır fonksiyonu düşün. Bitiş değeri üretilen sayılara dahil mi?",
    )
