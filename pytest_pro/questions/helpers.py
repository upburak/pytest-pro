"""Soru şablonlarında ortak kullanılan yardımcılar."""
import html
import random

STR_VALUES = ["Python", "Kodlama", "Gelisim", "Yazilim", "Bilgisayar", "Algoritma"]
PEOPLE = ["Ali", "Ayşe", "Can", "Deniz", "Ece", "Elif", "Mert", "Zeynep"]
FRUITS = ["elma", "armut", "kiraz", "muz", "nar", "erik", "incir"]


def err(name):
    """Hata seçeneği metni: err('TypeError') -> 'Hata verir (TypeError)'."""
    return f"Hata verir ({name})"


def e(value):
    """HTML kaçışı (soru metnine/açıklamaya değer gömerken)."""
    return html.escape(str(value), quote=False)


def shown(s):
    """Boşlukları görünür yapar: ' - ' -> '"␣-␣"', '' -> 'boş metin ("")'."""
    return '"' + s.replace(" ", "␣") + '"' if s else 'boş metin ("")'


def _fillers(correct):
    """Yanlışlar yetmezse kullanılacak, cevaba benzeyen yedek çeldiriciler."""
    text = str(correct)
    try:
        num = int(text)
        return [str(num + d) for d in (1, -1, 2, -2, 10)]
    except ValueError:
        pass
    try:
        num = float(text)
        return [str(round(num + d, 2)) for d in (1, -1, 0.1, -0.1)]
    except ValueError:
        pass
    return ["None", err("TypeError"), "[]", text + " " + text]


def unique_options(correct, wrongs, n=4):
    """Doğru cevap + birbirinden farklı yanlışlar (tam n seçenek), karıştırılmış."""
    opts = [correct]
    for w in list(wrongs) + _fillers(correct):
        if len(opts) == n:
            break
        if str(w).strip() and w not in opts:
            opts.append(w)
    random.shuffle(opts)
    return opts


def output_question(code, answer, solution, wrongs=None, text=None, stdin=None):
    """Kod çıktısı sorusu. wrongs verilirse çoktan seçmeli, verilmezse kısa cevap olur."""
    q = {
        "type": "mc" if wrongs is not None else "short",
        "text": text or ("Aşağıdaki kodun ekran çıktısı ne olur?" if wrongs is not None
                         else "Aşağıdaki kodun ekran çıktısını yazınız:"),
        "code": code,
        "answer": answer,
        "solution": solution,
    }
    if wrongs is not None:
        q["options"] = unique_options(answer, wrongs)
    if stdin is not None:
        q["stdin"] = stdin
    return q


def tf_question(statements_true, statements_false, solution, code=None):
    """Doğru/yanlış sorusu: verilen ifadelerden rastgele biri seçilir."""
    is_true = random.random() < 0.5
    return {
        "type": "tf",
        "text": random.choice(statements_true if is_true else statements_false),
        "code": code,
        "answer": "True" if is_true else "False",
        "solution": solution,
    }
