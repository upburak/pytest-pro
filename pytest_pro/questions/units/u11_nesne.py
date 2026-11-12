"""Ünite 11 - Nesne Yönelimli Programlamaya Giriş."""
import random

from ..helpers import PEOPLE, Wrong, err, output_question, tf_question
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
        wrongs=[
            Wrong(f"{name} {age}", "buyu() metodu self.yas'ı kalıcı olarak artırır; değişiklik nesnede kalır."),
            Wrong(f"ad {age + k}", "o.ad özelliğin değerini yazar, özelliğin adını değil."),
            Wrong(err("TypeError"), "Metot doğru sayıda argümanla çağrılıyor; self kendiliğinden verilir."),
        ],
        hint="Nesne hangi değerlerle oluşturuldu? buyu() çağrısı hangi özelliği nasıl değiştiriyor?",
    )


@q("Sınıf Değişkenleri", verify="output")
def class_counter():
    n = random.randint(2, 7)
    cls = random.choice(["Sayac", "Oyuncu", "Kitap", "Araba"])
    if random.random() < 0.5:
        creates = "\n".join(f"n{i} = {cls}()" for i in range(1, n + 1))
    else:
        creates = f"for i in range({n}):\n    {cls}()"
    return output_question(
        f"class {cls}:\n    adet = 0\n\n    def __init__(self):\n        {cls}.adet += 1\n\n{creates}\nprint({cls}.adet)",
        str(n),
        "<code>adet</code> bir <strong>sınıf değişkenidir</strong>; tüm nesneler tarafından paylaşılır. Her nesne "
        f"oluşturulduğunda 1 artar: {n} nesne → {n}.",
        wrongs=[
            Wrong("1", "adet sınıf değişkenidir; her nesne aynı sayacı artırır, kendine ayrı sayaç tutmaz."),
            Wrong("0", "__init__ her nesne oluşturulduğunda kendiliğinden çalışır ve sayacı artırır."),
            Wrong(str(n + 1), f"Sayaç 0'dan başlar; {n} nesne oluşturulunca {n} olur."),
        ],
        hint="adet her nesneye ayrı mı, yoksa sınıfa ait tek bir değişken mi? Kaç nesne oluşturuluyor?",
    )


ANIMALS = [("Kedi", "Miyav"), ("Kopek", "Hav"), ("Inek", "Mo"), ("Kus", "Cik"), ("Koyun", "Mee"),
           ("Ordek", "Vak"), ("At", "Ihaa"), ("Horoz", "Kukuriku")]


@q("Kalıtım ve Metot Ezme", verify="output")
def inheritance():
    animal, sound = random.choice(ANIMALS)
    intro = random.choice(["Ben bir hayvanim: ", "Sesim: "])
    return output_question(
        "class Hayvan:\n    def ses(self):\n        return \"...\"\n\n    def tanit(self):\n"
        f"        return \"{intro}\" + self.ses()\n\n"
        f"class {animal}(Hayvan):\n    def ses(self):\n        return \"{sound}\"\n\nprint({animal}().tanit())",
        f"{intro}{sound}",
        f"{animal} sınıfı Hayvan'dan <strong>kalıtım</strong> alır; tanit() metodunu miras alır ama ses() metodunu "
        f"<strong>ezer</strong> (override). tanit() içindeki self.ses() çağrısı {animal}'in metodunu çalıştırır.",
        wrongs=[
            Wrong(f"{intro}...", f"{animal}, ses() metodunu ezer; self.ses() nesnenin kendi sınıfındaki metodu çağırır."),
            Wrong(sound, "tanit() sesi bir giriş metniyle birleştirerek döndürür."),
            Wrong(err("AttributeError"), f"tanit() üst sınıftan miras alınır; {animal} nesnesinde de bulunur."),
        ],
        hint=f"{animal} nesnesinde tanit() nereden geliyor? İçindeki self.ses() hangi sınıfın metodunu çağırır?",
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
        wrongs=[
            Wrong(f"{w}x{h} alan={w + h}", "Alan en ile boyun çarpımıdır: self.en * self.boy."),
            Wrong("Dikdortgen", "Sınıfta __str__ tanımlı olduğu için print onun döndürdüğü metni yazar."),
            Wrong(f"{w} {h}", "print, __str__'in döndürdüğü biçimi kullanır."),
        ],
        hint="print bir nesneyi yazdırırken hangi metodu kullanır?",
    )


@q("Nesne Yönelimli Kavramlar")
def concepts():
    return tf_question(
        [("Bir sınıftan birden fazla nesne oluşturulabilir ve her nesnenin özellikleri birbirinden bağımsızdır.",
          "Sınıf bir kalıptır; her nesne kendi özellik değerlerini taşır."),
         ("Metot tanımlarındaki ilk parametre (<code>self</code>), metodu çağıran nesnenin kendisini temsil eder.",
          "o.metot() çağrısında self, o nesnesidir; Python bunu kendiliğinden verir."),
         ("<code>__init__</code> metodu nesne oluşturulurken kendiliğinden çalışır.",
          "Ogrenci(...) yazıldığında __init__ otomatik çağrılır."),
         ("Alt sınıf, üst sınıfın metotlarını miras alır ve doğrudan kullanabilir.",
          "Kalıtımda alt sınıf, üst sınıfın metotlarına sahip olur."),
         ("Alt sınıf, üst sınıftan gelen bir metodu aynı adla yeniden tanımlayarak ezebilir (override).",
          "Aynı adla yeniden tanımlanan metot, alt sınıfın nesnelerinde üst sınıfınkinin yerine geçer."),
         ("Sınıf değişkeni o sınıftan oluşturulan tüm nesneler tarafından paylaşılır.",
          "Sınıf değişkeni sınıfa aittir; her nesnede ayrı bir kopyası yoktur.")],
        [("<code>__init__</code> metodu, nesne oluşturulduktan sonra elle çağrılmalıdır.",
          "__init__ nesne oluşturulurken kendiliğinden çalışır; elle çağırmak gerekmez."),
         ("Alt sınıf, üst sınıfın metotlarını kullanamaz; hepsini yeniden yazmak zorundadır.",
          "Alt sınıf üst sınıfın metotlarını miras alır; yalnızca değiştirmek istediklerini yeniden yazar."),
         ("Bir sınıftan yalnızca bir nesne oluşturulabilir.",
          "Bir sınıftan istenildiği kadar nesne oluşturulabilir."),
         ("Metot çağrılırken <code>self</code> değerini parantez içinde elle vermek gerekir: <code>o.buyu(o, 2)</code>.",
          "self'i Python kendiliğinden verir; doğru çağrı o.buyu(2)'dir."),
         ("Bir nesnenin özelliğini değiştirmek, aynı sınıftaki tüm nesnelerin özelliğini değiştirir.",
          "self ile atanan özellikler her nesneye özeldir; biri değişince diğerleri etkilenmez."),
         ("Sınıf tanımlamak (class) o sınıftan kendiliğinden bir nesne oluşturur.",
          "class yalnızca kalıbı tanımlar; nesne Sinif() çağrısıyla oluşturulur.")],
        "Sınıf bir kalıptır; her nesne kendi özelliklerini taşır. <code>__init__</code> nesne oluşturulurken "
        "otomatik çalışır. Alt sınıf üst sınıfın metotlarını miras alır, istediklerini ezebilir.",
        hint="Sınıf ile nesne arasındaki farkı, __init__'in ne zaman çalıştığını ve kalıtımı düşün.",
    )
