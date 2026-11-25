"""Ünite 8 - Sözlükler, Demetler ve Kümeler."""
import random

from ..helpers import FRUITS, PEOPLE, Wrong, err, output_question
from ..registry import register_unit

UNIT = register_unit(
    "koleksiyonlar", "Sözlük, Demet ve Küme", "Orta",
    "dict (anahtar-değer, get, keys/values/items, güncelleme), tuple (değiştirilemezlik, açma), "
    "set (tekrarsız elemanlar, kesişim/birleşim).",
    order=8,
)
q = UNIT.question


def _grades(k=3):
    """k öğrencinin birbirinden farklı notları (aynı not iki şıkkı aynı yapardı)."""
    names = random.sample(PEOPLE, k)
    return dict(zip(names, random.sample(range(40, 101), k)))


@q("Sözlükten Değer Okuma", verify="output")
def dict_access():
    d = _grades()
    name = random.choice(list(d))
    return output_question(
        f"notlar = {d}\nprint(notlar[\"{name}\"])", str(d[name]),
        "Sözlükte değere <strong>anahtar</strong> ile ulaşılır: <code>sozluk[anahtar]</code>.",
        wrongs=[Wrong(str(v), f"Bu, \"{k}\" anahtarının değeri; burada \"{name}\" anahtarı isteniyor.")
                for k, v in d.items() if k != name] + [
            Wrong(name, "print anahtarın değerini yazar, anahtarın kendisini değil.")],
        hint="Köşeli parantez içindeki anahtar hangisi ve o anahtarın karşılığındaki değer ne?",
    )


@q("Olmayan Anahtar", verify="outcome")
def dict_get():
    """get() hem olmayan hem var olan anahtarla, köşeli parantezle erişim de olmayan anahtarla sorulur;
    varsayılan değer de değişir (K4, O8)."""
    d = _grades()
    default = random.choice(["0", "-1", '"Yok"', '"Girmedi"', "None"])
    shown_default = default.strip('"')
    missing = random.choice([p for p in PEOPLE if p not in d])
    variant = random.choices(["get_missing", "get_present", "bracket_missing"], weights=[45, 30, 25])[0]
    if variant == "get_missing":
        key, res = missing, shown_default
        code = f"notlar = {d}\nprint(notlar.get(\"{key}\", {default}))"
        expl = ("<code>get(anahtar, varsayılan)</code> anahtar yoksa hata vermek yerine varsayılan değeri döndürür. "
                f"<code>notlar[\"{key}\"]</code> yazılsaydı KeyError oluşurdu.")
        wrongs = [
            Wrong(err("KeyError"), "get() anahtar yoksa hata vermez; varsayılan değeri döndürür. KeyError köşeli "
                                   "parantezle erişimde olur."),
            Wrong(f"{key} {shown_default}", "get() yalnızca değeri döndürür; anahtarı yazmaz."),
            Wrong(str(max(d.values())), f"\"{key}\" sözlükte yok; get() başka bir öğrencinin notunu döndürmez."),
        ]
        if default != "None":
            wrongs.insert(1, Wrong("None", "Varsayılan değer verildiği için None değil, o değer döner. Varsayılan "
                                           "verilmeseydi None dönerdi."))
        hint = f"\"{key}\" sözlükte var mı? Yoksa get() ne döndürür?"
    elif variant == "get_present":
        key = random.choice(list(d))
        res = str(d[key])
        code = f"notlar = {d}\nprint(notlar.get(\"{key}\", {default}))"
        expl = (f"\"{key}\" sözlükte var; <code>get()</code> onun değerini döndürür. Varsayılan değer yalnızca anahtar "
                "yoksa kullanılır.")
        wrongs = [
            Wrong(shown_default, "Varsayılan değer yalnızca anahtar sözlükte yoksa döner; bu anahtar sözlükte var."),
            Wrong(f"{key} {res}", "get() yalnızca değeri döndürür; anahtarı yazmaz."),
            Wrong(err("KeyError"), f"\"{key}\" sözlükte var; hata oluşmaz."),
        ]
        hint = f"\"{key}\" sözlükte var mı? Varsa get() ne döndürür?"
    else:
        key, res = missing, err("KeyError")
        code = f"notlar = {d}\nprint(notlar[\"{key}\"])"
        expl = (f"\"{key}\" sözlükte yok. Köşeli parantezle olmayan bir anahtara erişmek KeyError verir. Hata yerine "
                f"varsayılan bir değer istenirse <code>notlar.get(\"{key}\", 0)</code> kullanılır.")
        wrongs = [
            Wrong("None", "Köşeli parantezle erişimde anahtar yoksa None dönmez, KeyError oluşur. None'ı get() döndürür."),
            Wrong("0", "Python olmayan bir anahtar için kendiliğinden 0 vermez; KeyError oluşur."),
            Wrong(str(max(d.values())), f"\"{key}\" sözlükte yok; başka bir öğrencinin notu dönmez, hata oluşur."),
        ]
        hint = f"\"{key}\" sözlükte var mı? Köşeli parantezle olmayan bir anahtara erişilirse ne olur?"
    return output_question(code, res, expl, wrongs=wrongs, hint=hint)


@q("Sözlük Güncelleme", verify="output")
def dict_update():
    """Başlangıç boyutu ile güncellenen ve eklenen anahtar sayısı rastgele; cevap 3-7 arasında değişir (K5)."""
    size = random.randint(2, 5)
    d = _grades(size)
    updated = random.sample(list(d), random.randint(1, 2) if size > 2 else 1)
    added = random.sample([p for p in PEOPLE if p not in d], random.randint(1, 2))
    steps = [(name, random.randint(40, 100)) for name in updated + added]
    random.shuffle(steps)
    lines = "\n".join(f"notlar[\"{name}\"] = {value}" for name, value in steps)
    res = size + len(added)
    wrongs = [
        Wrong(str(size + len(steps)), "Var olan bir anahtara atama yeni eleman eklemez, değeri günceller ("
                                      + ", ".join(f'"{n}"' for n in updated) + " zaten sözlükte)."),
        Wrong(str(size), "Sözlükte olmayan anahtara atama yeni eleman ekler ("
                         + ", ".join(f'"{n}"' for n in added) + " yeni)."),
        Wrong(str(len(steps)), "len() sözlükteki bütün elemanları sayar; yalnızca bu kodda atananları değil."),
        Wrong(str(len(added)), "len() sözlükteki bütün elemanları sayar; yalnızca yeni eklenenleri değil."),
    ]
    if random.random() < 0.5:
        wrongs.insert(random.randint(0, 2), Wrong(err("KeyError"), "Sözlüğe yeni anahtarla atama yapmak hata "
                                                                   "vermez; eleman ekler."))
    return output_question(
        f"notlar = {d}\n{lines}\nprint(len(notlar))", str(res),
        "Var olan anahtara atama değeri <strong>günceller</strong> (eleman sayısı değişmez); yeni anahtara atama "
        f"yeni eleman <strong>ekler</strong>. {size} + {len(added)} = {res} eleman.",
        wrongs=wrongs,
        hint="Hangi atamalar var olan bir anahtara, hangileri yeni bir anahtara yapılıyor?",
    )


@q("Sözlük Üzerinde Döngü", verify="output")
def dict_loop():
    d = _grades()
    total = sum(d.values())
    last = list(d.values())[-1]
    return output_question(
        f"notlar = {d}\ntoplam = 0\nfor ad, puan in notlar.items():\n    toplam += puan\nprint(toplam)", str(total),
        "<code>items()</code> her adımda (anahtar, değer) çifti verir; burada yalnızca değerler toplanır.",
        wrongs=[
            Wrong(str(max(d.values())), "Kod en büyük değeri bulmuyor; tüm değerleri topluyor."),
            Wrong(str(len(d)), "toplam'a eleman sayısı değil, her elemanın puanı ekleniyor."),
            Wrong(str(last), "<code>+=</code> her turda puanı toplama ekler; yalnızca son puan kalmaz."),
            Wrong(str(min(d.values())), "Kod en küçük değeri bulmuyor; tüm değerleri topluyor."),
        ],
        hint="items() her adımda hangi iki değeri verir? toplam'a hangisi ekleniyor?",
    )


@q("Demetler Değiştirilemez", verify="outcome")
def tuple_immutable():
    """Demete atama (hata) ile listeye çevirip atama (hatasız) karışık sorulur (K5)."""
    t = tuple(random.sample(range(1, 20), 3))
    i = random.randint(0, 2)
    new = random.randint(90, 99)
    changed = list(t)
    changed[i] = new
    hint = "Değiştirilen yapı bir demet mi, yoksa demetten oluşturulmuş bir liste mi?"
    if random.random() < 0.35:
        return output_question(
            f"t = {t}\nt[{i}] = {new}\nprint(t)", err("TypeError"),
            "Demet (tuple) oluşturulduktan sonra değiştirilemez; elemana atama TypeError verir. Değiştirilebilir "
            "bir yapı gerekiyorsa liste kullanılır.",
            wrongs=[
                Wrong(str(tuple(changed)), "Demetler değiştirilemez; elemana atama hata verir."),
                Wrong(str(t), "Atama satırı hata verdiği için print'e hiç ulaşılmaz."),
                Wrong(str(changed), "Demet kendiliğinden listeye dönüşmez; atama hata verir."),
            ],
            hint=hint,
        )
    return output_question(
        f"t = {t}\nliste = list(t)\nliste[{i}] = {new}\nprint(liste)", str(changed),
        "<code>list(t)</code> demetin elemanlarıyla yeni bir <strong>liste</strong> oluşturur. Listeler "
        "değiştirilebilir; atama hata vermez.",
        wrongs=[
            Wrong(err("TypeError"), "Atama demete değil, list(t) ile oluşturulan listeye yapılıyor; listeler "
                                    "değiştirilebilir."),
            Wrong(str(tuple(changed)), "list() demeti listeye çevirir; liste köşeli parantezle yazılır."),
            Wrong(str(list(t)), f"liste[{i}] = {new} ataması listeyi değiştirir; print değişmiş listeyi yazar."),
        ],
        hint=hint,
    )


@q("Demet Açma", verify="output")
def tuple_unpack():
    a, b, c = random.sample(range(1, 30), 3)
    return output_question(
        f"nokta = ({a}, {b}, {c})\nx, y, z = nokta\nprint(y)", str(b),
        "Demet açmada elemanlar sırasıyla değişkenlere atanır: x = ilk, y = ikinci, z = üçüncü eleman.",
        wrongs=[
            Wrong(str(a), "x ilk elemanı alır; y ikinci elemanı alır."),
            Wrong(str(c), "z üçüncü elemanı alır; y ikinci elemanı alır."),
            Wrong(str((a, b, c)), "print(y) yalnızca y'yi yazar; demetin tamamını değil."),
        ],
        hint="Elemanlar soldaki değişkenlere hangi sırayla dağıtılır?",
    )


SET_OPS = {
    "&": "kesişim: iki kümede de olan elemanlar",
    "|": "birleşim: kümelerden en az birinde olan elemanlar",
    "-": "fark: ilk kümede olup ikincide olmayan elemanlar",
}


@q("Kümeler", verify="output")
def set_ops():
    a = set(random.sample(range(1, 10), 4))
    b = set(random.sample(range(1, 10), 4))
    if random.random() < 0.4:
        items = random.choices(FRUITS[:4], k=6)
        n = len(set(items))
        return output_question(
            f"liste = {items}\nprint(len(set(liste)))", str(n),
            "Küme (set) aynı elemanı yalnızca bir kez tutar; <code>set()</code> tekrarları atar.",
            wrongs=[Wrong(str(len(items)), "set() tekrar eden elemanları atar; her eleman bir kez sayılır."),
                    Wrong(str(n + 1), "Farklı elemanları tek tek say; set her birini bir kez tutar."),
                    Wrong(str(n - 1), "Farklı elemanları tek tek say; set her birini bir kez tutar.")],
            hint="Listede kaç farklı meyve var?",
        )
    op = random.choice(sorted(SET_OPS))
    res = {"&": a & b, "|": a | b, "-": a - b}[op]
    candidates = [(a & b, "&"), (a | b, "|"), (a - b, "-"), (b - a, "ters")]
    wrongs = []
    for value, kind in candidates:
        if kind == op:
            continue
        what = "b - a: ikinci kümede olup birincide olmayanlar" if kind == "ters" else SET_OPS[kind]
        wrongs.append(Wrong(str(sorted(value)), f"Bu, {what}. Burada <code>{op}</code> kullanılıyor."))
    return output_question(
        f"a = {sorted(a)}\nb = {sorted(b)}\nprint(sorted(set(a) {op} set(b)))", str(sorted(res)),
        f"<code>{op}</code> operatörü {SET_OPS[op]}. sorted() sonucu sıralı bir listeye çevirir.",
        wrongs=wrongs,
        hint=f"<code>{op}</code> hangi küme işlemidir?",
    )
