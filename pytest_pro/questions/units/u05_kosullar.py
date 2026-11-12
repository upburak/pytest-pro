"""Ünite 5 - Koşullu İfadeler."""
import random

from ..helpers import Wrong, output_question, tf_question
from ..registry import register_unit

UNIT = register_unit(
    "kosullar", "Koşullu İfadeler", "Başlangıç",
    "if, elif, else blokları, girinti, iç içe koşullar ve mantıksal operatörlerle koşul kurma.",
    order=5,
)
q = UNIT.question

ONLY_ONE_BLOCK = "if / elif / else zincirinde yalnızca bir blok çalışır."
LADDER = ((85, "A"), (70, "B"), (50, "C"))


def _grade(n):
    for limit, letter in LADDER:
        if n >= limit:
            return letter
    return "F"


@q("if / elif / else", verify="output")
def grade_ladder():
    n = random.choice([random.randint(85, 100), random.randint(70, 84), random.randint(50, 69), random.randint(0, 49)])
    code = (f"puan = {n}\n"
            "if puan >= 85:\n    print(\"A\")\n"
            "elif puan >= 70:\n    print(\"B\")\n"
            "elif puan >= 50:\n    print(\"C\")\n"
            "else:\n    print(\"F\")")
    res = _grade(n)
    wrongs = []
    for limit, letter in LADDER:
        if letter == res:
            continue
        if n >= limit:
            why = (f"puan >= {limit} de doğru, ama Python ilk doğru koşulda durur; sonraki elif'ler hiç "
                   "denenmez.")
        else:
            why = f"puan >= {limit} koşulu {n} için yanlış; bu blok çalışmaz."
        wrongs.append(Wrong(letter, why))
    if res != "F":
        wrongs.append(Wrong("F", "else yalnızca yukarıdaki koşulların hiçbiri sağlanmazsa çalışır."))
    wrongs.append(Wrong("A\nB", ONLY_ONE_BLOCK))
    return output_question(
        code, res,
        "Koşullar yukarıdan aşağı denenir; <strong>ilk</strong> True olan bloğun kodu çalışır ve diğerleri "
        f"atlanır. puan = {n} için ilk sağlanan koşul \"{res}\" sonucunu verir.",
        wrongs=wrongs,
        hint="Koşulları yukarıdan aşağı dene; ilk doğru çıkan hangisi?",
    )


@q("Ayrı if Blokları", verify="output")
def separate_ifs():
    x = random.randint(6, 30)
    limits = ((5, "Kucuk"), (10, "Orta"), (20, "Buyuk"))
    code = f"x = {x}\n" + "\n".join(f"if x > {lim}:\n    print(\"{word}\")" for lim, word in limits)
    out = [word for lim, word in limits if x > lim]

    def why_for(candidate):
        extra = [lim for lim, word in limits if word in candidate and word not in out]
        if extra:
            return f"x = {x}, x > {extra[0]} koşulunu sağlamıyor; o blok çalışmaz."
        return ("Bunlar elif değil, birbirinden bağımsız if bloklarıdır; koşulu sağlanan her blok çalışır "
                "ve biri diğerini durdurmaz.")

    candidates = [[out[-1]], [out[0]], ["Kucuk", "Orta", "Buyuk"], ["Kucuk", "Orta"]]
    return output_question(
        code, "\n".join(out),
        "Bunlar <code>elif</code> değil, birbirinden bağımsız <code>if</code> bloklarıdır; koşulu sağlanan "
        f"<strong>her</strong> blok çalışır. x = {x} için {len(out)} koşul sağlanır.",
        wrongs=[Wrong("\n".join(c), why_for(c)) for c in candidates],
        hint="Bunlar elif mi, ayrı if'ler mi? Her koşulu x'in değeriyle tek tek kontrol et.",
    )


@q("Koşullarda Mantıksal Operatörler", verify="output")
def compound_condition():
    yas = random.randint(10, 25)
    izin = random.choice([True, False])
    op = random.choice(["or", "and"])
    ok = (yas >= 18 or izin) if op == "or" else (yas >= 18 and izin)
    code = (f"yas = {yas}\nizin = {izin}\n"
            f"if yas >= 18 {op} izin:\n    print(\"Girebilir\")\nelse:\n    print(\"Giremez\")")
    res = "Girebilir" if ok else "Giremez"
    rule = "en az biri True ise" if op == "or" else "ikisi de True ise"
    return output_question(
        code, res,
        f"<code>{op}</code> ile bağlanan koşul, {rule} True olur. yas >= 18 → {yas >= 18}, izin → {izin}; "
        f"sonuç {ok}.",
        wrongs=[
            Wrong("Giremez" if ok else "Girebilir",
                  f"yas >= 18 → {yas >= 18} ve izin → {izin}. <code>{op}</code> {rule} True verir; "
                  f"burada sonuç {ok}."),
            Wrong("Girebilir\nGiremez", "if / else yapısında yalnızca bir blok çalışır."),
            Wrong("True", "print koşulun değerini değil, çalışan bloktaki metni yazar."),
        ],
        hint=f"Önce iki parçayı ayrı ayrı değerlendir, sonra {op} kuralını uygula.",
    )


@q("Tek / Çift Kontrolü", verify="output")
def even_odd():
    n = random.randint(10, 99)
    code = f"sayi = {n}\nif sayi % 2 == 0:\n    print(\"Cift\")\nelse:\n    print(\"Tek\")"
    res = "Cift" if n % 2 == 0 else "Tek"
    return output_question(
        code, res,
        f"<code>sayi % 2</code> sayının 2'ye bölümünden kalandır; kalan 0 ise sayı çifttir. {n} % 2 = {n % 2}.",
        wrongs=[
            Wrong("Tek" if res == "Cift" else "Cift", f"{n} % 2 = {n % 2}. Kalan 0 ise koşul doğrudur ve Cift yazılır."),
            Wrong(str(n % 2), "print, çalışan bloktaki metni yazar; kalanın kendisini değil."),
            Wrong("Cift\nTek", "if / else yapısında yalnızca bir blok çalışır."),
        ],
        hint=f"{n} sayısını 2'ye böldüğünde kalan kaç olur?",
    )


@q("Girinti ve Blok Yapısı")
def indentation():
    return tf_question(
        [("Python'da hangi satırların <code>if</code> bloğuna ait olduğunu <strong>girinti</strong> belirler.",
          "Python süslü parantez kullanmaz; bloğa ait satırlar girintiyle ayrılır."),
         ("<code>if</code> satırının sonuna iki nokta üst üste (<code>:</code>) konması zorunludur.",
          "Koşul satırı : ile bitmezse SyntaxError oluşur."),
         ("Bir <code>if</code> yapısında birden fazla <code>elif</code> kullanılabilir.",
          "elif sayısı sınırsızdır; koşullar sırayla denenir."),
         ("<code>else</code> bloğu kullanılmak zorunda değildir.",
          "else isteğe bağlıdır; yazılmazsa hiçbir koşul sağlanmadığında hiçbir şey çalışmaz."),
         ("Bir <code>if</code> bloğunun içine başka bir <code>if</code> yazılabilir.",
          "İç içe koşullar geçerlidir; içteki if bir girinti daha içeride yazılır."),
         ("Koşul satırındaki ifade True ya da False'a dönüşebilen herhangi bir değer olabilir.",
          "if x: gibi yazımlarda değerin doğruluk karşılığına bakılır (0 ve boş metin False'tur).")],
        [("Python'da <code>elif</code> bloğu, öncesinde <code>if</code> olmadan tek başına kullanılabilir.",
          "elif her zaman bir if'e bağlıdır; tek başına yazılırsa SyntaxError oluşur."),
         ("Bir <code>if</code> yapısında birden fazla <code>else</code> bloğu kullanılabilir.",
          "else en fazla bir kez, en sonda yer alır."),
         ("Python'da girinti yalnızca okunabilirlik içindir; programın çalışmasını etkilemez.",
          "Girinti blokları belirler; yanlış girinti hata ya da farklı davranış demektir."),
         ("<code>if</code> yapısında birden fazla koşul doğruysa, doğru olan tüm <code>elif</code> blokları "
          "çalışır.",
          "if / elif zincirinde yalnızca ilk doğru koşulun bloğu çalışır."),
         ("<code>else</code> bloğunun kendi koşulu yazılır: <code>else x &gt; 5:</code>",
          "else koşul almaz; koşul gerekiyorsa elif kullanılır."),
         ("<code>if</code> satırının sonuna noktalı virgül (<code>;</code>) konur.",
          "if satırı iki nokta üst üste (:) ile biter.")],
        "Python blokları girinti ile ayırır (genelde 4 boşluk) ve koşul satırı <code>:</code> ile biter. "
        "<code>elif</code> ve <code>else</code> mutlaka bir <code>if</code>'e bağlıdır; <code>else</code> en "
        "fazla bir kez, en sonda yer alır.",
        hint="Python'da bloklar nasıl belirlenir ve if / elif / else hangi kurallarla sıralanır?",
    )
