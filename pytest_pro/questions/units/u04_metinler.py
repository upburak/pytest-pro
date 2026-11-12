"""Ünite 4 - Metinler (str)."""
import random

from ..helpers import STR_VALUES, Wrong, e, err, output_question
from ..registry import register_unit

UNIT = register_unit(
    "metinler", "Metinler (String)", "Başlangıç",
    "İndeksleme, dilimleme, len(), metin metotları (upper, lower, replace, strip, split, count), "
    "in operatörü, metin tekrarı ve biçimlendirme.",
    order=4,
)
q = UNIT.question


@q("Metin Tekrarı", verify="output")
def str_repeat():
    word = random.choice(["ab", "Py", "ha", "xo", "-*"])
    k = random.randint(2, 4)
    return output_question(
        f'kelime = "{word}"\nprint(kelime * {k})', word * k,
        f'Bir metni tam sayıyla çarpmak o metni art arda tekrarlar: "{e(word)}" * {k} = "{e(word * k)}".',
        wrongs=[
            Wrong(f"{word}{k}", "* sayıyı metnin sonuna eklemez; metni o kadar kez tekrarlar."),
            Wrong(" ".join([word] * k), "Tekrarlanan metinlerin arasına boşluk konmaz."),
            Wrong(err("TypeError"), "Metin * tam sayı geçerli bir işlemdir; hata vermez."),
        ],
        hint="Bir metni tam sayıyla çarpmak ne yapar?",
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
    word = random.choice(STR_VALUES)
    a = random.randint(0, 2)
    b = random.randint(a + 2, min(len(word), a + 5))
    end_inclusive = "Bitiş indeksi dilime dahil değildir; dilim bir karakter önce biter."
    form, res, wrongs = random.choice([
        (f"[{a}:{b}]", word[a:b], [
            Wrong(word[a:b + 1], end_inclusive),
            Wrong(word[a + 1:b + 1], "Saymaya 1'den başlamış olabilirsin; indeksler 0'dan başlar ve başlangıç dahildir."),
        ]),
        (f"[:{b}]", word[:b], [
            Wrong(word[:b + 1], end_inclusive),
            Wrong(word[b:], f"[:{b}] baştan {b}. indekse kadar alır; {b}'den sonrasını değil."),
        ]),
        (f"[{a}:]", word[a:], [
            Wrong(word[a + 1:], "Başlangıç indeksi dilime dahildir."),
            Wrong(word[:a] or word[:1], f"[{a}:] {a}. indeksten sona kadar alır; öncesini değil."),
        ]),
        ("[::-1]", word[::-1], [
            Wrong(word, "[::-1] metni ters sırayla verir."),
            Wrong(word[-1], "[::-1] yalnızca son karakteri değil, tüm metni ters sırayla verir."),
        ]),
    ])
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


@q("Metin Metotları", verify="output")
def methods():
    word = random.choice(["python dersi", "Merhaba Dunya", "kodlama"])
    call, res, why = random.choice([
        ("upper()", word.upper(), "tüm harfleri büyütür"),
        ("lower()", word.lower(), "tüm harfleri küçültür"),
        ("title()", word.title(), "her kelimenin ilk harfini büyütür"),
        ('replace("a", "*")', word.replace("a", "*"), 'tüm "a" harflerini "*" ile değiştirir'),
        ('count("a")', str(word.count("a")), '"a" harfinin kaç kez geçtiğini sayar'),
    ])
    other_case = word.upper() if res != word.upper() else word.lower()
    return output_question(
        f'metin = "{word}"\nprint(metin.{call})', res,
        f"<code>{e(call)}</code> metodu {why}. Metotlar orijinal metni değiştirmez, yeni bir değer döndürür.",
        wrongs=[
            Wrong(word, f"print metodun döndürdüğü yeni değeri yazar; <code>{e(call)}</code> {why}."),
            Wrong(other_case, f"Bu, {'upper()' if other_case == word.upper() else 'lower()'} metodunun sonucu; "
                              f"burada çağrılan <code>{e(call)}</code>."),
            Wrong(word.capitalize(), "Bu, yalnızca ilk harfi büyüten capitalize() metodunun sonucu; "
                                     f"burada çağrılan <code>{e(call)}</code>."),
            Wrong(err("AttributeError"), "Bu metot str tipinde vardır; hata vermez."),
        ],
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
    word = random.choice(["Python", "Okul", "Sinav"])
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


@q("in Operatörü", verify="output")
def in_operator():
    word = random.choice(["Python", "Programlama", "Bilgisayar"])
    part = random.choice([word[1:4], word[2:5].upper(), "x", word[:3].lower(), word[-2:]])
    found = part in word
    res = str(found)
    if found:
        opposite_why = f'"{e(part)}" metnin içinde harfi harfine aynı sırayla geçiyor.'
    elif part.lower() in word.lower():
        opposite_why = "Harfler aynı ama büyük/küçük harf farklı; in büyük/küçük harfe duyarlıdır."
    else:
        opposite_why = f'"{e(part)}", "{e(word)}" içinde kesintisiz bir parça olarak geçmiyor.'
    return output_question(
        f'print("{part}" in "{word}")', res,
        f'<code>in</code> bir metnin diğerinin içinde geçip geçmediğini kontrol eder ve büyük/küçük harfe '
        f'duyarlıdır. "{e(part)}", "{e(word)}" içinde {"geçer" if found else "geçmez"}.',
        wrongs=[
            Wrong("False" if found else "True", opposite_why),
            Wrong("None", "in her zaman True ya da False verir."),
            Wrong(part, "print, in ifadesinin sonucunu yazar; aranan metni değil."),
        ],
        hint="in büyük/küçük harfe duyarlı mıdır? Aranan parça metinde aynen geçiyor mu?",
    )


@q("f-string Biçimlendirme", verify="output")
def fstring_format():
    val = round(random.uniform(1, 99), 4)
    digits = random.choice([1, 2])
    res = f"{val:.{digits}f}"
    other = 3 - digits
    return output_question(
        f"x = {val}\nprint(f\"{{x:.{digits}f}}\")", res,
        f"<code>:.{digits}f</code> biçimi sayıyı virgülden sonra {digits} basamağa <strong>yuvarlayarak</strong> yazar.",
        wrongs=[
            Wrong(str(val), f"<code>:.{digits}f</code> biçimi basamak sayısını sınırlar; sayı olduğu gibi yazılmaz."),
            Wrong(f"{val:.{other}f}", f"Bu, virgülden sonra {other} basamaklı yazım; burada <code>.{digits}f</code> var."),
            Wrong(f"{int(val)}", "f biçimi kesir kısmını silmez; belirtilen basamak sayısına yuvarlar."),
        ],
        hint=":.Nf biçimindeki N neyi belirtir? Sayı yuvarlanır mı, kesilir mi?",
    )
