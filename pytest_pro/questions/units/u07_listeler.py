"""Ünite 7 - Listeler."""
import ast
import random

from ..codecheck import OK, checker, find_loops, loop_problems, same_value
from ..helpers import FRUITS, Wrong, e, err, fill_question, output_question, tf_claim
from ..registry import register_unit
from .u05_kosullar import calls_name, given_ok, has_node, sim_run, top_assigns
from .u06_donguler import loop_note, numbers_in

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


# ================================================================= kod yazma denetleyicileri
def _printed_list(line):
    """Satırdaki liste gösterimi ("Çiftler: [4, 10]" -> [4, 10]); okunamazsa None. Metin, öğrencinin kodunun
    izlenmesinden çıkan çıktıdır; yalnızca ast.literal_eval ile okunur."""
    start = line.find("[")
    if start < 0:
        return None
    try:
        value = ast.literal_eval(line[start:].strip())
    except (ValueError, SyntaxError, MemoryError, RecursionError):
        return None
    return value if isinstance(value, list) else None


def _from_list_only(var, given, values, want):
    return (f"Kod yalnızca verilen liste için doğru sonuç veriyor; <code>{var} = {e(values)}</code> olsaydı "
            f"<code>{e(want)}</code> yazmalıydı. Sonucu {var} değişkenini kullanarak hesapla, elle yazma.")


@checker("liste_en_buyuk")
def check_max_loop(tree, p):
    """`var = [...]` listesindeki en büyük sayıyı max/sort/sorted kullanmadan döngüyle bulup yazdırma."""
    var, nums = p["var"], p["nums"]
    start = f"<code>{var} = {e(nums)}</code>"
    if not top_assigns(tree, var):
        return False, f"Kod {start} satırıyla başlamalı."
    for name, label in (("max", "max()"), ("sorted", "sorted()"), ("sort", "sort()")):
        if calls_name(tree, name):
            return False, f"Soru <code>{label}</code> kullanmadan çözmeni istiyor; en büyüğü döngüde karşılaştırarak bul."
    problem = loop_note(tree)
    if problem:
        return False, problem
    for k, values in enumerate((nums, [-5, -2, -9], [7], [3, 8, 8, 1], [-1, -20, -3])):
        sim, note = sim_run(tree, {var: values})
        if k == 0 and not given_ok(sim, var, nums):
            return False, f"Kod {start} satırıyla başlamalı; listeyi değiştirmeden kullan."
        if note:
            return False, f"<code>{var} = {e(values)}</code> olsaydı kod {note}."
        lines = sim.lines()
        want = max(values)
        if not lines:
            return False, "Ekrana hiçbir şey yazılmıyor; döngü bittikten sonra en büyük sayıyı yazdır."
        if len(lines) > 1:
            return False, "En büyük sayı yalnızca bir kez, döngü bittikten sonra yazdırılmalı."
        got = (numbers_in(lines[0]) or [None])[-1]
        if same_value(got, want):
            continue
        if k == 0:
            if same_value(got, min(values)):
                return False, "Kod en küçük sayıyı buluyor; karşılaştırma yönünü kontrol et."
            if same_value(got, values[-1]):
                return False, ("Kod listenin son elemanını yazıyor; her elemanı o ana kadarki en büyükle karşılaştır ve "
                               "yalnızca daha büyükse güncelle.")
            return False, f"Bu liste için {want} yazılmalı; döngüyü ve karşılaştırmayı kontrol et."
        if all(v < 0 for v in values) and got is not None and got not in values:
            return False, (f"Bütün sayılar negatif olsaydı (<code>{e(values)}</code>) kod {got} yazardı. Başlangıç değeri "
                           "listede olmayan bir sayı (ör. 0) olursa sonuç yanlış çıkar; listenin ilk elemanıyla başla.")
        return False, _from_list_only(var, nums, values, want)
    return True, OK


FILTER_RULES = {
    "even": (lambda x, k: x % 2 == 0, "çift"),
    "gt": (lambda x, k: x > k, "{k} sayısından büyük"),
    "div": (lambda x, k: x % k == 0, "{k} ile tam bölünen"),
}


def _filter_cases(rule, k):
    if rule == "even":
        return [[1, 2, 3, 4, 5, 6, 30, 31], [7, 9], [0, -4, 5]]
    if rule == "gt":
        return [[k - 1, k, k + 1, k + 5, 0], [k + 2, k - 3], [k]]
    return [[k, k + 1, 2 * k, 1, 0], [k - 1, k + 1], [3 * k]]


@checker("liste_suzme")
def check_filter_list(tree, p):
    """`var` listesinden kurala uyan elemanlarla `res` adında yeni bir liste kurup yazdırma (döngü ya da
    liste üreteci)."""
    var, nums, res, rule, k = p["var"], p["nums"], p["res"], p["rule"], p["k"]
    pred, words = FILTER_RULES[rule]
    words = words.format(k=k)
    start = f"<code>{var} = {e(nums)}</code>"
    if not top_assigns(tree, var):
        return False, f"Kod {start} satırıyla başlamalı."
    if calls_name(tree, "remove") or calls_name(tree, "pop"):
        return False, ("Soru yeni bir liste oluşturmanı istiyor; <code>remove</code> ya da <code>pop</code> ile asıl "
                       "listeden silme. Döngü sırasında silmek ayrıca bazı elemanların atlanmasına yol açar.")
    if not has_node(tree, ast.For, ast.While, ast.ListComp):
        return False, "Listeyi bir döngüyle (ya da liste üreteciyle) dolaşarak yeni listeyi kur."
    for loop in find_loops(tree):
        problem = loop_problems(loop)
        if problem:
            return False, problem
    if not top_assigns(tree, res):
        if any(isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == res for t in n.targets)
               for loop in find_loops(tree) for n in ast.walk(loop)):
            return False, (f"<code>{res}</code> listesi döngünün içinde her turda yeniden boşaltılıyor; boş listeyi "
                           "döngüden önce bir kez kur.")
        return False, f"Sonuç <code>{res}</code> adında yeni bir listede tutulmalı ve bu liste yazdırılmalı."
    for n, values in enumerate([nums] + _filter_cases(rule, k)):
        sim, note = sim_run(tree, {var: values})
        if n == 0 and not given_ok(sim, var, nums):
            return False, f"Kod {start} satırıyla başlamalı; listeyi değiştirmeden kullan."
        if note:
            return False, f"<code>{var} = {e(values)}</code> olsaydı kod {note}."
        lines = sim.lines()
        want = [x for x in values if pred(x, k)]
        if not lines:
            return False, f"Ekrana hiçbir şey yazılmıyor; döngüden sonra <code>{res}</code> listesini yazdır."
        if len(lines) > 1:
            return False, f"<code>{res}</code> listesi yalnızca bir kez, döngü bittikten sonra yazdırılmalı."
        got = _printed_list(lines[0])
        if got is None:
            return False, f"Ekrana <code>{res}</code> listesi liste biçiminde (ör. <code>{e(want)}</code>) yazdırılmalı."
        if got == want:
            continue
        if got == values:
            return False, f"Ekrana süzülmüş <code>{res}</code> listesi yazılmalı; kod asıl listeyi yazıyor."
        if n == 0 and len(got) == 1 and want and got[0] == want[-1]:
            return False, ("Liste her uygun elemanda yeniden kuruluyor ve yalnızca sonuncusu kalıyor; elemanı eklemek "
                           "için <code>append</code> kullan.")
        if n == 0:
            return False, f"Listeye yalnızca {words} sayılar girmeli; koşulu kontrol et."
        return False, _from_list_only(var, nums, values, want)
    return True, OK


# ================================================================= yeni şablonlar (ölçme raporu Ö7.1-Ö7.8)
@q("append ile extend (Doğru / Yanlış)", verify="tf_output")
def append_extend_claim():
    """Kazanım: append ile extend farkını ve liste metotlarının None döndürdüğünü bilir · Bloom: A"""
    a = random.sample(range(1, 20), random.randint(2, 4))
    b = random.sample(range(20, 40), random.randint(2, 3))
    var = random.choice(["a", "liste", "sayilar"])
    kind = random.choice(["append", "extend", "plus", "append_none"])
    show_len = random.random() < 0.5
    appended, extended = a + [b], a + b
    if kind == "append_none":
        x = b[0]
        code = f"{var} = {a}\nprint({var}.append({x}))"
        return tf_claim(code, "None",
                        [Wrong(str(a + [x]), "append listeyi yerinde değiştirir ama bir değer döndürmez; print None yazar.")],
                        "Liste metotları (append, sort...) listeyi yerinde değiştirir ve <code>None</code> döndürür.",
                        hint="append() bir değer döndürür mü, yoksa yalnızca listeyi mi değiştirir?")
    op = {"append": f"{var}.append({b})", "extend": f"{var}.extend({b})", "plus": f"{var} += {b}"}[kind]
    result = appended if kind == "append" else extended
    other = extended if kind == "append" else appended
    code = f"{var} = {a}\n{op}\nprint({'len(' + var + ')' if show_len else var})"
    shown, wrong = (str(len(result)), str(len(other))) if show_len else (str(result), str(other))
    if kind == "append":
        why = "append verilen listeyi tek bir eleman olarak ekler; elemanlarını tek tek eklemez."
        expl = f"append, {b} listesinin tamamını tek eleman olarak sona ekler."
    else:
        why = ("extend verilen listenin elemanlarını tek tek ekler; listeyi tek eleman olarak eklemez." if kind == "extend"
               else "+= listenin elemanlarını tek tek ekler (extend gibi); listeyi tek eleman olarak eklemez.")
        expl = f"{'extend' if kind == 'extend' else '+='}, {b} listesinin elemanlarını tek tek sona ekler."
    wrongs = [Wrong(wrong, why)]
    if show_len:
        wrongs.append(Wrong(str(len(a)), "Metot listeyi yerinde değiştirir; uzunluk artar."))
    return tf_claim(code, shown, wrongs, expl, hint="Eklenen liste tek bir eleman olarak mı, yoksa elemanları tek tek mi eklenir?")


LIST_METHODS = ["append", "remove", "pop", "insert", "sort", "reverse", "extend", "clear", "copy", "index", "count"]


def _apply(lst, method, args):
    out = list(lst)
    try:
        getattr(out, method)(*args)
    except (TypeError, ValueError, IndexError) as exc:
        return type(exc).__name__
    return out


METHOD_MISTAKES = {
    "append": [("extend", "extend tek sayı değil, bir liste ister; sayı verilirse TypeError oluşur."),
               ("insert", "insert iki argüman alır: konum ve değer.")],
    "remove": [("pop", "pop indekse göre siler; bu indeks listede yok, IndexError oluşur."),
               ("del", "del bir metot değil, deyimdir: <code>del liste[1]</code> biçiminde yazılır.")],
    "pop": [("remove", "remove değere göre siler; listede bu değer yok, ValueError oluşur."),
            ("del", "del bir metot değil, deyimdir: <code>del liste[1]</code> biçiminde yazılır.")],
    "pop_last": [("remove", "remove bir argüman ister: silinecek değer."),
                 ("clear", "clear listedeki bütün elemanları siler.")],
    "insert": [("append", "append tek argüman alır ve elemanı sona ekler.")],
    "sort": [("sorted", "sorted() bir fonksiyondur, metot değildir; <code>liste.sorted()</code> AttributeError verir."),
             ("reverse", "reverse sıralamaz; yalnızca sırayı ters çevirir.")],
    "reverse": [("sort", "sort küçükten büyüğe sıralar; sırayı ters çevirmez."),
                ("reversed", "reversed() bir fonksiyondur; <code>liste.reversed()</code> AttributeError verir.")],
}


@q("Liste Metodunu Bul (Boşluk Doldurma)", verify="fill")
def list_method_blank():
    """Kazanım: listedeki değişimden kullanılan metodu çıkarır · Bloom: An"""
    while True:
        lst = random.sample(range(4, 40), random.randint(3, 5))
        scenario = random.choice(list(METHOD_MISTAKES))
        if scenario == "append":
            args = [random.choice([x for x in range(41, 60)])]
        elif scenario == "remove":
            args = [random.choice(lst)]
        elif scenario == "pop":
            args = [random.randint(1, len(lst) - 1)]
        elif scenario == "insert":
            args = [0, random.randint(41, 60)]
        else:
            args = []
        method = "pop" if scenario == "pop_last" else scenario
        expected = _apply(lst, method, args)
        matches = [m for m in LIST_METHODS if _apply(lst, m, args) == expected]
        if matches == [method] and isinstance(expected, list) and expected != lst:
            break
    arg_text = ", ".join(map(str, args))
    wrongs = [Wrong(w, why) for w, why in METHOD_MISTAKES[scenario]]
    what = {"append": "sona ekler", "remove": "verilen değeri siler", "pop": "verilen indeksteki elemanı çıkarır",
            "pop_last": "son elemanı çıkarır", "insert": "verilen konuma ekler", "sort": "küçükten büyüğe sıralar",
            "reverse": "sırayı ters çevirir"}[scenario]
    return fill_question(
        f"liste = {lst}\nliste.____({arg_text})\nprint(liste)",
        [[method]], str(expected),
        f"Kod ekrana <code>{e(expected)}</code> yazmalı. Boşluğa gelmesi gereken liste metodunu yazınız.",
        f"<code>{method}({e(arg_text)})</code> listeyi yerinde değiştirir: {what}. Sonuç <code>{e(expected)}</code>.",
        hint="Liste nasıl değişmiş: eleman mı eklenmiş, çıkarılmış mı, sırası mı değişmiş? Argüman bir değer mi, indeks mi?",
        wrongs=[wrongs],
    )


COMP_TRANSFORMS = [
    # (kabul edilenler, yanlışlar, açıklama)
    (["{v} * {v}", "{v} ** 2", "pow({v}, 2)"],
     [("{v} * 2", "Bu her sayının 2 katını alır; kare için sayı kendisiyle çarpılır."),
      ("{v} ^ 2", "Python'da ^ üs değil, bit düzeyinde XOR işlemidir; üs için ** kullanılır.")], "her sayının karesi"),
    (["{v} * 2", "2 * {v}", "{v} + {v}"],
     [("{v} ** 2", "Bu her sayının karesini alır; 2 katı için 2 ile çarpılır."),
      ("{v} + 2", "Bu her sayıya 2 ekler; 2 katı için 2 ile çarpılır.")], "her sayının 2 katı"),
    (["{v} + 1", "1 + {v}"],
     [("{v}", "Sayılar olduğu gibi kalır; her birine 1 eklenmeli."),
      ("{v} += 1", "Liste üretecinin ifade kısmına atama yazılamaz; sözdizimi hatası oluşur.")], "her sayının 1 fazlası"),
    (["{v} * 10", "10 * {v}"],
     [("{v} + 10", "Bu her sayıya 10 ekler; 10 katı için 10 ile çarpılır."),
      ("{v} ** 10", "Bu sayının 10. kuvvetidir; 10 katı için 10 ile çarpılır.")], "her sayının 10 katı"),
    (["{v} % 10"],
     [("{v} // 10", "// bölümün tam kısmını verir; son basamak 10'a bölümden kalandır."),
      ("{v} / 10", "/ bölme sonucunu verir; son basamak 10'a bölümden kalandır.")], "her sayının son basamağı"),
]


@q("Liste Üreteci (Boşluk Doldurma)", verify="fill")
def comp_blank():
    """Kazanım: liste üretecinin ifade kısmını istenen sonuca göre yazar · Bloom: U"""
    accepts_, mistakes, what = random.choice(COMP_TRANSFORMS)
    v = random.choice(["x", "n", "i", "s"])
    last_digit = "% 10" in accepts_[0]
    a = random.randint(11, 25) if last_digit else random.randint(1, 5)
    b = a + random.randint(4, 6)
    alts = [t.format(v=v) for t in accepts_]
    if last_digit and a // 10 == (b - 1) // 10:
        # sayılar aynı onluktaysa onluğu çıkarmak da aynı listeyi verir (25..28 -> s - 20)
        alts.append(f"{v} - {a - a % 10}")
    expected = [eval(alts[0], {v: x}) for x in range(a, b)]  # noqa: S307 - yalnızca bizim ürettiğimiz sabit ifade
    var = random.choice(["sonuc", "yeni", "liste"])
    return fill_question(
        f"{var} = [____ for {v} in range({a}, {b})]\nprint({var})",
        [alts], str(expected),
        f"Kod ekrana <code>{e(expected)}</code> yazmalı. Boşluğa gelmesi gereken ifadeyi yazınız.",
        f"range({a}, {b}) sırasıyla {', '.join(map(str, range(a, b)))} değerlerini verir; listede {what} var. "
        f"Bu yüzden ifade <code>{e(alts[0])}</code> (ya da eşdeğeri) olmalı.",
        hint=f"Her {v} değerinden listede hangi sayı üretilmiş? İlk iki eleman arasındaki ilişkiye bak.",
        wrongs=[[Wrong(w.format(v=v), why) for w, why in mistakes]],
    )


@q("index() ve count()", verify="output")
def index_count():
    """Kazanım: liste içinde bir değerin konumunu ve tekrar sayısını bulur · Bloom: U"""
    while True:
        base = random.sample(range(1, 40), random.randint(4, 5))
        v = random.choice(base)
        lst = base + [v] * random.randint(0, 2)
        random.shuffle(lst)
        first, count = lst.index(v), lst.count(v)
        if count == 1 or lst.index(v) != len(lst) - 1 - lst[::-1].index(v):
            break
    last = len(lst) - 1 - lst[::-1].index(v)
    var = random.choice(["liste", "sayilar", "veriler"])
    if random.random() < 0.55:
        code, res = f"{var} = {lst}\nprint({var}.index({v}))", first
        common = [Wrong(str(first + 1), "Saymaya 1'den başlamış olabilirsin; indeksler 0'dan başlar."),
                  Wrong(str(count), "count() tekrar sayısını verir; index() konumu verir.")]
        if last != first:
            common.append(Wrong(str(last), f"index() değerin ilk geçtiği konumu verir; {v} daha önce de geçiyor."))
        expl = f"index() aranan değerin <strong>ilk</strong> geçtiği konumu verir; {v} ilk kez {first}. indekstedir."
        hint = f"{v} listede ilk kez hangi indekste? İndeksler kaçtan başlar?"
    else:
        code, res = f"{var} = {lst}\nprint({var}.count({v}))", count
        common = [Wrong(str(first), "index() konumu verir; count() değerin kaç kez geçtiğini sayar."),
                  Wrong(str(len(lst)), "count() bütün elemanları değil, yalnızca aranan değeri sayar."),
                  Wrong("1" if count > 1 else "0", f"count() bütün tekrarları sayar; {v} listede {count} kez geçer."
                        if count > 1 else f"{v} listede var; count() onu sayar.")]
        expl = f"count() aranan değerin listede kaç kez geçtiğini verir: {v} değeri {count} kez geçer."
        hint = f"{v} listede kaç kez geçiyor? Tek tek say."
    return output_question(code, str(res), expl, common_wrongs=common, norm="sayi", hint=hint)


@q("İç İçe Liste", verify="outcome")
def nested_list():
    """Kazanım: iki boyutlu listede satır ve sütun indeksini kullanır; liste dışına çıkan indeksi tanır · Bloom: U"""
    cells = random.sample(range(1, 10), 9)
    m = [cells[0:3], cells[3:6], cells[6:9]]
    var = random.choice(["m", "tablo", "matris"])
    error = random.random() < 0.25
    if error:
        i, j = random.choice([(3, random.randint(0, 2)), (random.randint(0, 2), 3)])
    else:
        i, j = random.choice([0, 1, 2, -1]), random.choice([0, 1, 2, -1])
    code = f"{var} = [{m[0]},\n     {m[1]},\n     {m[2]}]\nprint({var}[{i}][{j}])".replace("     ", " " * (len(var) + 4))
    if error:
        res = err("IndexError")
        bad = "satır" if i == 3 else "sütun"
        one_based = m[2][j - 1] if i == 3 else m[i][2]
        wrapped = m[2][j] if i == 3 else m[i][0]
        wrongs = [Wrong(str(one_based),
                        f"Saymaya 1'den başlamış olabilirsin; 3 elemanlı listede son indeks 2'dir, {bad} indeksi 3 yoktur."),
                  Wrong(str(wrapped), "İndeks liste dışına çıkınca son ya da ilk elemana dönülmez; IndexError oluşur."),
                  Wrong("None", "Python liste dışındaki bir indeks için None vermez; IndexError oluşur.")]
        expl = f"Her satırda ve listede 3 eleman var; geçerli indeksler 0 ile 2 arasındadır. {bad.capitalize()} indeksi 3 olduğu için IndexError oluşur."
    else:
        res = str(m[i][j])
        wrongs = []
        if m[j][i] != m[i][j]:
            wrongs.append(Wrong(str(m[j][i]), "İlk indeks satırı, ikinci indeks sütunu seçer; sırayı karıştırmış olabilirsin."))
        if i >= 1 and j >= 1:
            wrongs.append(Wrong(str(m[i - 1][j - 1]), "İndeksler 0'dan başlar; saymaya 1'den başlamış olabilirsin."))
        wrongs.append(Wrong(str(m[i]), "İkinci indeks, seçilen satırdan bir eleman seçer; satırın tamamı yazılmaz."))
        wrongs.append(Wrong(str(m[i][(j + 1) % 3]), "Sütun indeksini yeniden say; indeksler 0'dan başlar, -1 son elemandır."))
        wrongs.append(Wrong(err("IndexError"), "İki indeks de listenin içinde; hata oluşmaz."))
        expl = f"Önce <code>{var}[{i}]</code> satırı ({m[i]}) seçilir, sonra bu satırın [{j}] elemanı: {m[i][j]}."
    return output_question(code, res, expl, wrongs=wrongs,
                           hint=f"Önce {var}[{i}] satırını bul, sonra o satırın [{j}] elemanını. Geçerli indeksler hangileri?")


COPY_STYLES = [("b = a", False), ("b = a[:]", True), ("b = a.copy()", True), ("b = list(a)", True)]


@q("Listeyi Kopyalama", verify="output")
def list_copy():
    """Kazanım: takma ad (b = a) ile kopya ([:], copy(), list()) farkını ayırt eder · Bloom: An"""
    a = random.sample(range(1, 30), 3)
    style, is_copy = random.choice(COPY_STYLES + [COPY_STYLES[0]])
    x = random.randint(40, 99)
    target = random.choice(["b", "b", "a"])
    change = random.choice(["append", "set"])
    stmt = f"{target}.append({x})" if change == "append" else f"{target}[0] = {x}"
    changed = a + [x] if change == "append" else [x] + a[1:]
    if is_copy:
        res_a, res_b = (a, changed) if target == "b" else (changed, a)
    else:
        res_a = res_b = changed
    code = f"a = {a}\n{style}\n{stmt}\nprint(a)\nprint(b)"
    res = f"{res_a}\n{res_b}"
    whys = {}
    for va, vb in ((a, changed), (changed, a), (changed, changed), (a, a)):
        key = f"{va}\n{vb}"
        if key == res:
            continue
        if va == vb == a:
            why = f"<code>{stmt}</code> bir listeyi değiştirir; iki liste de değişmeden kalamaz."
        elif not is_copy:
            why = "<code>b = a</code> kopya oluşturmaz; a ve b aynı listeyi gösterir, değişiklik ikisinde de görünür."
        elif va == vb:
            why = f"<code>{style}</code> yeni bir liste oluşturur; değişiklik yalnızca {target} listesinde görünür."
        else:
            why = f"Değişiklik {target} üzerinden yapıldı; diğer liste değişmez."
        whys[key] = why
    return output_question(
        code, res,
        ("<code>b = a</code> yeni liste oluşturmaz; iki ad aynı listeyi gösterir ve değişiklik ikisinde de görünür."
         if not is_copy else f"<code>{style}</code> elemanları aynı olan <strong>yeni</strong> bir liste oluşturur; "
                             f"{target} üzerindeki değişiklik diğerini etkilemez."),
        wrongs=[Wrong(k, v) for k, v in whys.items()],
        hint="b, a ile aynı liste mi, yoksa yeni bir liste mi? Değişiklik hangi listeye yapılıyor?",
    )


@q("max() Kullanmadan En Büyük (Kod Yazma)")
def write_max_loop():
    """Kazanım: döngü ve karşılaştırmayla listedeki en büyük sayıyı bulur · Bloom: O"""
    var = random.choice(["sayilar", "degerler", "liste"])
    nums = random.sample(range(-20, 60), random.randint(5, 7))
    best = random.choice(["en_buyuk", "eb", "maks"])
    return {
        "type": "code",
        "text": f"<code>{var} = {e(nums)}</code> satırıyla başlayan ve listedeki en büyük sayıyı <strong>max(), sort() ve "
                "sorted() kullanmadan</strong>, bir döngüyle bulup yazdıran kodu yazınız. Kodunuz listenin her hâli "
                "için (ör. bütün sayılar negatifken) doğru çalışmalı.",
        "code": None,
        "check": {"kind": "liste_en_buyuk", "var": var, "nums": nums},
        "answer": f"{var} = {nums}\n{best} = {var}[0]\nfor s in {var}:\n    if s > {best}:\n        {best} = s\nprint({best})",
        "hint": "İlk elemanı en büyük kabul et; sonra her elemanı onunla karşılaştır.",
        "solution": "En büyük değişkeni listenin ilk elemanıyla başlatılır; döngüde daha büyük bir eleman görülünce "
                    "güncellenir. 0 ile başlamak bütün sayılar negatifken yanlış sonuç verir.",
    }


FILTER_TEXTS = {"even": ("çift", "ciftler"), "gt": ("{k} sayısından büyük", "buyukler"),
                "div": ("{k} ile tam bölünen", "bolunenler")}


@q("Listeyi Süzme (Kod Yazma)")
def write_filter_even():
    """Kazanım: koşullu eklemeyle yeni bir liste oluşturur · Bloom: O"""
    rule = random.choice(["even", "even", "gt", "div"])
    k = {"even": 2, "gt": random.randint(10, 30), "div": random.randint(3, 5)}[rule]
    pred = FILTER_RULES[rule][0]
    while True:
        nums = random.sample(range(1, 50), random.randint(6, 8))
        if 2 <= sum(pred(x, k) for x in nums) < len(nums):
            break
    words, res = FILTER_TEXTS[rule]
    words = words.format(k=k)
    cond = {"even": "s % 2 == 0", "gt": f"s > {k}", "div": f"s % {k} == 0"}[rule]
    want = [x for x in nums if pred(x, k)]
    return {
        "type": "code",
        "text": f"<code>sayilar = {e(nums)}</code> satırıyla başlayan; listedeki <strong>{words}</strong> sayılardan "
                f"<code>{res}</code> adında <strong>yeni bir liste</strong> oluşturup yazdıran kodu yazınız. Bu liste için "
                f"ekrana <code>{e(want)}</code> yazılmalı; kodunuz listenin her hâli için doğru çalışmalı.",
        "code": None,
        "check": {"kind": "liste_suzme", "var": "sayilar", "nums": nums, "res": res, "rule": rule, "k": k},
        "answer": f"sayilar = {nums}\n{res} = []\nfor s in sayilar:\n    if {cond}:\n        {res}.append(s)\nprint({res})",
        "hint": "Boş bir listeyle başla; koşulu sağlayan her elemanı ekle ve listeyi döngüden sonra yazdır.",
        "solution": f"Önce boş bir liste kurulur; döngüde koşulu (<code>{e(cond)}</code>) sağlayan her eleman "
                    f"<code>append</code> ile eklenir. Liste üreteciyle de yazılabilir: "
                    f"<code>{res} = [s for s in sayilar if {e(cond)}]</code>.",
    }
