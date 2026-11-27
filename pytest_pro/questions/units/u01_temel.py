"""Ünite 1 - Temel Giriş/Çıkış ve Değişkenler."""
import ast
import random
import re

from ..codecheck import OK, Tracker, assigned_names, checker, find_prints, is_print, print_values, same_value
from ..helpers import (
    PEOPLE,
    STR_VALUES,
    Wrong,
    code_options_question,
    e,
    fill_question,
    output_question,
    shown,
    tf_claim,
    tf_question,
    unique_options,
    whys_for_options,
)
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
        wrongs=[
            Wrong(f"{w1} {w2}", "Varsayılan ayırıcıyı (boşluk) yazdın; ama burada <code>sep</code> ile başka bir "
                                "ayırıcı verilmiş."),
            Wrong(f"{w1}{w2}{sep}", "<code>sep</code> değerlerin sonuna değil, <strong>arasına</strong> konur."),
            Wrong(f"{w1} {sep} {w2}", "<code>sep</code> boşluğun yerine geçer; ayırıcının çevresine ayrıca boşluk "
                                      "eklenmez."),
        ],
        hint="<code>sep</code> parametresinin değerlerin neresine konduğunu düşün.",
    )


@q("Print Parametreleri (end)", verify="output")
def print_end():
    w1, w2 = random.sample(STR_VALUES, 2)
    end = random.choice(["", " ", "-", "***", " | "])
    return output_question(
        f'print("{w1}", end="{end}")\nprint("{w2}")', f"{w1}{end}{w2}",
        "<code>end</code> parametresi print'in sonuna eklenecek metni belirler; varsayılanı yeni satırdır "
        f"(<code>\\n</code>). Burada sona {e(shown(end))} eklendiği için ikinci print aynı satırdan devam eder.",
        wrongs=[
            Wrong(f"{w1}\n{w2}", "Her print'in yeni satıra geçtiğini düşündün; ama ilk print'te <code>end</code> "
                                 "değiştirildiği için alt satıra geçilmez."),
            Wrong(f"{w1} {w2}", "Araya kendiliğinden boşluk girmez; sona yalnızca <code>end</code> ile verilen metin "
                                "eklenir."),
            Wrong(f"{w1}{w2}", "<code>end</code> ile verilen metni atladın; o metin ilk kelimenin hemen arkasına "
                               "yazılır."),
            Wrong(f"{w1}{end}\n{w2}", "<code>end</code> yeni satırın <strong>yerine</strong> geçer; ikisi birden "
                                      "yazılmaz."),
            Wrong(f"{w2}{end}{w1}", "print komutları yukarıdan aşağı sırayla çalışır; ilk yazılan ilk kelimedir."),
        ],
        hint="İlk print'in sonunda normalde ne olur, burada onun yerine ne yazılıyor?",
    )


@q("f-string Kullanımı", verify="output")
def fstring():
    vname = random.choice(["ad", "kullanici", "isim"])
    val = random.choice(PEOPLE)
    age = random.randint(14, 18)
    return output_question(
        f'{vname} = "{val}"\nyas = {age}\nprint(f"Merhaba {{{vname}}}, yaşınız: {{yas}}")',
        f"Merhaba {val}, yaşınız: {age}",
        "f-string içinde süslü parantez <code>{}</code> içindeki değişkenler kendi değerleriyle değiştirilir.",
        wrongs=[
            Wrong(f"Merhaba {{{vname}}}, yaşınız: {{yas}}", "Metnin başındaki <code>f</code> harfi süslü parantezleri "
                                                           "etkin hâle getirir; parantezler olduğu gibi yazılmaz."),
            Wrong(f"Merhaba {vname}, yaşınız: yas", "Parantez içindeki ad değişkenin <strong>değeriyle</strong> "
                                                   "değiştirilir, adının kendisi yazılmaz."),
            Wrong(f'f"Merhaba {val}, yaşınız: {age}"', "<code>f</code> ve tırnaklar metnin yazımına aittir; ekrana "
                                                      "yalnızca metnin içi çıkar."),
        ],
        text="Aşağıdaki f-string kodunun ekran çıktısı aşağıdakilerden hangisidir?",
        hint="Metnin başındaki f harfinin süslü parantezlere ne yaptığını düşün.",
    )


@q("input() Veri Tipi")
def input_type():
    return tf_question(
        [("Python'da <code>input()</code> fonksiyonu kullanıcıdan alınan veriyi her zaman "
          "<strong>str (metin)</strong> tipinde döndürür.",
          "Kullanıcı sayı yazsa bile input() bunu metin olarak döndürür; dönüşümü biz yaparız."),
         ("Kullanıcı klavyeden 25 yazarsa <code>input()</code> sonucu <code>\"25\"</code> metnidir.",
          "input() girilen her şeyi metin olarak döndürür; 25 de \"25\" olur."),
         ("<code>input()</code> ile alınan bir sayıyla toplama yapmak için önce <code>int()</code> ya da "
          "<code>float()</code> ile dönüştürmek gerekir.",
          "input() metin döndürdüğü için sayı gibi kullanmadan önce dönüştürmek gerekir."),
         ("<code>input(\"Adınız: \")</code> komutu parantez içindeki metni ekrana yazar ve kullanıcının "
          "girişini bekler.",
          "Parantez içindeki metin kullanıcıya gösterilen bir istem (soru) metnidir."),
         ("Kullanıcı tam sayı yazarsa <code>yas = int(input())</code> satırından sonra yas değişkeni int "
          "tipindedir.",
          "int() metni tam sayıya çevirir; sonuç değişkene int olarak atanır."),
         ("<code>type(input())</code> ifadesi, kullanıcı ne yazarsa yazsın <code>&lt;class 'str'&gt;</code> "
          "verir.",
          "input() her zaman str döndürdüğü için tipi her durumda str'dir.")],
        [("Python'da <code>input()</code> fonksiyonu kullanıcı bir sayı girdiğinde bunu otomatik olarak "
          "<strong>int (tam sayı)</strong> tipine dönüştürür.",
          "input() hiçbir dönüşüm yapmaz; sayı da olsa metin döndürür."),
         ("<code>input()</code> sonucu her zaman int tipindedir.",
          "input() her zaman str döndürür; int'e çevirmek için int() gerekir."),
         ("Kullanıcı 3.5 yazarsa <code>input()</code> float tipinde bir değer döndürür.",
          "input() 3.5'i de metin olarak döndürür: \"3.5\". float() ile çevirmek gerekir."),
         ("<code>sayi = input()</code> satırından sonra <code>sayi + 1</code> işlemi hatasız çalışır.",
          "sayi bir metindir; metin ile sayı + ile toplanamaz ve TypeError oluşur."),
         ("<code>input(\"Yaşınız: \")</code> komutu parantez içindeki metni değişkene atar.",
          "Parantez içindeki metin yalnızca ekrana yazılan istemdir; değişkene kullanıcının yazdığı atanır."),
         ("<code>input()</code> çalıştığında program kullanıcıyı beklemeden devam eder.",
          "input() kullanıcı Enter'a basana kadar programı bekletir.")],
        "<code>input()</code> ile alınan her girdi str türündedir. Sayısal işlem için <code>int()</code> veya "
        "<code>float()</code> dönüşümü gerekir.",
        hint="Sayıyla işlem yapmak için input()'tan sonra neden int() yazdığımızı hatırla.",
    )


INVALID_NAMES = {
    "2sayi": "Rakamla başlıyor; değişken adları harf ya da _ ile başlamalı.",
    "ogrenci no": "İçinde boşluk var; boşluk yerine _ kullanılır (ogrenci_no).",
    "ad-soyad": "Tire (-) çıkarma işaretidir, adda kullanılamaz; ad_soyad yazılır.",
    "class": "class, Python'un ayrılmış anahtar kelimesidir; değişken adı olamaz.",
    "for": "for, Python'un ayrılmış anahtar kelimesidir; değişken adı olamaz.",
    "toplam$": "$ gibi özel işaretler adda kullanılamaz; yalnızca harf, rakam ve _ olabilir.",
    "1_deger": "Rakamla başlıyor; değişken adları harf ya da _ ile başlamalı.",
    "if": "if, Python'un ayrılmış anahtar kelimesidir; değişken adı olamaz.",
}


@q("Değişken Adlandırma", verify="identifier")
def var_name():
    valid = random.choice(["ogrenci_no", "_sayac", "toplam2", "adSoyad", "yas_1", "not_ortalamasi"])
    wrongs = [Wrong(name, INVALID_NAMES[name]) for name in random.sample(sorted(INVALID_NAMES), 3)]
    options = unique_options(valid, wrongs)
    return {
        "type": "mc",
        "text": "Aşağıdakilerden hangisi Python'da <strong>geçerli</strong> bir değişken adıdır?",
        "code": None,
        "options": options,
        "answer": valid,
        "whys": whys_for_options(valid, wrongs, options),
        "hint": "Her seçeneğin ilk karakterine ve içinde boşluk ya da işaret olup olmadığına bak.",
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
        wrongs=[
            Wrong(str(n2), "b'nin a'ya bağlı kaldığını düşündün; ama b, atandığı andaki değeri kopyalar ve a "
                           "sonradan değişse de aynı kalır."),
            Wrong(str(n1 + n2), "Kodda toplama yok; her atama değişkenin eski değerinin yerine yenisini koyar."),
            Wrong("a", "print(b) b'nin değerini yazar; b'ye a'nın adı değil, o anki değeri atanmıştır."),
        ],
        hint="b = a satırı çalıştığında a'nın değeri neydi? Sonraki satır b'ye dokunuyor mu?",
    )


@q("Çoklu Atama", verify="output")
def swap():
    x, y = random.sample(range(1, 20), 2)
    return output_question(
        f"a, b = {x}, {y}\na, b = b, a\nprint(a, b)", f"{y} {x}",
        "<code>a, b = b, a</code> satırında önce sağ taraf hesaplanır, sonra değerler aynı anda atanır; "
        f"böylece a ile b yer değiştirir: a = {y}, b = {x}.",
        wrongs=[
            Wrong(f"{x} {y}", "İkinci satırı atladın; o satır a ile b'nin değerlerini yer değiştirir."),
            Wrong(f"{y} {y}", "Atamaları tek tek yaptığını düşündün (önce a = b, sonra b = a). Python sağ tarafı "
                              "önce hesaplar, sonra ikisini aynı anda atar."),
            Wrong(f"{x} {x}", "Atamaları sırayla yapıp ilk değeri ikisine de verdin. Sağ taraf önce bütünüyle "
                              "hesaplanır, sonra atama yapılır."),
        ],
        hint="İkinci satırda önce sağ taraf (b, a) hesaplanır; o anda a ve b neydi?",
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
        "hint": "Üç satır yeterli: iki atama ve bir print. Çarpma işareti * dır.",
        "solution": "Değişkenlere değer atanır, çarpım <code>*</code> operatörüyle yapılıp <code>print()</code> "
                    "ile yazdırılır.",
    }


@q("Print Parametreleri (Boşluk Doldurma)", verify="fill")
def fill_print_params():
    w1, w2, w3 = random.sample(STR_VALUES, 3)
    sep = random.choice(["-", "*", "#", "/", "+", "_"])
    end = random.choice(["!", "...", "?", ":", ";", "="])
    params = [("sep", sep), ("end", end)]
    random.shuffle(params)
    hidden = random.choice([{"sep", "end"}, {"sep"}, {"end"}])  # bazen yalnızca bir parametre boş bırakılır
    args = ", ".join(f'{"____" if name in hidden else name}="{value}"' for name, value in params)
    expect = f"{w1}{sep}{w2}{end}{w3}"
    return fill_question(
        f'print("{w1}", "{w2}", {args})\nprint("{w3}")',
        [[name] for name, _ in params if name in hidden],
        expect,
        f"Aşağıdaki kod ekrana tek satırda <code>{e(expect)}</code> yazdırmalı. "
        + ("Boşluklara gereken parametre adlarını yazın." if len(hidden) == 2
           else "Boşluğa gereken parametre adını yazın."),
        f'<code>sep="{e(sep)}"</code> değerlerin <strong>arasına</strong> "{e(sep)}" koyar; '
        f'<code>end="{e(end)}"</code> ise satırın <strong>sonuna</strong> yeni satır yerine "{e(end)}" ekler. '
        "Bu yüzden ikinci print aynı satırdan devam eder.",
        hint="Değerlerin arasına konan ayırıcıyı hangi parametre belirler? Satırın sonuna eklenen metni hangisi?",
    )


# ================================================================= yeni şablonlar (ölçme raporu Ö1.1-Ö1.7)
COMMENT_WORDS = ["Elma", "Armut", "Kiraz", "Muz", "Nar", "Erik", "İncir"]


@q("Yorum Satırları", verify="output")
def comments():
    """Kazanım: # işaretinden sonrasının çalıştırılmadığını bilir · Bloom: H/U"""
    full, real, tail, nospace, inner = random.sample(COMMENT_WORDS, 5)
    in_string = random.random() < 0.3  # tırnak içindeki # yorum başlatmaz
    shown_text = f"{real} # {inner.lower()}" if in_string else real
    lines = [f'# print("{full}")', f'print("{shown_text}")  # print("{tail}")', f'#print("{nospace}")']
    random.shuffle(lines)
    common = [
        Wrong(full, "<code>#</code> ile başlayan satırın tamamı yorumdur; içinde print yazsa da çalışmaz."),
        Wrong(nospace, "<code>#</code> ile kod arasında boşluk olmasa da satır yorumdur ve çalışmaz."),
        Wrong(f"{shown_text} {tail}", "Satırdaki <code>#</code> işaretinden sonrası yorumdur; o print çalışmaz."),
        Wrong(f"{shown_text}{tail}", "Satırdaki <code>#</code> işaretinden sonrası yorumdur; o print çalışmaz."),
    ]
    if in_string:
        common.append(Wrong(real, "Tırnak içindeki <code>#</code> metnin bir parçasıdır, yorum başlatmaz; "
                                  "metnin tamamı yazılır."))
    return output_question(
        "\n".join(lines), shown_text,
        "<code>#</code> işaretinden satırın sonuna kadar olan kısım yorumdur ve çalıştırılmaz; satırın başındaysa "
        "satırın tamamı yorum olur. Tırnak içindeki <code>#</code> ise metnin bir parçasıdır.",
        common_wrongs=common, norm="metin",
        hint="<code>#</code> işaretinden sonra satırın sonuna kadar olan kısım çalışır mı? Tırnak içindeki "
             "<code>#</code> de yorum mu başlatır?",
    )


SEP_CHOICES = ["-", "*", "", ", ", "+"]
END_CHOICES = ["!", "", " ", "...", "?"]


@q("sep ve end Birlikte (Doğru/Yanlış)", verify="tf_output")
def sep_end_claim():
    """Kazanım: sep ve end parametrelerinin birlikte etkisini izler · Bloom: U"""
    words = random.sample(PEOPLE, random.choice([3, 4]))
    first, last = words[:-1], words[-1]
    sep, end = random.choice(SEP_CHOICES), random.choice(END_CHOICES)
    kwargs = [f'sep="{sep}"', f'end="{end}"']
    random.shuffle(kwargs)
    args = ", ".join(f'"{w}"' for w in first)
    line1 = sep.join(first)
    newline = [] if end == " " else [  # sondaki boşluk alt alta yazılan iddiada görünmez
        Wrong(line1 + end + "\n" + last, "<code>end</code> yeni satırın <strong>yerine</strong> geçer; ilk print "
                                        "alt satıra inmez, ikinci print aynı satırdan devam eder.")]
    return tf_claim(
        f'print({args}, {", ".join(kwargs)})\nprint("{last}")',
        line1 + end + last,
        newline + [
         Wrong(" ".join(first) + end + last, f"<code>sep</code> verildiği için değerlerin arasına boşluk değil "
                                             f"{e(shown(sep))} konur."),
         Wrong(sep.join(words) + end, "<code>sep</code> yalnızca aynı print'e verilen değerlerin arasına girer; "
                                      "<code>end</code> ise ilk print'in sonuna eklenir."),
         Wrong(end.join(first) + sep + last, "<code>sep</code> ile <code>end</code> yer değiştirmiş: sep değerlerin "
                                             "arasına, end ise satırın sonuna gelir.")],
        f"<code>sep</code> ({e(shown(sep))}) ilk print'teki değerlerin arasına, <code>end</code> ({e(shown(end))}) "
        "ise satırın sonuna yeni satır yerine eklenir; bu yüzden ikinci print aynı satırdan devam eder.",
        hint="sep nereye, end nereye eklenir? İkinci print hangi satırdan başlar?",
    )


FSTRING_SECOND = [("yas", (14, 18), "yaşım"), ("sinif", (9, 12), "sınıfım"), ("puan", (50, 100), "puanım")]


@q("f-string Tamamlama (Boşluk Doldurma)", verify="fill")
def fstring_blank():
    """Kazanım: f-string sözdizimini kurar · Bloom: U"""
    v1 = random.choice(["ad", "isim", "kullanici"])
    v2, (lo, hi), label = random.choice(FSTRING_SECOND)
    name, value = random.choice(PEOPLE), random.randint(lo, hi)
    shape = random.choice(["Benim adım {A}, {L} {B}", "Adım {A}; {L} {B}."])
    template = shape.replace("{L}", label)
    expect = template.replace("{A}", name).replace("{B}", str(value))
    head = f'{v1} = "{name}"\n{v2} = {value}\n'
    solution = ("Tırnağın önündeki <code>f</code> metni f-string yapar; süslü parantez içine yazılan değişken "
                "adları, değişkenlerin değerleriyle değiştirilir.")
    if random.random() < 0.3:
        body = template.replace("{A}", "{" + v1 + "}").replace("{B}", "{" + v2 + "}")
        return fill_question(
            head + f'print(____"{body}")', [["f", "F"]], expect,
            f"Aşağıdaki kod ekrana <code>{e(expect)}</code> yazmalı. Boşluğa gereken öneki yazın.",
            solution,
            hint="Süslü parantezlerin değişken değerine dönüşmesi için tırnağın önüne ne gelir?",
            wrongs=[[Wrong("str", "<code>str()</code> bir fonksiyondur; tırnağın önüne önek olarak yazılmaz."),
                     Wrong("%", "Burada süslü parantezleri çalıştıran tek harflik bir önek isteniyor."),
                     Wrong("format", "Burada süslü parantezleri çalıştıran tek harflik bir önek isteniyor."),
                     Wrong("r", "<code>r</code> öneki ham metin yapar; süslü parantezler olduğu gibi yazılır.")]],
        )
    body = template.replace("{A}", "{____}").replace("{B}", "{____}")
    quoted = "Tırnak içindeki ad metin olarak yazılır; süslü parantezin içine değişkenin adı tırnaksız yazılır."
    return fill_question(
        head + f'print(f"{body}")', [[v1], [v2]], expect,
        f"Aşağıdaki kod ekrana <code>{e(expect)}</code> yazmalı. Süslü parantezlere gereken "
        "<strong>değişken adlarını</strong> yazın.",
        solution,
        hint="Süslü parantezin içine değerin kendisi mi, onu tutan değişkenin adı mı yazılır?",
        wrongs=[[Wrong(f'"{v1}"', quoted),
                 Wrong(name, f"<code>{e(name)}</code> bir değişken adı değil, değerin kendisi; tırnaksız yazılınca "
                             "Python onu değişken sanar ve NameError verir."),
                 Wrong(v2, "Sıra önemli: ilk süslü parantezde ad, ikincisinde sayı yazılmalı.")],
                [Wrong(f'"{v2}"', quoted),
                 Wrong(v1, "Sıra önemli: ilk süslü parantezde ad, ikincisinde sayı yazılmalı.")]],
    )


SWAP_PAIRS = [("a", "b"), ("x", "y"), ("sol", "sag"), ("ilk", "son")]
SWAP_TRIPLES = [("a", "b", "c"), ("x", "y", "z")]


@q("Değer Takası (Boşluk Doldurma)", verify="fill")
def swap_blank():
    """Kazanım: çoklu atamayla değer takası yapar · Bloom: U/An"""
    hint = "Sağ taraf önce bütünüyle hesaplanır; sağa hangi sırayla yazarsan sola o sırayla atanır."
    solution = ("Çoklu atamada önce sağ taraf bütünüyle hesaplanır, sonra değerler soldaki değişkenlere aynı anda "
                "atanır. Bu yüzden geçici bir değişkene gerek kalmaz. Parantezli ya da köşeli parantezli yazım da "
                "aynı sonucu verir.")
    if random.random() < 0.7:
        p, r = random.choice(SWAP_PAIRS)
        x, y = random.sample(range(1, 31), 2)
        expect = f"{y} {x}"
        names = f"{r}, {p}"
        wrongs = [Wrong(f"{p}, {r}", "Sağ taraf aynı sırada kalırsa değerler değişmez."),
                  Wrong(f"{r}, {r}", "İki değişkene de aynı değeri atarsın; biri kaybolur."),
                  Wrong(f"{p}, {p}", "İki değişkene de aynı değeri atarsın; biri kaybolur.")]
        code = f"{p}, {r} = {x}, {y}\n{p}, {r} = ____\nprint({p}, {r})"
        task = f"<code>{p}</code> ile <code>{r}</code> değişkenlerinin değerlerini yer değiştirmeli"
    else:
        a, b, c = random.choice(SWAP_TRIPLES)
        x, y, z = random.sample(range(1, 31), 3)
        expect = f"{y} {z} {x}"
        names = f"{b}, {c}, {a}"
        wrongs = [Wrong(f"{c}, {a}, {b}", "Değerleri sağa kaydırdın; istenen çıktıda her değer bir sola kayıyor."),
                  Wrong(f"{a}, {b}, {c}", "Sağ taraf aynı sırada kalırsa değerler değişmez."),
                  Wrong(f"{b}, {a}, {c}", "Yalnızca ilk iki değeri değiştirdin; üçü de yer değiştirmeli.")]
        code = f"{a}, {b}, {c} = {x}, {y}, {z}\n{a}, {b}, {c} = ____\nprint({a}, {b}, {c})"
        task = "değişkenlerin değerlerini birer sola kaydırmalı"
    return fill_question(
        code, [[names, f"({names})", f"[{names}]"]], expect,
        f"Aşağıdaki kod {task}; yani ekrana <code>{expect}</code> yazmalı. Boşluğa <strong>değişken adlarını "
        "kullanarak</strong> gereken ifadeyi yazın (sayı yazmayın).",
        solution, hint=hint, wrongs=[wrongs],
    )


GREETINGS = ["Merhaba", "Selam", "Hoş geldin"]


@q("Selamlama (Kod Yazma)")
def write_greet():
    """Kazanım: değişkendeki metni print içinde başka metinle birlikte kullanır · Bloom: O"""
    greet = random.choice(GREETINGS)
    var = random.choice(["ad", "isim", "kullanici"])
    name = random.choice(PEOPLE)
    return {
        "type": "code",
        "text": (
            "Şu adımları gerçekleştiren Python kodunu yazınız:<br>"
            f"1. <code>{var}</code> adında bir değişken tanımlayıp <code>\"{e(name)}\"</code> metnini atayın.<br>"
            f"2. Ekrana <strong>{e(greet)}</strong> sözcüğüyle birlikte adı yazdırın (çıktı: "
            f"<code>{e(greet)} {e(name)}</code>).<br>"
            f"Adı print içine elle yazmayın; <code>{var}</code> değişkenini kullanın."
        ),
        "code": None,
        "check": {"kind": "greet_var", "var": var, "name": name, "greet": greet},
        "answer": f'{var} = "{name}"\nprint("{greet}", {var})',
        "hint": "İki satır yeterli: önce atama, sonra print. print'e virgülle birden çok değer verilebilir.",
        "solution": "Değişkene metin atanır; print'e selam metni ve değişken virgülle verilir. Virgül araya bir "
                    "boşluk koyar. <code>+</code> ile birleştirirken boşluğu metnin içine yazmak gerekir; "
                    "f-string de kullanılabilir.",
    }


RECT_NAMES = [("en", "boy"), ("a", "b"), ("kisa", "uzun")]


@q("Dikdörtgen Alan ve Çevre (Kod Yazma)")
def write_rect():
    """Kazanım: değişkenlerle aritmetik ifade kurup sonucu yazdırır · Bloom: O"""
    en_ad, boy_ad = random.choice(RECT_NAMES)
    while True:
        en, boy = random.randint(3, 15), random.randint(2, 12)
        if en != boy and en * boy != 2 * (en + boy):
            break
    if en_ad == "kisa":
        en, boy = min(en, boy), max(en, boy)
    return {
        "type": "code",
        "text": (
            f"<code>{en_ad}</code> değişkenine <strong>{en}</strong>, <code>{boy_ad}</code> değişkenine "
            f"<strong>{boy}</strong> atayın. Ardından dikdörtgenin önce <strong>alanını</strong>, sonra "
            f"<strong>çevresini</strong> iki ayrı satırda yazdırın (çıktı: alt alta {en * boy} ve {2 * (en + boy)}). "
            "Değerleri elle hesaplamayın; değişkenleri kullanın."
        ),
        "code": None,
        "check": {"kind": "rect_area", "en_ad": en_ad, "boy_ad": boy_ad, "en": en, "boy": boy},
        "answer": f"{en_ad} = {en}\n{boy_ad} = {boy}\nprint({en_ad} * {boy_ad})\nprint(2 * ({en_ad} + {boy_ad}))",
        "hint": "Alan iki kenarın çarpımı, çevre iki kenarın toplamının iki katıdır. İşlem önceliğine dikkat et.",
        "solution": "Alan <code>en * boy</code>, çevre <code>2 * (en + boy)</code> ile hesaplanır. Parantez "
                    "olmazsa çarpma önce yapılır ve çevre yanlış çıkar.",
    }


WHICH_SEPS = ["-", "*", "/", "_", "."]


@q("Hangi Kod Bu Çıktıyı Verir?", verify="code_one")
def which_print():
    """Kazanım: aynı çıktıyı üreten print biçimlerini ayırt eder · Bloom: An"""
    a, b = random.sample(PEOPLE, 2)
    s = random.choice(WHICH_SEPS)
    target = f"{a}{s}{b}"
    correct = random.choice([f'print("{a}", "{b}", sep="{s}")', f'print("{a}" + "{s}" + "{b}")'])
    pool = [
        Wrong(f'print("{a}", "{s}", "{b}")', f"Varsayılan sep boşluktur; ekrana <code>{e(a)} {e(s)} {e(b)}</code> "
                                             "yazılır."),
        Wrong(f'print("{a}", "{b}", end="{s}")', f"end araya değil sona eklenir; ekrana <code>{e(a)} {e(b)}{e(s)}"
                                                 "</code> yazılır."),
        Wrong(f'print("{a}" + "{b}" + "{s}")', f"+ metinleri yazıldığı sırayla birleştirir; ekrana "
                                               f"<code>{e(a)}{e(b)}{e(s)}</code> yazılır."),
        Wrong(f'print("{a}", "{b}", sep=" {s} ")', f"Ayırıcının çevresine boşluk koydun; ekrana "
                                                   f"<code>{e(a)} {e(s)} {e(b)}</code> yazılır."),
        Wrong(f'print("{a}" + "{s}", "{b}")', f"Virgül araya bir boşluk ekler; ekrana <code>{e(a)}{e(s)} {e(b)}"
                                              "</code> yazılır."),
    ]
    if s in "-*/":
        pool.append(Wrong(f'print("{a}" {s} "{b}")', f"Metinler arasında <code>{e(s)}</code> işlemi yapılamaz; "
                                                     "TypeError oluşur."))
    return code_options_question(
        f"Aşağıdakilerden hangisi ekrana <code>{e(target)}</code> yazar?",
        correct, random.sample(pool, 3),
        cases=[{"expect": target}],
        solution=f"<code>sep</code> değerlerin arasına konan metni belirler; <code>+</code> ise metinleri araya "
                 f"hiçbir şey koymadan birleştirir. Bu yüzden <code>{e(correct)}</code> tam olarak "
                 f"<code>{e(target)}</code> yazar.",
        hint="Her seçenekte araya ne konduğunu ve sona ne eklendiğini ayrı ayrı yaz.",
    )


# ================================================================= düz kod izleme (Ünite 1-3 denetleyicileri)
UNSET = object()


def straight_run(tree, overrides=None):
    """Dallanmayan koddaki üst düzey print satırlarını, o satırdan önceki izleme durumuyla döndürür.

    Dönüş: (prints, firsts) -> prints: [(print çağrısı, Tracker kopyası)], firsts: {ad: ilk atanan değer}.
    overrides {ad: değer}: adın ilk atamasından hemen sonra değeri bununla değiştirilir. Böylece kod
    "verilen değer" değişince sonucun da değişip değişmediği (sabit cevap yazılmış mı) denetlenir."""
    tr = Tracker()
    pending = dict(overrides or {})
    prints, firsts = [], {}
    for stmt in tree.body:
        if isinstance(stmt, ast.Expr) and is_print(stmt):
            prints.append((stmt.value, tr.copy()))
        tr.feed(stmt)
        if isinstance(stmt, (ast.Assign, ast.AnnAssign)):
            for name in sorted(assigned_names(stmt)):
                if name not in firsts:
                    firsts[name] = tr.values.get(name, UNSET)
                    if name in pending:
                        tr.values[name] = pending.pop(name)
                        tr.defs.pop(name, None)
    return prints, firsts


def print_numbers(call, tr):
    """print'in yazdırdığı değerler (etiket metinleri hariç); sayı biçimindeki metinler sayıya çevrilir,
    demetler açılır, hesaplanamayan değer UNSET olur."""
    out = []
    for node in print_values(call):
        for item in (node.elts if isinstance(node, ast.Tuple) else [node]):
            if isinstance(item, ast.FormattedValue):
                item = ast.JoinedStr(values=[item])
            value = tr.try_value(item, UNSET)
            if isinstance(value, str) and re.fullmatch(r"\s*-?\d+(\.\d+)?\s*", value):
                value = float(value) if "." in value else int(value)
            out.append(value)
    return out


_PLAIN_FIELDS = re.compile(r"\{(\d*)\}")
_PERCENT_FIELDS = re.compile(r"%[sd]")


def format_value(node, tr):
    """'... {} ...'.format(x) ve '... %s ...' % x biçimlerini (yalnızca düz {} / {0} / %s / %d alanlarıyla)
    hesaplar; diğer her şeyde tr.try_value'ya döner. Öğrenci kodu çalıştırılmaz: şablon metni kendi
    kodumuzla doldurulur; alanlarda nitelik ya da indeks erişimine izin verilmez."""
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "format"
            and isinstance(node.func.value, ast.Constant) and isinstance(node.func.value.value, str)
            and not node.keywords):
        template = node.func.value.value
        rest = _PLAIN_FIELDS.sub("", template)
        args = [tr.try_value(a, UNSET) for a in node.args]
        if any(a is UNSET for a in args) or "{" in rest or "}" in rest:
            return UNSET
        auto = iter(args)
        try:
            return _PLAIN_FIELDS.sub(lambda m: str(args[int(m.group(1))] if m.group(1) else next(auto)), template)
        except (IndexError, StopIteration):
            return UNSET
    if (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod) and isinstance(node.left, ast.Constant)
            and isinstance(node.left.value, str)):
        template = node.left.value
        items = node.right.elts if isinstance(node.right, ast.Tuple) else [node.right]
        args = [tr.try_value(a, UNSET) for a in items]
        if (any(a is UNSET for a in args) or "%" in _PERCENT_FIELDS.sub("", template)
                or len(args) != len(_PERCENT_FIELDS.findall(template))):
            return UNSET
        auto = iter(args)
        return _PERCENT_FIELDS.sub(lambda m: str(next(auto)), template)
    return tr.try_value(node, UNSET)


def print_text(call, tr):
    """print satırının ekrana yazacağı metin (sep dahil, end hariç); hesaplanamazsa None."""
    pieces = []
    for arg in call.args:
        value = format_value(arg, tr)
        if value is UNSET or isinstance(arg, ast.Starred):
            return None
        pieces.append(str(value))
    sep = tr.try_value(next((k.value for k in call.keywords if k.arg == "sep"), ast.Constant(" ")), UNSET)
    return str(sep).join(pieces) if isinstance(sep, str) else None


def _greet_norm(text):
    text = text.replace("İ", "i").replace("I", "ı").lower()
    return " ".join(re.sub(r"[,.!?;:'\"]", " ", text).split())


GREET_ALT_NAMES = ["Kerem", "Selin"]


@checker("greet_var")
def check_greet_var(tree, p):
    """var değişkenine name atanır; print ile "greet name" yazdırılır (ad değişkenden gelmeli)."""
    var, name, greet = p["var"], p["name"], p["greet"]
    prints, firsts = straight_run(tree)
    if firsts.get(var) != name:
        return False, f"<code>{var}</code> değişkenine <code>\"{e(name)}\"</code> metni atanmamış."
    if not find_prints(tree):
        return False, "Ekrana yazdırmak için <code>print()</code> kullanılmalı."
    goal = _greet_norm(f"{greet} {name}")
    texts = [print_text(call, tr) for call, tr in prints]
    good = [i for i, t in enumerate(texts) if t is not None and _greet_norm(t) == goal]
    if good:
        alt = next(n for n in GREET_ALT_NAMES if n != name)
        alt_prints, _ = straight_run(tree, {var: alt})
        alt_text = print_text(*alt_prints[good[0]])
        if alt_text is None or _greet_norm(alt_text) != _greet_norm(f"{greet} {alt}"):
            return False, (f"Adı print içine elle yazma; <code>{var}</code> değişkenini kullan. Değişkendeki ad "
                           "değişince çıktı da değişmeli.")
        return True, OK
    known = [t for t in texts if t is not None]
    if any(re.search(rf"\b{re.escape(var)}\b", t) and name not in t for t in known):
        return False, (f"Tırnak içine yazdığın <code>{var}</code> metin olarak yazılır; değişkenin değerini yazdırmak "
                       "için onu tırnaksız kullan.")
    if any(_greet_norm(t).replace(" ", "") == goal.replace(" ", "") for t in known):
        return False, "Selam sözcüğü ile ad arasında bir boşluk olmalı."
    if any(name in t for t in known):
        return False, f"Ekrana <strong>{e(greet)}</strong> sözcüğü ve ad birlikte, bu sırayla yazılmalı."
    return False, (f"Ekrana <code>{e(greet)} {e(name)}</code> yazdıran bir print bulunamadı; print satırının atamadan "
                   "sonra geldiğinden emin ol.")


def print_lines(prints):
    """Her print'in yazdırdığı sayılar; sep="\\n" verilen print'in değerleri ayrı satırlar sayılır."""
    lines = []
    for call, tr in prints:
        vals = print_numbers(call, tr)
        if not vals:
            continue
        sep = next((k.value for k in call.keywords if k.arg == "sep"), None)
        if len(vals) > 1 and sep is not None and tr.try_value(sep, UNSET) == "\n":
            lines.extend([v] for v in vals)
        else:
            lines.append(vals)
    return lines


@checker("rect_area")
def check_rect_area(tree, p):
    """en ve boy atanır; önce alan, sonra çevre ayrı satırlarda yazdırılır (değişkenlerle hesaplanmalı)."""
    en_ad, boy_ad, en, boy = p["en_ad"], p["boy_ad"], p["en"], p["boy"]
    names = f"<code>{en_ad}</code> ve <code>{boy_ad}</code>"
    prints, firsts = straight_run(tree)
    if not (same_value(firsts.get(en_ad), en) and same_value(firsts.get(boy_ad), boy)):
        return False, f"{names} değişkenlerine istenen değerler atanmamış."
    lines = print_lines(prints)
    if not lines:
        return False, "Alan ve çevre <code>print()</code> ile yazdırılmalı."
    if any(len(vals) > 1 for vals in lines):
        return False, "Alan ve çevreyi ayrı satırlarda (iki ayrı print ile) yazdır."
    if len(lines) != 2:
        return False, "Tam iki değer yazdırılmalı: önce alan, sonra çevre."
    area, per = lines[0][0], lines[1][0]
    want_area, want_per = en * boy, 2 * (en + boy)
    if not same_value(area, want_area):
        if same_value(area, want_per) and same_value(per, want_area):
            return False, "Sıra ters: önce alan, sonra çevre yazdırılmalı."
        return False, "Alan değeri beklenen sonucu vermiyor; alan iki kenarın çarpımıdır."
    if not same_value(per, want_per):
        if same_value(per, en + 2 * boy) or same_value(per, 2 * en + boy):
            return False, "Çevre 2 * (en + boy) olmalı; parantez gerekiyor mu?"
        if same_value(per, en + boy):
            return False, "Çevre, iki kenarın toplamının iki katıdır."
        return False, "Çevre değeri beklenen sonucu vermiyor; formülü kontrol et."
    alt_en, alt_boy = en + 3, boy + 5
    alt_prints, _ = straight_run(tree, {en_ad: alt_en, boy_ad: alt_boy})
    alt_lines = print_lines(alt_prints)
    if not (len(alt_lines) == 2 and same_value(alt_lines[0][0], alt_en * alt_boy)
            and same_value(alt_lines[1][0], 2 * (alt_en + alt_boy))):
        return False, f"Sonuçları elle yazma; {names} değişkenleriyle hesapla. Değerler değişince sonuç da değişmeli."
    return True, OK
