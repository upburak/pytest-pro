"""Ünite 1 - Temel Giriş/Çıkış ve Değişkenler."""
import random

from ..helpers import PEOPLE, STR_VALUES, Wrong, e, output_question, shown, tf_question, unique_options, whys_for_options
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
        f'{vname} = "{val}"\nyas = {age}\nprint(f"Merhaba {{{vname}}}, yasiniz: {{yas}}")',
        f"Merhaba {val}, yasiniz: {age}",
        "f-string içinde süslü parantez <code>{}</code> içindeki değişkenler kendi değerleriyle değiştirilir.",
        wrongs=[
            Wrong(f"Merhaba {{{vname}}}, yasiniz: {{yas}}", "Metnin başındaki <code>f</code> harfi süslü parantezleri "
                                                           "etkin hâle getirir; parantezler olduğu gibi yazılmaz."),
            Wrong(f"Merhaba {vname}, yasiniz: yas", "Parantez içindeki ad değişkenin <strong>değeriyle</strong> "
                                                   "değiştirilir, adının kendisi yazılmaz."),
            Wrong(f'f"Merhaba {val}, yasiniz: {age}"', "<code>f</code> ve tırnaklar metnin yazımına aittir; ekrana "
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
