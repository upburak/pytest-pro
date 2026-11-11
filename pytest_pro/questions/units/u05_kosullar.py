"""Ünite 5 - Koşullu İfadeler."""
import random

from ..helpers import output_question, tf_question
from ..registry import register_unit

UNIT = register_unit(
    "kosullar", "Koşullu İfadeler", "Başlangıç",
    "if, elif, else blokları, girinti, iç içe koşullar ve mantıksal operatörlerle koşul kurma.",
    order=5,
)
q = UNIT.question


def _grade(n):
    if n >= 85:
        return "A"
    elif n >= 70:
        return "B"
    elif n >= 50:
        return "C"
    else:
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
    return output_question(
        code, res,
        "Koşullar yukarıdan aşağı denenir; <strong>ilk</strong> True olan bloğun kodu çalışır ve diğerleri "
        f"atlanır. puan = {n} için ilk sağlanan koşul \"{res}\" sonucunu verir.",
        wrongs=[g for g in "ABCF" if g != res] + ["A\nB"],
    )


@q("Ayrı if Blokları", verify="output")
def separate_ifs():
    x = random.randint(6, 30)
    limits = ((5, "Kucuk"), (10, "Orta"), (20, "Buyuk"))
    code = f"x = {x}\n" + "\n".join(f"if x > {lim}:\n    print(\"{word}\")" for lim, word in limits)
    out = [word for lim, word in limits if x > lim]
    return output_question(
        code, "\n".join(out),
        "Bunlar <code>elif</code> değil, birbirinden bağımsız <code>if</code> bloklarıdır; koşulu sağlanan "
        f"<strong>her</strong> blok çalışır. x = {x} için {len(out)} koşul sağlanır.",
        wrongs=[out[-1], out[0], "Kucuk\nOrta\nBuyuk", "Kucuk\nOrta"],
    )


@q("Koşullarda Mantıksal Operatörler", verify="output")
def compound_condition():
    yas = random.randint(10, 25)
    izin = random.choice([True, False])
    code = (f"yas = {yas}\nizin = {izin}\n"
            "if yas >= 18 or izin:\n    print(\"Girebilir\")\nelse:\n    print(\"Giremez\")")
    res = "Girebilir" if (yas >= 18 or izin) else "Giremez"
    return output_question(
        code, res,
        f"<code>or</code> ile bağlanan koşullardan biri True ise blok çalışır. yas >= 18 → {yas >= 18}, "
        f"izin → {izin}; sonuç {yas >= 18 or izin}.",
        wrongs=["Giremez" if res == "Girebilir" else "Girebilir", "Girebilir\nGiremez", "True"],
    )


@q("Tek / Çift Kontrolü", verify="output")
def even_odd():
    n = random.randint(10, 99)
    code = f"sayi = {n}\nif sayi % 2 == 0:\n    print(\"Cift\")\nelse:\n    print(\"Tek\")"
    res = "Cift" if n % 2 == 0 else "Tek"
    return output_question(
        code, res,
        f"<code>sayi % 2</code> sayının 2'ye bölümünden kalandır; kalan 0 ise sayı çifttir. {n} % 2 = {n % 2}.",
        wrongs=["Tek" if res == "Cift" else "Cift", str(n % 2), "Cift\nTek"],
    )


@q("Girinti ve Blok Yapısı")
def indentation():
    return tf_question(
        ["Python'da hangi satırların <code>if</code> bloğuna ait olduğunu <strong>girinti</strong> belirler.",
         "<code>if</code> satırının sonuna iki nokta üst üste (<code>:</code>) konması zorunludur."],
        ["Python'da <code>elif</code> bloğu, öncesinde <code>if</code> olmadan tek başına kullanılabilir.",
         "Bir <code>if</code> yapısında birden fazla <code>else</code> bloğu kullanılabilir."],
        "Python blokları girinti ile ayırır (genelde 4 boşluk) ve koşul satırı <code>:</code> ile biter. "
        "<code>elif</code> ve <code>else</code> mutlaka bir <code>if</code>'e bağlıdır; <code>else</code> en "
        "fazla bir kez, en sonda yer alır.",
    )
