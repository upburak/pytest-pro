"""Ünite 10 - Hatalar ve Hata Yönetimi."""
import ast
import random

from ..codecheck import (
    OK,
    Tracker,
    Unknown,
    checker,
    computes,
    const_value,
    find_prints,
    print_texts,
    print_values,
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
    unique_options,
    whys_for_options,
)
from ..registry import register_unit
from .u09_fonksiyonlar import find_def, return_note

UNIT = register_unit(
    "hatalar", "Hata Yönetimi", "Orta",
    "Sık karşılaşılan hata türleri (ZeroDivisionError, ValueError, TypeError, IndexError, KeyError, NameError), "
    "try / except / else / finally.",
    order=10,
)
q = UNIT.question

ERROR_CAUSES = {
    "ZeroDivisionError": "sıfıra bölmede oluşur",
    "ValueError": "doğru tipte ama uygun olmayan bir değer verilince oluşur (int(\"abc\") gibi)",
    "TypeError": "uyumsuz tipler birlikte kullanılınca oluşur (metin + sayı gibi)",
    "IndexError": "liste ya da metinde olmayan bir indekse erişilince oluşur",
    "KeyError": "sözlükte olmayan bir anahtara erişilince oluşur",
    "NameError": "tanımlanmamış bir ad kullanılınca oluşur",
}
ALSO = {"Bitti": "de", "Son": "da", "Tamam": "da", "Kapandı": "da"}  # "... de yazılır" ünlü uyumu
NUMBER_WORDS = ["yirmi", "on beş", "iki", "yüz", "otuz", "beş"]
VAR_NAMES = ["sayi", "toplam", "puan", "adet", "sonuc", "deger"]
TYPO_NAMES = {"sayi": "sayl", "toplam": "topam", "puan": "pun", "adet": "adte", "sonuc": "sonu", "deger": "degr"}


def _snippet():
    """Rastgele değerlerle hata veren kısa bir kod: (kod, hata adı, açıklama). Y6: kod parçaları sabit değil."""
    name = random.choice(list(ERROR_CAUSES))
    v = random.choice(VAR_NAMES)
    n = random.randint(2, 50)
    if name == "ZeroDivisionError":
        return random.choice([
            (f"{v} = {n}\nprint({v} / 0)", "Sıfıra bölme yapılamaz."),
            (f"a = {n}\nb = a - {n}\nprint(a / b)", "b sıfır olur ve sıfıra bölme yapılamaz."),
            (f"{v} = {n}\nprint({v} % 0)", "Sıfıra bölümden kalan da hesaplanamaz."),
            (f"{v} = {n}\nadet = 0\nprint({v} // adet)", "adet sıfır; sıfıra tam bölme yapılamaz."),
        ]) + (name,)
    if name == "ValueError":
        word = random.choice(NUMBER_WORDS)
        whole, frac = random.randint(1, 9), random.randint(1, 9)
        return random.choice([
            (f'{v} = int("{word}")', "int() yalnızca rakamlarla yazılmış metni çevirebilir."),
            (f'{v} = float("{whole},{frac}")', "float() ondalık ayırıcı olarak nokta bekler, virgül değil."),
            (f'{v} = int("{whole}.{frac}")', "int() ondalık noktalı metni çeviremez; önce float() gerekir."),
        ]) + (name,)
    if name == "TypeError":
        label = random.choice(["Puan: ", "Toplam: ", "Yaş: ", "Sonuç: "])
        return random.choice([
            (f'{v} = {n}\nprint("{label}" + {v})', "str ile int + ile birleştirilemez."),
            (f"print(len({n}))", "len() sayıya uygulanamaz; metin, liste gibi yapılar ister."),
            (f'{v} = "{n}"\nprint({v} + 1)', f"{v} bir metin; metne sayı eklenemez."),
        ]) + (name,)
    if name == "IndexError":
        k = random.randint(2, 5)
        items = random.sample(range(1, 20), k)
        word = random.choice(["abc", "Ali", "kod", "Python"])
        extra = random.randint(0, 2)
        return random.choice([
            (f"liste = {items}\nprint(liste[{k + extra}])", f"Liste {k} elemanlı; geçerli indeksler 0 ile {k - 1} "
                                                            "arasındadır."),
            (f'metin = "{word}"\nprint(metin[{len(word) + extra}])',
             f"Metin {len(word)} karakterli; geçerli indeksler 0 ile {len(word) - 1} arasındadır."),
            (f"liste = {items}\nprint(liste[-{k + 1 + extra}])", f"Liste {k} elemanlı; en küçük negatif indeks -{k}."),
        ]) + (name,)
    if name == "KeyError":
        keys = random.sample(PEOPLE, 3)
        d = {keys[0]: random.randint(40, 100), keys[1]: random.randint(40, 100)}
        return (f'notlar = {d}\nprint(notlar["{keys[2]}"])', f'Sözlükte "{keys[2]}" anahtarı yoktur.', name)
    return random.choice([
        (f"print({v})", f"{v} adında tanımlı bir değişken yoktur."),
        (f"{v} = {n}\nprint({TYPO_NAMES[v]})", f"Değişkenin adı {v}; {TYPO_NAMES[v]} diye bir ad tanımlanmamış."),
        (f"Print({n})", "Python büyük/küçük harfe duyarlıdır; Print tanımlı değildir, doğrusu print'tir."),
    ]) + (name,)


@q("Hata Türleri", verify="error")
def error_type():
    code, why, name = _snippet()
    wrongs = [Wrong(other, f"{other} {ERROR_CAUSES[other]}; bu kodda böyle bir durum yok.")
              for other in random.sample([x for x in ERROR_CAUSES if x != name], 3)]
    options = unique_options(name, wrongs)
    return {
        "type": "mc",
        "text": "Aşağıdaki kod çalıştırıldığında hangi hata oluşur?",
        "code": code,
        "options": options,
        "answer": name,
        "whys": whys_for_options(name, wrongs, options),
        "hint": "Hatanın oluştuğu satırda hangi işlem yapılıyor: bölme mi, dönüşüm mü, erişim mi, tanımsız bir ad mı?",
        "solution": f"{why} Bu durumda Python <strong>{name}</strong> hatası verir.",
    }


@q("try / except", verify="output")
def try_except():
    good = random.random() < 0.5
    value = str(random.randint(2, 30)) if good else random.choice(["abc", "3.5", "on", "12a", "iki", "7,5"])
    msg = random.choice(["Geçersiz", "Hatalı giriş", "Sayı değil"])
    end = random.choice(["Bitti", "Son", "Tamam"])
    code = (f"try:\n    sayi = int(veri)\n    print(sayi * 2)\nexcept ValueError:\n    print(\"{msg}\")\n"
            f"print(\"{end}\")")
    if good:
        res = f"{int(value) * 2}\n{end}"
        wrongs = [
            Wrong(f"{msg}\n{end}", f'"{value}" tam sayı biçiminde; dönüşüm başarılı olur ve except çalışmaz.'),
            Wrong(f"{value * 2}\n{end}", "int(veri) metni sayıya çevirir; sonuç sayı olarak çarpılır, metin "
                                         "tekrarlanmaz."),
            Wrong(f"{int(value) * 2}", f"try / except yapısından sonra program devam eder; {end} {ALSO[end]} yazılır."),
        ]
    else:
        res = f"{msg}\n{end}"
        wrongs = [
            Wrong(msg, f"except bloğundan sonra program devam eder; {end} {ALSO[end]} yazılır."),
            Wrong(end, f"Hata oluşunca except bloğu çalışır ve önce {msg} yazılır."),
            Wrong(f"{msg}\n{msg}", "except bloğu bir kez çalışır."),
        ]
    return output_question(
        f'veri = "{value}"\n' + code, res,
        ("Dönüşüm başarılı olduğu için except bloğu atlanır. " if good else
         "int() ValueError verince try bloğunun geri kalanı atlanır ve except bloğu çalışır. ")
        + "try yapısından sonra program normal şekilde devam eder.",
        wrongs=wrongs,
        hint=f'int("{value}") hata verir mi? Verirse hangi bloklar çalışır?',
    )


@q("else ve finally", verify="output")
def try_finally():
    """Çıktıda hesaplanan değer ya da sayıyı içeren mesaj yer alır; cevap iki seçenekten biri değildir (K4)."""
    a = random.randint(10, 40)
    b = random.choice([0, random.randint(2, 9)])
    end = random.choice(["Son", "Bitti", "Kapandı"])
    code = (f"a = {a}\nb = {b}\ntry:\n    sonuc = a // b\nexcept ZeroDivisionError:\n    print(a, \"bölünemedi\")\n"
            f"else:\n    print(sonuc)\nfinally:\n    print(\"{end}\")")
    if b == 0:
        res = f"{a} bölünemedi\n{end}"
        wrongs = [
            Wrong(f"{a} bölünemedi", f"finally her durumda çalışır; {end} {ALSO[end]} yazılır."),
            Wrong(f"0\n{end}", f"{a} // 0 sıfır vermez; ZeroDivisionError oluşur ve except çalışır."),
            Wrong(end, "finally'den önce, hatayı yakalayan except bloğu da çalışır."),
            Wrong(f"{a} bölünemedi\n0\n{end}", "Hata oluşunca else çalışmaz; else yalnızca hata olmazsa çalışır."),
        ]
    else:
        res = f"{a // b}\n{end}"
        wrongs = [
            Wrong(str(a // b), f"finally her durumda çalışır; {end} {ALSO[end]} yazılır."),
            Wrong(f"{a} bölünemedi\n{end}", f"{a} // {b} hatasız çalışır; except atlanır, else çalışır."),
            Wrong(f"{a % b}\n{end}", "// bölümün tam kısmını verir; kalanı veren % operatörüdür.")
            if a % b != a // b else Wrong(f"{a / b}\n{end}", "// tam bölmedir; sonuç ondalıklı değil, tam sayıdır."),
            Wrong(end, "Hata olmadığı için else de çalışır ve sonucu yazar."),
        ]
    return output_question(
        code, res,
        "<code>else</code> yalnızca hata <strong>olmazsa</strong>, <code>finally</code> ise her durumda çalışır. "
        + (f"{a} // 0 ZeroDivisionError verdiği için except çalışır." if b == 0
           else f"{a} // {b} = {a // b}; hata olmadığı için else çalışır."),
        wrongs=wrongs,
        hint=f"{a} // {b} hata verir mi? Hata olursa ve olmazsa hangi bloklar çalışır?",
    )


@q("Hata Yönetimi Kavramları")
def concepts():
    return tf_question(
        [("try bloğunda hata oluşursa, try içinde hatadan sonra gelen satırlar çalıştırılmaz.",
          "Hata oluşunca kontrol hemen except bloğuna geçer; try'ın geri kalanı atlanır."),
         ("Bir try bloğundan sonra farklı hata türleri için birden fazla except bloğu yazılabilir.",
          "Her except farklı bir hata türünü yakalayabilir: except ValueError, except ZeroDivisionError gibi."),
         ("finally bloğu, hata olsa da olmasa da çalışır.",
          "finally her durumda çalışır; genellikle dosya kapatma gibi temizlik işleri için kullanılır."),
         ("else bloğu yalnızca try bloğunda hata oluşmazsa çalışır.",
          "Hata olursa except, olmazsa else çalışır."),
         ("<code>int(\"abc\")</code> ifadesi ValueError verir.",
          "\"abc\" sayı biçiminde değildir; int() ValueError verir."),
         ("Hata yakalanmazsa program o noktada durur ve hata mesajı gösterilir.",
          "Yakalanmayan hata programı sonlandırır.")],
        [("except bloğu, try bloğunda hata olsa da olmasa da her zaman çalışır.",
          "except yalnızca eşleşen bir hata olduğunda çalışır; her durumda çalışan blok finally'dir."),
         ("Bir dosyadaki yazım hatası (SyntaxError), aynı dosyadaki bir try / except bloğuyla yakalanabilir.",
          "Yazım hataları dosya çalışmaya başlamadan önce bulunur; aynı dosyadaki try bloğu hiç çalışmadığı için "
          "onu yakalayamaz."),
         ("except ValueError: bloğu ZeroDivisionError hatasını da yakalar.",
          "except yalnızca yazılan hata türünü yakalar; ZeroDivisionError için ayrı except gerekir."),
         ("Bir try bloğu, except ya da finally olmadan tek başına yazılabilir.",
          "try'dan sonra en az bir except ya da finally gelmelidir."),
         ("<code>10 / 0</code> işlemi Python'da sonsuz (inf) değerini verir.",
          "Python'da sıfıra bölme ZeroDivisionError verir."),
         ("Hata oluşunca try bloğu baştan tekrar çalıştırılır.",
          "Hata oluşunca except çalışır; try kendiliğinden tekrarlanmaz.")],
        "except yalnızca eşleşen bir hata olduğunda çalışır; her durumda çalışan blok finally'dir. Yazım "
        "hataları dosya çalışmaya başlamadan önce tespit edildiği için aynı dosyadaki try ile yakalanamaz.",
        hint="try, except, else ve finally bloklarından hangisi hangi durumda çalışır?",
    )


# ================================================================= yeni şablonlar (ölçme raporu Ö10.1-Ö10.8)
def _safe_snippet():
    """Hata vermeyen ama öğrencinin hata bekleyebileceği kısa kod: (kod, çıktı, beklenen sanılan hata, neden)."""
    n = random.randint(2, 50)
    whole, frac = random.randint(1, 9), random.choice([25, 5, 75])
    k = random.randint(2, 5)
    items = random.sample(range(1, 20), k)
    word = random.choice(["abc", "Ali", "kod", "Ece"])
    keys = random.sample(PEOPLE, 3)
    d = {keys[0]: random.randint(40, 100), keys[1]: random.randint(40, 100)}
    i = random.randint(1, k)
    return random.choice([
        (f'sayi = int(" {n} ")\nprint(sayi + 1)', str(n + 1), "ValueError",
         "int() baştaki ve sondaki boşlukları yok sayar; dönüşüm başarılı olur."),
        (f'x = float("{whole}.{frac}")\nprint(x * 2)', str(float(f"{whole}.{frac}") * 2), "ValueError",
         "Ondalık ayırıcı nokta olduğu için float() bu metni çevirebilir."),
        (f"liste = {items}\nprint(liste[-{i}])", str(items[-i]), "IndexError",
         f"Negatif indeks sondan sayar; liste {k} elemanlı olduğu için -{i} geçerli bir indekstir."),
        (f'metin = "{word}"\nprint(metin * {k})', word * k, "TypeError",
         "Metin bir tam sayıyla çarpılabilir; metin o kadar kez tekrarlanır."),
        (f'notlar = {d}\nprint(notlar.get("{keys[2]}", 0))', "0", "KeyError",
         "get() olmayan anahtarda hata vermez; verilen varsayılan değeri döndürür."),
        (f'puan = {n}\nprint("Puan: " + str(puan))', f"Puan: {n}", "TypeError",
         "str() sayıyı metne çevirdiği için iki metin birleştirilebilir."),
    ])


@q("Hata Türü İddiası (Doğru/Yanlış)", verify="tf_output")
def error_claim():
    """Kazanım: kodun hangi hatayı vereceğini (ya da hata vermeyeceğini) öngörür · Bloom: A/U"""
    if random.random() < 0.3:
        code, output, expected, why = _safe_snippet()
        wrongs = [Wrong(err(expected), why)]
        solution = why
    else:
        code, why, name = _snippet()
        output = err(name)
        wrongs = [Wrong(err(other), f"Bu kodda {other} değil, {name} oluşur. {why}")
                  for other in random.sample([x for x in ERROR_CAUSES if x != name], 2)]
        solution = f"{why} Bu durumda Python <strong>{name}</strong> hatası verir."
    true_why = (f"İddia doğru: bu kodda gerçekten <code>{output[len('Hata verir ('):-1]}</code> hatası oluşur."
                if output.startswith("Hata verir (") else None)
    return tf_claim(code, output, wrongs, solution, true_why=true_why,
                    hint="Hata hangi işlemde oluşabilir: bölme mi, dönüşüm mü, indeks mi, anahtar mı? Yoksa kod "
                         "sorunsuz mu çalışır?")


def _except_case():
    """(kod, hata adı, çıktı mesajı, ipucu, açıklama)"""
    kind = random.choice(["ValueError", "ZeroDivisionError", "IndexError", "KeyError", "TypeError"])
    if kind == "ValueError":
        word = random.choice(NUMBER_WORDS + ["12a", "3.5", "7,5"])
        msg = random.choice(["Geçersiz sayı", "Sayı girilmedi", "Dönüştürülemedi"])
        code = f'veri = "{word}"\ntry:\n    sayi = int(veri)\n    print(sayi + 1)\nexcept ____:\n    print("{msg}")'
        return (code, kind, msg, "int() rakamlardan oluşmayan bir metni çevirmeye çalışınca hangi hata oluşur?",
                f'"{word}" tam sayı biçiminde olmadığı için int() ValueError verir.')
    if kind == "ZeroDivisionError":
        pay, kisi = random.randint(50, 300), random.choice(["kisi", "adet", "bolen"])
        msg = random.choice(["Sıfıra bölünemez", "Paylaşılamadı", "Bölen sıfır"])
        code = f'pay = {pay}\n{kisi} = 0\ntry:\n    print(pay / {kisi})\nexcept ____:\n    print("{msg}")'
        return (code, kind, msg, "Bir sayı sıfıra bölünmeye çalışılınca hangi hata oluşur?",
                f"{kisi} sıfır olduğu için bölme ZeroDivisionError verir.")
    if kind == "IndexError":
        k = random.randint(2, 5)
        items = random.sample(range(1, 30), k)
        idx = k + random.randint(0, 2)
        msg = random.choice(["Böyle bir sıra yok", "Sıra dışı", "Eleman bulunamadı"])
        code = f'liste = {items}\ntry:\n    print(liste[{idx}])\nexcept ____:\n    print("{msg}")'
        return (code, kind, msg, "Listede olmayan bir sıra numarasına erişilince hangi hata oluşur?",
                f"Liste {k} elemanlı; {idx} geçerli bir indeks olmadığı için IndexError oluşur.")
    if kind == "KeyError":
        keys = random.sample(["elma", "armut", "kiraz", "muz", "nar", "erik"], 3)
        d = {keys[0]: random.randint(1, 20), keys[1]: random.randint(1, 20)}
        msg = random.choice(["Ürün bulunamadı", "Stokta yok", "Kayıt yok"])
        code = f'stok = {d}\ntry:\n    print(stok["{keys[2]}"])\nexcept ____:\n    print("{msg}")'
        return (code, kind, msg, "Sözlükte olmayan bir anahtara erişilince hangi hata oluşur?",
                f'Sözlükte "{keys[2]}" anahtarı olmadığı için KeyError oluşur.')
    yas = random.randint(14, 18)
    label = random.choice(["Yaş: ", "Yaşın: ", "Yaşınız: "])
    msg = random.choice(["Tip uyuşmuyor", "Birleştirilemedi", "Metin ve sayı karıştı"])
    code = f'yas = {yas}\ntry:\n    print("{label}" + yas)\nexcept ____:\n    print("{msg}")'
    return (code, kind, msg, "Bir metin ile bir sayı + ile birleştirilmeye çalışılınca hangi hata oluşur?",
            "Metin ile tam sayı + ile birleştirilemez; TypeError oluşur.")


@q("Doğru except Türü (Boşluk Doldurma)", verify="fill")
def except_blank():
    """Kazanım: oluşacak hataya uygun except türünü yazar · Bloom: An"""
    code, name, msg, hint, why = _except_case()
    others = random.sample([x for x in ERROR_CAUSES if x not in (name, "NameError")], 2)
    wrongs = [Wrong(o, f"{o} {ERROR_CAUSES[o]}; bu kodda oluşan hata bu değil, bu yüzden yakalanmaz.") for o in others]
    wrongs.append(Wrong(name.lower(), "Hata adları büyük/küçük harfe duyarlıdır; Python bu adı tanımaz."))
    return fill_question(
        code, [[name]], msg,
        f"Kod ekrana <code>{e(msg)}</code> yazmalı. Boşluğa, <strong>yalnızca bu kodda oluşan hatayı</strong> "
        "yakalayacak hata türünü yazınız.",
        f"{why} except satırına bu hata türü yazılınca hata yakalanır ve <code>{e(msg)}</code> yazılır. "
        "<code>Exception</code> da hatayı yakalardı, ama her hatayı yakaladığı için soru buna özel türü istiyor.",
        hint=hint, wrongs=[wrongs],
    )


def _sequence_output(steps, letters):
    """try içindeki adımlar: [(değer ya da None, hata harfi)]. İlk hatada durulur. Çıktı parçaları listesi."""
    out = []
    for value, letter in steps:
        if value is None:
            out.append(letters[letter])
            break
        out.append(str(value))
    return out


@q("Birden Fazla except")
def multi_except():
    """Kazanım: ilk hatada try'ın kesildiğini ve eşleşen except'in çalıştığını izler · Bloom: U/An"""
    k = random.randint(3, 5)
    items = random.sample(range(10, 60), k)
    bad_index, zero = random.random() < 0.45, random.random() < 0.45
    i = random.randint(k, k + 2) if bad_index else random.randint(0, k - 1)
    a, b = random.randint(20, 90), (0 if zero else random.randint(2, 9))
    index_first = random.random() < 0.5
    stmt_idx = (f"print(liste[{i}], end=\" \")", (None if bad_index else items[i], "idx"))
    stmt_div = (f"print({a} // {b}, end=\" \")", (None if zero else a // b, "div"))
    order = [stmt_idx, stmt_div] if index_first else [stmt_div, stmt_idx]
    letters = {"idx": "A", "div": "B"}
    code = (f"liste = {items}\ntry:\n    {order[0][0]}\n    {order[1][0]}\nexcept IndexError:\n"
            "    print(\"A\", end=\" \")\nexcept ZeroDivisionError:\n    print(\"B\", end=\" \")\nfinally:\n"
            "    print(\"C\")")
    parts = _sequence_output([s[1] for s in order], letters)
    answer = " ".join(parts + ["C"])
    wrongs = [Wrong(" ".join(parts), "finally bloğu her durumda çalışır; C de yazılır.")]
    first, second = order[0][1], order[1][1]
    if first[0] is None:  # ilk satırda hata
        nxt = letters[second[1]] if second[0] is None else str(second[0])
        wrongs.append(Wrong(f"{letters[first[1]]} {nxt} C", "Hata oluşunca try bloğunun geri kalanı atlanır; ikinci "
                                                            "satır hiç çalışmaz."))
    elif second[0] is None:  # ikinci satırda hata
        wrongs.append(Wrong(f"{letters[second[1]]} C", "İlk satır hatadan önce çalışır ve değerini yazar."))
        wrongs.append(Wrong(f"{first[0]} A B C", "Yalnızca hataya uyan except bloğu çalışır."))
    else:
        wrongs.append(Wrong(f"{first[0]} {second[0]} A B C", "Hata oluşmadığı için except blokları çalışmaz."))
        wrongs.append(Wrong("A B C", f"Bu kodda hata oluşmaz: liste[{i}] geçerli bir indeks ve bölen sıfır değil."))
    return output_question(
        code, answer,
        "try bloğunda ilk hata oluşan satırda durulur ve yalnızca o hataya uyan except çalışır; finally her durumda "
        f"çalışır. Çıktı: {answer}.",
        text="Aşağıdaki kodun ekran çıktısını yazınız (çıktı tek satırdır; değerleri aralarında birer boşlukla "
             "yazınız):",
        common_wrongs=wrongs, norm="metin_esnek",
        hint="Hata hangi satırda oluşuyor? O satırdan sonraki satırlar çalışır mı? finally ne zaman çalışır?",
    )


INVALID_INPUTS = ["abc", "3.5", "x", "", "on", "7,5", "12a", "bir"]


@q("Doğrulama Döngüsü")
def retry_loop():
    """Kazanım: hata yakalayan döngüde sayaç izler · Bloom: An"""
    pos = random.randint(0, 3)
    valid = str(random.choice([v for v in range(-20, 100) if v]))
    before = random.sample(INVALID_INPUTS, pos)
    # sonrasında en az iki geçersiz girdi: "hepsini say" yanılgısı "geçerliyi de say" yanılgısından ayrı çıksın
    after = random.sample([x for x in INVALID_INPUTS if x not in before], random.randint(2, 3))
    if random.random() < 0.3:
        after.insert(random.randint(0, len(after)), str(random.randint(1, 99)))
    inputs = before + [valid] + after
    show_n = random.random() < 0.4
    code = (f"girdiler = {inputs}\nhata = 0\nfor g in girdiler:\n    try:\n        n = int(g)\n        break\n"
            "    except ValueError:\n        hata += 1\n" + ("print(hata, n)" if show_n else "print(hata)"))

    def shown(count):
        return f"{count} {valid}" if show_n else str(count)

    total_bad = sum(1 for x in inputs if x in INVALID_INPUTS)
    decimals = sum(1 for x in before if x in ("3.5", "7,5"))
    wrongs = [Wrong(shown(total_bad), "break çalışınca döngü biter; geçerli girdiden sonrakiler hiç denenmez."),
              Wrong(shown(pos + 1), "Geçerli girdide int() başarılı olur; except çalışmadığı için hata artmaz.")]
    if decimals:
        wrongs.append(Wrong(shown(pos - decimals), "int() ondalıklı ya da virgüllü metni de çeviremez; ValueError "
                                                   "verir."))
    return output_question(
        code, shown(pos),
        (f"Geçerli girdiden önceki {pos} girdi int() ile çevrilemez ve her biri hata sayısını 1 artırır. " if pos
         else "İlk girdi hemen çevrilir; except hiç çalışmaz. ")
        + f"\"{valid}\" çevrilince <code>break</code> döngüyü bitirir; sonraki girdiler denenmez.",
        common_wrongs=wrongs, norm="metin",
        hint="Hangi girdide int() başarılı olur? break çalışınca döngü ne olur?",
    )


PROPAGATION_FUNCS = {
    "bol": ("def bol(a, b):\n    return a / b", "ZeroDivisionError"),
    "cevir": ("def cevir(metin):\n    return int(metin)", "ValueError"),
    "eleman": ("def eleman(liste, i):\n    return liste[i]", "IndexError"),
}
PROPAGATION_MSGS = [("Devam", "Yakalandı", "Son"), ("Devam ediliyor", "Hata yakalandı", "Bitti"),
                    ("İkinci satır", "Sorun var", "Program bitti"), ("Sürüyor", "Yakalandı", "Tamam")]


@q("Hatanın Yayılması", verify="outcome")
def error_propagation():
    """Kazanım: fonksiyonda yakalanmayan hatanın çağıran koddaki try ile yakalandığını bilir · Bloom: An"""
    fname = random.choice(list(PROPAGATION_FUNCS))
    fdef, name = PROPAGATION_FUNCS[fname]
    cont, caught, end = random.choice(PROPAGATION_MSGS)
    r = random.random()
    safe, matching = r < 0.2, r < 0.7
    if fname == "bol":
        x = random.randint(2, 9) * 2
        call, val = (f"bol({x}, 2)", str(x / 2)) if safe else (f"bol({x}, 0)", None)
    elif fname == "cevir":
        good = str(random.randint(10, 99))
        call, val = (f'cevir("{good}")', good) if safe else (f'cevir("{random.choice(NUMBER_WORDS)}")', None)
    else:
        items = random.sample(range(1, 30), 3)
        call, val = (f"eleman({items}, 1)", str(items[1])) if safe else (f"eleman({items}, {random.randint(3, 5)})",
                                                                          None)
    handler = name if matching else random.choice([x for x in ("ValueError", "ZeroDivisionError", "IndexError",
                                                                "KeyError") if x != name])
    code = (f"{fdef}\n\ntry:\n    print({call})\n    print(\"{cont}\")\nexcept {handler}:\n    print(\"{caught}\")\n"
            f"print(\"{end}\")")
    if safe:
        answer = f"{val}\n{cont}\n{end}"
        wrongs = [Wrong(f"{caught}\n{end}", f"Bu çağrıda hata oluşmaz; {call} geçerli bir değer döndürür."),
                  Wrong(f"{val}\n{end}", "Hata olmadığında try bloğunun bütün satırları çalışır."),
                  Wrong(err(name), f"{call} geçerli bir işlem; hata oluşmaz.")]
        solution = f"{call} hatasız çalışıp {val} döndürür; try bloğunun tümü çalışır, except atlanır."
    elif matching:
        answer = f"{caught}\n{end}"
        wrongs = [Wrong(err(name), "Fonksiyonda yakalanmayan hata, onu çağıran koda iletilir ve oradaki try onu "
                                   "yakalar."),
                  Wrong(f"{cont}\n{end}", "Hata oluşunca try bloğunun geri kalanı atlanır; ikinci print çalışmaz."),
                  Wrong(f"{caught}\n{cont}\n{end}", "except çalıştıktan sonra try bloğuna geri dönülmez.")]
        solution = (f"Fonksiyonda {name} oluşur ve fonksiyonda try olmadığı için hata çağıran koda iletilir. Oradaki "
                    f"<code>except {name}</code> hatayı yakalar; try'ın geri kalanı atlanır, program devam eder.")
    else:
        answer = err(name)
        wrongs = [Wrong(f"{caught}\n{end}", f"<code>except {handler}</code> yalnızca {handler} hatasını yakalar; "
                                            f"oluşan hata {name} olduğu için yakalanmaz."),
                  Wrong(end, "Yakalanmayan hata programı durdurur; sonraki satırlar çalışmaz."),
                  Wrong(f"{cont}\n{end}", "Hata oluşunca try bloğunun geri kalanı atlanır.")]
        solution = (f"Fonksiyonda {name} oluşur ve çağıran koda iletilir; ama <code>except {handler}</code> bu hatayı "
                    "yakalamaz. Yakalanmayan hata programı durdurur.")
    return output_question(
        code, answer, solution, wrongs=wrongs,
        hint="Fonksiyonda try yok; hata nereye gider? Çağıran koddaki except bu hatayı yakalar mı?",
    )


@q("Hata Yönetimi Kavramları II")
def concepts2():
    """Kazanım: except ... as e, except sırası, hatanın yayılması ve raise kavramlarını bilir · Bloom: H/A"""
    return tf_question(
        [("<code>except ValueError as e:</code> satırında <code>e</code>, yakalanan hata nesnesidir; "
          "<code>print(e)</code> hatanın mesajını yazar.",
          "as ile verilen ad, yakalanan hatayı tutar; print(e) mesajını yazar."),
         ("Aynı try için yazılan except blokları yukarıdan aşağı denenir; yalnızca ilk eşleşen blok çalışır.",
          "Python except bloklarını sırayla dener ve ilk uyan bloğu çalıştırır."),
         ("Bir fonksiyonda oluşan ve orada yakalanmayan hata, fonksiyonu çağıran koddaki try ile yakalanabilir.",
          "Yakalanmayan hata çağıran koda iletilir; oradaki try onu yakalayabilir."),
         ("<code>raise ValueError(\"Negatif olamaz\")</code> satırı, programda bilerek bir hata oluşturur.",
          "raise ile istenen an bir hata oluşturulabilir."),
         ("<code>except Exception:</code> bloğu ZeroDivisionError ve ValueError gibi hataların hepsini yakalar.",
          "Exception, bu hata türlerinin hepsini kapsar."),
         ("Tek bir except satırında birden fazla hata türü yakalanabilir: "
          "<code>except (ValueError, ZeroDivisionError):</code>",
          "Hata türleri parantez içinde virgülle yazılabilir."),
         ("try bloğunda hiç hata oluşmazsa except blokları hiç çalışmaz.",
          "except yalnızca eşleşen bir hata olduğunda çalışır."),
         ("Kullanıcı harf yazarsa <code>int(input())</code> satırı ValueError verir.",
          "int() rakam olmayan metni çeviremez; ValueError verir."),
         ("while döngüsü içinde try / except kullanılarak kullanıcı geçerli bir sayı girene kadar tekrar girdi "
          "istenebilir.",
          "Hata olunca döngü sürer; geçerli girdide break ile çıkılır."),
         ("else bloğu, except bloklarından sonra ve finally bloğundan önce yazılır.",
          "Sıra try, except, else, finally biçimindedir."),
         ("Hata yakalandıktan sonra program, try / except yapısından sonraki satırdan devam eder.",
          "Yakalanan hata programı durdurmaz; program sonraki satırla sürer."),
         ("3 elemanlı bir listede <code>liste[10]</code> ifadesi IndexError verir.",
          "Geçerli indeksler 0, 1 ve 2'dir; 10 liste dışındadır."),
         ("Sözlükte olmayan bir anahtara <code>sozluk[\"x\"]</code> biçiminde erişmek KeyError verir.",
          "Sözlükte olmayan anahtar KeyError verir."),
         ("Türü yazılmamış bir <code>except:</code> bloğu her türlü hatayı yakalar; bu yüzden gözden kaçan hataları "
          "da gizleyebilir.",
          "Çıplak except bütün hataları yakalar."),
         ("Python'un hata mesajında hatanın türü (ör. KeyError) ve oluştuğu satırın numarası yer alır.",
          "Hata mesajı satır numarasını ve hata türünü gösterir.")],
        [("<code>except Exception:</code> bloğu önce yazılırsa, sonraki <code>except ValueError:</code> bloğu yine de "
          "ValueError'ı yakalar.",
          "Exception bütün hataları kapsar ve önce eşleşir; sonraki blok hiç çalışmaz."),
         ("finally bloğu yalnızca hata oluştuğunda çalışır.",
          "finally hata olsa da olmasa da çalışır."),
         ("Bir fonksiyonda oluşan hata yalnızca o fonksiyonun içindeki try ile yakalanabilir.",
          "Yakalanmayan hata çağıran koda iletilir; oradaki try onu yakalayabilir."),
         ("Aynı try için yazılan bütün except blokları sırayla çalışır.",
          "Yalnızca hataya uyan ilk except bloğu çalışır."),
         ("<code>except ValueError as e:</code> satırındaki <code>e</code>, hatanın oluştuğu satırın numarasıdır.",
          "e, yakalanan hata nesnesidir; print(e) hatanın mesajını yazar."),
         ("<code>raise</code> yalnızca Python'un kendi hatalarında kullanılır; programcı kendisi hata oluşturamaz.",
          "raise ile programcı istediği an hata oluşturabilir: raise ValueError(...)."),
         ("Hata yakalandıktan sonra program try bloğunun başına döner ve işlemi kendiliğinden tekrar dener.",
          "try kendiliğinden tekrarlanmaz; tekrar denemek için döngü gerekir."),
         ("Bir except satırına yalnızca bir hata türü yazılabilir.",
          "Parantez içinde birden fazla tür yazılabilir: except (ValueError, KeyError):"),
         ("<code>int(\"3.5\")</code> ifadesi 3 sonucunu verir.",
          "int() ondalık noktalı metni çeviremez; ValueError verir."),
         ("Sözlükte olmayan bir anahtara erişmek IndexError verir.",
          "Sözlükte olmayan anahtar KeyError verir; IndexError liste ve metinlerde oluşur."),
         ("else bloğu, try bloğunda hata oluştuğunda çalışır.",
          "else yalnızca hata olmazsa çalışır; hata olunca except çalışır."),
         ("try / except kullanılan bir programda hiçbir zaman hata mesajı görülmez.",
          "Yalnızca yakalanan türler susturulur; yakalanmayan hatalar programı yine durdurur."),
         ("<code>except valueerror:</code> yazımı da ValueError hatasını yakalar.",
          "Python büyük/küçük harfe duyarlıdır; hatanın adı ValueError'dır."),
         ("try bloğundan sonra mutlaka bir except bloğu gelmelidir; try yalnızca finally ile yazılamaz.",
          "try'dan sonra except ya da finally'den en az biri yeterlidir; try / finally geçerlidir."),
         ("Türü yazılmamış bir <code>except:</code> bloğu yalnızca ValueError hatalarını yakalar.",
          "Türü yazılmamış except her türlü hatayı yakalar.")],
        "except blokları sırayla denenir ve yalnızca ilk eşleşen çalışır. Fonksiyonda yakalanmayan hata çağıran koda "
        "iletilir. <code>as e</code> yakalanan hatayı bir ada bağlar; <code>raise</code> bilerek hata oluşturur.",
        hint="except blokları hangi sırayla denenir? Yakalanmayan bir hata nereye gider?",
    )


SAFE_DIV_FALLBACKS = [("None", "None"), ("0", "0"), ('"Tanımsız"', "Tanımsız")]


@q("Güvenli Bölme Fonksiyonu (Kod Yazma)")
def write_safe_div():
    """Kazanım: try/except ile hatayı yakalayıp anlamlı değer döndürür · Bloom: O"""
    name = random.choice(["guvenli_bol", "bol", "guvenli_bolme"])
    fallback, shown_fb = random.choice(SAFE_DIV_FALLBACKS)
    x, y = random.choice([(8, 2), (9, 4), (15, 6), (7, 2), (12, 5), (20, 8)])
    z = random.randint(1, 9)
    return {
        "type": "code",
        "text": f"<code>{name}(a, b)</code> fonksiyonunu yazınız: <code>a / b</code> sonucunu döndürsün; b sıfırsa "
                f"hata vermek yerine <code>{e(fallback)}</code> döndürsün. <strong>try / except kullanınız.</strong> "
                f"(Örnek: <code>{name}({x}, {y})</code> → <code>{x / y}</code>, <code>{name}({z}, 0)</code> → "
                f"<code>{e(shown_fb)}</code>)",
        "code": None,
        "check": {"kind": "safe_div", "name": name, "fallback": fallback},
        "answer": f"def {name}(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n"
                  f"        return {fallback}",
        "hint": "Hata çıkabilecek satırı try içine al; except bloğunda istenen değeri döndür.",
        "solution": "Bölme <code>try</code> bloğunda yapılır ve sonucu döndürülür. b sıfırsa ZeroDivisionError oluşur; "
                    f"<code>except ZeroDivisionError:</code> bloğu bunu yakalar ve <code>return {e(fallback)}</code> "
                    "çalışır.",
    }


@q("Geçerli Girdiyi Yakala (Kod Yazma)")
def write_parse_guard():
    """Kazanım: dönüşüm hatasını yakalayıp program akışını sürdürür · Bloom: O"""
    var = random.choice(["veri", "girdi", "metin"])
    value = random.choice(["12", "45", "abc", "7.5", "-4", "on"])
    k = random.choice([2, 3, 10])
    msg = random.choice(["Geçersiz", "Hatalı giriş", "Sayı değil"])
    return {
        "type": "code",
        "text": f"<code>{var} = \"{e(value)}\"</code> satırıyla başlayan bir kod yazınız: <code>{var}</code> tam "
                f"sayıya çevrilebiliyorsa sayının {k} katını, çevrilemiyorsa <code>{msg}</code> yazdırsın. "
                f"<strong>try / except kullanınız.</strong> (Örnek: \"12\" → {12 * k}, \"abc\" → {msg})",
        "code": None,
        "check": {"kind": "parse_guard", "var": var, "factor": k, "msg": msg},
        "answer": f"{var} = \"{value}\"\ntry:\n    sayi = int({var})\n    print(sayi * {k})\nexcept ValueError:\n"
                  f"    print(\"{msg}\")",
        "hint": "int() hata verirse hangi blok çalışır? Katını yazdıran satır nerede olmalı?",
        "solution": f"<code>int({var})</code> dönüşümü try bloğunda yapılır; başarılı olursa sonraki satır sayının "
                    f"{k} katını yazar. Metin sayı değilse ValueError oluşur ve except bloğu <code>{msg}</code> yazar. "
                    "isdigit() ile denetim \"-4\" gibi negatif sayıları geçersiz sayar.",
    }


# ================================================================= kod yazma denetleyicileri
BROAD_NOTE = "Kabul edildi; ama yalnızca beklenen hatayı ({name}) yakalamak daha iyidir."


def _handler_kind(handler, name):
    """'exact' (adı geçiyor), 'broad' (Exception ya da türsüz) ya da None."""
    t = handler.type
    if t is None or (isinstance(t, ast.Name) and t.id in ("Exception", "BaseException")):
        return "broad"
    names = t.elts if isinstance(t, ast.Tuple) else [t]
    if any(isinstance(n, ast.Name) and n.id == name for n in names):
        return "exact"
    if any(isinstance(n, ast.Name) and n.id in ("Exception", "BaseException") for n in names):
        return "broad"
    return None


def _pick_handler(tries, name):
    """try'lar içinde hatayı yakalayan ilk (try, handler, tür); yoksa (ilk try, None, None)."""
    for t in tries:
        for h in t.handlers:
            kind = _handler_kind(h, name)
            if kind:
                return t, h, kind
    return tries[0], None, None


_MISSING = object()


def _divides(node, a, b):
    return computes(node, [a, b], lambda x, y: x / y)


@checker("safe_div")
def check_safe_div(tree, p):
    """İki parametreli fonksiyon: try içinde a / b döndürür, ZeroDivisionError'da istenen değeri döndürür
    (except içinde return ile ya da try'dan sonra döndürülen değişkene atayarak)."""
    name = p["name"]
    want = ast.literal_eval(p["fallback"])
    func, note = find_def(tree, name, 2)
    note = note or return_note(func)
    if note:
        return False, note
    a, b = func.args.args[0].arg, func.args.args[1].arg
    tries = [s for s in func.body if isinstance(s, ast.Try)]
    if not tries:
        if any(isinstance(n, ast.Try) for n in ast.walk(func)):
            raise Unknown("iç içe try")
        return False, (f"Soru try / except kullanmanı istiyor; <code>{b}</code> değerini if ile denetlemek yerine "
                       "oluşan hatayı yakala.")
    t, handler, kind = _pick_handler(tries, "ZeroDivisionError")
    if handler is None:
        return False, f"except bloğu, <code>{b}</code> sıfır olunca oluşan hatayı (ZeroDivisionError) yakalamıyor."
    if not any(isinstance(n, ast.BinOp) and isinstance(n.op, (ast.Div, ast.FloorDiv)) for s in t.body
               for n in ast.walk(s)):
        return False, "Bölme işlemi try bloğunun içinde olmalı; hata ancak orada yakalanır."
    # except bloğu: döndürdüğü ya da atadığı değerler
    h_tr = Tracker()
    h_returns = [s.value for s in h_tr.run(handler.body) if isinstance(s, ast.Return)]
    fallback_ok = any((r is None and want is None)
                      or (r is not None and same_value(const_value(r, default=_MISSING), want)) for r in h_returns)
    # hatasız yol: try ve else içindeki, sonra try'dan sonraki return'ler (try'daki tanımlarla)
    idx = func.body.index(t)
    tr = Tracker(keep={a, b})
    exprs = []
    for stmt in tr.run(func.body[:idx] + t.body + t.orelse + func.body[idx + 1:]):
        if isinstance(stmt, ast.Return) and stmt.value is not None:
            exprs.append(tr.inline(stmt.value))
            ret = stmt.value
            if (stmt in func.body[idx + 1:] and not h_returns and isinstance(ret, ast.Name)
                    and ret.id in h_tr.values):  # except'te atanıp try'dan sonra döndürülen değişken
                fallback_ok = fallback_ok or same_value(h_tr.values[ret.id], want)
    if not exprs:
        return False, f"<code>{b}</code> sıfır değilken fonksiyon bölmenin sonucunu <code>return</code> ile döndürmeli."
    if not all(_divides(x, a, b) for x in exprs):
        return False, f"Fonksiyon <code>{b}</code> sıfır değilken <code>{a} / {b}</code> sonucunu döndürmeli."
    if not fallback_ok:
        if any(r is not None for r in h_returns):
            # except return ile başka bir değer döndürüyor (ör. "tanımsız"): yazdırma sorunu değil
            return False, (f"<code>{b}</code> sıfır olduğunda fonksiyon tam olarak <code>{e(p['fallback'])}</code> "
                           "döndürmeli (büyük/küçük harf ve tırnak dahil).")
        return False, (f"<code>{b}</code> sıfır olduğunda fonksiyon <code>{e(p['fallback'])}</code> değerini "
                       "<code>return</code> ile döndürmeli; ekrana yazdırma.")
    if kind == "broad":
        return True, BROAD_NOTE.format(name="ZeroDivisionError")
    return True, OK


def _fold(text):
    return text.replace("İ", "i").replace("I", "ı").lower().translate(str.maketrans("çğıöşü", "cgiosu"))


def _int_calls(node, var):
    return [n for n in ast.walk(node) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
            and n.func.id == "int" and len(n.args) == 1 and isinstance(n.args[0], ast.Name) and n.args[0].id == var]


class _IntToName(ast.NodeTransformer):
    def __init__(self, var):
        self.var = var

    def visit_Call(self, node):
        if (isinstance(node.func, ast.Name) and node.func.id == "int" and len(node.args) == 1
                and isinstance(node.args[0], ast.Name) and node.args[0].id == self.var):
            return ast.Name(id="sayi_", ctx=ast.Load())
        self.generic_visit(node)
        return node


@checker("parse_guard")
def check_parse_guard(tree, p):
    """var = "..." ile başlayan kod: try içinde int(var); başarılıysa factor katı yazdırılır, ValueError'da msg."""
    var, k, msg = p["var"], p["factor"], p["msg"]
    tr = Tracker(keep={var})
    first = None
    for stmt in tree.body:
        if isinstance(stmt, ast.Assign) and any(isinstance(t, ast.Name) and t.id == var for t in stmt.targets):
            first = stmt
            break
    if first is None or not isinstance(const_value(first.value), str):
        return False, f"Kod <code>{var} = \"...\"</code> satırıyla (metin değerle) başlamalı."
    tries = [s for s in tree.body if isinstance(s, ast.Try)]
    if not tries:
        return False, "Soru try / except kullanmanı istiyor; dönüşüm hatasını except bloğuyla yakala."
    t, handler, kind = _pick_handler(tries, "ValueError")
    if any(_int_calls(s, var) for s in tree.body[:tree.body.index(t)]):
        return False, "<code>int()</code> dönüşümü try bloğunun içinde olmalı; hata ancak orada yakalanır."
    if not any(_int_calls(s, var) for s in t.body):
        if any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "float"
               for n in ast.walk(t)):
            return False, "Metni tam sayıya çevirmek için <code>int()</code> kullanmalısın."
        return False, f"try bloğunda <code>int({var})</code> ile dönüşüm yapılmalı."
    if handler is None:
        return False, "except bloğu, int() dönüşümünde oluşan hatayı (ValueError) yakalamıyor."
    # try ve else bloklarında katı yazdıran print
    for _ in tr.run(tree.body[:tree.body.index(t)]):
        pass
    doubled = False
    for stmt in tr.run(t.body + t.orelse):
        for call in find_prints(stmt):
            for node in print_values(call):
                expr = _IntToName(var).visit(tr.inline(node))
                if computes(expr, ["sayi_"], lambda n: k * n):
                    doubled = True
    if not doubled:
        later = [c for s in tree.body[tree.body.index(t) + 1:] for c in find_prints(s)]
        if later:
            return False, ("Sayının katını yazdıran satır try (ya da else) bloğunda olmalı; aksi hâlde geçersiz "
                           "girdide hata oluşur.")
        return False, f"try bloğunda, çevrilen sayının {k} katını hesaplayıp yazdırmalısın."
    texts = [_fold(" ".join(print_texts(c))) for s in handler.body for c in find_prints(s)]
    if not any(_fold(msg) in t_ for t_ in texts):
        return False, f"Geçersiz girdide except bloğu ekrana <code>{msg}</code> yazmalı."
    if kind == "broad":
        return True, BROAD_NOTE.format(name="ValueError")
    return True, OK
