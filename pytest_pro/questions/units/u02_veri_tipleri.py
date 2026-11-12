"""Ünite 2 - Veri Tipleri ve Tip Dönüşümleri."""
import random

from ..helpers import Wrong, e, err, output_question, unique_options, whys_for_options
from ..registry import register_unit

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


@q("bool() Dönüşümü", verify="output")
def bool_conversion():
    value, result, why, opposite_why = random.choice([
        ("0", "False", "Sıfır sayısı False kabul edilir.",
         "Sıfır False sayılır; yalnızca sıfırdan farklı sayılar True'dur."),
        ("7", "True", "Sıfırdan farklı her sayı True kabul edilir.",
         "Yalnızca sıfır False sayılır; sıfırdan farklı her sayı True'dur."),
        ('""', "False", "Boş metin False kabul edilir.",
         "Boş metin False sayılır; içinde en az bir karakter olan metin True'dur."),
        ('"0"', "True", 'İçinde karakter olan her metin True\'dur; "0" da boş değildir.',
         '"0" bir sayı değil, içinde bir karakter olan metindir; boş olmadığı için True\'dur.'),
        ('" "', "True", "Bir boşluk karakteri içeren metin boş değildir, True'dur.",
         "Boşluk da bir karakterdir; metin boş olmadığı için True'dur."),
        ("0.0", "False", "0.0 sıfıra eşit olduğu için False kabul edilir.",
         "0.0 da sıfırdır; sıfır olan her sayı False sayılır."),
        ("[]", "False", "Boş liste False kabul edilir.",
         "Boş liste False sayılır; en az bir elemanı olan liste True'dur."),
        ("-3", "True", "Negatif sayılar da sıfırdan farklıdır, True kabul edilir.",
         "Yalnızca sıfır False sayılır; negatif sayılar da True'dur."),
        ('"False"', "True", '"False" yazısı bir metindir; boş olmadığı için True\'dur.',
         'Tırnak içindeki "False" mantıksal değer değil, içi dolu bir metindir; bu yüzden True\'dur.'),
        ("0.5", "True", "0.5 sıfırdan farklıdır, True kabul edilir.",
         "Sıfırdan farklı her sayı, kesirli olsa bile True'dur."),
        ("[0]", "True", "İçinde bir eleman olan liste boş değildir, True'dur.",
         "Liste boş değil; içindeki elemanın 0 olması önemli değil, liste True'dur."),
        ("None", "False", "None 'hiçbir şey' anlamına gelir ve False kabul edilir.",
         "None değer yokluğunu gösterir ve False sayılır."),
    ])
    return output_question(
        f"print(bool({value}))", result, f"<code>bool()</code> değerin doğruluk karşılığını verir. {e(why)}",
        wrongs=[
            Wrong("True" if result == "False" else "False", opposite_why),
            Wrong(err("ValueError"), "<code>bool()</code> her değeri True ya da False'a çevirebilir; hata vermez."),
            Wrong("None", "<code>bool()</code> her zaman True ya da False döndürür, None döndürmez."),
        ],
        hint="Python'da hangi değerler 'boş' ya da 'sıfır' sayılır? Bu değer o gruptan mı?",
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
        wrongs=[
            Wrong(str(n * k), "Sayı gibi çarptın; ama <code>input()</code> metin döndürür ve metin * sayı, metni "
                              "tekrarlar."),
            Wrong(err("TypeError"), "Metin * tam sayı geçerli bir işlemdir; metni tekrarlar, hata vermez."),
            Wrong(" ".join([str(n)] * k), "Tekrarlanan metinlerin arasına boşluk konmaz."),
        ],
        text=f"Kod çalıştırıldığında kullanıcı klavyeden <strong>{n}</strong> yazıp Enter'a basıyor. "
             "Ekrana ne yazdırılır?",
        stdin=str(n),
        hint="input() hangi tipte değer döndürür? O tipteki bir değer bir sayıyla çarpılınca ne olur?",
    )


@q("Metin ve Sayı Birleştirme", verify="output")
def str_concat():
    n1, n2 = random.randint(1, 9), random.randint(1, 9)
    correct = f"{n1}{n2}"
    return output_question(
        f'a = "{n1}"\nb = "{n2}"\nprint(a + b)', correct,
        "İki değişken de tırnak içinde olduğu için str tipindedir. Metinlerde <code>+</code> toplama değil "
        f'birleştirme yapar: "{n1}" + "{n2}" = "{correct}".',
        wrongs=[
            Wrong(str(n1 + n2), "Sayı gibi topladın; ama ikisi de tırnak içinde, yani metin. Metinlerde + "
                                "birleştirme yapar."),
            Wrong(f"{n1} {n2}", "+ araya boşluk koymaz; boşluk, print'e virgülle birden fazla değer verilince gelir."),
            Wrong(err("TypeError"), "İki metni + ile birleştirmek hata vermez; hata, metinle sayıyı + ile "
                                    "birleştirmeye çalışınca olur."),
        ],
        hint="a ile b tırnak içinde mi? Öyleyse + ne yapar?",
    )


@q("Metin ve Sayı Birleştirme", verify="error")
def str_plus_int():
    var, label = random.choice([("yas", "Yaşım"), ("puan", "Puanım"), ("sinif", "Sınıfım"), ("adet", "Adet:"),
                                ("no", "Numaram"), ("skor", "Skor:")])
    value = random.randint(9, 99)
    return output_question(
        f'{var} = {value}\nprint("{label} " + {var})', err("TypeError"),
        f"str ile int <code>+</code> ile birleştirilemez. Çözüm: <code>\"{label} \" + str({var})</code>, "
        f"<code>print(\"{label}\", {var})</code> veya <code>f\"{label} {{{var}}}\"</code>.",
        wrongs=[
            Wrong(f"{label} {value}", f"Python sayıyı metne kendiliğinden eklemez; + iki tarafın da metin olmasını "
                                      f"ister. Önce str({var}) ile çevirmek gerekir."),
            Wrong(f"{label}{value}", "Python sayıyı metne kendiliğinden eklemez; + iki tarafın da metin olmasını ister."),
            Wrong(f"{label} + {value}", "+ ekrana yazılmaz; iki değeri birleştirmeye çalışan bir işlemdir."),
        ],
        hint="+ işaretinin iki yanındaki değerlerin tipine bak: ikisi de metin mi?",
    )


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
