"""Ünite 8 - Sözlükler, Demetler ve Kümeler."""
import random

from ..helpers import FRUITS, PEOPLE, err, output_question
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
        wrongs=[str(v) for k, v in d.items() if k != name] + [name],
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
        wrongs=[err("KeyError"), "None", f"{missing} {default}"],
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
        wrongs=["5", "3", err("KeyError")],
    )


@q("Sözlük Üzerinde Döngü", verify="output")
def dict_loop():
    d = _grades()
    total = sum(d.values())
    return output_question(
        f"notlar = {d}\ntoplam = 0\nfor ad, puan in notlar.items():\n    toplam += puan\nprint(toplam)", str(total),
        "<code>items()</code> her adımda (anahtar, değer) çifti verir; burada yalnızca değerler toplanır.",
        wrongs=[str(max(d.values())), str(len(d)), err("TypeError")],
    )


@q("Demetler Değiştirilemez", verify="error")
def tuple_immutable():
    t = tuple(random.sample(range(1, 20), 3))
    return output_question(
        f"t = {t}\nt[0] = 99\nprint(t)", err("TypeError"),
        "Demet (tuple) oluşturulduktan sonra değiştirilemez; elemana atama TypeError verir. Değiştirilebilir "
        "bir yapı gerekiyorsa liste kullanılır.",
        wrongs=[str((99,) + t[1:]), str(t), str([99] + list(t[1:]))],
    )


@q("Demet Açma", verify="output")
def tuple_unpack():
    a, b, c = random.sample(range(1, 30), 3)
    return output_question(
        f"nokta = ({a}, {b}, {c})\nx, y, z = nokta\nprint(y)", str(b),
        "Demet açmada elemanlar sırasıyla değişkenlere atanır: x = ilk, y = ikinci, z = üçüncü eleman.",
        wrongs=[str(a), str(c), str((a, b, c))],
    )


@q("Kümeler", verify="output")
def set_ops():
    a = set(random.sample(range(1, 10), 4))
    b = set(random.sample(range(1, 10), 4))
    if random.random() < 0.4:
        items = random.choices(FRUITS[:4], k=6)
        return output_question(
            f"liste = {items}\nprint(len(set(liste)))", str(len(set(items))),
            "Küme (set) aynı elemanı yalnızca bir kez tutar; <code>set()</code> tekrarları atar.",
            wrongs=[str(len(items)), str(len(set(items)) + 1), str(len(set(items)) - 1)],
        )
    op, res, why = random.choice([
        ("&", a & b, "kesişim: iki kümede de olan elemanlar"),
        ("|", a | b, "birleşim: kümelerden en az birinde olan elemanlar"),
        ("-", a - b, "fark: ilk kümede olup ikincide olmayan elemanlar"),
    ])
    return output_question(
        f"a = {sorted(a)}\nb = {sorted(b)}\nprint(sorted(set(a) {op} set(b)))", str(sorted(res)),
        f"<code>{op}</code> operatörü {why}. sorted() sonucu sıralı bir listeye çevirir.",
        wrongs=[str(sorted(a & b)), str(sorted(a | b)), str(sorted(a - b)), str(sorted(b - a))],
    )
