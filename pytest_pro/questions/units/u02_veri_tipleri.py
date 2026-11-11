"""Ünite 2 - Veri Tipleri ve Tip Dönüşümleri."""
import random

from ..helpers import e, err, output_question, unique_options
from ..registry import register_unit

UNIT = register_unit(
    "veri_tipleri", "Veri Tipleri ve Dönüşümler", "Başlangıç",
    "int, float, str, bool; type(), int()/float()/str()/bool() dönüşümleri, input() ile sayı alma.",
    order=2,
)
q = UNIT.question


@q("type() ve Veri Tipleri", verify="output")
def type_func():
    literal, typ = random.choice([
        ("3.14", "float"), ("0.0", "float"), ("42", "int"), ("-7", "int"),
        ('"100"', "str"), ('"3.14"', "str"), ('"True"', "str"), ("True", "bool"), ("False", "bool"),
    ])
    answer = f"<class '{typ}'>"
    note = " Tırnak içindeki her değer, içeriği ne olursa olsun metindir." if literal.startswith('"') else ""
    opts = ["<class 'int'>", "<class 'float'>", "<class 'str'>", "<class 'bool'>"]
    random.shuffle(opts)
    return {
        "type": "mc", "text": "Aşağıdaki kodun çıktısı ne olur?",
        "code": f"x = {literal}\nprint(type(x))", "options": opts, "answer": answer,
        "solution": f"<code>type()</code> değerin tipini döndürür. <code>{e(literal)}</code> değeri "
                    f"{e(answer)} tipindedir.{note}",
    }


@q("Tip Dönüşümleri (int/str)", verify="output")
def str_to_int():
    n1, n2 = random.randint(2, 9), random.randint(10, 50)
    op = random.choice(["+", "*"])
    res = n1 + n2 if op == "+" else n1 * n2
    return output_question(
        f'a = "{n1}"\nb = {n2}\nsonuc = int(a) {op} b\nprint(sonuc)', str(res),
        f'<code>a</code> metin ("{n1}") olarak tanımlanmıştır. <code>int(a)</code> ile {n1} sayısına '
        f"dönüşür; {n1} {op} {n2} = {res}.",
        text="Aşağıdaki kod çalıştırıldığında ekrana yazdırılacak <strong>sayısal değeri</strong> giriniz:",
    )


@q("Tip Dönüşümleri (float/int)", verify="output")
def float_int():
    if random.random() < 0.5:
        whole, frac = random.randint(2, 20), random.randint(1, 9)
        return output_question(
            f"x = {whole}.{frac}\nprint(int(x))", str(whole),
            f"<code>int()</code> ondalıklı sayının kesir kısmını atar (yuvarlamaz): int({whole}.{frac}) = {whole}.",
        )
    n = random.randint(2, 20)
    return output_question(
        f'x = "{n}"\ny = float(x)\nprint(y)', f"{n}.0",
        f'<code>float("{n}")</code> metni ondalıklı sayıya çevirir; float değerler ekrana {n}.0 biçiminde yazılır.',
    )


@q("bool() Dönüşümü", verify="output")
def bool_conversion():
    value, result, why = random.choice([
        ("0", "False", "Sıfır sayısı False kabul edilir."),
        ("7", "True", "Sıfırdan farklı her sayı True kabul edilir."),
        ('""', "False", "Boş metin False kabul edilir."),
        ('"0"', "True", 'İçinde karakter olan her metin True\'dur; "0" da boş değildir.'),
        ('" "', "True", "Bir boşluk karakteri içeren metin boş değildir, True'dur."),
        ("0.0", "False", "0.0 sıfıra eşit olduğu için False kabul edilir."),
        ("[]", "False", "Boş liste False kabul edilir."),
    ])
    return output_question(
        f"print(bool({value}))", result, f"<code>bool()</code> değerin doğruluk karşılığını verir. {e(why)}",
        wrongs=["True" if result == "False" else "False", err("ValueError"), "None"],
    )


@q("input() ve Tip Dönüşümü", verify="output")
def input_concat():
    n = random.randint(2, 9)
    k = random.choice([2, 3])
    correct = str(n) * k
    return output_question(
        f"sayi = input()\nprint(sayi * {k})", correct,
        f'<code>input()</code> metin döndürür: sayi = "{n}". Metin * {k} işlemi metni {k} kez tekrarlar, bu '
        f"yüzden sonuç {correct} olur. Sayı olarak çarpmak için <code>int(input())</code> gerekir.",
        wrongs=[str(n * k), err("TypeError"), " ".join([str(n)] * k)],
        text=f"Kod çalıştırıldığında kullanıcı klavyeden <strong>{n}</strong> yazıp Enter'a basıyor. "
             "Ekrana ne yazdırılır?",
        stdin=str(n),
    )


@q("Metin ve Sayı Birleştirme", verify="output")
def str_concat():
    n1, n2 = random.randint(1, 9), random.randint(1, 9)
    correct = f"{n1}{n2}"
    return output_question(
        f'a = "{n1}"\nb = "{n2}"\nprint(a + b)', correct,
        "İki değişken de tırnak içinde olduğu için str tipindedir. Metinlerde <code>+</code> toplama değil "
        f'birleştirme yapar: "{n1}" + "{n2}" = "{correct}".',
        wrongs=[str(n1 + n2), f"{n1} {n2}", err("TypeError")],
    )


@q("Metin ve Sayı Birleştirme", verify="error")
def str_plus_int():
    age = random.randint(14, 18)
    return output_question(
        f'yas = {age}\nprint("Yaşım " + yas)', err("TypeError"),
        "str ile int <code>+</code> ile birleştirilemez. Çözüm: <code>\"Yaşım \" + str(yas)</code>, "
        "<code>print(\"Yaşım\", yas)</code> veya <code>f\"Yaşım {yas}\"</code>.",
        wrongs=[f"Yaşım {age}", f"Yaşım{age}", f"Yaşım + {age}"],
    )


@q("Dönüşüm Hataları", verify="raises_one")
def conversion_error():
    bad = random.choice(['int("3.5")', 'int("on")', 'float("2,5")', 'int("")'])
    good = random.sample(['int("12")', 'float("3.5")', "str(45)", "int(7.9)", 'float("8")', "bool(0)"], 3)
    return {
        "type": "mc",
        "text": "Aşağıdaki ifadelerden hangisi çalıştırıldığında <strong>hata verir</strong>?",
        "code": None,
        "options": unique_options(bad, good),
        "answer": bad,
        "solution": f"<code>{e(bad)}</code> ValueError verir: int() yalnızca tam sayı biçimindeki metni, float() "
                    "ise noktalı ondalık biçimini çevirebilir. Ondalık ayırıcı virgül değil noktadır.",
    }
