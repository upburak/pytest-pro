"""Ünite 10 - Hatalar ve Hata Yönetimi."""
import random

from ..helpers import PEOPLE, Wrong, output_question, tf_question, unique_options, whys_for_options
from ..registry import register_unit

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
