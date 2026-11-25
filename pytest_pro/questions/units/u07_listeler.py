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


@q("Liste Sınırları", verify="outcome")
def list_index_error():
    """Liste dışına taşan ve sınırdaki geçerli indeksler karışık sorulur (K5)."""
    k = random.randint(3, 5)
    items = random.sample(FRUITS, k)
    var = random.choice(["meyveler", "liste", "sepet"])
    i = random.choices([k, k + 1, -(k + 1), k - 1, -k, -1, 1], weights=[2, 1, 0.5, 2.5, 2, 1, 1])[0]
    valid = -k <= i < k
    hint = f"{k} elemanlı bir listede geçerli indeksler hangi aralıktadır? Negatif indeks sondan sayar."
    if valid:
        answer = items[i]
        expl = (f"{k} elemanlı listenin geçerli indeksleri 0 ile {k - 1} ya da -{k} ile -1 arasındadır. "
                f"<code>[{i}]</code> bu aralıkta; sonuç \"{answer}\".")
        neighbours = [items[j] for j in (i - 1, i + 1) if -k <= j < k and items[j] != answer]
        wrongs = [Wrong(err("IndexError"), f"[{i}] listenin içinde: {k} elemanlı listede indeksler 0 ile {k - 1} ya da "
                                           f"-{k} ile -1 arasındadır.")]
        if i >= 0:
            wrongs.append(Wrong(items[i - 1], f"İndeksler 0'dan başlar; [{i}] {i + 1}. elemandır."))
        else:
            wrongs.append(Wrong(items[i + 1] if i + 1 < 0 else items[0],
                                "Negatif indeksler sondan sayar: [-1] son eleman, [-2] sondan ikinci elemandır."))
        wrongs += [Wrong(x, f'"{x}" listenin başka bir konumunda; soru [{i}] konumunu soruyor.') for x in neighbours]
        wrongs.append(Wrong("None", "Geçerli bir indeks elemanın kendisini verir; None değil."))
    else:
        answer = err("IndexError")
        expl = (f"{k} elemanlı listenin geçerli indeksleri 0 ile {k - 1} ya da -{k} ile -1 arasındadır. "
                f"<code>[{i}]</code> liste dışına çıktığı için IndexError oluşur.")
        wrongs = [
            Wrong(items[-1] if i > 0 else items[0], f"[{i}] listenin içinde değil: {k} elemanlı listede indeksler 0 ile "
                                                    f"{k - 1} ya da -{k} ile -1 arasındadır."),
            Wrong(items[0] if i > 0 else items[-1], "İndeks başa ya da sona dönmez; liste dışına çıkılınca hata oluşur."),
            Wrong("None", "Python liste dışındaki bir indeks için None vermez, IndexError verir."),
        ]
    return output_question(f"{var} = {items}\nprint({var}[{i}])", answer, expl, wrongs=wrongs, hint=hint)


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
    """Dört değişke (sorted/sort, hangi değişkenin yazdırıldığı); şıklar her zaman aynı dört anlamlı sonuçtur:
    ilk liste, sıralı liste, ters sıralı liste ve None (Y1, O8)."""
    while True:
        nums = random.sample(range(1, 30), random.randint(4, 5))
        if nums not in (sorted(nums), sorted(nums, reverse=True)):
            break
    asc, desc = sorted(nums), sorted(nums, reverse=True)
    variant = random.choice(["sorted_a", "sorted_b", "sort_a", "sort_result"])
    if variant == "sorted_a":
        code, res = f"a = {nums}\nb = sorted(a)\nprint(a)", nums
        expl = "<code>sorted()</code> sıralanmış <strong>yeni</strong> bir liste döndürür; orijinal liste (a) değişmez."
        whys = {"asc": "sorted() yeni bir liste döndürür ve b'ye atanır; a değişmez.",
                "desc": "sorted() a'yı değiştirmez; üstelik varsayılan sıralama küçükten büyüğedir.",
                "none": "print(a) a listesini yazar; a hâlâ ilk tanımlandığı gibidir."}
        hint = "sorted() hangi listeyi değiştirir? print hangi listeyi yazdırıyor?"
    elif variant == "sorted_b":
        code, res = f"a = {nums}\nb = sorted(a)\nprint(b)", asc
        expl = "<code>sorted()</code> sıralanmış yeni bir liste döndürür; b bu yeni listedir. Sıralama küçükten büyüğedir."
        whys = {"orig": "sorted() sıralanmış yeni bir liste döndürür; b o listedir.",
                "desc": "Varsayılan sıralama küçükten büyüğedir; büyükten küçüğe için reverse=True gerekir.",
                "none": "None döndüren sort() metodudur; sorted() yeni bir liste döndürür."}
        hint = "sorted() ne döndürür? b'ye ne atanıyor?"
    elif variant == "sort_a":
        code, res = f"a = {nums}\na.sort()\nprint(a)", asc
        expl = "<code>sort()</code> listeyi <strong>yerinde</strong> sıralar; a artık sıralıdır."
        whys = {"orig": "sort() listeyi yerinde değiştirir; print a'nın sıralanmış hâlini yazar.",
                "desc": "Varsayılan sıralama küçükten büyüğedir; büyükten küçüğe için reverse=True gerekir.",
                "none": "print(a) listeyi yazar; None, sort() metodunun dönüş değeridir ve burada kullanılmıyor."}
        hint = "sort() listeyi değiştirir mi, yoksa yeni bir liste mi döndürür?"
    else:
        code, res = f"a = {nums}\nsonuc = a.sort()\nprint(sonuc)", None
        expl = ("<code>sort()</code> listeyi yerinde sıralar ve <strong>None</strong> döndürür; sıralanmış liste "
                "a'nın kendisidir.")
        whys = {"asc": "sort() listeyi yerinde sıralar ama None döndürür; sonuc None olur.",
                "orig": "sonuc a değil, sort() metodunun dönüş değeridir.",
                "desc": "sort() hiçbir liste döndürmez; dönüş değeri None'dır."}
        hint = "sort() bir değer döndürür mü, yoksa listeyi yerinde mi değiştirir?"
    values = {"orig": str(nums), "asc": str(asc), "desc": str(desc), "none": "None"}
    answer = str(res)
    wrongs = [Wrong(values[key], why) for key, why in whys.items()]
    return output_question(code, answer, expl, wrongs=wrongs, hint=hint)


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


COMPREHENSIONS = [
    # (ifade, koşul, açıklama, koşulun tersi)
    ("x * x", "", "her sayının karesini alır", None),
    ("x * 2", "", "her sayıyı 2 ile çarpar", None),
    ("x + 3", "", "her sayıya 3 ekler", None),
    ("x", " if x % 2 == 0", "yalnızca çift sayıları alır", " if x % 2 == 1"),
    ("x", " if x % 3 == 0", "yalnızca 3'e tam bölünenleri alır", " if x % 3 != 0"),
    ("x + 1", " if x > 2", "2'den büyük sayıların bir fazlasını alır", " if x <= 2"),
    ("x * 10", " if x < 3", "3'ten küçük sayıların 10 katını alır", " if x >= 3"),
]


def _comp(expr, cond, rng):
    return str(eval(f"[{expr} for x in {rng}{cond}]"))  # noqa: S307 - yalnızca bizim ürettiğimiz sabit ifade


@q("Liste Üreteçleri", verify="output")
def comprehension():
    """Hesaplanan yanlışlar çakışırsa sıradaki anlamlı yanlışa geçilir; dolgu şık gerekmez (Y1)."""
    n = random.randint(4, 8)
    expr, cond, why, opposite = random.choice(COMPREHENSIONS)
    var = random.choice(["sonuc", "liste", "yeni"])
    res = _comp(expr, cond, f"range({n})")
    wrongs = [
        Wrong(_comp(expr, cond, f"range(1, {n + 1})"), f"range({n}) 0'dan başlar, 1'den değil."),
        Wrong(_comp(expr, cond, f"range({n + 1})"), f"range({n}) bitiş değerini ({n}) üretmez."),
        Wrong(_comp(expr, cond, f"range({n - 1})"), f"range({n}) 0'dan başlayıp {n} değer üretir; son değer {n - 1}."),
    ]
    if cond:
        if expr != "x":
            wrongs.insert(1, Wrong(_comp("x", cond, f"range({n})"), "Koşulu sağlayan sayılara baştaki ifade "
                                                                    f"(<code>{expr}</code>) de uygulanır."))
        wrongs.insert(1, Wrong(_comp(expr, opposite, f"range({n})"), "Koşul, alınacak sayıları seçer; koşulu "
                                                                     "sağlamayanlar listeye girmez."))
        wrongs.append(Wrong(_comp(expr, "", f"range({n})"), "Koşul (if) yalnızca onu sağlayan sayıları listeye alır."))
    else:
        wrongs.insert(1, Wrong(str(list(range(n))), "Liste üreteci her elemana baştaki ifadeyi uygular; x'ler olduğu "
                                                    "gibi kalmaz."))
    return output_question(
        f"{var} = [{expr} for x in range({n}){cond}]\nprint({var})", res,
        f"Liste üreteci range({n}) içindeki her x için {why}. Bu, for döngüsüyle liste doldurmanın kısa yazımıdır.",
        wrongs=wrongs,
        hint="Önce range'in ürettiği x değerlerini yaz, sonra her birine koşulu ve ifadeyi uygula.",
    )
