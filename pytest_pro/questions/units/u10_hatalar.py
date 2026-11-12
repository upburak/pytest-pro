"""Ünite 10 - Hatalar ve Hata Yönetimi."""
import random

from ..helpers import Wrong, output_question, tf_question, unique_options, whys_for_options
from ..registry import register_unit

UNIT = register_unit(
    "hatalar", "Hata Yönetimi", "Orta",
    "Sık karşılaşılan hata türleri (ZeroDivisionError, ValueError, TypeError, IndexError, KeyError, NameError), "
    "try / except / else / finally.",
    order=10,
)
q = UNIT.question

ERROR_CAUSES = {
    "ZeroDivisionError": "sıfıra bölmede oluşur",
    "ValueError": "doğru tipte ama uygun olmayan bir değer verilince oluşur (int(\"abc\") gibi)",
    "TypeError": "uyumsuz tipler birlikte kullanılınca oluşur (metin + sayı gibi)",
    "IndexError": "liste ya da metinde olmayan bir indekse erişilince oluşur",
    "KeyError": "sözlükte olmayan bir anahtara erişilince oluşur",
    "NameError": "tanımlanmamış bir ad kullanılınca oluşur",
}
SNIPPETS = [
    ("x = 10\nprint(x / 0)", "ZeroDivisionError", "Sıfıra bölme yapılamaz."),
    ("a = 5\nb = a - 5\nprint(a / b)", "ZeroDivisionError", "b sıfır olur ve sıfıra bölme yapılamaz."),
    ('sayi = int("yirmi")', "ValueError", "int() yalnızca sayı biçimindeki metni çevirebilir."),
    ('sayi = float("3,5")', "ValueError", "float() ondalık ayırıcı olarak nokta bekler, virgül değil."),
    ('print("Puan: " + 90)', "TypeError", "str ile int + ile birleştirilemez."),
    ('print(len(5))', "TypeError", "len() sayıya uygulanamaz; metin, liste gibi yapılar ister."),
    ("liste = [1, 2, 3]\nprint(liste[5])", "IndexError", "Liste 3 elemanlı; 5. indeks yoktur."),
    ('metin = "abc"\nprint(metin[3])', "IndexError", "Metin 3 karakterli; son indeks 2'dir."),
    ('d = {"a": 1}\nprint(d["b"])', "KeyError", 'Sözlükte "b" anahtarı yoktur.'),
    ("print(toplam)", "NameError", "toplam adında tanımlı bir değişken yoktur."),
    ("Print(5)", "NameError", "Python büyük/küçük harfe duyarlıdır; Print tanımlı değildir, doğrusu print'tir."),
]


@q("Hata Türleri", verify="error")
def error_type():
    code, name, why = random.choice(SNIPPETS)
    wrongs = [Wrong(other, f"{other} {ERROR_CAUSES[other]}; bu kodda böyle bir durum yok.")
              for other in random.sample([x for x in ERROR_CAUSES if x != name], 3)]
    options = unique_options(name, wrongs)
    return {
        "type": "mc",
        "text": "Aşağıdaki kod çalıştırıldığında hangi hata oluşur?",
        "code": code,
        "options": options,
        "answer": name,
        "whys": whys_for_options(name, wrongs, options),
        "hint": "Hatanın oluştuğu satırda hangi işlem yapılıyor: bölme mi, dönüşüm mü, erişim mi, tanımsız bir ad mı?",
        "solution": f"{why} Bu durumda Python <strong>{name}</strong> hatası verir.",
    }


@q("try / except", verify="output")
def try_except():
    good = random.random() < 0.5
    value = str(random.randint(2, 30)) if good else random.choice(["abc", "3.5", "on", "12a", "iki", "7,5"])
    code = ("try:\n    sayi = int(veri)\n    print(sayi * 2)\nexcept ValueError:\n    print(\"Gecersiz\")\n"
            "print(\"Bitti\")")
    if good:
        res = f"{int(value) * 2}\nBitti"
        wrongs = [
            Wrong("Gecersiz\nBitti", f'"{value}" tam sayı biçiminde; dönüşüm başarılı olur ve except çalışmaz.'),
            Wrong(f"{value * 2}\nBitti", "int(veri) metni sayıya çevirir; sonuç sayı olarak çarpılır, metin "
                                          "tekrarlanmaz."),
            Wrong(f"{int(value) * 2}", "try / except yapısından sonra program devam eder; Bitti de yazılır."),
        ]
    else:
        res = "Gecersiz\nBitti"
        wrongs = [
            Wrong("Gecersiz", "except bloğundan sonra program devam eder; Bitti de yazılır."),
            Wrong("Bitti", "Hata oluşunca except bloğu çalışır ve önce Gecersiz yazılır."),
            Wrong("Gecersiz\nGecersiz", "except bloğu bir kez çalışır."),
        ]
    return output_question(
        f'veri = "{value}"\n' + code, res,
        ("Dönüşüm başarılı olduğu için except bloğu atlanır. " if good else
         "int() ValueError verince try bloğunun geri kalanı atlanır ve except bloğu çalışır. ")
        + "try yapısından sonra program normal şekilde devam eder.",
        wrongs=wrongs,
        hint=f'int("{value}") hata verir mi? Verirse hangi bloklar çalışır?',
    )


@q("else ve finally", verify="output")
def try_finally():
    a = random.randint(10, 40)
    b = random.choice([0, 0, random.randint(1, 9)])
    code = (f"try:\n    sonuc = {a} / {b}\nexcept ZeroDivisionError:\n    print(\"Hata\")\n"
            "else:\n    print(\"Basarili\")\nfinally:\n    print(\"Son\")")
    if b == 0:
        res = "Hata\nSon"
        opposite = Wrong("Basarili\nSon", f"{a} / 0 ZeroDivisionError verir; except çalışır, else atlanır.")
        single = Wrong("Hata", "finally her durumda çalışır; Son da yazılır.")
    else:
        res = "Basarili\nSon"
        opposite = Wrong("Hata\nSon", f"{a} / {b} hatasız çalışır; except atlanır, else çalışır.")
        single = Wrong("Basarili", "finally her durumda çalışır; Son da yazılır.")
    return output_question(
        code, res,
        "<code>else</code> yalnızca hata <strong>olmazsa</strong>, <code>finally</code> ise her durumda çalışır.",
        wrongs=[opposite, Wrong("Son", "finally her zaman çalışır, ama ondan önce except ya da else de çalışır."),
                single, Wrong("Hata\nBasarili\nSon", "except ile else aynı anda çalışmaz.")],
        hint=f"{a} / {b} hata verir mi? Hata olursa ve olmazsa hangi bloklar çalışır?",
    )


@q("Hata Yönetimi Kavramları")
def concepts():
    return tf_question(
        [("try bloğunda hata oluşursa, try içinde hatadan sonra gelen satırlar çalıştırılmaz.",
          "Hata oluşunca kontrol hemen except bloğuna geçer; try'ın geri kalanı atlanır."),
         ("Bir try bloğundan sonra farklı hata türleri için birden fazla except bloğu yazılabilir.",
          "Her except farklı bir hata türünü yakalayabilir: except ValueError, except ZeroDivisionError gibi."),
         ("finally bloğu, hata olsa da olmasa da çalışır.",
          "finally her durumda çalışır; genellikle dosya kapatma gibi temizlik işleri için kullanılır."),
         ("else bloğu yalnızca try bloğunda hata oluşmazsa çalışır.",
          "Hata olursa except, olmazsa else çalışır."),
         ("<code>int(\"abc\")</code> ifadesi ValueError verir.",
          "\"abc\" sayı biçiminde değildir; int() ValueError verir."),
         ("Hata yakalanmazsa program o noktada durur ve hata mesajı gösterilir.",
          "Yakalanmayan hata programı sonlandırır.")],
        [("except bloğu, try bloğunda hata olsa da olmasa da her zaman çalışır.",
          "except yalnızca eşleşen bir hata olduğunda çalışır; her durumda çalışan blok finally'dir."),
         ("SyntaxError (yazım hatası) try / except ile yakalanarak program çalıştırılabilir.",
          "Yazım hataları kod çalışmadan önce bulunur; o kodu çalıştıran try onu yakalayamaz."),
         ("except ValueError: bloğu ZeroDivisionError hatasını da yakalar.",
          "except yalnızca yazılan hata türünü yakalar; ZeroDivisionError için ayrı except gerekir."),
         ("Bir try bloğu, except ya da finally olmadan tek başına yazılabilir.",
          "try'dan sonra en az bir except ya da finally gelmelidir."),
         ("<code>10 / 0</code> işlemi Python'da sonsuz (inf) değerini verir.",
          "Python'da sıfıra bölme ZeroDivisionError verir."),
         ("Hata oluşunca try bloğu baştan tekrar çalıştırılır.",
          "Hata oluşunca except çalışır; try kendiliğinden tekrarlanmaz.")],
        "except yalnızca eşleşen bir hata olduğunda çalışır; her durumda çalışan blok finally'dir. Yazım "
        "hataları kod çalışmadan önce tespit edildiği için o kodu çalıştıran try ile yakalanamaz.",
        hint="try, except, else ve finally bloklarından hangisi hangi durumda çalışır?",
    )
