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
    """Üç sonuç (1, 2 ya da 3 satır) eşit olasılıkla; yanlışlar elif yanılgısından ve sınır değerlerinden (Y1)."""
    limits = ((5, "Küçük"), (10, "Orta"), (20, "Büyük"))
    words = [w for _, w in limits]
    band = random.choice([(6, 10), (11, 20), (21, 30)])
    x = random.choice([band[0], band[1], random.randint(*band)])  # sınır değerleri sık gelir
    code = f"x = {x}\n" + "\n".join(f"if x > {lim}:\n    print(\"{word}\")" for lim, word in limits)
    out = [word for lim, word in limits if x > lim]

    def why_for(candidate):
        extra = [lim for lim, word in limits if word in candidate and word not in out]
        if extra:
            return f"x = {x}, x &gt; {extra[0]} koşulunu sağlamıyor; o blok çalışmaz."
        return ("Bunlar elif değil, birbirinden bağımsız if bloklarıdır; koşulu sağlanan her blok çalışır "
                "ve biri diğerini durdurmaz.")

    candidates = [[out[-1]], [out[0]], out + words[len(out):len(out) + 1], out[:-1], words, words[:2], [words[1]]]
    wrongs = []
    for c in candidates:
        value = "\n".join(c)
        if c and value != "\n".join(out) and value not in [w.value for w in wrongs]:
            wrongs.append(Wrong(value, why_for(c)))
    return output_question(
        code, "\n".join(out),
        "Bunlar <code>elif</code> değil, birbirinden bağımsız <code>if</code> bloklarıdır; koşulu sağlanan "
        f"<strong>her</strong> blok çalışır. x = {x} için {len(out)} koşul sağlanır.",
        wrongs=wrongs,
        hint="Bunlar elif mi, ayrı if'ler mi? Her koşulu x'in değeriyle tek tek kontrol et.",
    )


TICKETS = ("Öğrenci bileti", "İndirimli bilet", "Tam bilet")


@q("Koşullarda Mantıksal Operatörler", verify="output")
def compound_condition():
    """and ile or aynı değişkenlerle üç dallı bir zincirde: üç sonuç eşit olasılıklı (K4)."""
    limit = random.choice([12, 15, 18])
    var = random.choice(["ogrenci", "kartli", "uye"])
    case = random.choice(["both", "one", "none"])
    if case == "both":
        yas, flag = random.randint(7, limit - 1), True
    elif case == "one":
        yas, flag = random.choice([(random.randint(7, limit - 1), False), (random.randint(limit, 30), True)])
    else:
        yas, flag = random.randint(limit, 30), False
    young = yas < limit
    res = TICKETS[0] if young and flag else TICKETS[1] if young or flag else TICKETS[2]
    code = (f"yas = {yas}\n{var} = {flag}\n"
            f"if yas < {limit} and {var}:\n    print(\"{TICKETS[0]}\")\n"
            f"elif yas < {limit} or {var}:\n    print(\"{TICKETS[1]}\")\n"
            f"else:\n    print(\"{TICKETS[2]}\")")
    facts = f"yas &lt; {limit} → {young}, {var} → {flag}"
    whys = {
        TICKETS[0]: f"<code>and</code> için iki koşulun da True olması gerekir; burada {facts}.",
        TICKETS[1]: (f"<code>or</code> için en az bir koşulun True olması yeter; burada {facts}." if not (young or flag)
                     else f"İlk koşul (and) zaten True; Python ilk doğru koşulda durur, elif'e bakmaz. {facts}."),
        TICKETS[2]: f"else yalnızca yukarıdaki iki koşul da False olunca çalışır; burada {facts}.",
    }
    wrongs = [Wrong(t, whys[t]) for t in TICKETS if t != res]
    wrongs.append(Wrong(f"{TICKETS[0]}\n{TICKETS[1]}" if res != TICKETS[2] else f"{TICKETS[1]}\n{TICKETS[2]}",
                        "if / elif / else zincirinde yalnızca bir blok çalışır."))
    return output_question(
        code, res,
        "<code>and</code> ile bağlanan koşul iki taraf da True ise, <code>or</code> ile bağlanan koşul en az biri "
        f"True ise True olur. {facts}; bu yüzden \"{res}\" yazılır.",
        wrongs=wrongs,
        hint="Önce yas koşulunu ve diğer değişkeni ayrı ayrı değerlendir, sonra and ile or kurallarını uygula.",
    )


@q("Tek / Çift Kontrolü", verify="output")
def even_odd():
    """Sayıya göre iki farklı hesap yapılır; cevap sayıdır ve sayıyla birlikte değişir (K4)."""
    n = random.randint(11, 99)
    var = random.choice(["sayi", "n", "x"])
    code = f"{var} = {n}\nif {var} % 2 == 0:\n    print({var} // 2)\nelse:\n    print({var} * 3 + 1)"
    even = n % 2 == 0
    res = str(n // 2 if even else n * 3 + 1)
    other = str(n * 3 + 1 if even else n // 2)
    wrongs = [
        Wrong(other, f"{n} % 2 = {n % 2}; kalan {'0 olduğu için koşul doğru, if' if even else '1 olduğu için koşul yanlış, else'} "
                     "bloğu çalışır."),
        Wrong(f"{res}\n{other}" if even else f"{other}\n{res}", "if / else yapısında yalnızca bir blok çalışır."),
    ]
    if even:
        wrongs.append(Wrong(str(n / 2), "<code>//</code> tam bölmedir; sonuç ondalıklı değil, tam sayıdır."))
    else:
        wrongs.append(Wrong(str(n * 4), "Çarpma toplamadan önce yapılır: önce sayı 3 ile çarpılır, sonra 1 eklenir."))
    return output_question(
        code, res,
        f"<code>{var} % 2</code> sayının 2'ye bölümünden kalandır; kalan 0 ise sayı çifttir. {n} % 2 = {n % 2}, "
        f"bu yüzden {'if' if even else 'else'} bloğu çalışır ve {res} yazılır.",
        wrongs=wrongs,
        hint=f"{n} sayısını 2'ye böldüğünde kalan kaç olur? Hangi blok çalışır?",
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
