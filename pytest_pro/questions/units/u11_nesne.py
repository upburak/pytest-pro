"""Ünite 11 - Nesne Yönelimli Programlamaya Giriş."""
import ast
import copy
import random

from ..codecheck import (
    OK,
    Tracker,
    Unknown,
    checker,
    computes,
    const_value,
    find_prints,
    function_params,
    function_returns,
    same_value,
)
from ..helpers import (
    PEOPLE,
    Wrong,
    e,
    err,
    fill_question,
    output_question,
    tf_claim,
    tf_question,
)
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
            Wrong(f"{name} {k}", "<code>self.yas += yil</code> yaşı yil kadar artırır; yaşın yerine yil'i koymaz."),
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


# Sınıf adları Python tanımlayıcısı olduğu için ASCII; ekrana yazılan sesler doğru Türkçe yazımla.
ANIMALS = [("Kedi", "Miyav"), ("Kopek", "Hav"), ("Inek", "Möö"), ("Kus", "Cik cik"), ("Koyun", "Mee"),
           ("Ordek", "Vak vak"), ("At", "İhaa"), ("Horoz", "Kukuriku")]


@q("Kalıtım ve Metot Ezme", verify="output")
def inheritance():
    animal, sound = random.choice(ANIMALS)
    intro = random.choice(["Ben bir hayvanım: ", "Sesim: ", "Benim sesim: "])
    wrongs = [
        Wrong(f"{intro}...", f"{animal}, ses() metodunu ezer; self.ses() nesnenin kendi sınıfındaki metodu çağırır."),
        Wrong(sound, "tanit() sesi bir giriş metniyle birleştirerek döndürür."),
        Wrong("...", f"tanit() giriş metnini de ekler; ses() ezildiği için \"...\" yerine {animal}'in sesi gelir."),
    ]
    if random.random() < 0.5:  # hata şıkkı her soruda görünmesin (O8)
        wrongs.append(Wrong(err("AttributeError"), f"tanit() üst sınıftan miras alınır; {animal} nesnesinde de bulunur."))
    random.shuffle(wrongs)
    return output_question(
        "class Hayvan:\n    def ses(self):\n        return \"...\"\n\n    def tanit(self):\n"
        f"        return \"{intro}\" + self.ses()\n\n"
        f"class {animal}(Hayvan):\n    def ses(self):\n        return \"{sound}\"\n\nprint({animal}().tanit())",
        f"{intro}{sound}",
        f"{animal} sınıfı Hayvan'dan <strong>kalıtım</strong> alır; tanit() metodunu miras alır ama ses() metodunu "
        f"<strong>ezer</strong> (override). tanit() içindeki self.ses() çağrısı {animal}'in metodunu çalıştırır.",
        wrongs=wrongs,
        hint=f"{animal} nesnesinde tanit() nereden geliyor? İçindeki self.ses() hangi sınıfın metodunu çağırır?",
    )


@q("__str__ Metodu", verify="output")
def str_method():
    w, h = 2, 2
    while (w, h) == (2, 2):  # 2 + 2 = 2 * 2: "toplam" şıkkı doğru cevaba eşit olurdu
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



# ================================================================= yeni şablonlar (ölçme raporu Ö11.1-Ö11.8)
SHADOW_CLASSES = [("Oyuncu", "puan"), ("Ayar", "seviye"), ("Takim", "skor"), ("Kutu", "adet"), ("Robot", "hiz")]


@q("Sınıf mı Nesne mi? (Doğru/Yanlış)", verify="tf_output")
def attr_shadow_claim():
    """Kazanım: örnek niteliğinin sınıf niteliğini gölgelediğini bilir · Bloom: An"""
    cls, attr = random.choice(SHADOW_CLASSES)
    o1, o2 = random.choice([("a", "b"), ("o1", "o2"), ("ilk", "ikinci"), ("n1", "n2")])
    v0, v1, v2 = random.sample(range(1, 20), 3)
    variant = random.choice(["other", "both", "class", "class_change", "class_only"])
    code = f"class {cls}:\n    {attr} = {v0}\n\n{o1} = {cls}()\n{o2} = {cls}()\n"
    own = (f"<code>{o1}.{attr} = {v1}</code> ataması yalnızca {o1} nesnesine ait yeni bir nitelik oluşturur; "
           f"{o2} nesnesi ve sınıf etkilenmez.")
    if variant == "other":
        code += f"{o1}.{attr} = {v1}\nprint({o2}.{attr})"
        output = str(v0)
        wrongs = [Wrong(str(v1), own),
                  Wrong(err("AttributeError"), f"{o2} nesnesinin kendi {attr} niteliği yok, ama sınıfınki okunur; hata "
                                               "oluşmaz.")]
    elif variant == "both":
        code += f"{o1}.{attr} = {v1}\nprint({o1}.{attr}, {o2}.{attr})"
        output = f"{v1} {v0}"
        wrongs = [Wrong(f"{v1} {v1}", own),
                  Wrong(f"{v0} {v0}", f"{o1} nesnesine atanan {v1} değeri o nesnede kalır; {o1}.{attr} artık {v1}.")]
    elif variant == "class":
        code += f"{o1}.{attr} = {v1}\nprint({cls}.{attr})"
        output = str(v0)
        wrongs = [Wrong(str(v1), "Nesneye yapılan atama sınıf niteliğini değiştirmez; sınıfın kendi değeri aynı "
                                 "kalır.")]
    elif variant == "class_change":
        code += f"{o1}.{attr} = {v1}\n{cls}.{attr} = {v2}\nprint({o1}.{attr}, {o2}.{attr})"
        output = f"{v1} {v2}"
        wrongs = [Wrong(f"{v2} {v2}", f"{o1} nesnesinin kendi {attr} niteliği olduğu için sınıf niteliği değişse de "
                                      f"{o1}.{attr} {v1} kalır."),
                  Wrong(f"{v1} {v0}", f"Sınıf niteliği {v2} oldu; kendi niteliği olmayan {o2} sınıfınkini okur.")]
    else:
        code += f"{cls}.{attr} = {v2}\nprint({o1}.{attr}, {o2}.{attr})"
        output = f"{v2} {v2}"
        wrongs = [Wrong(f"{v0} {v0}", "Nesnelerin kendi niteliği yok; sınıf niteliği değişince ikisi de yeni değeri "
                                      "okur."),
                  Wrong(f"{v2} {v0}", f"{o2} nesnesinin de kendi niteliği yok; o da sınıfın yeni değerini okur.")]
    return tf_claim(
        code, output, wrongs,
        "Nesneye yapılan atama (<code>nesne.nitelik = ...</code>) yalnızca o nesneye ait bir nitelik oluşturur ve "
        "sınıf niteliğini o nesne için gölgeler. Kendi niteliği olmayan nesneler sınıf niteliğini okur.",
        hint="Atama nesneye mi yapılıyor, sınıfa mı? Okunan nesnenin kendi niteliği var mı?",
    )


SELF_CLASSES = [
    ("Kitap", "k", ("baslik", "sayfa"), ["Simyacı", "Çalıkuşu", "Sefiller", "Nutuk"], (120, 600)),
    ("Ogrenci", "o", ("ad", "numara"), PEOPLE, (100, 999)),
    ("Araba", "a", ("renk", "hiz"), ["kırmızı", "mavi", "beyaz", "siyah"], (60, 180)),
    ("Telefon", "t", ("model", "fiyat"), ["A12", "X5", "Nova", "M3"], (900, 4000)),
    ("Bitki", "b", ("tur", "boy"), ["lale", "gül", "papatya", "nergis"], (10, 90)),
]


@q("self Boşlukları (Boşluk Doldurma)", verify="fill")
def self_blank():
    """Kazanım: metot tanımında self'i ve nitelik erişiminde nitelik adını kullanır · Bloom: H/A"""
    cls, obj, (a1, a2), texts, (lo, hi) = random.choice(SELF_CLASSES)
    text_val, num_val = random.choice(texts), random.randint(lo, hi)
    chosen = random.choice([a1, a2])
    shown = text_val if chosen == a1 else str(num_val)
    in_print = random.random() < 0.5
    lines = {a: (f"        self.{a} = {a}" if in_print or a != chosen else f"        self.____ = {a}")
             for a in (a1, a2)}
    code = (f"class {cls}:\n    def __init__(____, {a1}, {a2}):\n{lines[a1]}\n{lines[a2]}\n\n"
            f"{obj} = {cls}(\"{text_val}\", {num_val})\nprint({obj}.{'____' if in_print else chosen})")
    other = a2 if chosen == a1 else a1
    attr_wrongs = [Wrong(other, f"Bu nitelik başka bir değeri tutar; ekrana {shown} yazılması isteniyor.")]
    if in_print:
        attr_wrongs.append(Wrong(f"self.{chosen}", "Sınıfın dışında self kullanılmaz; nesnenin adı ve nokta zaten "
                                                   "yazılı."))
    return fill_question(
        code, [["self"], [chosen]], shown,
        f"Kod ekrana <code>{e(shown)}</code> yazmalı. Boşlukları Python geleneğine uygun biçimde doldurunuz.",
        "Metotların ilk parametresi, metodu çağıran nesneyi temsil eden <code>self</code>'tir; nitelikler "
        f"<code>self.ad = ad</code> biçiminde nesneye bağlanır. Ekrana {e(shown)} yazması için <code>{chosen}</code> "
        "niteliği kullanılır.",
        hint="Metodun ilk parametresi kimi temsil eder? Ekrana yazılacak değer hangi nitelikte saklanıyor?",
        wrongs=[[Wrong(cls, "Sınıf adı değil, oluşturulan nesneyi temsil eden parametre yazılır; gövdede self "
                            "kullanıldığı için başka ad NameError verir."),
                 Wrong("this", "Python'da this değil self kullanılır; gövdede self tanımsız kalır.")],
                attr_wrongs],
    )


SUPER_CLASSES = [
    ("Kisi", "Ogrenci", "ad", "no", PEOPLE, (100, 999)),
    ("Arac", "Araba", "marka", "hiz", ["Anadol", "Murat", "Devrim"], (60, 180)),
    ("Hayvan", "Kedi", "ad", "yas", ["Tekir", "Pamuk", "Boncuk"], (1, 15)),
    ("Calisan", "Mudur", "ad", "maas", PEOPLE, (30, 90)),
    ("Sekil", "Kare", "renk", "kenar", ["kırmızı", "mavi", "yeşil"], (2, 20)),
]


@q("super() ile Kalıtım (Boşluk Doldurma)", verify="fill")
def super_blank():
    """Kazanım: alt sınıfı üst sınıftan türetir ve üst sınıfın __init__ metodunu super() ile çağırır · Bloom: U"""
    parent, child, a1, a2, texts, (lo, hi) = random.choice(SUPER_CLASSES)
    v1, v2 = random.choice(texts), random.randint(lo, hi)
    obj = child[0].lower()
    code = (f"class {parent}:\n    def __init__(self, {a1}):\n        self.{a1} = {a1}\n\n"
            f"class {child}(____):\n    def __init__(self, {a1}, {a2}):\n        ____.__init__({a1})\n"
            f"        self.{a2} = {a2}\n\n{obj} = {child}(\"{v1}\", {v2})\nprint({obj}.{a1}, {obj}.{a2})")
    return fill_question(
        code, [[parent], ["super()", f"super({child}, self)"]], f"{v1} {v2}",
        f"<code>{child}</code> sınıfı yukarıdaki sınıftan kalıtım almalı ve <code>{a1}</code> niteliğini üst "
        f"sınıfın <code>__init__</code> metoduyla atamalı. Kod ekrana <code>{e(v1)} {v2}</code> yazmalı. Boşlukları "
        "doldurunuz.",
        f"<code>class {child}({parent}):</code> kalıtımı kurar. <code>super().__init__({a1})</code> üst sınıfın "
        "<code>__init__</code> metodunu çağırır; self kendiliğinden iletilir.",
        hint="Alt sınıf hangi sınıftan türüyor? Üst sınıfın __init__ metoduna hangi hazır fonksiyonla ulaşılır?",
        wrongs=[[Wrong("self", "Sınıf satırında üst sınıfın adı yazılır; self burada tanımlı değildir."),
                 Wrong(child, "Sınıf kendinden türeyemez; bu satır çalışırken sınıf henüz tanımlanmamıştır."),
                 Wrong("object", f"Her sınıf zaten object'ten türer; {a1} niteliği {parent} sınıfından gelmeli.")],
                [Wrong(parent, f"<code>{parent}.__init__({a1})</code> self'i iletmez ve TypeError verir; bu biçimde "
                               f"<code>{parent}.__init__(self, {a1})</code> yazmak gerekirdi."),
                 Wrong("self", "<code>self.__init__</code> alt sınıfın kendi metodunu yeniden çağırır; üst sınıfa "
                               "ulaşılmaz."),
                 Wrong("super", "super bir fonksiyondur; parantezle çağrılmalıdır.")]],
    )


@q("Banka Hesabı")
def account_trace():
    """Kazanım: metot çağrılarıyla nesne durumunun değişimini izler · Bloom: U/An"""
    obj = random.choice(["h", "hesap", "kumbara"])
    while True:
        start = random.randrange(50, 201, 10)
        ops = [(random.choice(["yatir", "cek", "cek"]), random.randrange(10, 260, 10))
               for _ in range(random.randint(3, 4))]
        bal = naive = deposits = start
        rejected = 0
        for kind, amount in ops:
            if kind == "yatir":
                bal += amount
                naive += amount
                deposits += amount
            else:
                naive -= amount
                if amount <= bal:
                    bal -= amount
                else:
                    rejected += 1
        if any(k == "cek" for k, _ in ops) and (rejected or random.random() < 0.3):
            break
    calls = "\n".join(f"{obj}.{kind}({amount})" for kind, amount in ops)
    code = ("class Hesap:\n    def __init__(self, bakiye):\n        self.bakiye = bakiye\n\n"
            "    def yatir(self, miktar):\n        self.bakiye += miktar\n\n    def cek(self, miktar):\n"
            "        if miktar <= self.bakiye:\n            self.bakiye -= miktar\n\n"
            f"{obj} = Hesap({start})\n{calls}\nprint({obj}.bakiye)")
    wrongs = [Wrong(str(naive), "cek() yetersiz bakiyede işlem yapmaz; koşul sağlanmazsa bakiye değişmez."),
              Wrong(str(start), "Metotlar self.bakiye değerini kalıcı olarak değiştirir; başlangıç değeri kalmaz."),
              Wrong(str(deposits), "Bakiye yeterli olduğunda çekme işlemi yapılır ve bakiye azalır.")]
    return output_question(
        code, str(bal),
        "Her metot çağrısı aynı nesnenin <code>bakiye</code> niteliğini değiştirir. <code>cek()</code> yalnızca "
        f"miktar bakiyeden büyük değilse çeker. Son bakiye {bal}.",
        common_wrongs=wrongs, norm="sayi",
        hint="Her çağrıdan sonra bakiyeyi bir kenara yaz; cek() içindeki koşula dikkat et.",
    )


ISINSTANCE_SETS = [("Hayvan", "Kedi", "Kopek"), ("Arac", "Araba", "Bisiklet"), ("Sekil", "Kare", "Daire"),
                   ("Kisi", "Ogrenci", "Ogretmen")]


@q("isinstance ve Kalıtım")
def isinstance_check():
    """Kazanım: alt sınıf nesnesinin üst sınıfın da örneği olduğunu bilir · Bloom: A/U"""
    base, c1, c2 = random.choice(ISINSTANCE_SETS)
    b, o1, o2 = base.lower(), c1.lower(), c2.lower()
    pool = [
        (f"isinstance({o1}, {base})", True, o1,
         f"{c1} sınıfı {base} sınıfından türediği için her {c1} nesnesi aynı zamanda bir {base} nesnesidir."),
        (f"isinstance({o2}, {base})", True, o2,
         f"{c2} sınıfı {base} sınıfından türediği için her {c2} nesnesi aynı zamanda bir {base} nesnesidir."),
        (f"isinstance({b}, {c1})", False, b,
         f"Üst sınıf nesnesi alt sınıfın örneği sayılmaz: bir {base} nesnesi {c1} değildir."),
        (f"isinstance({o1}, {c2})", False, o1,
         f"{c1} ve {c2} ayrı alt sınıflardır; bir {c1} nesnesi {c2} sınıfının örneği değildir."),
        (f"isinstance({b}, {c2})", False, b,
         f"Üst sınıf nesnesi alt sınıfın örneği sayılmaz: bir {base} nesnesi {c2} değildir."),
        (f"isinstance({o1}, {c1})", True, o1, f"{o1} doğrudan {c1} sınıfından oluşturulmuştur."),
        (f"isinstance({b}, {base})", True, b, f"{b} doğrudan {base} sınıfından oluşturulmuştur."),
    ]
    # her ifade yarı olasılıkla True: dört birleşim (doğru cevap) dengeli dağılsın
    t1, t2 = random.random() < 0.5, random.random() < 0.5
    e1 = random.choice([x for x in pool if x[1] == t1])
    e2 = random.choice([x for x in pool if x[1] == t2 and x is not e1])
    objs = [(name, cls) for name, cls in ((b, base), (o1, c1), (o2, c2)) if name in (e1[2], e2[2])]
    code = (f"class {base}:\n    pass\n\nclass {c1}({base}):\n    pass\n\nclass {c2}({base}):\n    pass\n\n"
            + "\n".join(f"{name} = {cls}()" for name, cls in objs) + f"\nprint({e1[0]}, {e2[0]})")
    answer = f"{e1[1]} {e2[1]}"
    wrongs = [Wrong(f"{x} {y}", e1[3] if x != e1[1] else e2[3]) for x in (True, False) for y in (True, False)
              if f"{x} {y}" != answer]
    return output_question(
        code, answer,
        f"<code>{e1[0]}</code> → {e1[1]}: {e1[3]} <code>{e2[0]}</code> → {e2[1]}: {e2[3]}",
        wrongs=wrongs,
        hint=f"Her {c1} nesnesi bir {base} nesnesi midir? Her {base} nesnesi bir {c1} nesnesi midir?",
    )


LIST_ITEMS = ["kalem", "defter", "silgi", "cetvel", "çanta", "boya", "makas"]


@q("Nesne Listesi")
def object_list():
    """Kazanım: nesne listesinde döngüyle nitelik toplar ya da sayar · Bloom: U"""
    k = random.randint(3, 4)
    names = random.sample(LIST_ITEMS, k)
    prices = random.sample(range(5, 65, 5), k)
    srt = sorted(prices)
    edge = random.random() < 0.4
    limit = random.choice(srt[1:-1]) if edge else random.choice(srt[:-1]) + random.choice([1, 2, 3, 4])
    picked = [p for p in prices if p > limit]
    count_mode = random.random() < 0.35
    body = "        sayac += 1" if count_mode else "        toplam += u.fiyat"
    var = "sayac" if count_mode else "toplam"
    items = ", ".join(f"Urun(\"{n}\", {p})" for n, p in zip(names, prices))
    code = ("class Urun:\n    def __init__(self, ad, fiyat):\n        self.ad = ad\n        self.fiyat = fiyat\n\n"
            f"urunler = [{items}]\n{var} = 0\nfor u in urunler:\n    if u.fiyat > {limit}:\n{body}\nprint({var})")
    answer = len(picked) if count_mode else sum(picked)
    with_eq = [p for p in prices if p >= limit]
    if count_mode:
        wrongs = [Wrong(str(sum(picked)), "Kod fiyatları toplamıyor; koşulu sağlayan her ürün için sayacı 1 "
                                          "artırıyor."),
                  Wrong(str(k), "Yalnızca koşulu sağlayan ürünler sayılır.")]
    else:
        wrongs = [Wrong(str(sum(prices)), "Koşulu sağlamayan ürünlerin fiyatı eklenmez."),
                  Wrong(str(len(picked)), "Ürün sayısı değil, koşulu sağlayan ürünlerin fiyatları toplanıyor."),
                  Wrong(str(sum(prices) - sum(picked)), "Koşulu sağlayan ürünlerin fiyatları eklenir; sağlamayanlar "
                                                        "değil.")]
    if len(with_eq) != len(picked):
        val = len(with_eq) if count_mode else sum(with_eq)
        wrongs.append(Wrong(str(val), f"Koşul > ile yazılmış; fiyatı tam {limit} olan ürün dahil edilmez."))
    return output_question(
        code, str(answer),
        "Döngü her Urun nesnesinin <code>fiyat</code> niteliğine bakar; koşulu sağlayanlar "
        f"({', '.join(map(str, picked)) or 'yok'}) " + ("sayılır." if count_mode else "toplanır.") + f" Sonuç {answer}.",
        common_wrongs=wrongs, norm="sayi",
        hint="Her nesnenin fiyatına koşulu uygula; koşulu sağlayanlarla ne yapılıyor?",
    )


SHAPES = {
    "dikdortgen_alan": ("Dikdortgen", ["en", "boy"], "alan", "alanını", "self.en * self.boy", lambda a, b: a * b),
    "dikdortgen_cevre": ("Dikdortgen", ["en", "boy"], "cevre", "çevresini", "2 * (self.en + self.boy)",
                         lambda a, b: 2 * (a + b)),
    "kare_alan": ("Kare", ["kenar"], "alan", "alanını", "self.kenar * self.kenar", lambda a: a * a),
    "kare_cevre": ("Kare", ["kenar"], "cevre", "çevresini", "4 * self.kenar", lambda a: 4 * a),
    "ucgen_alan": ("Ucgen", ["taban", "yukseklik"], "alan", "alanını", "self.taban * self.yukseklik / 2",
                   lambda a, b: a * b / 2),
    "kutu_hacim": ("Kutu", ["en", "boy", "yukseklik"], "hacim", "hacmini", "self.en * self.boy * self.yukseklik",
                   lambda a, b, c: a * b * c),
}


@q("Şekil Sınıfı (Kod Yazma)")
def write_rect_class():
    """Kazanım: __init__ ve değer döndüren metot içeren sınıf yazar · Bloom: O"""
    key = random.choice(list(SHAPES))
    cls, params, method, desc, formula, func = SHAPES[key]
    ex = [random.randint(2, 9) for _ in params]
    res = func(*ex)
    init = "".join(f"        self.{p} = {p}\n" for p in params)
    names = ", ".join(f"<code>{p}</code>" for p in params)
    return {
        "type": "code",
        "text": f"<code>{cls}</code> adında bir sınıf yazınız: <code>__init__</code> metodu {names} "
                f"{'değerini' if len(params) == 1 else 'değerlerini'} alıp nesnede saklasın; <code>{method}()</code> "
                f"metodu şeklin {desc} <strong>döndürsün</strong> (<code>return</code>). (Örnek: "
                f"<code>{cls}({', '.join(map(str, ex))}).{method}()</code> → <code>{res}</code>)",
        "code": None,
        "check": {"kind": "class_method", "cls": cls, "params": params, "method": method, "formula": key},
        "answer": f"class {cls}:\n    def __init__(self, {', '.join(params)}):\n{init}\n"
                  f"    def {method}(self):\n        return {formula}",
        "hint": "Değerleri __init__ içinde self ile sakla; metotta onlara self üzerinden ulaş ve sonucu döndür.",
        "solution": f"<code>__init__</code> içinde <code>self.{params[0]} = {params[0]}</code> gibi atamalar değerleri "
                    f"nesneye bağlar. <code>{method}(self)</code> metodu bu nitelikleri kullanarak "
                    f"<code>return {formula}</code> ile sonucu döndürür.",
    }


COUNTER_OTHERS = {"sifirla": ("değeri 0 yapmalı", lambda d: 0, "0 yapsın"),
                  "azalt": ("değeri 1 azaltmalı", lambda d: d - 1, "1 azaltsın")}


@q("Sayaç Sınıfı (Kod Yazma)")
def write_counter_class():
    """Kazanım: nesne durumunu değiştiren metotlar yazar · Bloom: O"""
    cls = random.choice(["Sayac", "Tiklayici", "Adimsayar"])
    attr = random.choice(["deger", "sayi", "adim"])
    inc = random.choice(["artir", "ileri", "say"])
    other, kind = random.choice([("sifirla", "sifirla"), ("azalt", "azalt"), ("geri", "azalt")])
    n = random.randint(2, 4)
    obj = cls[0].lower()
    other_body = f"self.{attr} = 0" if kind == "sifirla" else f"self.{attr} -= 1"
    return {
        "type": "code",
        "text": f"<code>{cls}</code> adında bir sınıf yazınız: <code>__init__</code> metodunda <code>{attr}</code> "
                f"niteliği 0 olsun; <code>{inc}()</code> metodu bu değeri 1 artırsın; <code>{other}()</code> metodu "
                f"değeri {COUNTER_OTHERS[kind][2]}. (Örnek: <code>{obj} = {cls}()</code> ardından {n} kez "
                f"<code>{obj}.{inc}()</code> çağrılınca <code>{obj}.{attr}</code> → <code>{n}</code>)",
        "code": None,
        "check": {"kind": "counter_class", "cls": cls, "attr": attr, "inc": inc, "other": other, "other_kind": kind},
        "answer": f"class {cls}:\n    def __init__(self):\n        self.{attr} = 0\n\n    def {inc}(self):\n"
                  f"        self.{attr} += 1\n\n    def {other}(self):\n        {other_body}",
        "hint": "Değer her nesneye özel olmalı: hep self üzerinden eriş ve değiştir.",
        "solution": f"<code>self.{attr} = 0</code> başlangıç değerini her nesneye ayrı verir. Metotlar "
                    f"<code>self.{attr}</code> niteliğini değiştirir (<code>self.{attr} += 1</code>). Sınıf değişkeni "
                    f"(<code>{cls}.{attr}</code>) kullanılsaydı bütün nesneler aynı sayacı paylaşırdı.",
    }


# ================================================================= kod yazma denetleyicileri
SELF_FIRST = "Metodun ilk parametresi <code>self</code> olmalı."


class _MissingAttr(Exception):
    def __init__(self, attr):
        super().__init__(attr)
        self.attr = attr


def _find_class(tree, name):
    found = [s for s in tree.body if isinstance(s, ast.ClassDef) and s.name == name]
    return found[-1] if found else None


def _method(cls, name):
    found = [s for s in cls.body if isinstance(s, ast.FunctionDef) and s.name == name]
    return found[-1] if found else None


def _attr_assigns(stmt, self_name):
    """self.x = değer atamaları: [(x, değer düğümü)] (self.a, self.b = a, b dahil)."""
    if isinstance(stmt, ast.AnnAssign) and stmt.value is not None:
        pairs = [(stmt.target, stmt.value)]
    elif isinstance(stmt, ast.Assign):
        pairs = []
        for target in stmt.targets:
            if (isinstance(target, ast.Tuple) and isinstance(stmt.value, ast.Tuple)
                    and len(target.elts) == len(stmt.value.elts)):
                pairs += list(zip(target.elts, stmt.value.elts))
            else:
                pairs.append((target, stmt.value))
    else:
        return []
    return [(t.attr, v) for t, v in pairs
            if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id == self_name]


class _SelfAttrs(ast.NodeTransformer):
    """self.x düğümlerini mapping[x] ile değiştirir; bilinmeyen nitelikte _MissingAttr."""

    def __init__(self, self_name, mapping):
        self.self_name = self_name
        self.mapping = mapping

    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name) and node.value.id == self.self_name:
            if node.attr not in self.mapping:
                raise _MissingAttr(node.attr)
            return copy.deepcopy(self.mapping[node.attr])
        self.generic_visit(node)
        return node


def _method_self(method):
    """Yalnızca self alan metot: (self adı, None) ya da (None, öğrenciye not)."""
    params = function_params(method)
    if not params:
        return None, SELF_FIRST
    if len(params) != 1:
        return None, f"<code>{method.name}()</code> metodu yalnızca self parametresini almalı."
    return params[0], None


@checker("class_method")
def check_class_method(tree, p):
    """__init__ değerleri self ile saklar; metot bu nitelikleri kullanıp formülün sonucunu döndürür."""
    cls_name, params, mname = p["cls"], p["params"], p["method"]
    formula = SHAPES[p["formula"]][5]
    cls = _find_class(tree, cls_name)
    if cls is None:
        return False, f"<code>{cls_name}</code> adında bir sınıf tanımlanmamış (<code>class {cls_name}:</code>)."
    init = _method(cls, "__init__")
    if init is None:
        return False, "Sınıfta <code>__init__</code> metodu yok; değerler nesne oluşturulurken saklanmalı."
    ip = function_params(init)
    if not ip:
        return False, SELF_FIRST
    if len(ip) != len(params) + 1:
        return False, f"<code>__init__</code> metodu self'ten sonra {len(params)} parametre almalı."
    s, init_params = ip[0], ip[1:]
    mapping, computed = {}, set()
    for stmt in init.body:
        for attr, value in _attr_assigns(stmt, s):
            if isinstance(value, ast.Name) and value.id in init_params:
                mapping[attr] = ast.Name(id=params[init_params.index(value.id)], ctx=ast.Load())
            else:
                computed.add(attr)
    stored = {node.id for node in mapping.values()}
    for given, own in zip(params, init_params):
        if given not in stored:
            return False, (f"<code>__init__</code> metodu <code>{own}</code> değerini nesnede saklamalı (self ile bir "
                           "niteliğe ata).")
    meth = _method(cls, mname)
    if meth is None:
        return False, f"Sınıfta <code>{mname}</code> metodu tanımlanmamış."
    ms, note = _method_self(meth)
    if note:
        return False, note
    if not function_returns(meth):
        if find_prints(meth):
            return False, f"<code>{mname}()</code> metodu sonucu yazdırmak yerine <code>return</code> ile döndürmeli."
        return False, f"<code>{mname}()</code> metodunda <code>return</code> yok."
    tr = Tracker()
    expr = None
    for stmt in tr.run(meth.body):
        if isinstance(stmt, ast.Return):
            if stmt.value is None:
                return False, "<code>return</code> satırına döndürülecek değeri yazmayı unutma."
            expr = tr.inline(stmt.value)
            break
        if isinstance(stmt, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
            raise Unknown("dallanan metot")
    if expr is None:
        raise Unknown("return bulunamadı")
    called = {id(n.func) for n in ast.walk(expr) if isinstance(n, ast.Call)}
    free = [n.id for n in ast.walk(expr) if isinstance(n, ast.Name) and n.id != ms and id(n) not in called]
    if free:
        example = next((a for a, node in mapping.items() if node.id == free[0]), next(iter(mapping)))
        return False, (f"Metotta nesnenin değerlerine <code>{ms}.{example}</code> biçiminde ulaşılır; yalnızca "
                       f"<code>{free[0]}</code> yazmak yetmez.")
    try:
        expr = _SelfAttrs(ms, mapping).visit(copy.deepcopy(expr))
    except _MissingAttr as miss:
        if miss.attr in computed:
            return False, (f"<code>{mname}()</code> hesabı metodun içinde, saklanan değerler kullanılarak yapılmalı; "
                           "böylece nitelikler değişince sonuç da güncellenir.")
        return False, f"<code>{ms}.{miss.attr}</code> niteliği <code>__init__</code> içinde tanımlanmamış."
    if not computes(expr, params, formula):
        return False, f"<code>{mname}()</code> metodu doğru değeri döndürmüyor; formülü kontrol et."
    return True, OK


def _attr_effect(func, self_name, attr, initial):
    """Metot bittiğinde self.<attr> değerinin ifadesi (initial: başlangıç ifadesi); değişmiyorsa None.
    Yerel ara değişkenler yerine konur; dallanan yapılar içinde niteliğe atama varsa Unknown."""
    cur, changed, defs = initial, False, {}

    def sub(node):
        class Sub(ast.NodeTransformer):
            def visit_Attribute(self, n):
                if isinstance(n.value, ast.Name) and n.value.id == self_name:
                    if n.attr == attr and cur is not None:
                        return copy.deepcopy(cur)
                    raise Unknown("başka nitelik")
                self.generic_visit(n)
                return n

            def visit_Name(self, n):
                if isinstance(n.ctx, ast.Load) and n.id in defs:
                    return copy.deepcopy(defs[n.id])
                return n
        return Sub().visit(copy.deepcopy(node))

    def is_attr(t):
        return isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id == self_name

    for stmt in func.body:
        if isinstance(stmt, ast.Assign):
            for t in stmt.targets:
                if is_attr(t) and t.attr == attr:
                    cur, changed = sub(stmt.value), True
                elif isinstance(t, ast.Name):
                    defs[t.id] = sub(stmt.value)
                elif not is_attr(t):
                    raise Unknown("desteklenmeyen atama")
        elif isinstance(stmt, ast.AugAssign):
            t = stmt.target
            if is_attr(t) and t.attr == attr:
                if cur is None:
                    raise Unknown("başlangıç değeri yok")
                cur, changed = ast.BinOp(left=copy.deepcopy(cur), op=stmt.op, right=sub(stmt.value)), True
            elif isinstance(t, ast.Name):
                left = defs.get(t.id, ast.Name(id=t.id, ctx=ast.Load()))
                defs[t.id] = ast.BinOp(left=copy.deepcopy(left), op=stmt.op, right=sub(stmt.value))
            elif not is_attr(t):
                raise Unknown("desteklenmeyen atama")
        elif isinstance(stmt, (ast.Expr, ast.Pass, ast.Return)):
            continue
        elif any(is_attr(n) and n.attr == attr and isinstance(n.ctx, ast.Store) for n in ast.walk(stmt)):
            raise Unknown("dallanan atama")
    return cur if changed else None


@checker("counter_class")
def check_counter_class(tree, p):
    """__init__'te self.<attr> = 0; inc metodu 1 artırır; other metodu sıfırlar ya da 1 azaltır."""
    cls_name, attr, inc, other, kind = p["cls"], p["attr"], p["inc"], p["other"], p["other_kind"]
    cls = _find_class(tree, cls_name)
    if cls is None:
        return False, f"<code>{cls_name}</code> adında bir sınıf tanımlanmamış (<code>class {cls_name}:</code>)."
    if any(isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == cls_name
           and n.attr == attr for n in ast.walk(cls)):
        return False, (f"<code>{attr}</code> her nesneye ait olmalı; <code>{cls_name}.{attr}</code> yerine "
                       f"<code>self.{attr}</code> kullan.")
    init = _method(cls, "__init__")
    if init is None:
        return False, (f"Sınıfta <code>__init__</code> metodu yok; <code>{attr}</code> başlangıç değerini nesne "
                       "oluşturulurken __init__ içinde ver.")
    ip = function_params(init) or []
    if len(ip) > 1 and len(init.args.defaults) == len(ip) - 1 and not init.args.kwonlyargs:
        # __init__(self, deger=0): Sayac() çağrısında varsayılan değer kullanılır; parametreyi o değerle izle
        s = ip[0]
        init = copy.deepcopy(init)
        init.body = [ast.Assign(targets=[ast.Name(id=name, ctx=ast.Store())], value=default)
                     for name, default in zip(ip[1:], init.args.defaults)] + init.body
    else:
        s, note = _method_self(init)
        if note:
            return False, note
    start = _attr_effect(init, s, attr, None)
    start_value = const_value(start) if start is not None else None
    if isinstance(start_value, bool) or not same_value(start_value, 0):
        return False, f"<code>__init__</code> içinde <code>self.{attr}</code> başlangıçta 0 olmalı."
    want_text, want_func, _ = COUNTER_OTHERS[kind]
    for mname, func, text in ((inc, lambda d: d + 1, "değeri 1 artırmalı"), (other, want_func, want_text)):
        meth = _method(cls, mname)
        if meth is None:
            return False, f"Sınıfta <code>{mname}</code> metodu tanımlanmamış."
        ms, note = _method_self(meth)
        if note:
            return False, note
        effect = _attr_effect(meth, ms, attr, ast.Name(id="d_", ctx=ast.Load()))
        if effect is None:
            return False, (f"<code>{mname}()</code> metodu <code>self.{attr}</code> değerini değiştirmeli; yeni değeri "
                           "döndürmek ya da yerel bir değişkene yazmak nesneyi değiştirmez.")
        if not computes(effect, ["d_"], func):
            return False, f"<code>{mname}()</code> metodu {text}."
    return True, OK
