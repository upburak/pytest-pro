"""Ünite 10 - Hatalar ve Hata Yönetimi."""
import random

from ..helpers import output_question, tf_question, unique_options
from ..registry import register_unit

UNIT = register_unit(
    "hatalar", "Hata Yönetimi", "Orta",
    "Sık karşılaşılan hata türleri (ZeroDivisionError, ValueError, TypeError, IndexError, KeyError, NameError), "
    "try / except / else / finally.",
    order=10,
)
q = UNIT.question

ERRORS = ["ZeroDivisionError", "ValueError", "TypeError", "IndexError", "KeyError", "NameError"]
SNIPPETS = [
    ("x = 10\nprint(x / 0)", "ZeroDivisionError", "Sıfıra bölme yapılamaz."),
    ('sayi = int("yirmi")', "ValueError", "int() yalnızca sayı biçimindeki metni çevirebilir."),
    ('print("Puan: " + 90)', "TypeError", "str ile int + ile birleştirilemez."),
    ("liste = [1, 2, 3]\nprint(liste[5])", "IndexError", "Liste 3 elemanlı; 5. indeks yoktur."),
    ('d = {"a": 1}\nprint(d["b"])', "KeyError", 'Sözlükte "b" anahtarı yoktur.'),
    ("print(toplam)", "NameError", "toplam adında tanımlı bir değişken yoktur."),
    ('print(len(5))', "TypeError", "len() sayıya uygulanamaz; metin, liste gibi yapılar ister."),
]


@q("Hata Türleri", verify="error")
def error_type():
    code, name, why = random.choice(SNIPPETS)
    return {
        "type": "mc",
        "text": "Aşağıdaki kod çalıştırıldığında hangi hata oluşur?",
        "code": code,
        "options": unique_options(name, random.sample([x for x in ERRORS if x != name], 3)),
        "answer": name,
        "solution": f"{why} Bu durumda Python <strong>{name}</strong> hatası verir.",
    }


@q("try / except", verify="output")
def try_except():
    good = random.random() < 0.5
    value = str(random.randint(2, 9)) if good else random.choice(["abc", "3.5", "on"])
    code = ("try:\n    sayi = int(veri)\n    print(sayi * 2)\nexcept ValueError:\n    print(\"Gecersiz\")\n"
            "print(\"Bitti\")")
    res = (f"{int(value) * 2}\nBitti" if good else "Gecersiz\nBitti")
    return output_question(
        f'veri = "{value}"\n' + code, res,
        ("Dönüşüm başarılı olduğu için except bloğu atlanır. " if good else
         "int() ValueError verince try bloğunun geri kalanı atlanır ve except bloğu çalışır. ")
        + "try yapısından sonra program normal şekilde devam eder.",
        wrongs=["Gecersiz", f"{value * 2}\nBitti", "Gecersiz\nBitti" if good else "Bitti",
                f"{int(value) * 2}" if good else "Gecersiz\nGecersiz"],
    )


@q("else ve finally", verify="output")
def try_finally():
    b = random.choice([0, 2, 5])
    code = (f"try:\n    sonuc = 10 / {b}\nexcept ZeroDivisionError:\n    print(\"Hata\")\n"
            "else:\n    print(\"Basarili\")\nfinally:\n    print(\"Son\")")
    res = "Hata\nSon" if b == 0 else "Basarili\nSon"
    return output_question(
        code, res,
        "<code>else</code> yalnızca hata <strong>olmazsa</strong>, <code>finally</code> ise her durumda çalışır.",
        wrongs=["Hata\nSon" if b else "Basarili\nSon", "Son", "Hata" if b == 0 else "Basarili",
                "Hata\nBasarili\nSon"],
    )


@q("Hata Yönetimi Kavramları")
def concepts():
    return tf_question(
        ["try bloğunda hata oluşursa, try içinde hatadan sonra gelen satırlar çalıştırılmaz.",
         "Bir try bloğundan sonra farklı hata türleri için birden fazla except bloğu yazılabilir."],
        ["except bloğu, try bloğunda hata olsa da olmasa da her zaman çalışır.",
         "SyntaxError (yazım hatası) try / except ile yakalanarak program çalıştırılabilir."],
        "except yalnızca eşleşen bir hata olduğunda çalışır; her durumda çalışan blok finally'dir. Yazım "
        "hataları kod çalışmadan önce tespit edildiği için o kodu çalıştıran try ile yakalanamaz.",
    )
