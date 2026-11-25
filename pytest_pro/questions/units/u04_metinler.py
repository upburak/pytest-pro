"""Ünite 4 - Metinler (str)."""
import ast
import random
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal

from ..codecheck import (
    OK,
    UNREADABLE,
    Tracker,
    assigned_names,
    assignments,
    checker,
    const_value,
    find_prints,
    loop_problems,
    print_texts,
    print_values,
    range_values,
    same_value,
    uses_name,
)
from ..helpers import STR_VALUES, Wrong, e, err, fill_question, output_question, tf_claim
from ..registry import register_unit
from .u01_temel import UNSET

UNIT = register_unit(
    "metinler", "Metinler (String)", "Başlangıç",
    "İndeksleme, dilimleme, len(), metin metotları (upper, lower, replace, strip, split, count), "
    "in operatörü, metin tekrarı ve biçimlendirme.",
    order=4,
)
q = UNIT.question


REPEAT_WORDS = ["ab", "Py", "ha", "xo", "-*", "la", "ok", "=+", "Ali", "na", "tik", "*"]


@q("Metin Tekrarı", verify="outcome")
def str_repeat():
    word = random.choice(REPEAT_WORDS)
    k = random.randint(2, 4)
    hint = "Bir metni tam sayıyla çarpmak ne yapar? Çarpılan değerin tipi ne?"
    if random.random() < 0.25:  # sayı tırnak içinde: metin * metin hata verir
        return output_question(
            f'kelime = "{word}"\nsayi = "{k}"\nprint(kelime * sayi)', err("TypeError"),
            "Metin yalnızca bir <strong>tam sayıyla</strong> çarpılarak tekrarlanabilir. <code>sayi</code> tırnak "
            "içinde olduğu için metindir; iki metin <code>*</code> ile çarpılamaz ve TypeError oluşur. Çözüm: "
            "<code>kelime * int(sayi)</code>.",
            wrongs=[
                Wrong(word * k, f'sayi tırnak içinde ("{k}"), yani metin; Python onu kendiliğinden sayıya çevirmez. '
                                "Metin * metin geçersizdir."),
                Wrong(f"{word}{k}", "* metinleri birleştirmez; üstelik iki metin * ile çarpılamaz."),
                Wrong(" ".join([word] * k), "Tekrarlanan metinlerin arasına boşluk konmaz; ama burada sayi bir metin "
                                            "olduğu için tekrar bile yapılamaz."),
            ],
            hint=hint,
        )
    wrongs = [
        Wrong(f"{word}{k}", "* sayıyı metnin sonuna eklemez; metni o kadar kez tekrarlar."),
        Wrong(" ".join([word] * k), "Tekrarlanan metinlerin arasına boşluk konmaz."),
        Wrong(err("TypeError"), "Metin * tam sayı geçerli bir işlemdir; hata vermez."),
        Wrong(word * (k + 1), f"Metin tam {k} kez yazılır; bir fazlası değil."),
    ]
    random.shuffle(wrongs)
    return output_question(
        f'kelime = "{word}"\nprint(kelime * {k})', word * k,
        f'Bir metni tam sayıyla çarpmak o metni art arda tekrarlar: "{e(word)}" * {k} = "{e(word * k)}".',
        wrongs=wrongs,
        hint=hint,
    )


@q("İndeksleme", verify="output")
def indexing():
    word = random.choice(STR_VALUES)
    i = random.choice([0, 1, 2, -1, -2])
    wrongs = []
    for j in (i - 1, i + 1, 0, -1, 1, -2, 3):
        if -len(word) <= j < len(word) and word[j] != word[i] and all(w.value != word[j] for w in wrongs):
            if i >= 0 and j == i - 1:
                why = f"Saymaya 1'den başlamış olabilirsin; indeksler 0'dan başlar, [{i}] aslında {i + 1}. karakterdir."
            elif i < 0 and j == i + 1:
                why = "Negatif indeksler sondan sayar ve [-1] son karakterdir; [-2] sondan ikinci karakterdir."
            else:
                why = (f'"{e(word[j])}" karakteri [{j}] konumunda; soru [{i}] konumunu soruyor. İndeksler 0\'dan '
                       "başlar, negatif indeksler sondan sayar.")
            wrongs.append(Wrong(word[j], why))
    return output_question(
        f'metin = "{word}"\nprint(metin[{i}])', word[i],
        "İndeksler 0'dan başlar: ilk karakter <code>[0]</code>. Negatif indeksler sondan sayar: son karakter "
        f"<code>[-1]</code>. <code>\"{word}\"[{i}]</code> = \"{word[i]}\".",
        wrongs=wrongs,
        hint="İlk karakterin indeksi kaçtır? İndeks negatifse sondan say.",
    )


@q("Dilimleme", verify="output")
def slicing():
    """Her biçimde en az üç anlamlı yanlış vardır; dolgu şık gerekmez (Y1)."""
    word = random.choice(STR_VALUES)
    end_inclusive = "Bitiş indeksi dilime dahil değildir; dilim bir karakter önce biter."
    one_less = "Bitiş indeksindeki karakter dahil değildir ama ondan önceki karakter dahildir; bir karakter eksik aldın."
    form = random.choice(["ab", "b", "a", "rev"])
    if form == "ab":
        a = random.randint(0, 2)
        b = random.randint(a + 2, min(len(word) - 1, a + 5))
        form, res = f"[{a}:{b}]", word[a:b]
        wrongs = [
            Wrong(word[a:b + 1], end_inclusive),
            Wrong(word[a + 1:b + 1], "Saymaya 1'den başlamış olabilirsin; indeksler 0'dan başlar ve başlangıç dahildir."),
            Wrong(word[a:b - 1], one_less),
            Wrong(word[a + 1:b], "Başlangıç indeksi dilime dahildir."),
        ]
    elif form == "b":
        b = random.randint(2, len(word) - 2)
        form, res = f"[:{b}]", word[:b]
        wrongs = [
            Wrong(word[:b + 1], end_inclusive),
            Wrong(word[b:], f"[:{b}] baştan {b}. indekse kadar alır; {b}. indeks ve sonrasını değil."),
            Wrong(word[:b - 1], one_less),
            Wrong(word[1:b], "Boş bırakılan başlangıç 0 demektir; ilk karakter de dilime dahildir."),
        ]
    elif form == "a":
        a = random.randint(1, 3)
        form, res = f"[{a}:]", word[a:]
        wrongs = [
            Wrong(word[a + 1:], "Başlangıç indeksi dilime dahildir."),
            Wrong(word[:a], f"[{a}:] {a}. indeksten sona kadar alır; öncesini değil."),
            Wrong(word[a - 1:], f"İndeksler 0'dan başlar; [{a}] {a + 1}. karakterdir, dilim oradan başlar."),
            Wrong(word[a:-1], "Boş bırakılan bitiş metnin sonu demektir; son karakter de dahildir."),
        ]
    else:
        form, res = "[::-1]", word[::-1]
        wrongs = [
            Wrong(word, "[::-1] metni ters sırayla verir."),
            Wrong(word[:0:-1], "Ters çevrilen metnin sonuna ilk harf gelir; o harf de dahildir."),
            Wrong(word[-1], "[::-1] yalnızca son karakteri değil, tüm metni ters sırayla verir."),
            Wrong(word[-2::-1], "Son karakter ters metnin başına gelir; o da dahildir."),
        ]
    return output_question(
        f'metin = "{word}"\nprint(metin{form})', res,
        "<code>[başlangıç:bitiş]</code> dilimi başlangıç indeksini <strong>içerir</strong>, bitiş indeksini "
        "<strong>içermez</strong>. Boş bırakılan başlangıç 0, bitiş ise metnin sonudur. "
        "<code>[::-1]</code> metni ters çevirir.",
        wrongs=[w for w in wrongs if w.value and w.value != res],
        hint="Başlangıç dahil, bitiş hariç. Boş bırakılan yer neyi ifade eder?",
    )


@q("len() Fonksiyonu", verify="output")
def length():
    word = random.choice(["Merhaba Dünya", "Python 3", "Ankara", "  boşluk  ", "a,b,c", "İstanbul",
                          "Bilgisayar Bilimi", "print()", "3.14", "x = 5", "Kodlama!", "ğüşiöç", "Ders 1-2", "Okul"])
    n = len(word)
    common = [Wrong(str(n - 1), "len() son indeksi değil, karakter sayısını verir.")]
    if " " in word:
        common.append(Wrong(str(len(word.replace(" ", ""))), "Boşluklar da karakterdir ve sayılır."))
    marks = "".join(ch for ch in word if not ch.isalnum() and ch != " ")
    if marks:
        common.append(Wrong(str(len([ch for ch in word if ch.isalnum() or ch == " "])),
                            "Noktalama ve işaretler de karakterdir ve sayılır."))
    return output_question(
        f'print(len("{word}"))', str(n),
        f"<code>len()</code> metindeki karakter sayısını verir; boşluk ve noktalama da sayılır. "
        f'"{e(word)}" metninde {n} karakter vardır.',
        common_wrongs=common,
        hint="Boşluklar ve noktalama işaretleri de karakter sayılır mı?",
    )


METHOD_WORDS = ["python dersi", "Merhaba Dünya", "bilgisayar dersi", "Ankara kalesi", "kitap okuma", "ilk ders"]
CASE_METHODS = {  # metot: (ne yapar, onu yapan)
    "upper()": ("tüm harfleri büyütür", "tüm harfleri büyüten"),
    "lower()": ("tüm harfleri küçültür", "tüm harfleri küçülten"),
    "title()": ("her kelimenin ilk harfini büyütür", "her kelimenin ilk harfini büyüten"),
    "capitalize()": ("yalnızca metnin ilk harfini büyütür", "yalnızca ilk harfi büyüten"),
}
I_NOTE = (" Dikkat: Python, küçük <code>i</code> harfini büyütürken Türkçedeki gibi <code>İ</code> değil, "
          "İngilizcedeki gibi <code>I</code> yapar.")


def _case_result(word, name):
    return getattr(word, name[:-2])()


@q("Metin Metotları", verify="output")
def methods():
    word = random.choice(METHOD_WORDS)
    calls = ["upper()", "lower()", "title()"]
    if word.count("a") >= 2:
        calls += ['replace("a", "*")', 'count("a")']
    call = random.choice(calls)
    note = ""
    if call in CASE_METHODS:
        res, why = _case_result(word, call), CASE_METHODS[call][0]
        pool = []
        if call == "upper()" and "i" in word:
            pool.append(Wrong(word.replace("i", "İ").upper(), "Türkçe kuralını uyguladın; ama Python <code>upper()</code> "
                                                               "ile küçük i harfini İ'ye değil I'ya çevirir."))
        for other, (_, doer) in CASE_METHODS.items():
            if other != call:
                pool.append(Wrong(_case_result(word, other), f"Bu, {doer} <code>{other}</code> metodunun sonucu; "
                                                             f"burada <code>{e(call)}</code> çağrılıyor."))
        pool.append(Wrong(word, f"Metot, değiştirilmiş yeni bir metin döndürür ve print onu yazar; "
                                f"<code>{e(call)}</code> {why}."))
        if "I" in res and "i" in word and call in ("upper()", "title()"):
            note = I_NOTE
    elif call.startswith("replace"):
        res, why = word.replace("a", "*"), 'tüm "a" harflerini "*" ile değiştirir'
        pool = [
            Wrong(word.replace("a", "*", 1), "replace() yalnızca ilk eşleşmeyi değil, metindeki bütün eşleşmeleri "
                                             "değiştirir."),
            Wrong(word.replace("a", "*").replace("A", "*"), "replace() büyük/küçük harfe duyarlıdır; büyük A "
                                                            "değişmez."),
            Wrong(word.replace("a", ""), 'replace("a", "*") harfleri silmez; her "a" yerine "*" koyar.'),
            Wrong(word, 'replace(eski, yeni): ilk parametre aranan, ikincisi yerine konandır; "a" harfleri '
                        "değişir. Değişmiş yeni metin yazdırılır."),
        ]
    else:
        count = word.count("a")
        res, why = str(count), '"a" harfinin kaç kez geçtiğini sayar'
        pool = [
            Wrong(str(word.find("a")), 'Bu, find("a") sonucu: ilk "a" harfinin konumu. count() kaç kez geçtiğini '
                                       "sayar."),
            Wrong(str(word.lower().count("a")), "count() büyük/küçük harfe duyarlıdır; büyük A sayılmaz."),
            Wrong(str(len(word)), "count() bütün karakterleri değil, yalnızca aranan harfi sayar."),
            Wrong(str(count - 1), 'Metindeki her "a" harfini say; ilki de dahil.'),
            Wrong(str(count + 1), '"a" harflerini tek tek yeniden say; fazladan saydın.'),
        ]
    return output_question(
        f'metin = "{word}"\nprint(metin.{call})', res,
        f"<code>{e(call)}</code> metodu {why}. Metotlar orijinal metni değiştirmez, yeni bir değer döndürür.{note}",
        wrongs=pool,
        hint=f"<code>{e(call)}</code> metodu metne ne yapar?",
    )


@q("split() ve strip()", verify="output")
def split_strip():
    if random.random() < 0.5:
        items = random.sample(["elma", "armut", "kiraz", "muz"], 3)
        sep = random.choice([",", "-", ";"])
        text = sep.join(items)
        return output_question(
            f'veri = "{text}"\nprint(veri.split("{sep}"))', str(text.split(sep)),
            f'<code>split("{sep}")</code> metni "{sep}" karakterinden bölerek bir <strong>liste</strong> döndürür.',
            wrongs=[
                Wrong(str(items).replace("'", '"'), "Python listedeki metinleri ekrana tek tırnakla yazar."),
                Wrong(" ".join(items), "split() bir liste döndürür; print listeyi köşeli parantezlerle yazar."),
                Wrong(f"['{text}']", f'Ayırıcı verildiği için metin her "{sep}" karakterinden bölünür.'),
            ],
            hint="split() ne tür bir değer döndürür ve metni hangi karakterden böler?",
        )
    word = random.choice(["Python", "Okul", "Sınav", "Kodlama", "Ödev"])
    left, right = " " * random.randint(1, 3), " " * random.randint(1, 3)
    return output_question(
        f'metin = "{left}{word}{right}"\nprint("[" + metin.strip() + "]")', f"[{word}]",
        "<code>strip()</code> metnin başındaki ve sonundaki boşlukları siler; aradaki boşluklara dokunmaz.",
        wrongs=[
            Wrong(f"[{left}{word}{right}]", "strip() baştaki ve sondaki boşlukları siler."),
            Wrong(f"[{word}{right}]", "strip() iki taraftaki boşlukları da siler; yalnızca soldakini silen lstrip()'tir."),
            Wrong(f"[{left}{word}]", "strip() iki taraftaki boşlukları da siler; yalnızca sağdakini silen rstrip()'tir."),
        ],
        hint="strip() boşlukları nereden siler: baştan mı, sondan mı, ikisinden de mi?",
    )


IN_WORDS = ["Python", "Programlama", "Bilgisayar", "Algoritma", "Klavye", "Ekran", "Değişken"]


def _in_parts(word):
    """Aranacak parçalar ve her birinin sonucuna dair açıklama: [(parça, sonuç, açıklama)]."""
    raw = [word[1:4], word[2:5].upper(), word[:3].lower(), word[-2:], word[1:3][::-1], word[0] + word[2], "x",
           word[-3:].upper(), word[3:6]]
    out = []
    for part in dict.fromkeys(raw):
        found = part in word
        if found:
            why = f'"{e(part)}" metnin içinde harfi harfine aynı sırayla geçiyor; in True verir.'
        elif part.lower() in word.lower():
            why = f'"{e(part)}" harfleri metinde var ama büyük/küçük harf farklı; in büyük/küçük harfe duyarlıdır.'
        else:
            why = f'"{e(part)}", "{e(word)}" içinde kesintisiz bir parça olarak geçmiyor; in False verir.'
        out.append((part, found, why))
    return out


@q("in Operatörü", verify="output")
def in_operator():
    """İki arama birlikte yazdırılır; dört birleşimin hepsi anlamlı bir şıktır (K4)."""
    word = random.choice(IN_WORDS)
    parts = _in_parts(word)
    picks = []
    for _ in range(2):
        want = random.random() < 0.5
        pool = [p for p in parts if p[1] == want and p not in picks] or [p for p in parts if p not in picks]
        picks.append(random.choice(pool))
    (p1, r1, why1), (p2, r2, why2) = picks
    wrongs = []
    for x in (True, False):
        for y in (True, False):
            if (x, y) == (r1, r2):
                continue
            if x != r1 and y != r2:
                why = f"İki sonucu da ters buldun. {why1} {why2}"
            elif x != r1:
                why = f"İlk arama yanlış: {why1}"
            else:
                why = f"İkinci arama yanlış: {why2}"
            wrongs.append(Wrong(f"{x} {y}", why))
    return output_question(
        f'metin = "{word}"\nprint("{p1}" in metin, "{p2}" in metin)', f"{r1} {r2}",
        "<code>in</code> bir metnin diğerinin içinde kesintisiz geçip geçmediğini kontrol eder ve büyük/küçük harfe "
        f"duyarlıdır. {why1} {why2}",
        wrongs=wrongs,
        hint="in büyük/küçük harfe duyarlı mıdır? Aranan parça metinde harfi harfine, aynı sırayla geçiyor mu?",
    )


def _decimal_round(value, digits, mode=ROUND_HALF_UP):
    """Ondalık yazımla yuvarlama: ROUND_HALF_UP okulda öğretilen (5 ve üstü yukarı), ROUND_DOWN kesme."""
    return str(Decimal(str(value)).quantize(Decimal(1).scaleb(-digits), rounding=mode))


@q("f-string Biçimlendirme", verify="output")
def fstring_format():
    digits = random.choice([1, 2])
    other = 3 - digits
    while True:
        # en az 3 ondalık basamak; Python'un sonucu okulda öğretilen yuvarlamayla aynı olmalı (Y4)
        val = round(random.uniform(1, 99), random.choice([3, 4]))
        res = f"{val:.{digits}f}"
        if len(str(val).split(".")[1]) >= 3 and res == _decimal_round(val, digits):
            break
    cut = _decimal_round(val, digits, ROUND_DOWN)
    if cut != res:
        near = Wrong(cut, f"<code>:.{digits}f</code> fazla basamakları kesip atmaz; yuvarlar.")
    else:
        up = str(Decimal(cut) + Decimal(1).scaleb(-digits))
        near = Wrong(up, "Atılan ilk basamak 5'ten küçük olduğu için sayı aşağı yuvarlanır; son basamak değişmez.")
    return output_question(
        f"x = {val}\nprint(f\"{{x:.{digits}f}}\")", res,
        f"<code>:.{digits}f</code> biçimi sayıyı virgülden sonra {digits} basamağa <strong>yuvarlayarak</strong> yazar.",
        wrongs=[
            near,
            Wrong(str(val), f"<code>:.{digits}f</code> biçimi basamak sayısını sınırlar; sayı olduğu gibi yazılmaz."),
            Wrong(f"{val:.{other}f}", f"Bu, virgülden sonra {other} basamaklı yazım; burada <code>.{digits}f</code> var."),
            Wrong(f"{int(val)}", "f biçimi kesir kısmını silmez; belirtilen basamak sayısına yuvarlar."),
        ],
        hint=":.Nf biçimindeki N neyi belirtir? Sayı yuvarlanır mı, kesilir mi?",
    )


# ================================================================= yeni şablonlar (ölçme raporu Ö4.1-Ö4.8)
CLAIM_WORDS = ["Bilgisayar", "Kalem", "Defter", "Python", "Kitap", "Klavye", "Ekran", "Program", "Öğrenci",
               "Değişken", "Sözlük", "Pencere"]


@q("İndeks İddiası (Doğru/Yanlış)", verify="tf_output")
def index_claim():
    """Kazanım: pozitif ve negatif indeksi doğru okur · Bloom: U"""
    word = random.choice(CLAIM_WORDS)
    while True:
        i = random.randint(-3, min(4, len(word) - 2))
        if i >= 0:
            wrongs = [Wrong(word[i + 1], f"Bir sonraki karakteri aldın; [{i}] ilk karakterden {i} adım sonradır.")]
            if i > 0:
                wrongs.append(Wrong(word[i - 1], f"Saymaya 1'den başlamış olabilirsin; indeksler 0'dan başlar, [{i}] "
                                                 f"{i + 1}. karakterdir."))
        else:
            wrongs = [Wrong(word[i - 1], f"Sondan bir fazla saydın; [-1] son karakterdir, [{i}] sondan {-i}. "
                                         "karakterdir.")]
            if i == -1:
                wrongs.append(Wrong(word[0], "[-1] ilk karakter değil, son karakterdir."))
            else:
                wrongs.append(Wrong(word[i + 1], f"Sondan bir eksik saydın; [-1] son karakterdir, [{i}] sondan {-i}. "
                                                 "karakterdir."))
        wrongs = [w for w in wrongs if w.value != word[i]]
        if wrongs:
            break
    return tf_claim(
        f'metin = "{word}"\nprint(metin[{i}])', word[i], wrongs,
        "İndeksler 0'dan başlar: ilk karakter <code>[0]</code>. Negatif indeksler sondan sayar: son karakter "
        f"<code>[-1]</code>. <code>\"{e(word)}\"[{i}]</code> = \"{e(word[i])}\".",
        hint="[0] ilk karakter, [-1] son karakterdir. Bu indeks baştan mı sondan mı sayılıyor?",
    )


SLICE_WORDS = ["Python", "Bilgisayar", "Kalemlik", "Defter", "Klavye", "Program", "Ankara", "Algoritma",
               "Kodlama", "Ekranlar", "Yazılım", "Sözlük"]


def _slice_text(word, s, t):
    return word[(None if s == "" else s):(None if t == "" else t)]


@q("Dilimi Tamamla (Boşluk Doldurma)", verify="fill")
def slice_blank():
    """Kazanım: istenen parçayı verecek dilimi kurar; eşdeğer dilimleri görür · Bloom: An"""
    word = random.choice(SLICE_WORDS)
    n = len(word)
    size = random.randint(2, 4)
    a = random.randint(0, n - size)
    target = word[a:a + size]
    canonical = f"{a}:{a + size}"
    found = [f"{s}:{t}" for s in [""] + list(range(-n, n + 1)) for t in [""] + list(range(-n, n + 1))
             if _slice_text(word, s, t) == target]
    alts = [canonical] + [x for x in found if x != canonical]
    pool = [Wrong(f"{a}:{a + size - 1}", "Bitiş indeksi dilime dahil değildir; dilim bitişten bir karakter önce "
                                         "biter. Bitişi bir artır."),
            Wrong(f"{a + 1}:{a + size + 1}", "Saymaya 1'den başlamış olabilirsin; indeksler 0'dan başlar."),
            Wrong(f"{a}:{size}", "İkinci sayı parçanın uzunluğu değil, bitiş indeksidir.")]
    wrongs = [w for w in pool if w.value not in alts
              and _slice_text(word, *[int(x) if x else "" for x in w.value.split(":")]) != target]
    return fill_question(
        f'metin = "{word}"\nprint(metin[____])', [alts], target,
        f"Aşağıdaki kod ekrana <code>{e(target)}</code> yazmalı. Boşluğa gereken dilimi "
        "(<code>başlangıç:bitiş</code>) yazın.",
        f"Parça {a}. indeksten başlıyor ve {size} karakter uzunluğunda; bitiş indeksi dahil olmadığı için "
        f"<code>[{a}:{a + size}]</code> yazılır. Negatif indeksli ya da boş bırakılan eşdeğer dilimler de kabul "
        "edilir.",
        hint="İlk karakterin indeksi kaç? Bitiş indeksi dilime dahil mi?",
        wrongs=[wrongs],
    )


METHOD_TEXTS = ["okul zamanı", "python dersi", "Merhaba Dünya", "bilgisayar", "ANKARA kalesi", "kitap OKUMA",
                "istanbul", "yazılım dersi", "  python  ", "  Okul Zamanı  ", "  kodlama dersi  ", "KOD yazmak",
                "yapay zeka", "Dünya kupası", "bilgi yarışması", "sınav haftası", "  Kitap Kurdu  ", "  ödev  "]
CASE_DESC = {
    "upper": "tüm harfleri büyütür", "lower": "tüm harfleri küçültür",
    "title": "her kelimenin ilk harfini büyütür, diğerlerini küçültür",
    "capitalize": "yalnızca metnin ilk harfini büyütür, diğerlerini küçültür",
    "strip": "baştaki ve sondaki boşlukları siler", "lstrip": "yalnızca baştaki boşlukları siler",
    "rstrip": "yalnızca sondaki boşlukları siler", "swapcase": "büyük harfleri küçük, küçükleri büyük yapar",
}
TARGET_METHODS = ["upper", "lower", "title", "capitalize", "strip"]


@q("Metot Bul (Boşluk Doldurma)", verify="fill")
def method_blank():
    """Kazanım: çıktıdan metodu belirler; Türkçe büyük harf sorununu tanır · Bloom: An"""
    while True:
        text = random.choice(METHOD_TEXTS)
        method = random.choice(TARGET_METHODS)
        results = {m: getattr(text, m)() for m in CASE_DESC}
        target = results[method]
        if target != text and list(results.values()).count(target) == 1:
            break
    padded = text != text.strip()
    code = f'metin = "{text}"\n' + ('print("[" + metin.____() + "]")' if padded else "print(metin.____())")
    expect = f"[{target}]" if padded else target
    wrongs = [Wrong(m, f"<code>{m}()</code> {CASE_DESC[m]}; sonuç <code>{e(r)}</code> olur.")
              for m, r in results.items() if m != method]
    note = ""
    if "i" in text and method in ("upper", "title", "capitalize") and "I" in target:
        note = (" Dikkat: Python küçük <code>i</code> harfini Türkçedeki gibi <code>İ</code> değil, <code>I</code> "
                "yapar.")
    return fill_question(
        code, [[method]], expect,
        f"Aşağıdaki kod ekrana <code>{e(expect)}</code> yazmalı. Boşluğa gereken metot adını yazın."
        + (" (Köşeli parantezler boşlukları görünür kılmak için eklendi.)" if padded else ""),
        f"<code>{method}()</code> {CASE_DESC[method]}. Metotlar orijinal metni değiştirmez, yeni bir metin "
        f"döndürür.{note}",
        hint="Çıktıda ne değişmiş: harflerin büyüklüğü mü, baştaki ve sondaki boşluklar mı?",
        wrongs=[wrongs],
    )


FIND_WORDS = ["Bilgisayar", "Kalemlik", "Defterim", "Programlama", "Klavye", "Algoritma", "Pencere", "Ankara",
              "Kodlama", "Matematik", "Sözlük", "Yazılım"]


@q("find() ve count()", verify="output")
def find_index():
    """Kazanım: aranan parçanın konumunu bulur; bulunamayınca -1 döndüğünü bilir · Bloom: U"""
    word = random.choice(FIND_WORDS)
    form = random.choices(["find", "absent", "index", "count"], weights=[3, 2, 2, 3])[0]
    letters = sorted(set(word))
    hint = "Saymaya 0'dan başla. Aranan bulunamazsa find() ne döndürür? count() neyi sayar?"
    if form == "absent":
        ch = random.choice([c for c in "xzqwçğ" if c not in word.lower()])
        call, answer = f'find("{ch}")', "-1"
        common = [Wrong("None", "find() aradığını bulamazsa -1 döndürür."),
                  Wrong("0", "0 ilk karakterin indeksidir; bulunamayınca find() -1 döndürür."),
                  Wrong(err("ValueError"), "find() bulamayınca hata vermez, -1 döndürür; hata veren index()'tir.")]
    elif form in ("find", "index"):
        ch = random.choice(letters)
        method = form
        call, pos = f'{method}("{ch}")', word.find(ch)
        answer = str(pos)
        common = [Wrong(str(pos + 1), f"İndeksler 0'dan başlar; \"{e(ch)}\" {pos + 1}. karakterdir ama indeksi {pos}.")]
        if word.rfind(ch) != pos:
            common.append(Wrong(str(word.rfind(ch)), f"<code>{method}()</code> aranan parçanın ilk geçtiği yeri "
                                                     "verir; son geçtiği yeri değil."))
        if word.lower().find(ch.lower()) != pos:
            common.append(Wrong(str(word.lower().find(ch.lower())), "Arama büyük/küçük harfe duyarlıdır."))
        common.append(Wrong(str(word.count(ch)), "Bu count() sonucu (kaç kez geçtiği); burada konum soruluyor."))
    else:
        ch = random.choice([c for c in letters if c.isalpha()])
        call, answer = f'count("{ch}")', str(word.count(ch))
        common = [Wrong(str(word.find(ch)), "Bu find() sonucu (ilk konum); count() kaç kez geçtiğini sayar."),
                  Wrong(str(len(word)), "count() bütün karakterleri değil, yalnızca aranan parçayı sayar.")]
        if word.lower().count(ch.lower()) != word.count(ch):
            common.append(Wrong(str(word.lower().count(ch.lower())), "count() büyük/küçük harfe duyarlıdır."))
    return output_question(
        f'metin = "{word}"\nprint(metin.{call})', answer,
        "<code>find()</code> ve <code>index()</code> aranan parçanın ilk geçtiği indeksi verir (0'dan sayılır). "
        "Bulunamazsa <code>find()</code> -1 döndürür, <code>index()</code> hata verir. <code>count()</code> kaç kez "
        f"geçtiğini sayar. Sonuç: {answer}.",
        common_wrongs=common, norm="sayi", hint=hint,
    )


IMMUTABLE_WORDS = ["kalem", "defter", "kutu", "masa", "okul", "ekran", "dolap", "bardak", "tahta", "kapak"]


@q("Metinler Değiştirilemez", verify="outcome")
def str_immutable():
    """Kazanım: metnin karakterine atama yapılamayacağını, metotların yeni metin döndürdüğünü bilir · Bloom: H/U"""
    word = random.choice(IMMUTABLE_WORDS)
    var = random.choice(["s", "kelime", "metin"])
    i = random.randint(0, min(3, len(word) - 1))
    new = random.choice([c for c in "KTMZR" if c != word[i].upper()])
    fixed = word[:i] + new + word[i + 1:]
    variant = random.choices(["assign", "rebuild", "method", "method_assign"], weights=[35, 25, 20, 20])[0]
    hint = "Metin oluşturulduktan sonra tek bir karakteri değiştirilebilir mi? Metot sonucu bir yere atanıyor mu?"
    rebuilt = f'"{new}" + {var}[1:]' if i == 0 else f'{var}[:{i}] + "{new}" + {var}[{i + 1}:]'
    if variant == "assign":
        code, answer = f'{var} = "{word}"\n{var}[{i}] = "{new}"\nprint({var})', err("TypeError")
        expl = ("Metinler değiştirilemez (immutable): bir karakterine atama yapılamaz ve TypeError oluşur. Yeni bir "
                f"metin oluşturulmalı: <code>{var} = {e(rebuilt)}</code>.")
        wrongs = [Wrong(fixed, "Metnin tek bir karakteri değiştirilemez; atama satırı hata verir."),
                  Wrong(word, "Atama satırı hata verir; program print satırına ulaşmaz."),
                  Wrong(err("IndexError"), f"[{i}] geçerli bir indeks; sorun atamanın kendisinde.")]
    elif variant == "rebuild":
        code, answer = f'{var} = "{word}"\n{var} = {rebuilt}\nprint({var})', fixed
        expl = (f"Karakter değiştirilmiyor; parçalardan <strong>yeni</strong> bir metin oluşturulup <code>{var}</code> "
                "değişkenine atanıyor. Bu geçerlidir.")
        wrongs = [Wrong(err("TypeError"), "Burada karaktere değil, değişkenin tamamına yeni metin atanıyor; bu "
                                          "geçerlidir."),
                  Wrong(word, f"<code>{var}</code> yeni metne bağlandı; print yeni metni yazar."),
                  Wrong(word[:i] + new + word[i:], f"<code>[{i + 1}:]</code> değiştirilen karakteri atlar; harf araya "
                                                   "eklenmez, onun yerine geçer.")]
    elif variant == "method":
        call, result = random.choice([("upper()", word.upper()), (f'replace("{word[i]}", "{new}")',
                                                                  word.replace(word[i], new))])
        code, answer = f'{var} = "{word}"\n{var}.{call}\nprint({var})', word
        expl = (f"Metotlar metni değiştirmez, yeni bir metin döndürür. <code>{var}.{e(call)}</code> sonucu bir "
                f"değişkene atanmadığı için kaybolur; <code>{var}</code> aynı kalır.")
        wrongs = [Wrong(result, f"Metot yeni metin döndürür ama sonuç atanmadı; <code>{var}</code> değişmez."),
                  Wrong(err("TypeError"), "Metot çağırmak hata vermez; yalnızca sonucu kullanılmaz."),
                  Wrong(err("AttributeError"), "Metinlerde bu metot vardır; çağrı hatasız çalışır.")]
    else:
        call, result = random.choice([("upper()", word.upper()), (f'replace("{word[i]}", "{new}")',
                                                                  word.replace(word[i], new))])
        code, answer = f'{var} = "{word}"\n{var} = {var}.{call}\nprint({var})', result
        expl = (f"Metot yeni bir metin döndürür ve bu metin <code>{var}</code> değişkenine yeniden atanır. Metin "
                "değiştirilemez ama değişkene yeni metin atanabilir.")
        wrongs = [Wrong(word, f"Sonuç <code>{var}</code> değişkenine yeniden atandı; print yeni metni yazar."),
                  Wrong(err("TypeError"), "Metinler değiştirilemez ama değişkene yeni bir metin atanabilir; hata "
                                          "oluşmaz.")]
        if call == "upper()":
            wrongs.append(Wrong(word.capitalize(), "upper() tüm harfleri büyütür; yalnızca ilk harfi büyüten "
                                                   "capitalize()'dır."))
        else:
            wrongs.append(Wrong(word.replace(word[i], new, 1), "replace() yalnızca ilk eşleşmeyi değil, bütün "
                                                               "eşleşmeleri değiştirir."))
        wrongs.append(Wrong(err("AttributeError"), "Metinlerde bu metot vardır; çağrı hatasız çalışır."))
    return output_question(code, answer, expl, wrongs=wrongs, hint=hint)


@q("Metin İşlemleri İddiası (Doğru/Yanlış)", verify="tf_output")
def str_method_claim():
    """Kazanım: split, join ve replace sonuçlarını izler · Bloom: U"""
    items = random.sample(["elma", "armut", "kiraz", "muz", "nar", "erik"], 3)
    op = random.choice(["join", "split", "replace"])
    if op == "join":
        sep = random.choice(["-", ", ", "/", "+"])
        code, output = f'print("{sep}".join({items}))', sep.join(items)
        wrongs = [Wrong(sep.join(items) + sep, "join ayırıcıyı yalnızca elemanların <strong>arasına</strong> koyar; "
                                               "sona eklemez."),
                  Wrong(" ".join(items), "Ayırıcı olarak join'in önündeki metin kullanılır; boşluk değil."),
                  Wrong(str(items), "join bir liste değil, elemanları birleştirilmiş tek bir metin döndürür.")]
        solution = "<code>ayirici.join(liste)</code> elemanları aralarına ayırıcı koyarak tek bir metinde birleştirir."
    elif op == "split":
        sep = random.choice([",", "-", ";"])
        text = sep.join(items)
        code, output = f'print("{text}".split("{sep}"))', str(items)
        wrongs = [Wrong(" ".join(items), "split bir metin değil, liste döndürür; print listeyi köşeli parantezle "
                                         "yazar."),
                  Wrong(f"['{text}']", f'Ayırıcı verildiği için metin her "{sep}" karakterinden bölünür.'),
                  Wrong(str([x + sep for x in items[:-1]] + items[-1:]), "Ayırıcı parçalara eklenmez; split onu "
                                                                       "atar.")]
        solution = "<code>split(ayirici)</code> metni ayırıcıdan bölerek bir <strong>liste</strong> döndürür."
    else:
        phrase = random.choice(["ana kara", "masa ve kasa", "araba", "kalabalık", "bal ve kaymak", "sarı lale"])
        new = random.choice(["e", "*", "o"])
        code, output = f'print("{phrase}".replace("a", "{new}"))', phrase.replace("a", new)
        wrongs = [Wrong(phrase.replace("a", new, 1), "replace yalnızca ilk eşleşmeyi değil, bütün eşleşmeleri "
                                                     "değiştirir."),
                  Wrong(phrase, "replace yeni bir metin döndürür ve print onu yazar; değişiklik görünür."),
                  Wrong(phrase.replace("a", ""), f'replace harfleri silmez; her "a" yerine "{new}" koyar.')]
        solution = ("<code>replace(eski, yeni)</code> metindeki <strong>bütün</strong> eşleşmeleri değiştirip yeni "
                    "bir metin döndürür.")
    return tf_claim(
        code, output, wrongs, solution,
        hint="join ayırıcıyı nereye koyar? split ne tür bir değer döndürür? replace kaç eşleşmeyi değiştirir?",
    )


REVERSE_WORDS = ["kalem", "Python", "kitap", "defter", "okul", "ekran", "Ankara", "sınav", "bilgi", "masa", "örnek",
                 "klavye"]


@q("Kelimeyi Ters Çevir (Kod Yazma)")
def write_reverse():
    """Kazanım: dilimleme ya da döngüyle metni ters çevirir · Bloom: O"""
    var = random.choice(["kelime", "metin", "s"])
    word = random.choice(REVERSE_WORDS)
    return {
        "type": "code",
        "text": (
            f"<code>{var} = \"{e(word)}\"</code> satırıyla başlayan ve kelimeyi <strong>ters</strong> çevirip yazdıran "
            f"kodu yazınız (çıktı: <code>{e(word[::-1])}</code>). Ters metni elle yazmayın; kod her kelime için "
            "çalışmalı."
        ),
        "code": None,
        "check": {"kind": "reverse_text", "var": var, "word": word},
        "answer": f'{var} = "{word}"\nprint({var}[::-1])',
        "hint": "Dilimlemede adım -1 ne yapar? Döngüyle yapacaksan her harfi yeni metnin başına mı sonuna mı "
                "eklemelisin?",
        "solution": "<code>[::-1]</code> dilimi metni sondan başa doğru okur. Döngüyle de yapılabilir: boş bir "
                    "metinle başlayıp her harfi başa eklemek (<code>ters = h + ters</code>).",
    }


VOWEL_WORDS = ["bilgisayar", "okul", "kitap", "defter", "öğretmen", "kalem", "pencere", "çanta", "üzüm",
               "programlama", "klavye", "sözlük", "güneş", "matematik"]
VOWELS = "aeıioöuü"


@q("Sesli Harf Sayısı (Kod Yazma)")
def write_vowels():
    """Kazanım: döngü, in ve sayaçla metin işler · Bloom: O"""
    var = random.choice(["metin", "kelime", "s"])
    word = random.choice(VOWEL_WORDS)
    count = sum(ch in VOWELS for ch in word)
    return {
        "type": "code",
        "text": (
            f"<code>{var} = \"{e(word)}\"</code> satırıyla başlayan ve bu metindeki <strong>sesli harflerin</strong> "
            f"(a, e, ı, i, o, ö, u, ü) sayısını bulup yazdıran kodu yazınız (çıktı: <code>{count}</code>). Sonucu "
            "elle yazmayın; kod her küçük harfli metin için çalışmalı."
        ),
        "code": None,
        "check": {"kind": "count_vowels", "var": var, "word": word},
        "answer": (f'{var} = "{word}"\nsayac = 0\nfor harf in {var}:\n    if harf in "{VOWELS}":\n'
                   "        sayac += 1\nprint(sayac)"),
        "hint": "Her harf için 'sesli mi?' diye sor; evetse sayacı artır. Sayacı ne zaman yazdırmalısın?",
        "solution": "Sayaç 0 ile başlatılır; döngüde her harf için <code>in</code> ile sesli harf metninde olup "
                    "olmadığına bakılır ve sesliyse sayaç 1 artırılır. Sonuç döngü bittikten sonra yazdırılır.",
    }


# ================================================================= denetleyiciler
def _first_value(tree, name):
    """Adın üst düzeydeki ilk atamasının sabit değeri (yoksa UNSET)."""
    for stmt in tree.body:
        for target, value in assignments(stmt):
            if target == name:
                return const_value(value, None, UNSET)
    return UNSET


def _is_name(node, name):
    return isinstance(node, ast.Name) and node.id == name


REV_PROBES = ("kalem", "Python", "ab")


def _slices_to(node, var, text):
    """var[a:b:c] diliminin var = text iken sonucu; dilim değilse ya da hesaplanamazsa None."""
    if not (isinstance(node, ast.Subscript) and _is_name(node.value, var) and isinstance(node.slice, ast.Slice)):
        return None
    parts = []
    for part in (node.slice.lower, node.slice.upper, node.slice.step):
        value = None if part is None else const_value(part, {var: text}, UNSET)
        if value is not None and (not isinstance(value, int) or isinstance(value, bool)):
            return None
        parts.append(value)
    return None if parts[2] == 0 else text[slice(*parts)]


def _is_rev_slice(node, var):
    """var[::-1] ya da her uzunlukta aynı sonucu veren eşdeğeri (var[-1::-1], var[len(var) - 1::-1])."""
    return all(_slices_to(node, var, probe) == probe[::-1] for probe in REV_PROBES)


def _is_join_reversed(node, var):
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "join"
            and const_value(node.func.value) == "" and len(node.args) == 1 and isinstance(node.args[0], ast.Call)
            and _is_name(node.args[0].func, "reversed") and len(node.args[0].args) == 1
            and _is_name(node.args[0].args[0], var))


def _loop_chars(loop, var, word):
    """Döngünün her turda eklediği karakter ifadesi: (sıra, adı/indeksi) -> karakter listesi; çözülemezse None."""
    if not isinstance(loop.target, ast.Name):
        return None, None
    if _is_name(loop.iter, var):
        return list(word), ("item", loop.target.id)
    seq = range_values(loop.iter, {var: word})
    if seq is None or any(not -len(word) <= i < len(word) for i in seq):
        return None, None
    return [word[i] for i in seq], ("index", loop.target.id)


def _is_char(node, kind, var):
    """Döngüde eklenen ifade karakter mi: for h in var -> h; for i in range -> var[i]."""
    mode, name = kind
    if mode == "item":
        return _is_name(node, name)
    return isinstance(node, ast.Subscript) and _is_name(node.value, var) and _is_name(node.slice, name)


def _build_order(stmt, acc, kind, var):
    """acc = ch + acc -> "prepend"; acc = acc + ch ya da acc += ch -> "append"; değilse None."""
    if isinstance(stmt, ast.AugAssign) and _is_name(stmt.target, acc) and isinstance(stmt.op, ast.Add):
        return "append" if _is_char(stmt.value, kind, var) else None
    pairs = list(assignments(stmt))
    if len(pairs) == 1 and pairs[0][0] == acc and isinstance(pairs[0][1], ast.BinOp) \
            and isinstance(pairs[0][1].op, ast.Add):
        left, right = pairs[0][1].left, pairs[0][1].right
        if _is_char(left, kind, var) and _is_name(right, acc):
            return "prepend"
        if _is_name(left, acc) and _is_char(right, kind, var):
            return "append"
    return None


@checker("reverse_text")
def check_reverse_text(tree, p):
    """var = word; kelimenin tersi [::-1], "".join(reversed(...)) ya da döngüyle (boş metne başa ekleyerek)
    oluşturulup yazdırılır."""
    var, word = p["var"], p["word"]
    target = word[::-1]
    if _first_value(tree, var) != word:
        return False, f"<code>{var}</code> değişkenine <code>\"{e(word)}\"</code> atanmamış."
    tr = Tracker(keep={var})
    built, notes = {}, []
    for stmt in tr.run(tree.body):
        if isinstance(stmt, (ast.For, ast.While)):
            if find_prints(stmt):
                return False, "Ters metni döngü bittikten sonra bir kez yazdır; döngünün içinde yazdırma."
            problem = loop_problems(stmt) if isinstance(stmt, ast.For) else None
            if problem:
                return False, problem
            chars, kind = _loop_chars(stmt, var, word) if isinstance(stmt, ast.For) else (None, None)
            body = [s for s in stmt.body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
            if chars is None or len(body) != 1:
                notes.append("unknown")
                continue
            acc = next(iter(assigned_names(body[0])), None)
            order = _build_order(body[0], acc, kind, var) if acc else None
            if order is None or tr.values.get(acc) != "":
                notes.append("unknown")
                continue
            built[acc] = "".join(reversed(chars)) if order == "prepend" else "".join(chars)
            continue
        for name in assigned_names(stmt):
            built.pop(name, None)
        for call in find_prints(stmt):
            if not print_values(call) and target in print_texts(call):
                notes.append("const")  # print("melak"): metin sabiti etiket sayılır
            for node in print_values(call):
                if isinstance(node, ast.FormattedValue):
                    node = node.value
                if isinstance(node, ast.Name) and node.id in built:
                    if built[node.id] == target:
                        return True, OK
                    notes.append("forward")
                    continue
                expr = tr.inline(node)
                if _is_rev_slice(expr, var) or _is_join_reversed(expr, var):
                    return True, OK
                if isinstance(expr, ast.Call) and _is_name(expr.func, "reversed"):
                    notes.append("reversed")
                elif _is_name(expr, var):
                    notes.append("same")
                elif not uses_name(expr, var):
                    notes.append("const" if tr.try_value(expr) == target else "other")
                elif _slices_to(expr, var, word) == target:
                    notes.append("specific")
                else:
                    notes.append("other")
    if "forward" in notes:
        return False, "Döngü harfleri aynı sırayla ekliyor; ters çevirmek için her harfi yeni metnin başına ekle."
    if "const" in notes:
        return False, "Ters metni elle yazma; kod her kelime için çalışmalı. Değişkeni kullan."
    if "specific" in notes:
        return False, ("Dilim yalnızca bu kelimede doğru sonuç veriyor; kod her kelime için çalışmalı. Bu kelimenin "
                       "uzunluğuna bağlı sayı yazma.")
    if "reversed" in notes:
        return False, ("<code>reversed()</code> metin değil, bir sıralayıcı döndürür; harfleri <code>\"\".join(...)"
                       "</code> ile birleştir ya da dilimleme kullan.")
    if "same" in notes:
        return False, "Kelime ters çevrilmeden yazdırılıyor."
    if "other" in notes:
        return False, "Yazdırılan değer kelimenin tersi değil; dilimlemede adımı kontrol et."
    if not find_prints(tree):
        return False, "Ters metni <code>print()</code> ile yazdır."
    return False, UNREADABLE


def _letters(node, defs):
    """Sesli harf kümesi olarak kullanılan sabit: metin, liste, demet ya da küme -> harfler; değilse None."""
    if isinstance(node, ast.Name) and node.id in defs:
        node = defs[node.id]
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return set(node.value)
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        out = set()
        for elt in node.elts:
            if not (isinstance(elt, ast.Constant) and isinstance(elt.value, str)):
                return None
            out |= set(elt.value)
        return out
    return None


def _test_letters(test, item, defs):
    """if koşulunun kabul ettiği harfler: h in "aeı..." ya da h == "a" or h == "e" ...; çözülemezse None."""
    if (isinstance(test, ast.Compare) and len(test.ops) == 1 and isinstance(test.ops[0], ast.In)
            and _is_name(test.left, item)):
        return _letters(test.comparators[0], defs)
    if isinstance(test, ast.Compare) and len(test.ops) == 1 and isinstance(test.ops[0], ast.Eq):
        sides = [test.left, test.comparators[0]]
        if _is_name(sides[1], item):
            sides.reverse()
        if _is_name(sides[0], item) and isinstance(sides[1], ast.Constant) and isinstance(sides[1].value, str):
            return {sides[1].value}
        return None
    if isinstance(test, ast.BoolOp) and isinstance(test.op, ast.Or):
        out = set()
        for value in test.values:
            part = _test_letters(value, item, defs)
            if part is None:
                return None
            out |= part
        return out
    return None


def _is_increment(stmt, counter):
    if isinstance(stmt, ast.AugAssign) and _is_name(stmt.target, counter) and isinstance(stmt.op, ast.Add):
        return const_value(stmt.value) == 1
    pairs = list(assignments(stmt))
    return (len(pairs) == 1 and pairs[0][0] == counter and isinstance(pairs[0][1], ast.BinOp)
            and isinstance(pairs[0][1].op, ast.Add) and _is_name(pairs[0][1].left, counter)
            and const_value(pairs[0][1].right) == 1)


def _count_calls(node, var):
    """metin.count("a") + metin.count("e") + ... -> harf listesi; değilse None."""
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = _count_calls(node.left, var), _count_calls(node.right, var)
        return None if left is None or right is None else left + right
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "count"
            and _is_name(node.func.value, var) and len(node.args) == 1 and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)):
        return [node.args[0].value]
    return None


def _sum_generator(node, var, defs):
    """sum(1 for h in metin if h in "...") -> harfler; değilse None."""
    if not (isinstance(node, ast.Call) and _is_name(node.func, "sum") and len(node.args) == 1
            and isinstance(node.args[0], ast.GeneratorExp)):
        return None
    gen = node.args[0]
    if const_value(gen.elt) != 1 or len(gen.generators) != 1:
        return None
    comp = gen.generators[0]
    if not (isinstance(comp.target, ast.Name) and _is_name(comp.iter, var) and len(comp.ifs) == 1):
        return None
    return _test_letters(comp.ifs[0], comp.target.id, defs)


def _vowel_set_problem(letters):
    """Harf kümesi Türkçe sesli harfleri tam olarak içeriyor mu? Sorun varsa öğrenciye not."""
    missing = [v for v in VOWELS if v not in letters]
    if missing:
        listed = ", ".join(f"<code>{m}</code>" for m in missing)
        return f"Sesli harf listende eksik harfler var: {listed}. Türkçede 8 sesli harf vardır."
    extra = sorted(ch for ch in letters if ch not in VOWELS + "AEIİOÖUÜ")
    if extra:
        listed = ", ".join(f"<code>{e(x)}</code>" for x in extra)
        return f"Sesli harf listende sesli olmayan karakterler var: {listed}."
    return None


@checker("count_vowels")
def check_count_vowels(tree, p):
    """var = word; sesli harfler (a, e, ı, i, o, ö, u, ü) döngü + in + sayaçla (ya da count/sum ile) sayılıp
    döngüden sonra yazdırılır."""
    var, word = p["var"], p["word"]
    want = sum(ch in VOWELS for ch in word)
    if _first_value(tree, var) != word:
        return False, f"<code>{var}</code> değişkenine <code>\"{e(word)}\"</code> atanmamış."
    tr = Tracker(keep={var})
    counted, notes = {}, []
    for stmt in tr.run(tree.body):
        if isinstance(stmt, ast.For):
            problem = loop_problems(stmt)
            if problem:
                return False, problem
            if find_prints(stmt):
                return False, "Sayacı döngü bittikten sonra bir kez yazdır; döngünün içinde yazdırma."
            if not (isinstance(stmt.target, ast.Name) and _is_name(stmt.iter, var)):
                notes.append("unknown")
                continue
            item = stmt.target.id
            body = [s for s in stmt.body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
            if len(body) == 1 and isinstance(body[0], ast.If) and not body[0].orelse and len(body[0].body) == 1:
                counter = next(iter(assigned_names(body[0].body[0])), None)
                letters = _test_letters(body[0].test, item, tr.defs)
                if counter and _is_increment(body[0].body[0], counter) and letters is not None:
                    if tr.values.get(counter) != 0:
                        return False, "Sayacı döngüden önce 0 ile başlat."
                    problem = _vowel_set_problem(letters)
                    if problem:
                        return False, problem
                    counted[counter] = sum(ch in letters for ch in word)
                    continue
            if len(body) == 1 and any(_is_increment(body[0], n) for n in assigned_names(body[0])):
                return False, ("Döngü her harfte sayacı artırıyor; yalnızca sesli harflerde artırmak için "
                               "<code>if</code> ile kontrol et.")
            notes.append("unknown")
            continue
        for name in assigned_names(stmt):
            counted.pop(name, None)
        for call in find_prints(stmt):
            for node in print_values(call):
                if isinstance(node, ast.FormattedValue):
                    node = node.value
                if isinstance(node, ast.Name) and node.id in counted:
                    return (True, OK) if counted[node.id] == want else (False, "Sayılan değer doğru değil.")
                expr = tr.inline(node)
                letters = _count_calls(expr, var)
                letters = set(letters) if letters is not None else _sum_generator(expr, var, tr.defs)
                if letters is not None:
                    problem = _vowel_set_problem(letters)
                    return (False, problem) if problem else (True, OK)
                if not uses_name(expr, var) and same_value(tr.try_value(expr), want):
                    notes.append("const")
                else:
                    notes.append("other")
    if "const" in notes:
        return False, "Sonucu elle yazma; kod her metin için çalışmalı. Harfleri döngüyle say."
    if "other" in notes:
        return False, ("Yazdırılan değer sesli harf sayısı değil. Her harf için sesli olup olmadığına bakıp bir "
                       "sayaç artır.")
    if not find_prints(tree):
        return False, "Sonucu <code>print()</code> ile yazdır."
    return False, UNREADABLE
