"""
Boşluk doldurma (fill) soruları.

Soru kodu boşlukları `____` (dört alt çizgi) ile işaretler. Cevap anahtarı her boşluk için
kabul edilen cevapların listesidir: [["range"], ["1"], ["6"]]. Öğrencinin cevabı tek metin
olarak saklanır: boşluk cevaplarının JSON dizisi, örn. '["range","1","6"]'.

Karşılaştırmada metin (tırnak) dışındaki boşluk farkları ve ' ile " farkı önemsenmez;
tırnak içindeki boşluklar ise olduğu gibi karşılaştırılır. Python ifadesi olarak okunabilen
cevaplar ayrıca sözdizimi ağacıyla karşılaştırılır: `b, a` ile `(b, a)` aynıdır (öğrenci cevabı
yalnızca ast.parse ile okunur, çalıştırılmaz).

İsteğe bağlı alanlar:
    "answer_sets": birbirine bağlı boşluklar için kabul edilen tam takımlar: [[">=", "18"], [">", "17"]].
                   Varsa puanlama bu takımlara göre yapılır ("answer" gösterim ve kod izi içindir).
    "blank_whys":  her boşluk için yaygın yanlış cevapların açıklaması: [{"str": "..."}, {}].
"""
import ast
import json
import re

BLANK = "____"
MAX_BLANK_LEN = 200
UNREADABLE = "Cevap okunamadı."
EMPTY = "Boş bırakıldı."

# Sayıdan sonra gelen iyelik eki: "3 boşluktan 2'si doğru."
_ONES = {0: "ı", 1: "i", 2: "si", 3: "ü", 4: "ü", 5: "i", 6: "sı", 7: "si", 8: "i", 9: "u"}
_TENS = {1: "u", 2: "si", 3: "u", 4: "ı", 5: "si", 6: "ı", 7: "i", 8: "i", 9: "ı"}


def blank_count(code):
    return str(code or "").count(BLANK)


def fill_in(code, values):
    """Boşlukları sırayla verilen değerlerle doldurur."""
    parts = str(code).split(BLANK)
    out = parts[0]
    for i, part in enumerate(parts[1:]):
        out += (values[i] if i < len(values) else BLANK) + part
    return out


def _suffix(n):
    if n == 0:
        return "ı"
    if n % 10:
        return _ONES[n % 10]
    if n % 100:
        return _TENS[(n // 10) % 10]
    return "ü"  # yüz, bin... (pratikte görülmez)


def _norm_plain(text):
    text = " ".join(text.split())
    # işaretlerin çevresindeki boşluk önemsizdir; iki sözcük arasındaki tek boşluk korunur
    return re.sub(r" ?([^\w ]) ?", r"\1", text)


def normalize(value):
    """Karşılaştırma için tek biçim: tırnak dışında boşluk farkı yok, tırnaklar " olur."""
    s, out, plain, i = str(value), [], "", 0
    while i < len(s):
        ch = s[i]
        if ch in "'\"":
            j = i + 1
            while j < len(s) and s[j] != ch:
                j += 2 if s[j] == "\\" else 1
            out.append(_norm_plain(plain))
            out.append('"' + s[i + 1:j] + '"')
            plain, i = "", j + 1
        else:
            plain += ch
            i += 1
    out.append(_norm_plain(plain))
    return "".join(out).strip()


def parse_answer(raw, n):
    """Öğrenci cevabı -> n uzunlukta metin listesi; okunamazsa None."""
    try:
        data = json.loads(raw)
    except (TypeError, ValueError, RecursionError):
        return None
    if not isinstance(data, list):
        return None
    values = []
    for v in data[:n]:
        if v is None:
            v = ""
        elif isinstance(v, bool) or not isinstance(v, (str, int, float)):
            return None
        values.append(str(v)[:MAX_BLANK_LEN])
    return values + [""] * (n - len(values))


def _tree(value):
    try:
        return ast.dump(ast.parse(str(value).strip(), mode="eval"))
    except (SyntaxError, ValueError, RecursionError, MemoryError):
        return None


def same_blank(value, accepted):
    """Boşluğa yazılan değer kabul edilen cevapla eşdeğer mi?"""
    if not str(value).strip():
        return False
    if normalize(value) == normalize(accepted):
        return True
    tree = _tree(value)
    return tree is not None and tree == _tree(accepted)


def marks(question, raw):
    """Her boşluğun doğru olup olmadığı (okunamayan cevapta hepsi yanlış)."""
    key = question["answer"]
    values = parse_answer(raw, len(key)) or [""] * len(key)
    sets = question.get("answer_sets")
    if sets:
        rows = [[same_blank(v, a) for v, a in zip(values, combo)] for combo in sets]
        return max(rows, key=sum)
    return [any(same_blank(v, a) for a in alts) for v, alts in zip(values, key)]


def blank_why(question, raw):
    """Yanlış doldurulan ilk boşluğun açıklaması ("2. boşluk: ..."); yoksa None."""
    whys = question.get("blank_whys")
    if not whys:
        return None
    values = parse_answer(raw, len(question["answer"]))
    if values is None:
        return None
    for i, (value, ok) in enumerate(zip(values, marks(question, raw))):
        if ok or i >= len(whys):
            continue
        for wrong, why in whys[i].items():
            if same_blank(value, wrong):
                return why if len(values) == 1 else f"{i + 1}. boşluk: {why}"
    return None


def grade_fill(question, raw):
    """(doğru_mu, not): tüm boşluklar doğruysa doğru; not kaç boşluğun doğru olduğunu söyler."""
    key = question["answer"]
    values = parse_answer(raw, len(key))
    if values is None:
        return False, UNREADABLE
    if not any(v.strip() for v in values):
        return False, EMPTY
    right = sum(marks(question, raw))
    return right == len(key), f"{len(key)} boşluktan {right}'{_suffix(right)} doğru."
