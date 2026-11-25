"""Ünite 8 - Sözlükler, Demetler ve Kümeler."""
import ast
import random

from ..codecheck import OK, checker, find_loops, loop_problems, same_value
from ..helpers import FRUITS, PEOPLE, Wrong, e, err, fill_question, output_question, tf_claim
from ..registry import register_unit
from .u05_kosullar import calls_name, given_ok, has_node, says, sim_run, top_assigns
from .u06_donguler import numbers_in

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


# ================================================================= kod yazma denetleyicileri
def _printed_dict(line):
    """Satırdaki sözlük gösterimi ("Sayım: {'elma': 2}" -> {'elma': 2}); okunamazsa None. Metin, öğrencinin kodunun
    izlenmesinden çıkan çıktıdır; yalnızca ast.literal_eval ile okunur."""
    start = line.find("{")
    if start < 0:
        return None
    try:
        value = ast.literal_eval(line[start:].strip())
    except (ValueError, SyntaxError, MemoryError, RecursionError):
        return None
    return value if isinstance(value, dict) else None


def _only_given_data(var, value, want):
    return (f"Kodun yalnızca verilen veri için doğru sonuç veriyor; <code>{var} = {e(value)}</code> olsaydı "
            f"<code>{e(want)}</code> yazmalıydı. Sonucu {var} değişkenini kullanarak hesapla, elle yazma.")


def _loops_ok(tree):
    for loop in find_loops(tree):
        problem = loop_problems(loop)
        if problem:
            return problem
    return None


BEST_CASES = [{"Ece": 55, "Can": 90, "Ali": 70}, {"Zeynep": 30, "Mert": 20}, {"Selin": 100, "Emre": 99, "Deniz": 98},
              {"Can": 45}]


@checker("sozluk_en_yuksek")
def check_dict_max(tree, p):
    """`var = {ad: not, ...}` sözlüğünde en yüksek notu alanın ADINI yazdırma (döngü ya da max(..., key=...))."""
    var, data = p["var"], p["data"]
    start = f"<code>{var} = {e(data)}</code>"
    if not top_assigns(tree, var):
        return False, f"Kod {start} satırıyla başlamalı."
    if not (has_node(tree, ast.For, ast.While) or calls_name(tree, "max")):
        return False, "Sözlüğü bir döngüyle dolaşıp notları karşılaştırarak en yüksek notu alanı bul."
    problem = _loops_ok(tree)
    if problem:
        return False, problem
    for k, d in enumerate([data] + BEST_CASES):
        sim, note = sim_run(tree, {var: d})
        if k == 0 and not given_ok(sim, var, data):
            return False, f"Kod {start} satırıyla başlamalı; sözlüğü değiştirmeden kullan."
        if note:
            return False, f"<code>{var} = {e(d)}</code> olsaydı kod {note}."
        lines = sim.lines()
        want = max(d, key=d.get)
        if not lines:
            if sim.out:
                return False, ("Ekrana boş bir satır yazılıyor; ad değişkeni hiç güncellenmiyor olabilir. Her notu o "
                               "ana kadarki en yüksek notla karşılaştır.")
            return False, "Ekrana hiçbir şey yazılmıyor; en yüksek notu alan öğrencinin adını yazdır."
        if len(lines) > 1:
            return False, "Öğrencinin adı yalnızca bir kez, döngü bittikten sonra yazdırılmalı."
        line = lines[0]
        if says(line, want):
            continue
        nums = numbers_in(line)
        if nums and same_value(nums[-1], d[want]):
            return False, "Notu değil, en yüksek notu alan öğrencinin adını yazdır."
        if len(d) > 1 and calls_name(tree, "max") and says(line, max(d)):
            return False, (f"<code>max({var})</code> anahtarları (adları) harf sırasına göre karşılaştırır; "
                           "karşılaştırma notlara göre yapılmalı.")
        if k == 0:
            if says(line, min(d, key=d.get)):
                return False, "Kod en düşük notu alan öğrenciyi buluyor; karşılaştırma yönünü kontrol et."
            if says(line, list(d)[-1]):
                return False, ("Kod sözlükteki son öğrenciyi yazıyor; her notu o ana kadarki en yüksekle karşılaştır ve "
                               "yalnızca daha yüksekse güncelle.")
            return False, f"Bu sözlük için <code>{e(want)}</code> yazılmalı; döngüyü ve karşılaştırmayı kontrol et."
        return False, _only_given_data(var, d, want)
    return True, OK


FREQ_CASES = [["elma", "elma", "armut"], ["kiraz"], ["muz", "nar", "muz", "nar", "muz"]]


def _counts(items):
    out = {}
    for x in items:
        out[x] = out.get(x, 0) + 1
    return out


@checker("sozluk_sayim")
def check_freq(tree, p):
    """`var` listesindeki her öğenin kaç kez geçtiğini `res` sözlüğünde tutup sözlüğü yazdırma."""
    var, items, res = p["var"], p["items"], p["res"]
    start = f"<code>{var} = {e(items)}</code>"
    if not top_assigns(tree, var):
        return False, f"Kod {start} satırıyla başlamalı."
    if has_node(tree, ast.Import, ast.ImportFrom):
        return False, "Bu soruda hazır modül (ör. Counter) kullanmadan, sözlüğü bir döngüyle doldurmalısın."
    if not has_node(tree, ast.For, ast.While):
        return False, "Listeyi bir döngüyle dolaşıp her öğenin sayısını sözlükte biriktir."
    problem = _loops_ok(tree)
    if problem:
        return False, problem
    if not top_assigns(tree, res):
        return False, f"Sayılar <code>{res}</code> adında bir sözlükte tutulmalı ve bu sözlük yazdırılmalı."
    for k, values in enumerate([items] + FREQ_CASES):
        sim, note = sim_run(tree, {var: values})
        if k == 0 and not given_ok(sim, var, items):
            return False, f"Kod {start} satırıyla başlamalı; listeyi değiştirmeden kullan."
        if note and "KeyError" in note:
            return False, (f"Öğe sözlükte henüz yokken <code>{res}[...] += 1</code> KeyError verir; öğe ilk görüldüğünde "
                           "sayısını 1 ile başlat (get ya da if ... in ile).")
        if note:
            return False, f"<code>{var} = {e(values)}</code> olsaydı kod {note}."
        lines = sim.lines()
        want = _counts(values)
        if not lines:
            return False, f"Ekrana hiçbir şey yazılmıyor; döngüden sonra <code>{res}</code> sözlüğünü yazdır."
        if len(lines) > 1:
            return False, f"<code>{res}</code> sözlüğü yalnızca bir kez, döngü bittikten sonra yazdırılmalı."
        got = _printed_dict(lines[0])
        if got is None:
            return False, f"Ekrana <code>{res}</code> sözlüğü yazdırılmalı (ör. <code>{e(want)}</code>)."
        if got == want:
            continue
        if k == 0 and set(got) == set(want):
            if all(v == 1 for v in got.values()):
                return False, ("Her öğenin sayısı her seferinde 1 yapılıyor; öğe daha önce görüldüyse önceki sayının "
                               "üstüne 1 ekle.")
            if all(got[x] == want[x] + 1 for x in want):
                return False, "Her öğenin sayısı 1 fazla çıkıyor; get() ile okurken varsayılan değer 0 olmalı."
        if k == 0:
            return False, "Sözlükteki sayılar beklenen sonuçla aynı değil; her öğenin kaç kez geçtiğini kontrol et."
        return False, _only_given_data(var, values, want)
    return True, OK


# ================================================================= yeni şablonlar (ölçme raporu Ö8.1-Ö8.8)
@q("in Sözlükte Neye Bakar? (Doğru / Yanlış)", verify="tf_output")
def dict_in_claim():
    """Kazanım: in işlecinin sözlükte anahtarlara baktığını bilir · Bloom: A"""
    d = _grades(random.randint(2, 4))
    name = random.choice(list(d))
    missing = random.choice([p for p in PEOPLE if p not in d])
    value = d[name]
    kind = random.choice(["key", "value", "value_view", "missing", "name_in_values"])
    expr, result, why = {
        "key": (f"\"{name}\" in notlar", True, f"\"{name}\" sözlüğün bir anahtarıdır; in anahtarlara bakar."),
        "value": (f"{value} in notlar", False, f"in sözlükte anahtarlara bakar; {value} bir değerdir, anahtar değildir. "
                                               f"Değerlerde aramak için <code>{value} in notlar.values()</code> yazılır."),
        "value_view": (f"{value} in notlar.values()", True, f"values() değerleri verir; {value} değerlerden biridir."),
        "missing": (f"\"{missing}\" in notlar", False, f"\"{missing}\" sözlükte anahtar olarak yok."),
        "name_in_values": (f"\"{name}\" in notlar.values()", False, f"values() yalnızca notları verir; \"{name}\" bir "
                                                                     "anahtardır, değer değildir."),
    }[kind]
    code = f"notlar = {d}\nprint({expr})"
    opposite = "False" if result else "True"
    return tf_claim(code, str(result), [Wrong(opposite, f"{why} Bu yüzden ekrana {result} yazılır.")], why,
                    hint="in sözlüğün anahtarlarına mı, değerlerine mi bakar? values() neyi verir?",
                    true_why=f"İddia doğru: {why}")


@q("keys / values / items (Boşluk Doldurma)", verify="fill")
def dict_view_blank():
    """Kazanım: istenen çıktıya göre doğru sözlük görünümünü (keys, values, items) seçer · Bloom: An"""
    d = _grades(random.randint(2, 4))
    method = random.choice(["keys", "values", "items"])
    if method == "items":
        code = "for ad, puan in notlar.____():\n    print(ad, puan)"
        expect = "\n".join(f"{k} {v}" for k, v in d.items())
        wrongs = [Wrong("keys", "keys() yalnızca adları verir; bir ad iki değişkene (ad, puan) açılamaz, hata oluşur."),
                  Wrong("values", "values() yalnızca notları verir; bir sayı iki değişkene açılamaz, hata oluşur.")]
        what = "hem adlar hem notlar"
    else:
        code = "for x in notlar.____():\n    print(x)"
        expect = "\n".join(map(str, d if method == "keys" else d.values()))
        wrongs = [Wrong("items", "items() (ad, not) çiftleri verir; tek değişkenle döngü kurulursa demetler yazılır: "
                                 f"<code>{e(next(iter(d.items())))}</code>.")]
        wrongs.append(Wrong("values" if method == "keys" else "keys",
                            "values() notları verir; çıktıda adlar var." if method == "keys"
                            else "keys() adları (anahtarları) verir; çıktıda notlar var."))
        what = "yalnızca adlar" if method == "keys" else "yalnızca notlar"
    shown = ", ".join(expect.split("\n"))
    return fill_question(
        f"notlar = {d}\n{code}",
        [[method]], expect,
        f"Kod ekrana alt alta <code>{e(shown)}</code> yazmalı. Boşluğa gelmesi gereken sözlük metodunu yazınız.",
        f"Çıktıda {what} var. <code>keys()</code> anahtarları, <code>values()</code> değerleri, <code>items()</code> "
        f"(anahtar, değer) çiftlerini verir; burada <code>{method}()</code> gerekir.",
        hint="Çıktıda adlar mı, notlar mı, ikisi birden mi var? Döngüde kaç değişken var?",
        wrongs=[wrongs],
    )


COUNT_WORDS = ["programlama", "bilgisayar", "kelebek", "karakalem", "anahtar", "papatya", "matematik", "elektrik",
               "Kastamonu", "tencere", "kitaplik", "ananas", "dondurma", "salata"]


@q("Sözlükle Sayma", verify="output")
def dict_count():
    """Kazanım: get(k, 0) + 1 sayma kalıbını izler · Bloom: U"""
    word = random.choice(COUNT_WORDS)
    counts = {}
    for h in word:
        counts[h] = counts.get(h, 0) + 1
    var = random.choice(["sayim", "adet", "frekans"])
    head = f"{var} = {{}}\nfor h in \"{word}\":\n    {var}[h] = {var}.get(h, 0) + 1\n"
    if random.random() < 0.7:
        letters = sorted(counts)
        letter = random.choices(letters, weights=[counts[x] ** 2 for x in letters])[0]
        res = counts[letter]
        code = head + f"print({var}[\"{letter}\"])"
        common = [Wrong("1", "get() harf daha önce görüldüyse eski sayıyı döndürür; her görülüşte 1 eklenir, 1'de kalmaz.")
                  if res > 1 else Wrong("2", f"\"{letter}\" kelimede bir kez geçer; sayısı 1'dir."),
                  Wrong(str(res + 1), "get(h, 0) harf ilk görüldüğünde 0 verir; ilk görülüşte sayı 1 olur."),
                  Wrong(str(len(word)), "Her harf kendi anahtarında sayılır; sözlükteki değer tek bir harfin sayısıdır.")]
        expl = f"\"{letter}\" harfi \"{word}\" içinde {res} kez geçer; her görülüşünde sayısı 1 artar."
        hint = f"\"{letter}\" harfi her görüldüğünde sözlükteki değeri ne olur?"
    else:
        res = len(counts)
        code = head + f"print(len({var}))"
        common = [Wrong(str(len(word)), "Aynı anahtar ikinci kez eklenmez, değeri güncellenir; len() farklı harf sayısını verir."),
                  Wrong(str(max(counts.values())), "len() sözlükteki anahtar sayısını verir, en büyük sayıyı değil."),
                  Wrong(str(res - 1), "Her farklı harf bir anahtardır; ilk harfi de say.")]
        expl = f"Sözlükte her farklı harf bir anahtardır; \"{word}\" içinde {res} farklı harf vardır."
        hint = "Sözlükte aynı anahtar iki kez bulunabilir mi? len() neyi sayar?"
    return output_question(code, str(res), expl, common_wrongs=common, norm="sayi", hint=hint)


@q("Yinelenen Anahtar", verify="output")
def dict_dup_key():
    """Kazanım: sözlükte anahtarların tekil olduğunu, aynı anahtarın son değerinin geçerli olduğunu bilir · Bloom: A"""
    letters = random.random() < 0.5
    pool = list("abcdefg") if letters else ["Ali", "Can", "Ece", "Mert", "Zeynep", "Deniz"]
    keys = random.sample(pool, random.randint(2, 4))
    dup = random.choice(keys)
    values = random.sample(range(1, 60), len(keys) + 1)
    items = list(zip(keys, values))
    first = dict(items)[dup]
    last = values[-1]
    items.insert(random.randint(keys.index(dup) + 1, len(items)), (dup, last))
    body = ", ".join(f"\"{k}\": {v}" for k, v in items)
    n = len(keys)
    code = f"d = {{{body}}}\nprint(len(d), d[\"{dup}\"])"
    wrongs = [Wrong(f"{n + 1} {last}", "Aynı anahtar sözlükte iki kez bulunamaz; ikinci yazım yeni eleman eklemez."),
              Wrong(f"{n} {first}", "Aynı anahtar tekrar yazılınca sonraki değer öncekinin üstüne yazılır."),
              Wrong(f"{n + 1} {first}", "Aynı anahtar iki kez bulunamaz ve sonraki değer öncekinin üstüne yazılır.")]
    if random.random() < 0.4:
        wrongs.insert(random.randint(0, 2), Wrong(err("KeyError"), "Yinelenen anahtar hata vermez; son yazılan değer "
                                                                    "geçerli olur."))
    return output_question(
        code, f"{n} {last}",
        f"Sözlükte her anahtar bir kez bulunur. \"{e(dup)}\" iki kez yazıldığı için sözlükte {n} anahtar kalır ve "
        f"son yazılan değer ({last}) geçerli olur.",
        wrongs=wrongs,
        hint="Bir sözlükte aynı anahtar iki kez bulunabilir mi? Bulunamıyorsa hangi değer kalır?",
    )


@q("Sözlük Boyutu", verify="output")
def dict_size_ops():
    """Kazanım: ekleme, güncelleme ve silme (del, pop) sonrası sözlüğün boyutunu hesaplar · Bloom: U"""
    size = random.randint(2, 5)
    d = _grades(size)
    present = list(d)
    outside = [p for p in PEOPLE if p not in d]
    ops, added, removed, updated = [], 0, 0, 0
    for _ in range(random.randint(2, 4)):
        kind = random.choice(["update", "add", "del", "pop"])
        if kind in ("update", "del", "pop") and len(present) > 1:
            name = random.choice(present)
            if kind == "update":
                ops.append(f"notlar[\"{name}\"] = {random.randint(40, 100)}")
                updated += 1
            else:
                ops.append(f"del notlar[\"{name}\"]" if kind == "del" else f"notlar.pop(\"{name}\")")
                present.remove(name)
                removed += 1
        elif outside:
            name = outside.pop(random.randrange(len(outside)))
            ops.append(f"notlar[\"{name}\"] = {random.randint(40, 100)}")
            present.append(name)
            added += 1
    res = size + added - removed
    code = f"notlar = {d}\n" + "\n".join(ops) + "\nprint(len(notlar))"
    common = [Wrong(str(size + len(ops)), "Her satırı ekleme saymış olabilirsin; var olana atama günceller, del ve pop siler."),
              Wrong(str(size + added + updated), "Var olan anahtara atama yeni eleman eklemez; yalnızca değeri değiştirir."),
              Wrong(str(size + added), "del ve pop elemanı sözlükten siler; boyut azalır."),
              Wrong(str(size), "Yeni anahtara atama eleman ekler, del ve pop siler; boyut değişir.")]
    return output_question(
        code, str(res),
        f"Başlangıçta {size} eleman var. Yeni anahtara atama eleman ekler ({added}), del ve pop siler ({removed}), var "
        f"olan anahtara atama yalnızca değeri günceller ({updated}): {size} + {added} - {removed} = {res}.",
        common_wrongs=common, norm="sayi",
        hint="Hangi atama yeni anahtar ekler, hangisi günceller? del ve pop ne yapar?",
    )


@q("Kümeler ve Tek Elemanlı Demet (Doğru / Yanlış)", verify="tf_output")
def set_claim():
    """Kazanım: kümenin tekrarsız olduğunu bilir; tek elemanlı demeti tanır · Bloom: A"""
    kind = random.choice(["literal", "add_new", "add_old", "tuple_paren", "tuple_comma"])
    if kind == "literal":
        base = random.sample(range(1, 10), random.randint(3, 4))
        items = base + random.sample(base, random.randint(1, 2))
        random.shuffle(items)
        code = f"s = {{{', '.join(map(str, items))}}}\nprint(len(s))"
        output = str(len(set(items)))
        wrongs = [Wrong(str(len(items)), "Küme aynı elemanı bir kez tutar; tekrar eden elemanlar sayılmaz.")]
        expl = f"Küme tekrarları atar; {len(items)} yazımdan {len(set(items))} farklı eleman kalır."
    elif kind in ("add_new", "add_old"):
        base = random.sample(range(1, 20), random.randint(3, 5))
        x = random.choice(base) if kind == "add_old" else random.choice([v for v in range(1, 20) if v not in base])
        code = f"s = {set(base)}\ns.add({x})\nprint(len(s))"
        output = str(len(base) + (kind == "add_new"))
        wrongs = [Wrong(str(len(base) + 1), f"{x} kümede zaten var; add aynı elemanı ikinci kez eklemez.")
                  if kind == "add_old" else Wrong(str(len(base)), f"{x} kümede yok; add onu ekler ve boyut 1 artar.")]
        expl = "add() elemanı kümede yoksa ekler; varsa küme değişmez."
    else:
        v = random.randint(2, 99)
        literal = f"({v})" if kind == "tuple_paren" else f"({v},)"
        code = f"t = {literal}\nprint(type(t))"
        output = "<class 'int'>" if kind == "tuple_paren" else "<class 'tuple'>"
        wrongs = [Wrong("<class 'tuple'>", "Parantez tek başına demet oluşturmaz; tek elemanlı demet için virgül gerekir: "
                                           f"<code>({v},)</code>.") if kind == "tuple_paren"
                  else Wrong("<class 'int'>", f"Virgül demet oluşturur; <code>({v},)</code> tek elemanlı bir demettir.")]
        expl = (f"Demeti virgül oluşturur: <code>({v})</code> yalnızca {v} sayısıdır, <code>({v},)</code> tek elemanlı "
                "bir demettir.")
    hint = ("Tek elemanlı bir demet nasıl yazılır? Parantez mi, virgül mü demet oluşturur?" if kind.startswith("tuple")
            else "Kümede aynı eleman kaç kez bulunabilir?")
    return tf_claim(code, output, wrongs, expl, hint=hint)


@q("En Yüksek Notlu Öğrenci (Kod Yazma)")
def write_dict_max():
    """Kazanım: sözlüğü dolaşıp en büyük değerin anahtarını bulur · Bloom: O"""
    data = _grades(random.randint(3, 5))
    want = max(data, key=data.get)
    return {
        "type": "code",
        "text": f"<code>notlar = {e(data)}</code> satırıyla başlayan ve en yüksek notu alan öğrencinin <strong>adını</strong> "
                f"yazdıran kodu yazınız. Bu sözlük için ekrana <code>{e(want)}</code> yazılmalı; kodunuz sözlüğün her hâli "
                "için doğru çalışmalı.",
        "code": None,
        "check": {"kind": "sozluk_en_yuksek", "var": "notlar", "data": data},
        "answer": (f"notlar = {data}\nen_iyi = \"\"\nen_yuksek = -1\nfor ad, puan in notlar.items():\n"
                   "    if puan > en_yuksek:\n        en_yuksek = puan\n        en_iyi = ad\nprint(en_iyi)"),
        "hint": "Hem o ana kadarki en yüksek notu hem de o notun sahibini iki ayrı değişkende tut.",
        "solution": "items() her adımda (ad, not) çiftini verir. Daha yüksek bir not görülünce hem en yüksek not hem de "
                    "sahibinin adı güncellenir; döngüden sonra ad yazdırılır.",
    }


@q("Sözlükle Frekans (Kod Yazma)")
def write_freq():
    """Kazanım: listedeki öğeleri sözlükte sayar · Bloom: O"""
    kinds = random.sample(FRUITS, random.randint(2, 4))
    items = kinds + random.choices(kinds, k=random.randint(3, 5))
    random.shuffle(items)
    want = {}
    for x in items:
        want[x] = want.get(x, 0) + 1
    return {
        "type": "code",
        "text": f"<code>meyveler = {e(items)}</code> satırıyla başlayan; her meyvenin kaç kez geçtiğini <code>sayim</code> "
                "adında bir sözlükte tutan ve döngüden sonra bu sözlüğü yazdıran kodu yazınız. Bu liste için ekrana "
                f"<code>{e(want)}</code> yazılmalı.",
        "code": None,
        "check": {"kind": "sozluk_sayim", "var": "meyveler", "items": items, "res": "sayim"},
        "answer": f"meyveler = {items}\nsayim = {{}}\nfor m in meyveler:\n    sayim[m] = sayim.get(m, 0) + 1\nprint(sayim)",
        "hint": "Meyve sözlükte yoksa sayısını 1 ile başlat, varsa 1 artır.",
        "solution": "<code>sayim.get(m, 0)</code> meyve sözlükte yoksa 0, varsa o ana kadarki sayıyı verir; üstüne 1 "
                    "eklenip yeniden yazılır. <code>if m in sayim:</code> ile iki dal kurmak da aynı sonucu verir.",
    }
