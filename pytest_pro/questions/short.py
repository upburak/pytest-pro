"""
Kısa cevap (short) sorularının karşılaştırılması.

Soru isteğe bağlı iki alan taşıyabilir:
    "norm":   karşılaştırma biçimi (aşağıdaki NORMS); yoksa eski davranış (boşluklar silinir, virgül nokta olur)
    "accept": doğru cevaba ek olarak kabul edilen eşdeğer cevaplar listesi

Öğrenci cevabı ve kabul edilen cevaplar aynı biçimle anahtara (`short_key`) çevrilip karşılaştırılır.
"""
import ast
import re

MAX_PY_LEN = 300
_MINUS = str.maketrans({"−": "-", "–": "-", "—": "-"})
_TR_FOLD = str.maketrans("çğıöşüâîû", "cgiosuaiu")

NORMS = {
    "sayi": "Sayı metni: boşluk ve dıştaki tırnak atılır, virgül nokta, − işareti - olur. 5 ile 5.0 FARKLIDIR "
            "(tip ölçen sorular).",
    "sayi_degeri": "Sayısal değer: 5, 5.0, 5,0 ve +5 aynıdır (tip ölçmeyen sorular).",
    "metin": "Metin: baştaki/sondaki boşluk ve bir çift dış tırnak atılır, aradaki boşluklar teke iner; büyük/küçük "
             "harf ve Türkçe karakterler korunur.",
    "metin_esnek": "Metin (esnek): 'metin' + büyük/küçük harf ve Türkçe karakter farkı önemsenmez (Çift = cift = CIFT).",
    "python": "Python değeri: ast.literal_eval ile karşılaştırılır (['a', 1] = [\"a\",1]; 5 ile 5.0, True ile 1 farklı).",
}


def legacy_norm(s):
    """Eski davranış: "3,5" ile "3.5" aynı; boşluklar önemsenmez."""
    return "".join(str(s).split()).replace(",", ".")


def _unquote(s):
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "'\"":
        s = s[1:-1].strip()
    return s


def _text(s):
    return " ".join(_unquote(str(s)).split())


def _tr_lower(s):
    return s.replace("İ", "i").replace("I", "ı").lower()


def _number_text(s):
    return _unquote("".join(str(s).translate(_MINUS).split())).replace(",", ".")


def _py_value(s):
    text = str(s).translate(_MINUS).strip()
    if len(text) > MAX_PY_LEN:
        raise ValueError("çok uzun")
    return ast.literal_eval(text)


def _py_repr(value):
    """Tipi de içeren karşılaştırma anahtarı (5 ile 5.0, True ile 1 ayrı)."""
    if isinstance(value, (list, tuple)):
        return type(value).__name__ + "(" + ",".join(_py_repr(v) for v in value) + ")"
    if isinstance(value, (set, frozenset)):
        return type(value).__name__ + "(" + ",".join(sorted(_py_repr(v) for v in value)) + ")"
    if isinstance(value, dict):
        return "dict(" + ",".join(sorted(_py_repr(k) + ":" + _py_repr(v) for k, v in value.items())) + ")"
    return type(value).__name__ + ":" + repr(value)


def short_key(question, value):
    """Cevabın karşılaştırma anahtarı (puanlama, yanlış açıklaması ve istatistikte aynı biçim)."""
    mode = question.get("norm")
    if mode is None:
        return legacy_norm(value)
    if mode == "sayi":
        return "s:" + _number_text(value)
    if mode == "sayi_degeri":
        text = _number_text(value)
        if re.fullmatch(r"[+-]?(\d+\.?\d*|\.\d+)", text):
            return "n:" + repr(float(text))
        return "t:" + text
    if mode == "metin":
        return "t:" + _text(value)
    if mode == "metin_esnek":
        return "t:" + _tr_lower(_text(value)).translate(_TR_FOLD)
    if mode == "python":
        try:
            return "p:" + _py_repr(_py_value(value))
        except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
            return "t:" + _text(value)
    raise ValueError(f"Bilinmeyen kısa cevap biçimi: {mode}")


def short_correct(question, raw):
    """Öğrenci cevabı doğru cevaba ya da `accept` listesindekilerden birine eşit mi?"""
    key = short_key(question, raw)
    return any(key == short_key(question, a) for a in [question["answer"], *question.get("accept", [])])
