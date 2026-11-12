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


def _grades():
    names = random.sample(PEOPLE, 3)
    return {n: random.randint(40, 100) for n in names}


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


@q("Olmayan Anahtar", verify="output")
def dict_get():
    d = _grades()
    missing = random.choice([p for p in PEOPLE if p not in d])
    default = random.choice([0, -1])
    return output_question(
        f"notlar = {d}\nprint(notlar.get(\"{missing}\", {default}))", str(default),
        "<code>get(anahtar, varsayılan)</code> anahtar yoksa hata vermek yerine varsayılan değeri döndürür. "
        f"<code>notlar[\"{missing}\"]</code> yazılsaydı KeyError oluşurdu.",
        wrongs=[
            Wrong(err("KeyError"), "get() anahtar yoksa hata vermez; varsayılan değeri döndürür. KeyError köşeli "
                                   "parantezle erişimde olur."),
            Wrong("None", "Varsayılan değer verildiği için None değil, o değer döner. Varsayılan verilmeseydi None "
                          "dönerdi."),
            Wrong(f"{missing} {default}", "get() yalnızca değeri döndürür; anahtarı yazmaz."),
        ],
        hint=f"\"{missing}\" sözlükte var mı? Yoksa get() ne döndürür?",
    )


@q("Sözlük Güncelleme", verify="output")
def dict_update():
    d = _grades()
    existing = random.choice(list(d))
    new = random.choice([p for p in PEOPLE if p not in d])
    return output_question(
        f"notlar = {d}\nnotlar[\"{existing}\"] = 100\nnotlar[\"{new}\"] = 75\nprint(len(notlar))", "4",
        "Var olan anahtara atama değeri <strong>günceller</strong> (eleman sayısı değişmez); yeni anahtara atama "
        "yeni eleman <strong>ekler</strong>. 3 + 1 = 4 eleman.",
        wrongs=[
            Wrong("5", f"\"{existing}\" zaten sözlükte; ona atama yeni eleman eklemez, değeri günceller."),
            Wrong("3", f"\"{new}\" sözlükte yoktu; yeni anahtara atama yeni eleman ekler."),
            Wrong(err("KeyError"), "Sözlüğe yeni anahtarla atama yapmak hata vermez; eleman ekler."),
        ],
        hint="Hangi atama var olan bir anahtara, hangisi yeni bir anahtara yapılıyor?",
    )


@q("Sözlük Üzerinde Döngü", verify="output")
def dict_loop():
    d = _grades()
    total = sum(d.values())
    return output_question(
        f"notlar = {d}\ntoplam = 0\nfor ad, puan in notlar.items():\n    toplam += puan\nprint(toplam)", str(total),
        "<code>items()</code> her adımda (anahtar, değer) çifti verir; burada yalnızca değerler toplanır.",
        wrongs=[
            Wrong(str(max(d.values())), "Kod en büyük değeri bulmuyor; tüm değerleri topluyor."),
            Wrong(str(len(d)), "toplam'a eleman sayısı değil, her elemanın puanı ekleniyor."),
            Wrong(err("TypeError"), "items() (anahtar, değer) çiftleri verir; ad, puan olarak açılması hata vermez."),
        ],
        hint="items() her adımda hangi iki değeri verir? toplam'a hangisi ekleniyor?",
    )


@q("Demetler Değiştirilemez", verify="error")
def tuple_immutable():
    t = tuple(random.sample(range(1, 20), 3))
    return output_question(
        f"t = {t}\nt[0] = 99\nprint(t)", err("TypeError"),
        "Demet (tuple) oluşturulduktan sonra değiştirilemez; elemana atama TypeError verir. Değiştirilebilir "
        "bir yapı gerekiyorsa liste kullanılır.",
        wrongs=[
            Wrong(str((99,) + t[1:]), "Demetler değiştirilemez; elemana atama hata verir."),
            Wrong(str(t), "Atama satırı hata verdiği için print'e hiç ulaşılmaz."),
            Wrong(str([99] + list(t[1:])), "Demet kendiliğinden listeye dönüşmez; atama hata verir."),
        ],
        hint="Normal parantezle oluşturulan bir demetin elemanı sonradan değiştirilebilir mi?",
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
