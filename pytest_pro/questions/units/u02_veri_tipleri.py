"""Ünite 2 - Veri Tipleri ve Tip Dönüşümleri."""
import ast
import random

from ..codecheck import OK, checker, print_values, same_value
from ..helpers import Wrong, e, err, fill_question, output_question, tf_claim, unique_options, whys_for_options
from ..registry import register_unit
from .u01_temel import UNSET, print_numbers, straight_run

UNIT = register_unit(
    "veri_tipleri", "Veri Tipleri ve Dönüşümler", "Başlangıç",
    "int, float, str, bool; type(), int()/float()/str()/bool() dönüşümleri, input() ile sayı alma.",
    order=2,
)
q = UNIT.question

NOT_TEXT = "Değerin çevresinde tırnak yok; bu bir metin değil."
NOT_BOOL = "bool tipinde yalnızca True ve False değerleri vardır."


def _type_whys(literal, typ):
    """type() sorusunda her yanlış tip seçeneği için açıklama."""
    if literal.startswith('"'):
        reason = "Tırnak içindeki her değer metindir; içinde sayı ya da True yazsa bile tipi str'dir."
        return {t: reason for t in ("int", "float", "bool")}
    if typ == "float":
        return {"int": "Ondalık noktası olan sayılar (0.0 dahil) int değil float'tur.", "str": NOT_TEXT, "bool": NOT_BOOL}
    if typ == "int":
        return {"float": "Ondalık noktası olmayan sayılar int'tir; eksi işareti tipi değiştirmez.",
                "str": NOT_TEXT, "bool": NOT_BOOL}
    return {"str": "True ve False tırnaksız yazıldığında metin değil, mantıksal değerdir.",
            "int": "True ve False hesaplarda 1 ve 0 gibi davranabilir, ama tipleri bool'dur.",
            "float": "True ve False hesaplarda 1 ve 0 gibi davranabilir, ama tipleri bool'dur."}


@q("type() ve Veri Tipleri", verify="output")
def type_func():
    literal, typ = random.choice([
        ("3.14", "float"), ("0.0", "float"), ("-2.5", "float"), ("7.0", "float"),
        ("42", "int"), ("-7", "int"), ("0", "int"), ("100", "int"),
        ('"100"', "str"), ('"3.14"', "str"), ('"True"', "str"), ('"-4"', "str"), ('""', "str"),
        ("True", "bool"), ("False", "bool"),
    ])
    answer = f"<class '{typ}'>"
    note = " Tırnak içindeki her değer, içeriği ne olursa olsun metindir." if literal.startswith('"') else ""
    opts = ["<class 'int'>", "<class 'float'>", "<class 'str'>", "<class 'bool'>"]
    random.shuffle(opts)
    reasons = _type_whys(literal, typ)
    return {
        "type": "mc", "text": "Aşağıdaki kodun çıktısı ne olur?",
        "code": f"x = {literal}\nprint(type(x))", "options": opts, "answer": answer,
        "whys": {f"<class '{t}'>": why for t, why in reasons.items()},
        "hint": "Önce değerin tırnak içinde olup olmadığına, sonra ondalık noktası içerip içermediğine bak.",
        "solution": f"<code>type()</code> değerin tipini döndürür. <code>{e(literal)}</code> değeri "
                    f"{e(answer)} tipindedir.{note}",
    }


@q("Tip Dönüşümleri (int/str)", verify="output")
def str_to_int():
    n1, n2 = random.randint(2, 9), random.randint(10, 50)
    op = random.choice(["+", "*"])
    res = n1 + n2 if op == "+" else n1 * n2
    if op == "+":
        common = [Wrong(f"{n1}{n2}", "Metin birleştirme yaptın; ama <code>int(a)</code> a'yı sayıya çevirdiği için "
                                     "+ burada toplama yapar.")]
    else:
        common = [Wrong(str(n1 + n2), "İşlem toplama değil çarpma (*).")]
    return output_question(
        f'a = "{n1}"\nb = {n2}\nsonuc = int(a) {op} b\nprint(sonuc)', str(res),
        f'<code>a</code> metin ("{n1}") olarak tanımlanmıştır. <code>int(a)</code> ile {n1} sayısına '
        f"dönüşür; {n1} {op} {n2} = {res}.",
        text="Aşağıdaki kod çalıştırıldığında ekrana yazdırılacak <strong>sayısal değeri</strong> giriniz:",
        common_wrongs=common,
        hint="a metin olarak tanımlanmış; işlemde a'nın kendisi mi, int(a) mı kullanılıyor?",
    )


@q("Tip Dönüşümleri (float/int)", verify="output")
def float_int():
    if random.random() < 0.5:
        whole, frac = random.randint(2, 20), random.randint(1, 9)
        return output_question(
            f"x = {whole}.{frac}\nprint(int(x))", str(whole),
            f"<code>int()</code> ondalıklı sayının kesir kısmını atar (yuvarlamaz): int({whole}.{frac}) = {whole}.",
            common_wrongs=[
                Wrong(str(whole + 1), "<code>int()</code> yuvarlamaz; kesir kısmını doğrudan atar."),
                Wrong(f"{whole}.{frac}", "<code>int()</code> sonucu tam sayıdır; kesir kısmı silinir."),
            ],
            hint="int() ondalıklı bir sayıyı yuvarlar mı, yoksa kesir kısmını mı atar?",
        )
    n = random.randint(2, 20)
    return output_question(
        f'x = "{n}"\ny = float(x)\nprint(y)', f"{n}.0",
        f'<code>float("{n}")</code> metni ondalıklı sayıya çevirir; float değerler ekrana {n}.0 biçiminde yazılır.',
        common_wrongs=[Wrong(str(n), "float tipindeki sayılar tam olsa bile ondalık kısmıyla (.0) yazılır.")],
        hint="float() sonucu ekrana yazılırken ondalık kısmı görünür mü?",
    )


BOOL_VALUES = [
    # (değer, sonuç, doğru açıklama, ters sonucu seçene açıklama)
    ("0", False, "Sıfır sayısı False kabul edilir.",
     "Sıfır False sayılır; yalnızca sıfırdan farklı sayılar True'dur."),
    ('""', False, "Boş metin False kabul edilir.",
     "Boş metin False sayılır; içinde en az bir karakter olan metin True'dur."),
    ("0.0", False, "0.0 sıfıra eşit olduğu için False kabul edilir.",
     "0.0 da sıfırdır; sıfır olan her sayı False sayılır."),
    ("[]", False, "Boş liste False kabul edilir.",
     "Boş liste False sayılır; en az bir elemanı olan liste True'dur."),
    ("None", False, "None 'hiçbir şey' anlamına gelir ve False kabul edilir.",
     "None değer yokluğunu gösterir ve False sayılır."),
    ("7", True, "Sıfırdan farklı her sayı True kabul edilir.",
     "Yalnızca sıfır False sayılır; sıfırdan farklı her sayı True'dur."),
    ('"0"', True, 'İçinde karakter olan her metin True\'dur; "0" da boş değildir.',
     '"0" bir sayı değil, içinde bir karakter olan metindir; boş olmadığı için True\'dur.'),
    ('" "', True, "Bir boşluk karakteri içeren metin boş değildir, True'dur.",
     "Boşluk da bir karakterdir; metin boş olmadığı için True'dur."),
    ("-3", True, "Negatif sayılar da sıfırdan farklıdır, True kabul edilir.",
     "Yalnızca sıfır False sayılır; negatif sayılar da True'dur."),
    ('"False"', True, '"False" yazısı bir metindir; boş olmadığı için True\'dur.',
     'Tırnak içindeki "False" mantıksal değer değil, içi dolu bir metindir; bu yüzden True\'dur.'),
    ("0.5", True, "0.5 sıfırdan farklıdır, True kabul edilir.",
     "Sıfırdan farklı her sayı, kesirli olsa bile True'dur."),
    ("[0]", True, "İçinde bir eleman olan liste boş değildir, True'dur.",
     "Liste boş değil; içindeki elemanın 0 olması önemli değil, liste True'dur."),
]


@q("bool() Dönüşümü", verify="output")
def bool_conversion():
    """İki değerin doğruluk karşılığı birlikte sorulur; dört birleşimin hepsi anlamlı bir şıktır (K4)."""
    picks = []
    for _ in range(2):  # her değer için önce sonuç (True/False) eşit olasılıkla seçilir
        want = random.random() < 0.5
        picks.append(random.choice([v for v in BOOL_VALUES if v[1] == want and v not in picks]))
    (v1, r1, why1, opp1), (v2, r2, why2, opp2) = picks
    answer = f"{r1} {r2}"
    wrongs = []
    for a in (True, False):
        for b in (True, False):
            if (a, b) == (r1, r2):
                continue
            if a != r1 and b != r2:
                why = f"İki değeri de ters çevirdin. {opp1} {opp2}"
            elif a != r1:
                why = f"İlk değer yanlış: {opp1}"
            else:
                why = f"İkinci değer yanlış: {opp2}"
            wrongs.append(Wrong(f"{a} {b}", why))
    return output_question(
        f"print(bool({v1}), bool({v2}))", answer,
        f"<code>bool()</code> değerin doğruluk karşılığını verir. <code>bool({e(v1)})</code>: {e(why1)} "
        f"<code>bool({e(v2)})</code>: {e(why2)}",
        wrongs=wrongs,
        hint="Python'da hangi değerler 'boş' ya da 'sıfır' sayılır? Her değeri ayrı ayrı düşün.",
    )


@q("input() ve Tip Dönüşümü", verify="outcome")
def input_concat():
    n = random.randint(4, 9)  # k ile çakışmasın ("22" hem 2*"2" hem 2 ile 2 yan yana)
    k = random.choice([2, 3])
    var = random.choice(["sayi", "girdi", "deger"])
    variant = random.choice(["repeat", "repeat", "add", "convert"])
    text = (f"Kod çalıştırıldığında kullanıcı klavyeden <strong>{n}</strong> yazıp Enter'a basıyor. "
            "Ekrana ne yazdırılır?")
    hint = "input() hangi tipte değer döndürür? O tipteki bir değerle bu işlem yapılınca ne olur?"
    if variant == "repeat":
        correct = str(n) * k
        code = f"{var} = input()\nprint({var} * {k})"
        expl = (f'<code>input()</code> metin döndürür: {var} = "{n}". Metin * {k} işlemi metni {k} kez tekrarlar, bu '
                f"yüzden sonuç {correct} olur. Sayı olarak çarpmak için <code>int(input())</code> gerekir.")
        wrongs = [
            Wrong(str(n * k), "Sayı gibi çarptın; ama <code>input()</code> metin döndürür ve metin * sayı, metni "
                              "tekrarlar."),
            Wrong(" ".join([str(n)] * k), "Tekrarlanan metinlerin arasına boşluk konmaz."),
            Wrong(err("TypeError"), "Metin * tam sayı geçerli bir işlemdir; metni tekrarlar, hata vermez."),
            Wrong(f"{n}{k}", f"* sayıyı metnin sonuna eklemez; metni {k} kez yan yana yazar."),
        ]
        random.shuffle(wrongs)
    elif variant == "add":
        correct = err("TypeError")
        code = f"{var} = input()\nprint({var} + {k})"
        expl = (f'<code>input()</code> metin döndürür: {var} = "{n}". Metin ile sayı <code>+</code> ile toplanamaz ya da '
                "birleştirilemez; TypeError oluşur. Toplamak için <code>int(input())</code> gerekir.")
        wrongs = [
            Wrong(str(n + k), "Sayı gibi topladın; ama <code>input()</code> metin döndürür ve metin + sayı hata verir."),
            Wrong(f"{n}{k}", "Metin + sayı birleştirme yapmaz; + iki tarafın da metin olmasını ister, yoksa hata verir."),
            Wrong(str(n) * k, "Bu, metni tekrarlayan * işleminin sonucu olurdu; burada + kullanılıyor."),
        ]
    else:
        correct = str(n * k)
        code = f"{var} = int(input())\nprint({var} * {k})"
        expl = f"<code>int(input())</code> girilen metni sayıya çevirir: {var} = {n}. Sayı * {k} = {n * k}."
        wrongs = [
            Wrong(str(n) * k, "<code>int()</code> metni sayıya çevirdi; artık * metni tekrarlamaz, sayıyı çarpar."),
            Wrong(err("ValueError"), f'"{n}" tam sayı biçiminde bir metin; int() onu sorunsuz çevirir.'),
            Wrong(str(n + k), "İşlem toplama değil çarpma (*)."),
        ]
    return output_question(code, correct, expl, wrongs=wrongs, text=text, stdin=str(n), hint=hint)


@q("Metin ve Sayı Birleştirme", verify="outcome")
def str_concat():
    n1, n2 = random.randint(1, 9), random.randint(1, 9)
    variant = random.choice(["text", "text", "mixed", "numbers"])
    hint = "a ile b'nin tipine bak: ikisi de metin mi, ikisi de sayı mı, yoksa biri metin biri sayı mı?"
    if variant == "text":
        correct = f"{n1}{n2}"
        code = f'a = "{n1}"\nb = "{n2}"\nprint(a + b)'
        expl = ("İki değişken de tırnak içinde olduğu için str tipindedir. Metinlerde <code>+</code> toplama değil "
                f'birleştirme yapar: "{n1}" + "{n2}" = "{correct}".')
        wrongs = [
            Wrong(str(n1 + n2), "Sayı gibi topladın; ama ikisi de tırnak içinde, yani metin. Metinlerde + "
                                "birleştirme yapar."),
            Wrong(f"{n1} {n2}", "+ araya boşluk koymaz; boşluk, print'e virgülle birden fazla değer verilince gelir."),
            Wrong(err("TypeError"), "İki metni + ile birleştirmek hata vermez; hata, metinle sayıyı + ile "
                                    "birleştirmeye çalışınca olur."),
        ]
    elif variant == "mixed":
        correct = err("TypeError")
        code = f'a = "{n1}"\nb = {n2}\nprint(a + b)'
        expl = (f'a metin ("{n1}"), b ise sayıdır ({n2}). Metin ile sayı <code>+</code> ile birleştirilemez ya da '
                f"toplanamaz; TypeError oluşur. Çözüm: <code>a + str(b)</code> ya da <code>int(a) + b</code>.")
        wrongs = [
            Wrong(f"{n1}{n2}", "Python sayıyı metne kendiliğinden çevirmez; + iki tarafın da aynı türde olmasını ister."),
            Wrong(str(n1 + n2), "a tırnak içinde, yani metin; Python metni kendiliğinden sayıya çevirmez."),
            Wrong(f"{n1} {n2}", "+ araya boşluk koymaz; üstelik metin ile sayı + ile birleştirilemez."),
        ]
    else:
        correct = str(n1 + n2)
        code = f'a = "{n1}"\nb = "{n2}"\nprint(int(a) + int(b))'
        expl = f'<code>int()</code> iki metni de sayıya çevirir; sayılarda + toplama yapar: {n1} + {n2} = {n1 + n2}.'
        wrongs = [
            Wrong(f"{n1}{n2}", "int() metinleri sayıya çevirdiği için + burada birleştirme değil toplama yapar."),
            Wrong(err("ValueError"), "Metinler tam sayı biçiminde; int() onları sorunsuz çevirir."),
            Wrong(f"{n1} {n2}", "+ iki sayıyı toplar; ekrana tek bir sayı yazılır."),
        ]
    return output_question(code, correct, expl, wrongs=wrongs, hint=hint)


STR_INT_LABELS = [("yas", "Yaşım"), ("puan", "Puanım"), ("sinif", "Sınıfım"), ("adet", "Adet:"), ("no", "Numaram"),
                  ("skor", "Skor:")]


@q("Metin ve Sayı Birleştirme", verify="outcome")
def str_plus_int():
    """Hatalı (metin + sayı) ve hatasız (str() ile, virgülle) yazımlar karışık sorulur (K5)."""
    var, label = random.choice(STR_INT_LABELS)
    value = random.randint(9, 99)
    variant = random.choices(["plus", "str", "comma"], weights=[4, 3, 3])[0]
    hint = "Değerler + ile mi, virgülle mi veriliyor? + kullanılıyorsa iki yanı da metin mi?"
    if variant == "plus":
        code, correct = f'{var} = {value}\nprint("{label} " + {var})', err("TypeError")
        expl = (f"str ile int <code>+</code> ile birleştirilemez. Çözüm: <code>\"{label} \" + str({var})</code>, "
                f"<code>print(\"{label}\", {var})</code> veya <code>f\"{label} {{{var}}}\"</code>.")
        wrongs = [
            Wrong(f"{label} {value}", f"Python sayıyı metne kendiliğinden eklemez; + iki tarafın da metin olmasını "
                                      f"ister. Önce str({var}) ile çevirmek gerekir."),
            Wrong(f"{label}{value}", "Python sayıyı metne kendiliğinden eklemez; + iki tarafın da metin olmasını ister."),
            Wrong(f"{label} + {value}", "+ ekrana yazılmaz; iki değeri birleştirmeye çalışan bir işlemdir."),
        ]
    elif variant == "str":
        code, correct = f'{var} = {value}\nprint("{label} " + str({var}))', f"{label} {value}"
        expl = (f"<code>str({var})</code> sayıyı metne çevirir; iki metin <code>+</code> ile birleşir. Etiketin sonundaki "
                "boşluk da yazılır.")
        wrongs = [
            Wrong(err("TypeError"), f"<code>str({var})</code> sayıyı metne çevirdiği için iki taraf da metindir; hata "
                                    "oluşmaz."),
            Wrong(f"{label}{value}", f'Etiket metninin sonunda bir boşluk var ("{label} "); o boşluk da yazılır.'),
            Wrong(f"{label} str({value})", "str() bir fonksiyondur; ekrana çağrının sonucu (metne çevrilmiş sayı) yazılır."),
        ]
    else:
        code, correct = f'{var} = {value}\nprint("{label}", {var})', f"{label} {value}"
        expl = ("print'e virgülle verilen değerler birleştirilmez, ayrı ayrı yazılır; aralarına bir boşluk konur. "
                "Bu yüzden tiplerinin farklı olması sorun değildir.")
        wrongs = [
            Wrong(err("TypeError"), "Virgülle ayrılan değerler birleştirilmez, ayrı ayrı yazılır; tiplerin aynı olması "
                                    "gerekmez."),
            Wrong(f"{label}{value}", "print, virgülle verilen değerlerin arasına bir boşluk koyar."),
            Wrong(f"{label}, {value}", "Virgül ekrana yazılmaz; yalnızca değerleri ayırır."),
        ]
    return output_question(code, correct, expl, wrongs=wrongs, hint=hint)


SAFE_CONVERSIONS = {
    'int("12")': "Tam sayı biçimindeki metni int() sorunsuz çevirir: 12.",
    'float("3.5")': "Noktalı ondalık biçimindeki metni float() çevirir: 3.5.",
    "str(45)": "Her değer str() ile metne çevrilebilir: '45'.",
    "int(7.9)": "int() ondalıklı sayının kesir kısmını atarak çevirir: 7. Hata vermez.",
    'float("8")': "Tam sayı biçimindeki metin de float'a çevrilebilir: 8.0.",
    "bool(0)": "bool() her değeri çevirebilir: bool(0) False olur.",
}


@q("Dönüşüm Hataları", verify="raises_one")
def conversion_error():
    bad = random.choice(['int("3.5")', 'int("on")', 'float("2,5")', 'int("")'])
    wrongs = [Wrong(expr, SAFE_CONVERSIONS[expr]) for expr in random.sample(sorted(SAFE_CONVERSIONS), 3)]
    options = unique_options(bad, wrongs)
    return {
        "type": "mc",
        "text": "Aşağıdaki ifadelerden hangisi çalıştırıldığında <strong>hata verir</strong>?",
        "code": None,
        "options": options,
        "answer": bad,
        "whys": whys_for_options(bad, wrongs, options),
        "hint": "int() ve float() hangi biçimdeki metinleri sayıya çevirebilir? Virgüle ve noktaya dikkat et.",
        "solution": f"<code>{e(bad)}</code> ValueError verir: int() yalnızca tam sayı biçimindeki metni, float() "
                    "ise noktalı ondalık biçimini çevirebilir. Ondalık ayırıcı virgül değil noktadır.",
    }


# ================================================================= yeni şablonlar (ölçme raporu Ö2.1-Ö2.7)
TYPE_LITERALS = [
    ("3.14", "float"), ("0.0", "float"), ("-2.5", "float"), ("7.0", "float"),
    ("42", "int"), ("-7", "int"), ("0", "int"), ("100", "int"),
    ('"100"', "str"), ('"3.14"', "str"), ('"True"', "str"), ('"-4"', "str"), ('""', "str"),
    ("True", "bool"), ("False", "bool"),
]


@q("Tip İddiası (Doğru/Yanlış)", verify="tf_output")
def type_claim():
    """Kazanım: değerin tipini belirler · Bloom: H/A"""
    literal, typ = random.choice(TYPE_LITERALS)
    var = random.choice(["x", "veri", "deger"])
    reasons = _type_whys(literal, typ)
    return tf_claim(
        f"{var} = {literal}\nprint(type({var}))", f"<class '{typ}'>",
        [Wrong(f"<class '{t}'>", why) for t, why in reasons.items()],
        f"<code>type()</code> değerin tipini verir; <code>{e(literal)}</code> değeri {typ} tipindedir. Tırnak içindeki "
        "her değer metindir; ondalık noktası olan sayılar float, olmayanlar int'tir.",
        hint="Önce tırnağa, sonra ondalık noktaya bak.",
    )


INPUT_VARS = {False: ["yas", "sayi", "puan", "adet"], True: ["fiyat", "kilo", "sayi", "mesafe"]}


@q("int(input()) Boşluğu", verify="fill")
def input_int_blank():
    """Kazanım: girdiyi işlemden önce sayıya çevirmesi gerektiğini bilir · Bloom: U"""
    decimal = random.random() < 0.45
    var = random.choice(INPUT_VARS[decimal])
    k = random.randint(1, 9)
    if decimal:
        n = random.randint(10, 99) + random.choice([0.5, 0.25, 0.75])
        conv, expect = "float", str(n + k)
        conv_wrongs = [Wrong("int", f'<code>int()</code> "{n}" gibi ondalıklı bir metni çeviremez; ValueError oluşur.'),
                       Wrong("str", "Metin ile sayı + ile toplanamaz; TypeError oluşur.")]
    else:
        n = random.randint(10, 99)
        conv, expect = "int", str(n + k)
        conv_wrongs = [Wrong("float", f"<code>float()</code> ile toplam {n + k}.0 yazılır; çıktı tam sayı istiyor."),
                       Wrong("str", "Metin ile sayı + ile toplanamaz; TypeError oluşur.")]
    two = random.random() < 0.45
    text = (f"Kod çalıştırıldığında kullanıcı klavyeden <strong>{n}</strong> yazıp Enter'a basıyor. Kod ekrana "
            f"<code>{expect}</code> yazmalı. " + ("Boşlukları doldurun." if two else "Boşluğu doldurun."))
    solution = (f"<code>input()</code> her zaman metin döndürür; toplama yapmadan önce <code>{conv}()</code> ile "
                f"sayıya çevrilir: {n} + {k} = {expect}.")
    hint = "Klavyeden okunan değer hangi tipte gelir? Toplama yapmadan önce neye çevirmen gerekir?"
    if two:
        return fill_question(
            f"{var} = ____(____())\nprint({var} + {k})", [[conv], ["input"]], expect, text, solution, hint=hint,
            wrongs=[conv_wrongs, [Wrong("print", "Klavyeden değer alan fonksiyon print değil; print ekrana yazar.")]],
            stdin=str(n),
        )
    return fill_question(
        f"{var} = ____(input())\nprint({var} + {k})", [[conv]], expect, text, solution, hint=hint,
        wrongs=[conv_wrongs], stdin=str(n),
    )


CONV_NAMES = [("a", "b"), ("metin", "sayi"), ("x", "y")]


@q("Dönüşüm Yönü (Boşluk Doldurma)", verify="fill")
def conv_direction_blank():
    """Kazanım: toplama ile birleştirme arasında tip dönüşümüyle seçim yapar · Bloom: An"""
    m, s = random.choice(CONV_NAMES)
    a, b = random.randint(10, 99), random.randint(2, 9)
    form = random.choices(["add", "mul", "concat", "float"], weights=[20, 15, 35, 30])[0]
    head = f'{m} = "{a}"\n{s} = {b}\n'
    text_err = "Metin ile sayı birlikte kullanılamaz; TypeError oluşur."
    if form == "add":
        code, conv, expect = f"print(____({m}) + {s})", "int", str(a + b)
        wrongs = [Wrong("str", text_err), Wrong("float", f"<code>float()</code> ile sonuç {a + b}.0 olur; çıktı tam "
                                                         "sayı istiyor.")]
    elif form == "mul":
        code, conv, expect = f"print(____({m}) * {s})", "int", str(a * b)
        wrongs = [Wrong("str", f'Metin * sayı metni tekrarlar: "{a}" {b} kez yan yana yazılır.'),
                  Wrong("float", f"<code>float()</code> ile sonuç {a * b}.0 olur; çıktı tam sayı istiyor.")]
    elif form == "float":
        code, conv, expect = f"print(____({m}) + {s})", "float", f"{a + b}.0"
        wrongs = [Wrong("int", f"<code>int()</code> ile sonuç {a + b} olur; çıktıda .0 olması için ondalıklı sayıya "
                               "çevrilmeli."),
                  Wrong("str", text_err)]
    else:
        code, conv, expect = f"print({m} + ____({s}))", "str", f"{a}{b}"
        wrongs = [Wrong("int", f"<code>{s}</code> zaten sayı; <code>int()</code> onu değiştirmez ve metin + sayı yine "
                               "TypeError verir."),
                  Wrong("float", "Metin ile ondalıklı sayı da + ile birleştirilemez; TypeError oluşur.")]
    return fill_question(
        head + code, [[conv]], expect,
        f"Aşağıdaki kod ekrana <code>{e(expect)}</code> yazmalı. Boşluğa gereken dönüşüm fonksiyonunu yazın.",
        "İki sayı + ile toplanır, iki metin + ile yan yana eklenir. Çıktı bir toplam ise metin sayıya "
        "(<code>int</code>/<code>float</code>), yan yana yazılmış bir metin ise sayı metne (<code>str</code>) "
        "çevrilir.",
        hint="Çıktı bir toplam mı, çarpım mı, yoksa yan yana yazılmış metin mi? .0 var mı?",
        wrongs=[wrongs],
    )


@q("Karışık Dönüşüm Çıktısı", verify="output")
def mixed_conv():
    """Kazanım: int, float ve str dönüşümlerinin sonucunu hesaplar · Bloom: U"""
    form = random.choice(["int_float", "str_cat", "int_cut", "float_int"])
    hint = "Her dönüşümün sonucunun tipini ayrı ayrı yaz."
    if form == "int_float":
        n = random.randint(2, 9)
        m = random.randint(1, 9) + random.choice([0.5, 0.25, 0.75])
        code, answer = f'print(int("{n}") + float("{m}"))', str(n + m)
        why = f"<code>int(\"{n}\")</code> {n}, <code>float(\"{m}\")</code> {m} olur; toplam float'tır: {n + m}."
        common = [Wrong(str(int(n + m)), "float ile toplanan int'in sonucu float olur; kesir kısmı kaybolmaz."),
                  Wrong(f"{n}{m}", "int() ve float() metinleri sayıya çevirir; + burada birleştirme değil toplama "
                                   "yapar.")]
    elif form == "str_cat":
        n, k = random.randint(2, 9), random.randint(10, 99)
        code, answer = f'print(str({n}) + "{k}")', f"{n}{k}"
        why = f"<code>str({n})</code> metindir; iki metin + ile yan yana eklenir: \"{n}{k}\"."
        common = [Wrong(str(n + k), f"<code>str({n})</code> metin olduğu için + toplama değil birleştirme yapar."),
                  Wrong(err("TypeError"), "str() sayıyı metne çevirdiği için iki taraf da metindir; hata oluşmaz.")]
    elif form == "int_cut":
        x, d, k = random.randint(2, 20), random.randint(5, 9), random.randint(1, 9)
        code, answer = f'print(int({x}.{d}) + int("{k}"))', str(x + k)
        why = f"<code>int({x}.{d})</code> kesir kısmını atar ({x}); <code>int(\"{k}\")</code> {k} olur: {x + k}."
        common = [Wrong(str(x + 1 + k), "int() yuvarlamaz; kesir kısmını doğrudan atar."),
                  Wrong(f"{x + k}.{d}", "int() sonucu tam sayıdır; kesir kısmı silinir.")]
    else:
        n, x, d = random.randint(2, 9), random.randint(2, 9), random.randint(5, 9)
        code, answer = f'print(float("{n}") + int({x}.{d}))', f"{n + x}.0"
        why = f"<code>float(\"{n}\")</code> {n}.0 olur; float ile int toplanınca sonuç float'tır: {n + x}.0."
        common = [Wrong(str(n + x), "float ile toplanan int'in sonucu float olur; ekrana .0 ile yazılır."),
                  Wrong(f"{n + x + 1}.0", "int() yuvarlamaz; kesir kısmını doğrudan atar.")]
    return output_question(
        code, answer, why,
        common_wrongs=common, norm="sayi", hint=hint,
    )


@q("bool Aritmetiği", verify="output")
def bool_arith():
    """Kazanım: True ve False değerlerinin sayısal karşılığını bilir · Bloom: H/U"""
    n = random.randint(2, 20)
    form = random.choice(["true_add", "false_mul", "two_true", "mixed", "sum"])
    hint = "True ve False hesaplarda hangi sayılar gibi davranır?"
    type_err = Wrong(err("TypeError"), "bool, int'in özel bir türüdür; hesaplarda hata vermez.")
    if form == "true_add":
        code, answer = f"print(True + {n})", str(n + 1)
        common = [Wrong(f"True{n}", "bool metin değildir; birleştirme yapılmaz, toplama yapılır."), type_err,
                  Wrong(str(n), "True hesaplarda 1 değerindedir.")]
    elif form == "false_mul":
        code, answer = f"print(False * {n})", "0"
        common = [Wrong(str(n), "False hesaplarda 0 değerindedir; 0 ile çarpım 0 olur."), type_err,
                  Wrong("False", "Sonuç bir sayıdır; bool ile sayının çarpımı int verir.")]
    elif form == "two_true":
        code, answer = f"print(True + True + {n})", str(n + 2)
        common = [Wrong(str(n + 1), "İki tane True var; her biri 1 değerindedir."), type_err,
                  Wrong(f"TrueTrue{n}", "bool metin değildir; birleştirme yapılmaz, toplama yapılır.")]
    elif form == "mixed":
        code, answer = f"print({n} * True - False)", str(n)
        common = [Wrong(str(n - 1), "False hesaplarda 0 değerindedir; çıkarınca sayı değişmez."), type_err,
                  Wrong("0", f"True 1 değerindedir; {n} * True = {n}.")]
    else:
        values = [random.choice([True, False]) for _ in range(random.randint(3, 6))]
        values[random.randrange(len(values))] = True
        code, answer = f"print(sum({values}))", str(sum(values))
        common = [Wrong(str(len(values)), "sum() elemanların değerlerini toplar; False 0 sayılır."),
                  Wrong("True", "sum() bir sayı döndürür; True değerleri 1 olarak toplanır."), type_err]
    return output_question(
        code, answer,
        "<code>bool</code>, <code>int</code>'in özel bir türüdür: hesaplarda True 1, False 0 gibi davranır. "
        f"Sonuç: {answer}.",
        common_wrongs=common, norm="sayi", hint=hint,
    )


TSUM_NAMES = [("a", "b"), ("sayi1", "sayi2"), ("x", "y")]


@q("Metinleri Sayıya Çevirip Toplama (Kod Yazma)")
def write_text_sum():
    """Kazanım: metin olarak verilen sayıları int() ile çevirip toplar · Bloom: O"""
    v1, v2 = random.choice(TSUM_NAMES)
    s1, s2 = str(random.randint(10, 99)), str(random.randint(1, 99))
    return {
        "type": "code",
        "text": (
            f"Klavyeden okunan değerler gibi, iki sayı <strong>metin</strong> olarak verilmiş: <code>{v1} = "
            f"\"{s1}\"</code> ve <code>{v2} = \"{s2}\"</code>. Kodunuz bu iki satırla başlasın. Ardından bu iki "
            f"değeri <strong>tam sayıya</strong> çevirip toplamlarını yazdırın (çıktı: <code>{int(s1) + int(s2)}"
            "</code>). Sonucu elle yazmayın; değişkenleri kullanın."
        ),
        "code": None,
        "check": {"kind": "text_sum", "v1": v1, "v2": v2, "s1": s1, "s2": s2},
        "answer": f'{v1} = "{s1}"\n{v2} = "{s2}"\nprint(int({v1}) + int({v2}))',
        "hint": "Metinler + ile toplanmaz, yan yana eklenir. Toplamadan önce ne yapmalısın?",
        "solution": "<code>int()</code> metni tam sayıya çevirir; iki sayı + ile toplanır. Çevirmeden yazılan "
                    "<code>a + b</code> metinleri yan yana ekler.",
    }


CELSIUS_VALUES = [-10, -5, 0, 5, 10, 15, 20, 25, 30, 35, 37, 40, 45, 50, 100]


@q("Sıcaklık Dönüşümü (Kod Yazma)")
def write_celsius():
    """Kazanım: formülü Python ifadesine çevirir · Bloom: O"""
    var = random.choice(["c", "celsius", "derece"])
    c = random.choice(CELSIUS_VALUES)
    f = c * 9 / 5 + 32
    shown_f = int(f) if f == int(f) else f
    return {
        "type": "code",
        "text": (
            f"<code>{var}</code> değişkenine <strong>{c}</strong> atayın ve bu Celsius sıcaklığının Fahrenheit "
            f"karşılığını <strong>F = C × 9 / 5 + 32</strong> formülüyle hesaplayıp yazdırın (sonuç: {shown_f}). "
            "Sonucu elle hesaplamayın; değişkeni kullanın."
        ),
        "code": None,
        "check": {"kind": "celsius", "var": var, "c": c},
        "answer": f"{var} = {c}\nprint({var} * 9 / 5 + 32)",
        "hint": "Formülü olduğu gibi yaz; Python çarpma ve bölmeyi toplamadan önce yapar.",
        "solution": "Formül Python'a <code>c * 9 / 5 + 32</code> (ya da <code>1.8 * c + 32</code>) olarak yazılır. "
                    "<code>/</code> sonucu float olduğu için ekrana ondalıklı yazılabilir; değer aynıdır.",
    }


# ================================================================= denetleyiciler
def _node_value(node, tr):
    """İfadenin değeri; sum([a, b]) / sum((a, b)) biçimi de (elemanlar sayıysa) hesaplanır."""
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "sum"
            and len(node.args) == 1 and not node.keywords and isinstance(node.args[0], (ast.List, ast.Tuple))):
        items = [tr.try_value(item, UNSET) for item in node.args[0].elts]
        if items and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in items):
            return sum(items)
        return UNSET
    return tr.try_value(node, UNSET)


def _mixes_text_and_number(node, tr):
    """İfadede bir tarafı metin, öbür tarafı sayı olan bir + var mı? (TypeError verecek toplama)"""
    for sub in ast.walk(node):
        if isinstance(sub, ast.BinOp) and isinstance(sub.op, ast.Add):
            kinds = {type(tr.try_value(side, UNSET)) for side in (sub.left, sub.right)}
            if str in kinds and (int in kinds or float in kinds):
                return True
    return False


def _printed_values(prints):
    """Her print satırının yazdırdığı değerler (etiketler hariç, metinler sayıya çevrilmez)."""
    return [[_node_value(n, tr) for n in print_values(call)] for call, tr in prints]


def _flat(lines):
    return [v for vals in lines for v in vals]


@checker("text_sum")
def check_text_sum(tree, p):
    """v1 = "s1", v2 = "s2" (metin); int ile çevrilip toplamı yazdırılır."""
    v1, v2, s1, s2 = p["v1"], p["v2"], p["s1"], p["s2"]
    names = f"<code>{v1}</code> ve <code>{v2}</code>"
    prints, firsts = straight_run(tree)
    if firsts.get(v1) != s1 or firsts.get(v2) != s2:
        return False, (f"{names} değişkenlerine sayılar <strong>metin</strong> olarak (tırnak içinde) atanmalı: "
                       f"<code>{v1} = \"{s1}\"</code>.")
    values = _flat(_printed_values(prints))
    if not values:
        return False, "Toplamı <code>print()</code> ile yazdır."
    if len(values) > 1:
        return False, "Yalnızca toplamı yazdır (yanına açıklama metni ekleyebilirsin)."
    value, want = values[0], int(s1) + int(s2)
    if value == s1 + s2:
        return False, (f"Metinler + ile toplanmaz, yan yana eklenir: {s1 + s2}. Önce <code>int()</code> ile sayıya "
                       "çevir.")
    if isinstance(value, float) and same_value(value, want):
        return False, f"Tam sayı istendi; <code>float()</code> kullanınca {want}.0 yazılır. <code>int()</code> kullan."
    if value == int(s1 + s2):
        return False, "Metinleri önce birleştirip sonra çevirdin; her birini ayrı ayrı <code>int()</code> ile çevir."
    if value is UNSET and any(_mixes_text_and_number(n, tr) for call, tr in prints for n in print_values(call)):
        return False, ("Metin ile sayı + ile toplanamaz (TypeError oluşur); iki değeri de <code>int()</code> ile "
                       "çevir.")
    if not (isinstance(value, int) and value == want):
        return False, "Yazdırılan değer iki sayının toplamı değil; işlemi kontrol et."
    alt_prints, _ = straight_run(tree, {v1: "23", v2: "9"})
    alt = _flat(_printed_values(alt_prints))
    if alt != [32]:
        return False, f"Sonucu elle yazma; {names} değişkenlerini kullan. Değerler değişince sonuç da değişmeli."
    return True, OK


TRUNCATED_NOTE = ("Sonucun kesir kısmı atılıyor (örneğin 7 derece için 44.6 yerine 44 çıkar); <code>//</code> ya da "
                  "<code>int()</code> yerine <code>/</code> kullan.")


@checker("celsius")
def check_celsius(tree, p):
    """var = c; c * 9 / 5 + 32 değeri yazdırılır (eşdeğer yazımlar serbest, değer üzerinden)."""
    var, c = p["var"], p["c"]
    prints, firsts = straight_run(tree)
    if not same_value(firsts.get(var), c):
        return False, f"<code>{var}</code> değişkenine {c} atanmamış."
    values = _flat(print_numbers(call, tr) for call, tr in prints)
    if not values:
        return False, "Sonucu <code>print()</code> ile yazdır."
    if len(values) > 1:
        return False, "Yalnızca Fahrenheit değerini yazdır (yanına açıklama metni ekleyebilirsin)."
    value = values[0]
    if not same_value(value, c * 9 / 5 + 32):
        if same_value(value, c * 9 / 5):
            return False, "32'yi eklemeyi unutma."
        if same_value(value, c * 5 / 9 + 32):
            return False, "Formülde 9 / 5 olmalı; kesri ters yazdın."
        if isinstance(value, (int, float)) and same_value(value, int(c * 9 / 5 + 32)):
            return False, TRUNCATED_NOTE
        return False, "Sonuç formülün değerini vermiyor; işlem önceliğini ve parantezleri kontrol et."
    # İkinci deneme değeri 5'in katı değil: // ya da int() ile kesri atan yazımlar c = 45 gibi değerlerde
    # tesadüfen doğru sonuç verir, burada yakalanır.
    for alt in (c + 10, 7):
        alt_prints, _ = straight_run(tree, {var: alt})
        alt_values = _flat(print_numbers(call, tr) for call, tr in alt_prints)
        want = alt * 9 / 5 + 32
        if len(alt_values) == 1 and not same_value(alt_values[0], want) and isinstance(alt_values[0], (int, float)) \
                and same_value(alt_values[0], int(want)):
            return False, TRUNCATED_NOTE
        if len(alt_values) != 1 or not same_value(alt_values[0], want):
            return False, (f"Sonucu elle yazma; <code>{var}</code> değişkeniyle hesapla. Değer değişince sonuç da "
                           "değişmeli.")
    return True, OK
