"""Ünite 6 - Döngüler."""
import ast
import random
import re

from ..codecheck import OK, checker, find_loops, find_prints, loop_problems, same_value
from ..helpers import LOOP_OUTCOME, Wrong, code_options_question, e, fill_question, output_question, tf_claim
from ..registry import register_unit
from .u05_kosullar import calls_name, given_ok, has_node, sim_run, top_assigns

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


# ================================================================= kod yazma denetleyicileri
NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")


def _numbers(line):
    return [float(x) if "." in x else int(x) for x in NUM_RE.findall(line)]


def _loop_checks(tree):
    """Döngü yok ya da for döngüsünde break/continue/döngü değişkenine atama varsa öğrenciye not; yoksa None."""
    if not (has_node(tree, ast.For) or has_node(tree, ast.While)):
        return "Soru döngü kullanmanı istiyor; işlemi bir <code>for</code> ya da <code>while</code> döngüsüyle tekrarla."
    for loop in find_loops(tree):
        problem = loop_problems(loop)
        if problem:
            return problem
    return None


def _only_given(var, n, value, want):
    return (f"Kodun yalnızca <code>{var} = {n}</code> için doğru sonuç veriyor; <code>{var} = {value}</code> olsaydı "
            f"{want} yazmalıydı. Hesabı {var} değişkenini kullanarak kur, sayıyı elle yazma.")


@checker("dongu_toplam")
def check_sum_loop(tree, p):
    """`var = n` ile başlayan, döngüyle 1 + 2 + ... + n toplamını bulup tek satırda yazdıran kod."""
    var, n, kind = p["var"], p["n"], p.get("loop")
    if not top_assigns(tree, var):
        return False, f"Kod <code>{var} = {n}</code> satırıyla başlamalı."
    if calls_name(tree, "sum"):
        return False, "Soru döngü kullanmanı istiyor; <code>sum()</code> yerine toplamı döngüde adım adım biriktir."
    problem = _loop_checks(tree)
    if problem:
        return False, problem
    if kind == "for" and not has_node(tree, ast.For):
        return False, "Soru bu toplamı <code>for</code> döngüsüyle yazmanı istiyor."
    if kind == "while" and not has_node(tree, ast.While):
        return False, "Soru bu toplamı <code>while</code> döngüsüyle yazmanı istiyor."
    for k, value in enumerate((n, 1, 7, 12)):
        sim, note = sim_run(tree, {var: value})
        if k == 0 and not given_ok(sim, var, n):
            return False, f"Kod <code>{var} = {n}</code> satırıyla başlamalı; {var} değişkenine bu değeri ata."
        if note:
            return False, f"<code>{var} = {value}</code> olsaydı kod {note}."
        lines = sim.lines()
        want = value * (value + 1) // 2
        if not lines:
            return False, "Ekrana hiçbir şey yazılmıyor; döngüden sonra toplamı <code>print</code> ile yazdır."
        got = _numbers(lines[-1])[-1:] or [None]
        if len(lines) > 1:
            if same_value(got[0], want):
                return False, ("Ara toplamlar da yazdırılıyor; yalnızca sonucu yazdır (print'i döngünün içine değil, "
                               "sonrasına yaz).")
            return False, "Ekrana yalnızca bir satır, yani toplam yazılmalı."
        got = got[0]
        if same_value(got, want):
            continue
        if k > 0:
            return False, _only_given(var, n, value, want)
        if same_value(got, want - value):
            return False, f"Toplama {var} dahil edilmiyor; <code>range()</code> bitiş değerinin dahil olmadığını unutma."
        if same_value(got, value):
            return False, ("Toplam değişkeni her turda üzerine yazılıyor; önceki toplamı koruyarak ekle "
                           "(<code>toplam += i</code>).")
        return False, f"<code>{var} = {value}</code> için toplam {want} olmalı; döngünün sınırlarını ve eklenen değeri kontrol et."
    return True, OK


@checker("dongu_carpim")
def check_times_table(tree, p):
    """`var = n` ile başlayan, n x 1 = n ... n x stop satırlarını döngüyle alt alta yazdıran kod."""
    var, n, stop = p["var"], p["n"], p["stop"]
    if not top_assigns(tree, var):
        return False, f"Kod <code>{var} = {n}</code> satırıyla başlamalı."
    problem = _loop_checks(tree)
    if problem:
        return False, problem
    for call in find_prints(tree):
        if any(kw.arg == "end" for kw in call.keywords):
            return False, "Her işlem ayrı bir satıra, alt alta yazılmalı; print'te <code>end</code> kullanma."
    for k, value in enumerate((n, 3, 9)):
        sim, note = sim_run(tree, {var: value})
        if k == 0 and not given_ok(sim, var, n):
            return False, f"Kod <code>{var} = {n}</code> satırıyla başlamalı; {var} değişkenine bu değeri ata."
        if note:
            return False, f"<code>{var} = {value}</code> olsaydı kod {note}."
        lines = sim.lines()
        if len(lines) != stop:
            return False, (f"Çarpan 1 ile {stop} arasındaki her sayı için bir satır, toplam {stop} satır yazılmalı; kod "
                           f"{len(lines)} satır yazıyor. <code>range()</code> sınırlarını kontrol et.")
        for i, line in enumerate(lines, start=1):
            nums = _numbers(line)
            want = [value, i, value * i]
            if len(nums) != 3:
                return False, (f"Her satırda üç sayı olmalı: {var}, çarpan ve sonuç (ör. <code>{n} x 2 = {n * 2}</code>). "
                               f"{i}. satırda {len(nums)} sayı var.")
            if all(same_value(a, b) for a, b in zip(nums, want)):
                continue
            if k > 0:
                return False, _only_given(var, n, value, f"<code>{value} x {i} = {value * i}</code>")
            if all(same_value(a, b) for a, b in zip(nums[:2], want[:2])):
                return False, f"{i}. satırdaki sonuç yanlış; {var} ile çarpanı çarp."
            return False, (f"{i}. satır <code>{n} x {i} = {n * i}</code> olmalı; sayılar sırasıyla {var}, çarpan ve sonuç "
                           "olmalı.")
    return True, OK


# ================================================================= yeni şablonlar (ölçme raporu Ö6.1-Ö6.8)
@q("Kaç Tur? (Doğru / Yanlış)", verify="tf_output")
def loop_count_claim():
    """Kazanım: range ya da while ile kurulan döngünün tur sayısını hesaplar · Bloom: U"""
    var = random.choice(["tur", "sayac", "adet"])
    kind = random.choice(["up", "up", "down", "while"])
    if kind == "up":
        a, s = random.randint(0, 5), random.randint(1, 4)
        b = a + random.randint(5, 16)
        args = f"{a}, {b}" if s == 1 else f"{a}, {b}, {s}"
        if s == 1 and a == 0 and random.random() < 0.5:
            args = f"{b}"
        values = list(range(a, b, s))
        head = f"for i in range({args}):"
        detail = f"Döngü değişkeni i sırasıyla {', '.join(map(str, values))} değerlerini alır; bitiş ({b}) dahil değildir"
    elif kind == "down":
        b, s = random.randint(0, 4), random.randint(1, 3)
        a = b + random.randint(5, 14)
        values = list(range(a, b, -s))
        head = f"for i in range({a}, {b}, -{s}):"
        detail = f"Döngü değişkeni i sırasıyla {', '.join(map(str, values))} değerlerini alır; adım negatif, bitiş ({b}) dahil değildir"
    else:
        a, s = random.randint(0, 5), random.randint(1, 3)
        b = a + random.randint(5, 14)
        op = random.choice(["<", "<="])
        values = list(range(a, b + (op == "<="), s))
        head = f"i = {a}\nwhile i {op} {b}:"
        detail = (f"Koşul her turdan önce denenir; i sırasıyla {', '.join(map(str, values))} iken döngü çalışır")
    count = len(values)
    if kind == "while":
        code = f"{var} = 0\n{head}\n    {var} += 1\n    i += {s}\nprint({var})"
    else:
        code = f"{var} = 0\n{head}\n    {var} += 1\nprint({var})"
    wrongs = [Wrong(str(count + 1), "Bitiş değerini de saymış olabilirsin; döngü bitiş değerine ulaşınca durur."
                    if kind != "while" else "Koşul yanlış olduğu anda döngü durur; o tur çalışmaz."),
              Wrong(str(count - 1), "Başlangıç değeri de bir turdur; ilk turu atlamış olabilirsin.")]
    span = abs(b - a)
    if s > 1 and span not in (count, count + 1, count - 1):
        wrongs.append(Wrong(str(span), f"Adım {s}: i her turda {s} değişir; aradaki her sayı bir tur değildir."))
    return tf_claim(code, str(count), wrongs, f"{detail}. Döngü {count} kez döner.",
                    hint="Döngü değişkeninin aldığı değerleri tek tek yaz ve say.")


def _range_forms(seq):
    """seq dizisini üreten bütün range argüman yazımları (kısa olanlar önce)."""
    start, step, last = seq[0], seq[1] - seq[0], seq[-1]
    stops = range(last + 1, last + step + 1) if step > 0 else range(last - 1, last + step - 1, -1)
    forms = []
    for stop in stops:
        if start == 0 and step == 1:
            forms.append(f"{stop}")
        if step == 1:
            forms.append(f"{start}, {stop}")
        forms.append(f"{start}, {stop}, {step}")
    return list(dict.fromkeys(forms))


@q("range'i Tamamla (Boşluk Doldurma)", verify="fill")
def range_blank():
    """Kazanım: istenen sayı dizisini üreten range argümanlarını kurar · Bloom: An"""
    step = random.choice([1, 2, 3, 2, -1, -2])
    k = random.randint(4, 7)
    start = random.randint(0, 5) if step > 0 else random.randint(8, 15)
    seq = [start + i * step for i in range(k)]
    var = random.choice(["i", "x", "sayi"])
    forms = _range_forms(seq)
    last, wrongs = seq[-1], []
    if step > 0:
        wrongs.append(Wrong(f"{start}, {last}, {step}" if step > 1 else f"{start}, {last}",
                            f"Bitiş değeri dahil edilmez; {last} yazdırılmaz."))
    else:
        wrongs.append(Wrong(f"{start}, {last}, {step}", f"Bitiş değeri dahil edilmez; {last} yazdırılmaz."))
        wrongs.append(Wrong(f"{last}, {start + 1}", "Adım verilmezse 1 kabul edilir; sayılar artarak sıralanır, "
                                                     "azalmaz."))
    wrongs.append(Wrong(f"{start + 1}, {last + step + (1 if step > 0 else -1)}, {step}",
                        "Başlangıç değeri dahildir; dizi ilk yazılan sayıdan başlar."))
    if abs(step) > 1:
        wrongs.append(Wrong(f"{start}, {last + (1 if step > 0 else -1)}",
                            f"Adım yazılmazsa sayılar birer birer ilerler; burada her adımda {abs(step)} fark var."))
    shown = " ".join(map(str, seq))
    return fill_question(
        f"for {var} in range(____):\n    print({var}, end=\" \")",
        [forms], shown + " ",
        f"Kod ekrana <code>{shown}</code> sayılarını yan yana yazmalı. <code>range</code> parantezinin içine "
        "gelmesi gereken değerleri virgülle ayırarak yazınız.",
        f"<code>range(başlangıç, bitiş, adım)</code>: başlangıç {start}, adım {step}. Bitiş dahil olmadığı için son "
        f"sayı olan {last} değerinden bir adım ötede durulmalıdır; ör. <code>range({forms[-1]})</code>.",
        hint="İlk sayı, iki sayı arasındaki fark ve bitişin dahil olmadığını düşün.",
        wrongs=[wrongs],
    )


WHILE_OPS = ["<", "<=", "!=", ">", ">=", "=="]


def _while_out(a, op, b, k, limit=60):
    out, x = [], a
    while eval(f"{x} {op} {b}"):  # noqa: S307 - yalnızca bizim ürettiğimiz sabit ifade
        out.append(x)
        x += k
        if len(out) > limit:
            return None  # sonsuz döngü
    return out


@q("while Koşulunu Tamamla (Boşluk Doldurma)", verify="fill")
def while_blank():
    """Kazanım: istenen çıktıya göre while döngüsünün koşulunu kurar · Bloom: An"""
    var = random.choice(["sayac", "i", "x"])
    k = random.choice([1, 1, 2, 3, -1, -2])
    a = random.randint(0, 5) if k > 0 else random.randint(10, 20)
    n = random.randint(3, 6)
    seq = [a + i * k for i in range(n)]
    last = seq[-1]
    b = last if random.random() < 0.4 else (last + k if abs(k) == 1 else last + (1 if k > 0 else -1))
    accepted = [op for op in WHILE_OPS if _while_out(a, op, b, k) == seq]
    whys = []
    for op in WHILE_OPS:
        got = _while_out(a, op, b, k)
        if op in accepted:
            continue
        if got is None:
            why = f"{var} hiçbir zaman {b} olmaz ya da koşul hep doğru kalır; döngü hiç bitmez."
        elif not got:
            why = f"{var} = {a} iken koşul yanlış; döngü hiç çalışmaz."
        elif len(got) < n:
            why = f"Döngü {last} yazılmadan durur; {var} = {last} iken koşul da doğru olmalı."
        else:
            why = f"Döngü {last} değerinden sonra da devam eder; fazladan değer yazılır."
        whys.append(Wrong(op, why))
    sign = "+=" if k > 0 else "-="
    return fill_question(
        f"{var} = {a}\nwhile {var} ____ {b}:\n    print({var})\n    {var} {sign} {abs(k)}",
        [accepted], "\n".join(map(str, seq)),
        f"Kod ekrana <code>{', '.join(map(str, seq))}</code> sayılarını alt alta yazmalı. Boşluğa gelmesi gereken "
        "karşılaştırma işlecini yazınız.",
        f"Koşul her turdan önce denenir. {var} = {last} iken döngü bir kez daha çalışmalı, {last + k} olunca durmalı; "
        f"bunu <code>{e(' ya da '.join(accepted))}</code> sağlar.",
        hint=f"{var} = {last} iken döngü bir kez daha çalışmalı mı? Bir sonraki değerde ne olmalı?",
        wrongs=[whys],
    )


@q("Koşullu Toplam", verify="output")
def cond_sum():
    """Kazanım: döngü içinde koşula göre biriktirme ya da sayma yapar · Bloom: U"""
    end = random.randint(8, 20)
    d = random.randint(2, 5)
    count_mode = random.random() < 0.35
    var = random.choice(["toplam", "sonuc", "t"]) if not count_mode else random.choice(["adet", "sayac"])
    start = random.choice([0, 1])
    picked = [i for i in range(start, end + 1) if i % d == 0]
    res = len(picked) if count_mode else sum(picked)
    body = f"{var} += 1" if count_mode else f"{var} += i"
    code = f"{var} = 0\nfor i in range({start}, {end + 1}):\n    if i % {d} == 0:\n        {body}\nprint({var})"
    no_end = [i for i in picked if i != end]
    common = [Wrong(str(len(no_end) if count_mode else sum(no_end)),
                    f"range({start}, {end + 1}) {end} değerini de üretir; bitiş ({end + 1}) hariçtir ama ondan önceki sayı "
                    "dahildir.") if end % d == 0 else None,
              Wrong(str(sum(range(start, end + 1)) if not count_mode else end + 1 - start),
                    f"Yalnızca {d} ile tam bölünen i değerleri işlenir; koşulu sağlamayanlar atlanır.")]
    if count_mode:
        common.append(Wrong(str(sum(picked)), f"{var} değişkenine i değil, her seferinde 1 eklenir; kod sayıları toplamıyor, sayıyor."))
    else:
        common.append(Wrong(str(len(picked)), f"{var} değişkenine 1 değil, i eklenir; kod sayıları saymıyor, topluyor."))
    if start == 0 and count_mode:
        common.append(Wrong(str(res - 1), f"0 da <code>0 % {d} == 0</code> koşulunu sağlar; 0 da sayılır."))
    return output_question(
        code, str(res),
        f"Koşulu sağlayan i değerleri: {', '.join(map(str, picked))}. "
        + (f"Her birinde {var} 1 artar: {res}." if count_mode else f"Bunların toplamı {res}."),
        common_wrongs=[w for w in common if w], norm="sayi",
        hint="Önce koşulu sağlayan i değerlerini yaz; sonra her birinde değişkene ne eklendiğine bak.",
    )


@q("while True ve break", verify="output")
def sentinel_break():
    """Kazanım: while True döngüsünün break ile nasıl bittiğini izler · Bloom: U"""
    d = random.randint(3, 7)
    x0 = random.randint(15, 40)
    strict = random.random() < 0.5
    op = "<" if strict else "<="
    stop_at = (lambda v: v < 0) if strict else (lambda v: v <= 0)
    variant = random.choice(["value", "value", "count"])
    x, turns = x0, 0
    while True:
        x -= d
        turns += 1
        if stop_at(x):
            break
    if variant == "value":
        code = f"x = {x0}\nwhile True:\n    x -= {d}\n    if x {op} 0:\n        break\nprint(x)"
        res = x
        common = [Wrong(str(x + d), f"x = {x + d} iken koşul (x {e(op)} 0) yanlış; döngü bir tur daha döner."),
                  Wrong(str(x - d), "break çalışınca döngü hemen biter; x bir kez daha azalmaz."),
                  Wrong("0", f"x her turda {d} azalır; 0 değerine tam denk gelmesi gerekmez.")]
        expl = f"x değerleri: {', '.join(str(x0 - d * t) for t in range(1, turns + 1))}. x {e(op)} 0 olunca break çalışır."
        hint = "x'in her turdaki değerini yaz; break hangi değerde çalışıyor?"
    else:
        code = (f"x = {x0}\nadim = 0\nwhile True:\n    x -= {d}\n    adim += 1\n    if x {op} 0:\n        break\n"
                "print(adim)")
        res = turns
        common = [Wrong(str(turns - 1), "break'ten önce adim zaten artırılmıştır; son tur da sayılır."),
                  Wrong(str(turns + 1), "break çalışınca döngü hemen biter; bir tur daha dönmez."),
                  Wrong(str(x0 // d), "Bölme ile tahmin etmek yerine x'in değerlerini tek tek izle.")]
        expl = (f"x değerleri: {', '.join(str(x0 - d * t) for t in range(1, turns + 1))}. Döngü {turns} tur döner; "
                "son turda break çalışır.")
        hint = "Her turda x ve adim değerlerini bir tabloya yaz; break hangi turda çalışıyor?"
    return output_question(code, str(res), expl, common_wrongs=common, norm="sayi", hint=hint)


def _loop_pool(v, n):
    """(kod, sonsuz mu, açıklama) havuzu."""
    m_odd = n if n % 2 else n + 1  # 1'den başlayıp 2'şer artan sayı tek sayılara denk gelir
    m_even = m_odd + 1
    infinite = [
        (f"{v} = 0\nwhile {v} < {n}:\n    print({v})", f"{v} hiç artmıyor; koşul hep doğru kalır."),
        (f"{v} = 0\nwhile {v} < {n}:\n    {v} -= 1", f"{v} azaldıkça {n} değerinden hep küçük kalır; koşul hiç yanlış olmaz."),
        (f"{v} = 0\nj = 0\nwhile {v} < {n}:\n    j += 1", f"Artan değişken j; koşuldaki {v} hiç değişmez."),
        (f"{v} = 1\nwhile {v} != {m_even}:\n    {v} += 2", f"{v} hep tek sayıdır; hiçbir zaman {m_even} olmaz."),
    ]
    finite = [
        (f"{v} = 0\nwhile {v} < {n}:\n    {v} += 1", f"{v} her turda artar; döngü {n} kez döner."),
        (f"{v} = {n}\nwhile {v} > 0:\n    {v} -= 1", f"{v} her turda azalır; döngü {n} kez döner."),
        (f"son = {n}\nfor {v} in range(son):\n    son += 1",
         "range(son) döngü başlarken bir kez hesaplanır; son değişse de tur sayısı değişmez."),
        (f"{v} = 1\nwhile {v} != {m_odd}:\n    {v} += 2", f"{v} tek sayılarla ilerler ve {m_odd} olunca döngü biter."),
        (f"{v} = 0\nwhile True:\n    {v} += 1\n    if {v} == {n}:\n        break", f"{v} = {n} olunca break döngüyü bitirir."),
    ]
    return infinite, finite


@q("Hangi Döngü Hiç Bitmez?", verify="code_one")
def infinite_loop():
    """Kazanım: sonsuz döngüye yol açan hatayı fark eder · Bloom: An"""
    v = random.choice(["i", "sayac", "k"])
    n = random.randint(3, 9)
    infinite, finite = _loop_pool(v, n)
    correct, why_inf = random.choice(infinite)
    wrongs = [Wrong(code, why) for code, why in random.sample(finite, 3)]
    return code_options_question(
        "Aşağıdaki döngülerden hangisi <strong>hiç bitmez</strong> (sonsuz döngü)?",
        correct, wrongs, cases=[{"expect": LOOP_OUTCOME}],
        solution=f"Bir while döngüsünün bitmesi için koşulu yanlış yapacak bir değişiklik gerekir. Doğru seçenekte {why_inf}",
        hint="Her döngüde koşulu eninde sonunda yanlış yapacak bir değişiklik var mı?",
    )


@q("1'den n'e Toplam (Kod Yazma)")
def write_sum_loop():
    """Kazanım: biriktirici değişkenle döngü kurar · Bloom: O"""
    var = random.choice(["n", "sinir", "son"])
    n = random.randint(5, 30)
    kind = random.choice([None, "for", "while"])
    loop_text = {"for": "<code>for</code> döngüsü", "while": "<code>while</code> döngüsü", None: "döngü"}[kind]
    if kind == "while":
        answer = f"{var} = {n}\ntoplam = 0\ni = 1\nwhile i <= {var}:\n    toplam += i\n    i += 1\nprint(toplam)"
    else:
        answer = f"{var} = {n}\ntoplam = 0\nfor i in range(1, {var} + 1):\n    toplam += i\nprint(toplam)"
    return {
        "type": "code",
        "text": f"<code>{var} = {n}</code> satırıyla başlayan ve <strong>{loop_text} kullanarak</strong> 1 ile {var} "
                f"arasındaki ({var} dahil) sayıların toplamını <strong>tek satırda</strong> yazdıran kodu yazınız. "
                f"Örneğin {var} = 4 olsaydı ekrana 10 yazılmalıydı. <code>sum()</code> kullanmayınız.",
        "code": None,
        "check": {"kind": "dongu_toplam", "var": var, "n": n, "loop": kind},
        "answer": answer,
        "hint": "Döngüden önce toplamı 0 yap; her turda sayıyı toplama ekle ve sonucu döngüden sonra yazdır.",
        "solution": "Biriktirici değişken döngüden önce 0 yapılır, her turda o turun sayısı eklenir. "
                    f"<code>range(1, {var} + 1)</code> 1 ile {var} arasındaki sayıları üretir; print döngüden sonra "
                    "yazıldığı için yalnızca sonuç görünür.",
    }


@q("Çarpım Tablosu (Kod Yazma)")
def write_times_table():
    """Kazanım: döngü değişkenini biçimli çıktıda kullanır · Bloom: O"""
    var = random.choice(["n", "sayi", "x"])
    n = random.randint(2, 9)
    stop = random.choice([5, 6, 8, 10])
    sign = random.choice(["x", "*"])
    return {
        "type": "code",
        "text": f"<code>{var} = {n}</code> satırıyla başlayan ve <strong>döngü kullanarak</strong> <code>{n} {sign} 1 = {n}</code>, "
                f"<code>{n} {sign} 2 = {n * 2}</code>, ..., <code>{n} {sign} {stop} = {n * stop}</code> satırlarını alt alta "
                f"yazdıran kodu yazınız. Kodunuz <strong>{var} değişkeninin her değeri için</strong> doğru çalışmalı.",
        "code": None,
        "check": {"kind": "dongu_carpim", "var": var, "n": n, "stop": stop},
        "answer": f"{var} = {n}\nfor i in range(1, {stop + 1}):\n    print({var}, \"{sign}\", i, \"=\", {var} * i)",
        "hint": "Her satırda değişen tek şey çarpan; döngü değişkeni 1 ile kaç arasında değer almalı?",
        "solution": f"<code>range(1, {stop + 1})</code> çarpanı 1 ile {stop} arasında dolaştırır; her turda "
                    f"<code>{var} * i</code> hesaplanıp aynı satırda yazdırılır.",
    }
