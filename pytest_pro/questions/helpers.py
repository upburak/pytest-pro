"""Soru şablonlarında ortak kullanılan yardımcılar."""
import html
import random
from typing import NamedTuple

STR_VALUES = ["Python", "Kodlama", "Gelisim", "Yazilim", "Bilgisayar", "Algoritma"]
PEOPLE = ["Ali", "Ayşe", "Can", "Deniz", "Ece", "Elif", "Mert", "Zeynep"]
FRUITS = ["elma", "armut", "kiraz", "muz", "nar", "erik", "incir"]


FILLER_WHY_NUMBER = "Hesaptaki bir adımı atlamış ya da fazladan yapmış olabilirsin; kodu adım adım izle."
FILLER_WHY_OTHER = "Bu, kodun gerçek çıktısı değil; kodu adım adım izle."


class Wrong(NamedTuple):
    """Yanlış seçenek ve öğrencinin neden bunu seçmiş olabileceğinin açıklaması."""
    value: str
    why: str


def _value(w):
    return w.value if isinstance(w, Wrong) else w


def _is_number(text):
    try:
        float(str(text))
        return True
    except ValueError:
        return False


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
    for w in [_value(w) for w in wrongs] + _fillers(correct):
        if len(opts) == n:
            break
        if str(w).strip() and w not in opts:
            opts.append(w)
    random.shuffle(opts)
    return opts


def whys_for_options(correct, wrongs, options):
    """Gösterilen yanlış seçeneklerin açıklamaları. Açıklamasız (düz metin) yanlışlar dahil edilmez;
    yedek çeldiricilere genel bir açıklama verilir."""
    reasons = {w.value: w.why for w in wrongs if isinstance(w, Wrong)}
    plain = {w for w in wrongs if not isinstance(w, Wrong)}
    out = {}
    for opt in options:
        if opt == correct or opt in plain:
            continue
        if opt in reasons:
            out[opt] = reasons[opt]
        else:
            out[opt] = FILLER_WHY_NUMBER if _is_number(opt) else FILLER_WHY_OTHER
    return out


def output_question(code, answer, solution, wrongs=None, text=None, stdin=None, hint=None, common_wrongs=None):
    """Kod çıktısı sorusu. wrongs verilirse çoktan seçmeli, verilmezse kısa cevap olur.
    wrongs ve common_wrongs elemanları Wrong(değer, açıklama) ya da düz metin olabilir."""
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
        q["whys"] = whys_for_options(answer, wrongs, q["options"])
    else:
        q["whys"] = {w.value: w.why for w in (common_wrongs or []) if isinstance(w, Wrong)}
    if hint is not None:
        q["hint"] = hint
    if stdin is not None:
        q["stdin"] = stdin
    return q


def tf_question(statements_true, statements_false, solution, code=None, hint=None):
    """Doğru/yanlış sorusu: verilen ifadelerden rastgele biri seçilir."""
    is_true = random.random() < 0.5
    q = {
        "type": "tf",
        "text": random.choice(statements_true if is_true else statements_false),
        "code": code,
        "answer": "True" if is_true else "False",
        "solution": solution,
    }
    if hint is not None:
        q["hint"] = hint
    return q
