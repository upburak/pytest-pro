"""Ünite 1 - Temel Giriş/Çıkış ve Değişkenler."""
import random

from ..helpers import PEOPLE, STR_VALUES, e, output_question, shown, tf_question, unique_options
from ..registry import register_unit

UNIT = register_unit(
    "temel", "Temel Giriş/Çıkış ve Değişkenler", "Başlangıç",
    "print() ve parametreleri, input(), değişken tanımlama ve adlandırma, f-string, çoklu atama.",
    order=1,
)
q = UNIT.question


@q("Print Parametreleri (sep)", verify="output")
def print_sep():
    w1, w2 = random.sample(STR_VALUES, 2)
    sep = random.choice(["-", "*", "#", "...", "/", "_"])
    return output_question(
        f'print("{w1}", "{w2}", sep="{sep}")', f"{w1}{sep}{w2}",
        f'<code>sep="{e(sep)}"</code> parametresi, print\'e verilen değerlerin arasına "{e(sep)}" koyar. '
        "Varsayılan ayırıcı tek boşluktur.",
        wrongs=[f"{w1} {w2}", f"{w1}{w2}{sep}", f"{w1} {sep} {w2}"],
    )


@q("Print Parametreleri (end)", verify="output")
def print_end():
    w1, w2 = random.sample(STR_VALUES, 2)
    end = random.choice(["", " ", "-", "***", " | "])
    return output_question(
        f'print("{w1}", end="{end}")\nprint("{w2}")', f"{w1}{end}{w2}",
        "<code>end</code> parametresi print'in sonuna eklenecek metni belirler; varsayılanı yeni satırdır "
        f"(<code>\\n</code>). Burada sona {e(shown(end))} eklendiği için ikinci print aynı satırdan devam eder.",
        wrongs=[f"{w1}\n{w2}", f"{w1} {w2}", f"{w1}{w2}", f"{w1}{end}\n{w2}", f"{w2}{end}{w1}"],
    )


@q("f-string Kullanımı", verify="output")
def fstring():
    vname = random.choice(["ad", "kullanici", "isim"])
    val = random.choice(PEOPLE)
    age = random.randint(14, 18)
    return output_question(
        f'{vname} = "{val}"\nyas = {age}\nprint(f"Merhaba {{{vname}}}, yasiniz: {{yas}}")',
        f"Merhaba {val}, yasiniz: {age}",
        "f-string içinde süslü parantez <code>{}</code> içindeki değişkenler kendi değerleriyle değiştirilir.",
        wrongs=[f"Merhaba {{{vname}}}, yasiniz: {{yas}}", f"Merhaba {vname}, yasiniz: yas",
                f'f"Merhaba {val}, yasiniz: {age}"'],
        text="Aşağıdaki f-string kodunun ekran çıktısı aşağıdakilerden hangisidir?",
    )


@q("input() Veri Tipi")
def input_type():
    return tf_question(
        ["Python'da <code>input()</code> fonksiyonu kullanıcıdan alınan veriyi her zaman "
         "<strong>str (metin)</strong> tipinde döndürür."],
        ["Python'da <code>input()</code> fonksiyonu kullanıcı bir sayı girdiğinde bunu otomatik olarak "
         "<strong>int (tam sayı)</strong> tipine dönüştürür."],
        "<code>input()</code> ile alınan her girdi str türündedir. Sayısal işlem için <code>int()</code> veya "
        "<code>float()</code> dönüşümü gerekir.",
        code='veri = input("Bir şey giriniz: ")',
    )


@q("Değişken Adlandırma", verify="identifier")
def var_name():
    valid = random.choice(["ogrenci_no", "_sayac", "toplam2", "adSoyad", "yas_1", "not_ortalamasi"])
    invalid = random.sample(["2sayi", "ogrenci no", "ad-soyad", "class", "for", "toplam$", "1_deger", "if"], 3)
    return {
        "type": "mc",
        "text": "Aşağıdakilerden hangisi Python'da <strong>geçerli</strong> bir değişken adıdır?",
        "code": None,
        "options": unique_options(valid, invalid),
        "answer": valid,
        "solution": "Değişken adları harf veya alt çizgi (_) ile başlar; yalnızca harf, rakam ve _ içerebilir. "
                    "Boşluk, - ve $ gibi işaretler kullanılamaz; <code>class</code>, <code>for</code>, "
                    "<code>if</code> gibi anahtar kelimeler değişken adı olamaz.",
    }


@q("Değişken Atama", verify="output")
def reassign():
    n1, n2 = random.sample(range(2, 30), 2)
    return output_question(
        f"a = {n1}\nb = a\na = {n2}\nprint(b)", str(n1),
        f"<code>b = a</code> satırında b, a'nın <strong>o anki</strong> değerini ({n1}) alır. "
        "a'ya sonradan yeni değer atanması b'yi değiştirmez.",
        wrongs=[str(n2), str(n1 + n2), "a"],
    )


@q("Çoklu Atama", verify="output")
def swap():
    x, y = random.sample(range(1, 20), 2)
    return output_question(
        f"a, b = {x}, {y}\na, b = b, a\nprint(a, b)", f"{y} {x}",
        "<code>a, b = b, a</code> satırında önce sağ taraf hesaplanır, sonra değerler aynı anda atanır; "
        f"böylece a ile b yer değiştirir: a = {y}, b = {x}.",
        wrongs=[f"{x} {y}", f"{y} {y}", f"{x} {x}"],
    )


@q("Değişken & Aritmetik (Kod Yazma)")
def write_mult():
    v1 = random.choice(["sayi1", "a", "x"])
    v2 = random.choice(["sayi2", "b", "y"])
    n1, n2 = random.randint(5, 20), random.randint(2, 5)
    return {
        "type": "code",
        "text": (
            "Şu adımları gerçekleştiren Python kodunu yazınız:<br>"
            f"1. <code>{v1}</code> adında bir değişken tanımlayıp <strong>{n1}</strong> değerini atayın.<br>"
            f"2. <code>{v2}</code> adında bir değişken tanımlayıp <strong>{n2}</strong> değerini atayın.<br>"
            "3. Bu iki değişkenin çarpımını <code>print()</code> ile ekrana yazdırın."
        ),
        "code": None,
        "check": {"kind": "mult", "v1": v1, "v2": v2, "n1": n1, "n2": n2},
        "answer": f"{v1} = {n1}\n{v2} = {n2}\nprint({v1} * {v2})",
        "solution": "Değişkenlere değer atanır, çarpım <code>*</code> operatörüyle yapılıp <code>print()</code> "
                    "ile yazdırılır.",
    }
