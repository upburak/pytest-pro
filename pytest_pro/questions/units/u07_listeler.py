"""Ünite 7 - Listeler."""
import random

from ..helpers import FRUITS, Wrong, err, output_question
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
    wrongs = []
    for j, x in enumerate(items):
        if x == items[i]:
            continue
        if i >= 0 and j == i - 1:
            why = f"Saymaya 1'den başlamış olabilirsin; indeksler 0'dan başlar, [{i}] aslında {i + 1}. elemandır."
        elif i < 0 and j == len(items) + i + 1:
            why = "Negatif indeksler sondan sayar: [-1] son eleman, [-2] sondan ikinci elemandır."
        else:
            why = f'"{x}" listenin [{j}] konumunda; soru [{i}] konumunu soruyor.'
        wrongs.append(Wrong(x, why))
    wrongs.append(Wrong(err("IndexError"), "Bu indeks listenin içinde; hata oluşmaz."))
    return output_question(
        f"meyveler = {items}\nprint(meyveler[{i}])", items[i],
        "Liste indeksleri 0'dan başlar; negatif indeksler sondan sayar (<code>[-1]</code> son eleman).",
        wrongs=wrongs,
        hint="İlk elemanın indeksi kaçtır? İndeks negatifse sondan say.",
    )


@q("Liste Sınırları", verify="error")
def list_index_error():
    k = random.randint(3, 5)
    items = random.sample(FRUITS, k)
    return output_question(
        f"meyveler = {items}\nprint(meyveler[{k}])", err("IndexError"),
        f"{k} elemanlı listenin geçerli indeksleri 0'dan {k - 1}'e kadardır (veya -1'den -{k}'ya kadar). "
        f"<code>[{k}]</code> liste dışına çıktığı için IndexError oluşur.",
        wrongs=[
            Wrong(items[-1], f"[{k}] son eleman değil; {k} elemanlı listenin son indeksi {k - 1}'dir."),
            Wrong(items[0], "İndeks başa dönmez; liste dışına çıkılınca hata oluşur."),
            Wrong("None", "Python liste dışındaki bir indeks için None vermez, IndexError verir."),
        ],
        hint=f"{k} elemanlı bir listede en büyük geçerli indeks kaçtır?",
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
        wrongs=[
            Wrong(f"{nums} {len(nums)}", "Metot listeyi yerinde değiştirir; print değişmiş listeyi gösterir."),
            Wrong(f"{res_list[::-1]} {len(res_list)}", "Metot elemanların sırasını tersine çevirmez."),
            Wrong(f"{res_list} {len(nums)}", "len(liste), değişmiş listenin eleman sayısını verir."),
        ],
        hint=f"<code>{op.split('(')[0]}()</code> listeye ne yapar? Sonra listenin yeni hâlini ve uzunluğunu yaz.",
    )


@q("Liste Dilimleme", verify="output")
def list_slice():
    nums = _nums(6)
    a, b = random.randint(0, 2), random.randint(3, 5)
    return output_question(
        f"liste = {nums}\nprint(liste[{a}:{b}])", str(nums[a:b]),
        f"Dilim <code>[{a}:{b}]</code> {a}. indeksten başlar, {b}. indeksi içermez.",
        wrongs=[
            Wrong(str(nums[a:b + 1]), "Bitiş indeksi dilime dahil değildir; dilim bir eleman önce biter."),
            Wrong(str(nums[a + 1:b + 1]), "Saymaya 1'den başlamış olabilirsin; indeksler 0'dan başlar."),
            Wrong(str(nums[a + 1:b]), "Başlangıç indeksi dilime dahildir."),
        ],
        hint="Başlangıç dahil, bitiş hariç. İndeksler 0'dan başlar.",
    )


AGGREGATES = {"sum": "toplamı", "max": "en büyük elemanı", "min": "en küçük elemanı", "len": "eleman sayısını"}


@q("Hazır Fonksiyonlar", verify="output")
def aggregates():
    nums = _nums(5)
    func = random.choice(sorted(AGGREGATES))
    values = {"sum": sum(nums), "max": max(nums), "min": min(nums), "len": len(nums)}
    res = values[func]
    return output_question(
        f"notlar = {nums}\nprint({func}(notlar))", str(res),
        "<code>sum()</code> toplamı, <code>max()</code> en büyüğü, <code>min()</code> en küçüğü, "
        "<code>len()</code> eleman sayısını verir.",
        common_wrongs=[Wrong(str(v), f"Bu, listenin {AGGREGATES[name]}; burada {func}() kullanılıyor.")
                       for name, v in values.items() if name != func and v != res],
        hint=f"{func}() listeden ne hesaplar?",
    )


@q("sort() ve sorted()", verify="output")
def sorting():
    nums = _nums(4)
    if random.random() < 0.5:
        return output_question(
            f"a = {nums}\nb = sorted(a)\nprint(a)", str(nums),
            "<code>sorted()</code> sıralanmış <strong>yeni</strong> bir liste döndürür; orijinal liste değişmez.",
            wrongs=[
                Wrong(str(sorted(nums)), "sorted() yeni bir liste döndürür ve b'ye atanır; a değişmez."),
                Wrong(str(sorted(nums, reverse=True)), "sorted() a'yı değiştirmez, üstelik varsayılan sıralama küçükten büyüğedir."),
                Wrong("None", "print(a) a listesini yazar; a hâlâ ilk tanımlandığı gibidir."),
            ],
            hint="sorted() hangi listeyi değiştirir? print hangi listeyi yazdırıyor?",
        )
    return output_question(
        f"a = {nums}\nsonuc = a.sort()\nprint(sonuc)", "None",
        "<code>sort()</code> listeyi yerinde sıralar ve <strong>None</strong> döndürür; sıralanmış liste "
        "a'nın kendisidir.",
        wrongs=[
            Wrong(str(sorted(nums)), "sort() listeyi yerinde sıralar ama None döndürür; sonuc None olur."),
            Wrong(str(nums), "sonuc a değil, sort() metodunun dönüş değeridir."),
            Wrong(err("TypeError"), "sort() hata vermez; listeyi sıralar ve None döndürür."),
        ],
        hint="sort() bir değer döndürür mü, yoksa listeyi yerinde mi değiştirir?",
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
        wrongs=[
            Wrong(str(nums), "b = a kopya oluşturmaz; a ile b aynı listeyi gösterir, değişiklik ikisinde de görünür."),
            Wrong(str([x] + nums), "append() elemanı listenin sonuna ekler."),
            Wrong("None", "print(a) listeyi yazar; append'in dönüş değerini değil."),
        ],
        hint="b = a satırı yeni bir liste mi oluşturur, yoksa aynı listeye ikinci bir ad mı verir?",
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
        wrongs=[
            Wrong(str(list(range(n))), "Liste üreteci her elemana baştaki ifadeyi uygular; x'ler olduğu gibi kalmaz."),
            Wrong(str(eval(f"[{expr} for x in range(1, {n + 1}){cond}]")),  # noqa: S307
                  f"range({n}) 0'dan başlar, 1'den değil."),
            Wrong(str(eval(f"[{expr} for x in range({n - 1}){cond}]")),  # noqa: S307
                  f"range({n}) 0'dan {n - 1}'e kadar {n} değer üretir."),
        ],
        hint="Önce range'in ürettiği x değerlerini yaz, sonra her birine koşulu ve ifadeyi uygula.",
    )
