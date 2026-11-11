"""Ünite 4 - Metinler (str)."""
import random

from ..helpers import STR_VALUES, e, err, output_question
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
        wrongs=[f"{word}{k}", " ".join([word] * k), err("TypeError")],
    )


@q("İndeksleme", verify="output")
def indexing():
    word = random.choice(STR_VALUES)
    i = random.choice([0, 1, 2, -1, -2])
    others = [word[j] for j in (0, 1, 2, -1, -2, 3) if word[j] != word[i]]
    return output_question(
        f'metin = "{word}"\nprint(metin[{i}])', word[i],
        "İndeksler 0'dan başlar: ilk karakter <code>[0]</code>. Negatif indeksler sondan sayar: son karakter "
        f"<code>[-1]</code>. <code>\"{word}\"[{i}]</code> = \"{word[i]}\".",
        wrongs=others,
    )


@q("Dilimleme", verify="output")
def slicing():
    word = random.choice(STR_VALUES)
    a = random.randint(0, 2)
    b = random.randint(a + 2, min(len(word), a + 5))
    form, res = random.choice([
        (f"[{a}:{b}]", word[a:b]), (f"[:{b}]", word[:b]), (f"[{a}:]", word[a:]), ("[::-1]", word[::-1]),
    ])
    return output_question(
        f'metin = "{word}"\nprint(metin{form})', res,
        "<code>[başlangıç:bitiş]</code> dilimi başlangıç indeksini <strong>içerir</strong>, bitiş indeksini "
        "<strong>içermez</strong>. Boş bırakılan başlangıç 0, bitiş ise metnin sonudur. "
        "<code>[::-1]</code> metni ters çevirir.",
        wrongs=[word[a:b + 1], word[a + 1:b + 1], word[a:b - 1] or word, word[::-1] if form != "[::-1]" else word],
    )


@q("len() Fonksiyonu", verify="output")
def length():
    word = random.choice(["Merhaba Dünya", "Python 3", "Ankara", "  boşluk  ", "a,b,c"])
    return output_question(
        f'print(len("{word}"))', str(len(word)),
        f"<code>len()</code> metindeki karakter sayısını verir; boşluk ve noktalama da sayılır. "
        f'"{e(word)}" metninde {len(word)} karakter vardır.',
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
    return output_question(
        f'metin = "{word}"\nprint(metin.{call})', res,
        f"<code>{e(call)}</code> metodu {why}. Metotlar orijinal metni değiştirmez, yeni bir değer döndürür.",
        wrongs=[word, word.upper() if res != word.upper() else word.lower(), word.capitalize(), err("AttributeError")],
    )


@q("split() ve strip()", verify="output")
def split_strip():
    if random.random() < 0.5:
        items = random.sample(["elma", "armut", "kiraz", "muz"], 3)
        sep = random.choice([",", "-", ";"])
        text = sep.join(items)
        res = str(text.split(sep))
        return output_question(
            f'veri = "{text}"\nprint(veri.split("{sep}"))', res,
            f'<code>split("{sep}")</code> metni "{sep}" karakterinden bölerek bir <strong>liste</strong> döndürür.',
            wrongs=[str(items).replace("'", '"'), " ".join(items), f"['{text}']"],
        )
    word = random.choice(["Python", "Okul", "Sinav"])
    left, right = " " * random.randint(1, 3), " " * random.randint(1, 3)
    res = f"[{word}]"
    return output_question(
        f'metin = "{left}{word}{right}"\nprint("[" + metin.strip() + "]")', res,
        "<code>strip()</code> metnin başındaki ve sonundaki boşlukları siler; aradaki boşluklara dokunmaz.",
        wrongs=[f"[{left}{word}{right}]", f"[{word}{right}]", f"[{left}{word}]"],
    )


@q("in Operatörü", verify="output")
def in_operator():
    word = random.choice(["Python", "Programlama", "Bilgisayar"])
    part = random.choice([word[1:4], word[2:5].upper(), "x", word[:3].lower(), word[-2:]])
    res = str(part in word)
    return output_question(
        f'print("{part}" in "{word}")', res,
        f'<code>in</code> bir metnin diğerinin içinde geçip geçmediğini kontrol eder ve büyük/küçük harfe '
        f'duyarlıdır. "{e(part)}", "{e(word)}" içinde {"geçer" if res == "True" else "geçmez"}.',
        wrongs=["False" if res == "True" else "True", "None", part],
    )


@q("f-string Biçimlendirme", verify="output")
def fstring_format():
    val = round(random.uniform(1, 99), 4)
    digits = random.choice([1, 2])
    res = f"{val:.{digits}f}"
    return output_question(
        f"x = {val}\nprint(f\"{{x:.{digits}f}}\")", res,
        f"<code>:.{digits}f</code> biçimi sayıyı virgülden sonra {digits} basamağa <strong>yuvarlayarak</strong> yazar.",
        wrongs=[str(val), f"{val:.{3 - digits}f}", f"{int(val)}"],
    )
