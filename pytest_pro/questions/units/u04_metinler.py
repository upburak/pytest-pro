"""Ünite 4 - Metinler (str)."""
import random
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal

from ..helpers import STR_VALUES, Wrong, e, err, output_question
from ..registry import register_unit

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
