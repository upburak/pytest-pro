"""Ünite 7 - Listeler."""
import random

from ..helpers import FRUITS, err, output_question
from ..registry import register_unit

UNIT = register_unit(
    "listeler", "Listeler", "Orta",
    "Liste oluşturma, indeksleme, dilimleme, append/insert/remove/pop, len/sum/max/min, sort ve sorted, "
    "listelerin değiştirilebilirliği, liste üreteçleri (list comprehension).",
    order=7,
)
q = UNIT.question


def _nums(k=5):
    return random.sample(range(1, 30), k)


@q("Liste İndeksleme", verify="output")
def list_index():
    items = random.sample(FRUITS, 4)
    i = random.choice([0, 1, 2, -1, -2])
    return output_question(
        f"meyveler = {items}\nprint(meyveler[{i}])", items[i],
        "Liste indeksleri 0'dan başlar; negatif indeksler sondan sayar (<code>[-1]</code> son eleman).",
        wrongs=[x for x in items if x != items[i]] + [err("IndexError")],
    )


@q("Liste Sınırları", verify="error")
def list_index_error():
    items = random.sample(FRUITS, 3)
    return output_question(
        f"meyveler = {items}\nprint(meyveler[3])", err("IndexError"),
        "3 elemanlı listenin geçerli indeksleri 0, 1, 2'dir (veya -1, -2, -3). <code>[3]</code> liste dışına "
        "çıktığı için IndexError oluşur.",
        wrongs=[items[-1], items[0], "None"],
    )


@q("Liste Metotları", verify="output")
def list_methods():
    nums = _nums(4)
    x = random.randint(30, 50)
    op, res_list, why = random.choice([
        (f"append({x})", nums + [x], "append() elemanı listenin <strong>sonuna</strong> ekler."),
        (f"insert(0, {x})", [x] + nums, "insert(0, x) elemanı 0. indekse, yani <strong>başa</strong> ekler."),
        (f"remove({nums[1]})", [n for n in nums if n != nums[1]], "remove(x) x değerini listeden çıkarır."),
        ("pop()", nums[:-1], "pop() son elemanı listeden çıkarır."),
    ])
    return output_question(
        f"liste = {nums}\nliste.{op}\nprint(liste, len(liste))", f"{res_list} {len(res_list)}",
        f"{why} Liste metotları listeyi yerinde değiştirir.",
        wrongs=[f"{nums} {len(nums)}", f"{res_list[::-1]} {len(res_list)}", f"{res_list} {len(nums)}"],
    )


@q("Liste Dilimleme", verify="output")
def list_slice():
    nums = _nums(6)
    a, b = random.randint(0, 2), random.randint(3, 5)
    return output_question(
        f"liste = {nums}\nprint(liste[{a}:{b}])", str(nums[a:b]),
        f"Dilim <code>[{a}:{b}]</code> {a}. indeksten başlar, {b}. indeksi içermez.",
        wrongs=[str(nums[a:b + 1]), str(nums[a + 1:b + 1]), str(nums[a + 1:b])],
    )


@q("Hazır Fonksiyonlar", verify="output")
def aggregates():
    nums = _nums(5)
    func, res = random.choice([("sum", sum(nums)), ("max", max(nums)), ("min", min(nums)), ("len", len(nums))])
    return output_question(
        f"notlar = {nums}\nprint({func}(notlar))", str(res),
        "<code>sum()</code> toplamı, <code>max()</code> en büyüğü, <code>min()</code> en küçüğü, "
        "<code>len()</code> eleman sayısını verir.",
    )


@q("sort() ve sorted()", verify="output")
def sorting():
    nums = _nums(4)
    if random.random() < 0.5:
        return output_question(
            f"a = {nums}\nb = sorted(a)\nprint(a)", str(nums),
            "<code>sorted()</code> sıralanmış <strong>yeni</strong> bir liste döndürür; orijinal liste değişmez.",
            wrongs=[str(sorted(nums)), str(sorted(nums, reverse=True)), "None"],
        )
    return output_question(
        f"a = {nums}\nsonuc = a.sort()\nprint(sonuc)", "None",
        "<code>sort()</code> listeyi yerinde sıralar ve <strong>None</strong> döndürür; sıralanmış liste "
        "a'nın kendisidir.",
        wrongs=[str(sorted(nums)), str(nums), err("TypeError")],
    )


@q("Listeler Değiştirilebilir", verify="output")
def aliasing():
    nums = _nums(3)
    x = random.randint(40, 60)
    return output_question(
        f"a = {nums}\nb = a\nb.append({x})\nprint(a)", str(nums + [x]),
        "<code>b = a</code> yeni bir liste oluşturmaz; iki ad da <strong>aynı</strong> listeyi gösterir. "
        "b üzerinden yapılan değişiklik a'da da görünür. Kopya için <code>a.copy()</code> veya "
        "<code>a[:]</code> kullanılır.",
        wrongs=[str(nums), str([x] + nums), "None"],
    )


@q("Liste Üreteçleri", verify="output")
def comprehension():
    n = random.randint(4, 7)
    expr, cond, why = random.choice([
        ("x * x", "", "her sayının karesini alır"),
        ("x * 2", "", "her sayıyı 2 ile çarpar"),
        ("x", " if x % 2 == 0", "yalnızca çift sayıları alır"),
        ("x + 1", " if x > 2", "2'den büyük sayıların bir fazlasını alır"),
    ])
    res = str(eval(f"[{expr} for x in range({n}){cond}]"))  # noqa: S307
    return output_question(
        f"print([{expr} for x in range({n}){cond}])", res,
        f"Liste üreteci range({n}) içindeki her x için {why}. Bu, for döngüsüyle liste doldurmanın kısa yazımıdır.",
        wrongs=[str(list(range(n))), str(eval(f"[{expr} for x in range(1, {n + 1}){cond}]")),  # noqa: S307
                str(eval(f"[{expr} for x in range({n - 1}){cond}]"))],  # noqa: S307
    )
