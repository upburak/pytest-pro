"""Ünite 11 - Nesne Yönelimli Programlamaya Giriş."""
import random

from ..helpers import PEOPLE, err, output_question, tf_question
from ..registry import register_unit

UNIT = register_unit(
    "nesne", "Nesne Yönelimli Programlama", "İleri",
    "class, __init__ ve self, nesne özellikleri ve metotları, sınıf değişkenleri, kalıtım ve metot ezme, __str__.",
    order=11,
)
q = UNIT.question


@q("Sınıf ve Nesne", verify="output")
def class_basics():
    name = random.choice(PEOPLE)
    age = random.randint(14, 18)
    k = random.randint(1, 3)
    return output_question(
        "class Ogrenci:\n    def __init__(self, ad, yas):\n        self.ad = ad\n        self.yas = yas\n\n"
        f"    def buyu(self, yil):\n        self.yas += yil\n\no = Ogrenci(\"{name}\", {age})\no.buyu({k})\n"
        "print(o.ad, o.yas)",
        f"{name} {age + k}",
        "<code>__init__</code> nesne oluşturulurken çalışır ve özellikleri <code>self</code> üzerinden atar. "
        f"<code>buyu({k})</code> metodu nesnenin yas özelliğini {age}'den {age + k}'e günceller.",
        wrongs=[f"{name} {age}", f"ad {age + k}", err("TypeError")],
    )


@q("Sınıf Değişkenleri", verify="output")
def class_counter():
    n = random.randint(2, 5)
    creates = "\n".join(f"s{i} = Sayac()" for i in range(1, n + 1))
    return output_question(
        f"class Sayac:\n    adet = 0\n\n    def __init__(self):\n        Sayac.adet += 1\n\n{creates}\nprint(Sayac.adet)",
        str(n),
        "<code>adet</code> bir <strong>sınıf değişkenidir</strong>; tüm nesneler tarafından paylaşılır. Her nesne "
        f"oluşturulduğunda 1 artar: {n} nesne → {n}.",
        wrongs=["1", "0", str(n + 1)],
    )


@q("Kalıtım ve Metot Ezme", verify="output")
def inheritance():
    animal, sound = random.choice([("Kedi", "Miyav"), ("Kopek", "Hav"), ("Inek", "Mo")])
    return output_question(
        "class Hayvan:\n    def ses(self):\n        return \"...\"\n\n    def tanit(self):\n"
        "        return \"Ben bir hayvanim: \" + self.ses()\n\n"
        f"class {animal}(Hayvan):\n    def ses(self):\n        return \"{sound}\"\n\nprint({animal}().tanit())",
        f"Ben bir hayvanim: {sound}",
        f"{animal} sınıfı Hayvan'dan <strong>kalıtım</strong> alır; tanit() metodunu miras alır ama ses() metodunu "
        f"<strong>ezer</strong> (override). tanit() içindeki self.ses() çağrısı {animal}'in metodunu çalıştırır.",
        wrongs=["Ben bir hayvanim: ...", sound, err("AttributeError")],
    )


@q("__str__ Metodu", verify="output")
def str_method():
    w, h = random.randint(2, 9), random.randint(2, 9)
    return output_question(
        "class Dikdortgen:\n    def __init__(self, en, boy):\n        self.en = en\n        self.boy = boy\n\n"
        "    def __str__(self):\n        return f\"{self.en}x{self.boy} alan={self.en * self.boy}\"\n\n"
        f"print(Dikdortgen({w}, {h}))",
        f"{w}x{h} alan={w * h}",
        "<code>print(nesne)</code> nesnenin <code>__str__</code> metodunun döndürdüğü metni yazdırır.",
        wrongs=[f"{w}x{h} alan={w + h}", "Dikdortgen", f"{w} {h}"],
    )


@q("Nesne Yönelimli Kavramlar")
def concepts():
    return tf_question(
        ["Bir sınıftan birden fazla nesne oluşturulabilir ve her nesnenin özellikleri birbirinden bağımsızdır.",
         "Metot tanımlarındaki ilk parametre (<code>self</code>), metodu çağıran nesnenin kendisini temsil eder."],
        ["<code>__init__</code> metodu, nesne oluşturulduktan sonra elle çağrılmalıdır.",
         "Alt sınıf, üst sınıfın metotlarını kullanamaz; hepsini yeniden yazmak zorundadır."],
        "Sınıf bir kalıptır; her nesne kendi özelliklerini taşır. <code>__init__</code> nesne oluşturulurken "
        "otomatik çalışır. Alt sınıf üst sınıfın metotlarını miras alır, istediklerini ezebilir.",
    )
