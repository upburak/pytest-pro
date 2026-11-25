"""Ünite 5 - Koşullu İfadeler."""
import ast
import copy
import math
import operator
import random

from ..codecheck import OK, Unknown, checker
from ..helpers import Wrong, code_options_question, e, err, fill_question, output_question, tf_claim, tf_question
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


# ================================================================= kod yazma: sınırlı izleyici
# Öğrenci kodu ASLA çalıştırılmaz (exec/eval yok). Sim, ast.parse ile elde edilen ağacı bu dosyadaki kodla
# adım adım izler; yalnızca sayı, metin, bool, liste, demet ve sözlük değerlerini, atama, if, for, while,
# break/continue ve birkaç güvenli yerleşik fonksiyon ile metodu tanır. Başka her yapı Unknown fırlatır
# (öğrenciye "otomatik değerlendiremedim" notu gider). Adım, sayı ve uzunluk sınırları vardır. Ünite 6-8'deki
# denetleyiciler de bunu kullanır (ileride codecheck.py'ye taşınabilir).
SIM_STEPS = 20_000
SIM_LEN = 1000
SIM_OUT = 20_000
SIM_INT = 10 ** 15
_TR_FOLD = str.maketrans("çğıöşüâîû", "cgiosuaiu")


def fold(text):
    """Esnek metin karşılaştırması: büyük/küçük harf, Türkçe karakter ve fazla boşluk farkı yok."""
    s = str(text).replace("İ", "i").replace("I", "ı").lower().translate(_TR_FOLD)
    return " ".join(s.split()).strip(" .!:")


class Crash(Exception):
    """İzlenen kod bu durumda gerçekte hata verirdi (name: hata türü)."""

    def __init__(self, name):
        super().__init__(name)
        self.name = name


class Halt(Exception):
    """Adım sınırı aşıldı (sonsuz döngü olabilir)."""


class _Break(Exception):
    pass


class _Continue(Exception):
    pass


_SIM_BIN = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
            ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod, ast.Pow: operator.pow}
_SIM_CMP = {ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Lt: operator.lt, ast.LtE: operator.le,
            ast.Gt: operator.gt, ast.GtE: operator.ge}
_SCALARS = (int, float, str, bool, type(None))
_ERRORS = (TypeError, ValueError, ZeroDivisionError, IndexError, KeyError, AttributeError)


def _sized(v):
    """Değer sınırlar içindeyse kendisi; değilse Unknown."""
    if isinstance(v, bool) or v is None:
        return v
    if isinstance(v, int):
        if abs(v) > SIM_INT:
            raise Unknown("sayı çok büyük")
    elif isinstance(v, float):
        if not math.isfinite(v) or abs(v) > SIM_INT:
            raise Unknown("sayı çok büyük")
    elif isinstance(v, (str, list, tuple, dict, range)):
        if len(v) > SIM_LEN:
            raise Unknown("değer çok uzun")
        if isinstance(v, (list, tuple)):
            for x in v:
                _sized(x)
        elif isinstance(v, dict):
            for k, x in v.items():
                _sized(k)
                _sized(x)
    else:
        raise Unknown("desteklenmeyen değer")
    return v


def _bin(op, left, right):
    if op not in _SIM_BIN:
        raise Unknown("desteklenmeyen işlem")
    if op is ast.Pow and (not all(isinstance(x, (int, float)) for x in (left, right)) or abs(right) > 64
                          or (abs(left) > 10 ** 6 and abs(right) > 1)):
        raise Unknown("üs çok büyük")
    if op is ast.Mult:
        for seq, times in ((left, right), (right, left)):
            if isinstance(seq, (str, list, tuple)) and isinstance(times, int) and len(seq) * max(times, 0) > SIM_LEN:
                raise Unknown("değer çok uzun")
    if op is ast.Mod and isinstance(left, str):
        raise Unknown("% ile metin biçimlendirme desteklenmiyor")
    try:
        return _sized(_SIM_BIN[op](left, right))
    except _ERRORS as exc:
        raise Crash(type(exc).__name__) from None


def _fmt(value, spec):
    if len(spec) > 20 or any(int(d) > 100 for d in "".join(c if c.isdigit() else " " for c in spec).split()):
        raise Unknown("biçim çok uzun")
    try:
        return format(value, spec)
    except (TypeError, ValueError) as exc:
        raise Crash(type(exc).__name__) from None


def _arity():
    raise Crash("TypeError")


class Sim:
    """Sınırlı izleyici. overrides: {ad: değer}; üst düzeyde o ada yapılan İLK atamanın yerine bu değer
    konur (öğrencinin kodu farklı girdilerle denenir); koddaki asıl değer `given` içinde saklanır
    (hesaplanamazsa None). Çıktı `out` içinde biriktirilir; `lines()` satırları verir. `calls`: çağrılan
    fonksiyon ve metot adları (".append" gibi), yapı şartları için."""

    FUNCS = {"len", "sum", "max", "min", "abs", "int", "float", "str", "round", "range", "sorted", "list",
             "dict", "bool", "tuple", "print"}

    def __init__(self, overrides=None, max_steps=SIM_STEPS):
        self.env = {}
        self.out = []
        self.size = 0
        self.overrides = dict(overrides or {})
        self.given = {}
        self.steps = 0
        self.max_steps = max_steps
        self.calls = []

    # ------------------------------------------------------------ sonuç
    def lines(self):
        text = "".join(self.out)
        if text.endswith("\n"):
            text = text[:-1]
        return text.split("\n") if text else []

    # ------------------------------------------------------------ satırlar
    def run(self, body, top=False):
        for stmt in body:
            self.stmt(stmt, top)

    def tick(self):
        self.steps += 1
        if self.steps > self.max_steps:
            raise Halt

    def stmt(self, s, top=False):
        self.tick()
        if isinstance(s, ast.Assign):
            target = s.targets[0]
            if (top and len(s.targets) == 1 and isinstance(target, ast.Name) and target.id in self.overrides
                    and target.id not in self.given):
                try:
                    self.given[target.id] = copy.deepcopy(self.ev(s.value))
                except (Unknown, Crash):
                    self.given[target.id] = None
                self.env[target.id] = copy.deepcopy(self.overrides[target.id])
                return
            value = self.ev(s.value)
            for t in s.targets:
                self.assign(t, value)
        elif isinstance(s, ast.AnnAssign) and s.value is not None:
            self.assign(s.target, self.ev(s.value))
        elif isinstance(s, ast.AugAssign):
            current = self.load(s.target)
            right = self.ev(s.value)
            if isinstance(current, list) and isinstance(s.op, ast.Add):
                if not isinstance(right, (list, tuple, str)):
                    raise Crash("TypeError")
                current.extend(right)
                _sized(current)
            else:
                self.assign(s.target, _bin(type(s.op), current, right))
        elif isinstance(s, ast.Expr):
            if not (isinstance(s.value, ast.Constant) and isinstance(s.value.value, str)):
                self.ev(s.value)
        elif isinstance(s, ast.If):
            self.run(s.body if self.ev(s.test) else s.orelse)
        elif isinstance(s, ast.For):
            for item in self.iterate(self.ev(s.iter)):
                self.tick()
                self.assign(s.target, item)
                try:
                    self.run(s.body)
                except _Break:
                    break
                except _Continue:
                    continue
            else:
                self.run(s.orelse)
        elif isinstance(s, ast.While):
            while self.ev(s.test):
                self.tick()
                try:
                    self.run(s.body)
                except _Break:
                    break
                except _Continue:
                    continue
            else:
                self.run(s.orelse)
        elif isinstance(s, ast.Break):
            raise _Break
        elif isinstance(s, ast.Continue):
            raise _Continue
        elif not isinstance(s, ast.Pass):
            raise Unknown(f"{type(s).__name__} izlenemiyor")

    def assign(self, target, value):
        if isinstance(target, ast.Name):
            self.env[target.id] = value
        elif isinstance(target, (ast.Tuple, ast.List)):
            items = self.iterate(value)
            if len(items) != len(target.elts):
                raise Crash("ValueError")
            for t, v in zip(target.elts, items):
                self.assign(t, v)
        elif isinstance(target, ast.Subscript) and not isinstance(target.slice, ast.Slice):
            container, key = self.ev(target.value), self.ev(target.slice)
            if isinstance(container, dict):
                if isinstance(key, (list, dict)):
                    raise Crash("TypeError")
                container[key] = value
                _sized(container)
            elif isinstance(container, list):
                if not isinstance(key, int) or isinstance(key, bool):
                    raise Crash("TypeError")
                if not -len(container) <= key < len(container):
                    raise Crash("IndexError")
                container[key] = value
            else:
                raise Crash("TypeError")
        else:
            raise Unknown("desteklenmeyen atama")

    def load(self, target):
        if isinstance(target, (ast.Name, ast.Subscript)):
            node = copy.copy(target)
            node.ctx = ast.Load()
            return self.ev(node)
        raise Unknown("desteklenmeyen atama")

    # ------------------------------------------------------------ ifadeler
    @staticmethod
    def iterate(value):
        if isinstance(value, (list, tuple, str, range, dict)):
            return list(value)
        raise Crash("TypeError")

    def ev(self, node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, _SCALARS):
                return _sized(node.value)
            raise Unknown("desteklenmeyen sabit")
        if isinstance(node, ast.Name):
            if node.id in self.env:
                return self.env[node.id]
            raise Unknown(f"{node.id} bilinmiyor")
        if isinstance(node, ast.List):
            return _sized([self.ev(x) for x in node.elts])
        if isinstance(node, ast.Tuple):
            return _sized(tuple(self.ev(x) for x in node.elts))
        if isinstance(node, ast.Dict):
            if any(k is None for k in node.keys):
                raise Unknown("** ile sözlük")
            out = {}
            for k, v in zip(node.keys, node.values):
                key = self.ev(k)
                if isinstance(key, (list, dict)):
                    raise Crash("TypeError")
                out[key] = self.ev(v)
            return _sized(out)
        if isinstance(node, ast.BinOp):
            left, right = self.ev(node.left), self.ev(node.right)
            if isinstance(left, dict) or isinstance(right, dict):
                raise Crash("TypeError")
            return _bin(type(node.op), left, right)
        if isinstance(node, ast.UnaryOp):
            v = self.ev(node.operand)
            if isinstance(node.op, ast.Not):
                return not v
            if isinstance(node.op, (ast.USub, ast.UAdd)):
                if not isinstance(v, (int, float)):
                    raise Crash("TypeError")
                return _sized(-v if isinstance(node.op, ast.USub) else +v)
            raise Unknown("desteklenmeyen işlem")
        if isinstance(node, ast.BoolOp):
            value = None
            for sub in node.values:
                value = self.ev(sub)
                if isinstance(node.op, ast.And) and not value:
                    return value
                if isinstance(node.op, ast.Or) and value:
                    return value
            return value
        if isinstance(node, ast.Compare):
            left = self.ev(node.left)
            for op, comp in zip(node.ops, node.comparators):
                right = self.ev(comp)
                if isinstance(op, (ast.In, ast.NotIn)):
                    if not isinstance(right, (list, tuple, str, dict)) or (isinstance(right, str)
                                                                           and not isinstance(left, str)):
                        raise Crash("TypeError")
                    ok = (left in right) == isinstance(op, ast.In)
                elif isinstance(op, (ast.Is, ast.IsNot)):
                    if not (left is None or right is None):
                        raise Unknown("is yalnızca None ile")
                    ok = (left is right) == isinstance(op, ast.Is)
                else:
                    try:
                        ok = _SIM_CMP[type(op)](left, right)
                    except TypeError:
                        raise Crash("TypeError") from None
                if not ok:
                    return False
                left = right
            return True
        if isinstance(node, ast.IfExp):
            return self.ev(node.body if self.ev(node.test) else node.orelse)
        if isinstance(node, ast.JoinedStr):
            out = []
            for part in node.values:
                if isinstance(part, ast.Constant):
                    out.append(str(part.value))
                else:
                    v = self.ev(part.value)
                    if part.conversion == 114:
                        v = repr(v)
                    spec = self.ev(part.format_spec) if part.format_spec is not None else ""
                    out.append(_fmt(v, spec))
            return _sized("".join(out))
        if isinstance(node, ast.Subscript):
            container = self.ev(node.value)
            if isinstance(node.slice, ast.Slice):
                if not isinstance(container, (list, tuple, str)):
                    raise Crash("TypeError")
                parts = [None if x is None else self.ev(x) for x in (node.slice.lower, node.slice.upper,
                                                                     node.slice.step)]
                if any(p is not None and (not isinstance(p, int) or isinstance(p, bool)) for p in parts):
                    raise Crash("TypeError")
                if parts[2] == 0:
                    raise Crash("ValueError")
                return container[slice(*parts)]
            key = self.ev(node.slice)
            if not isinstance(container, (list, tuple, str, dict)):
                raise Crash("TypeError")
            try:
                return container[key]
            except _ERRORS as exc:
                raise Crash(type(exc).__name__) from None
        if isinstance(node, ast.Attribute):
            obj = self.ev(node.value)
            if isinstance(obj, dict) and node.attr == "get":
                return obj.get  # yalnızca max(..., key=d.get) için
            raise Unknown("desteklenmeyen nitelik")
        if isinstance(node, ast.Call):
            return self.call(node)
        if isinstance(node, ast.ListComp):
            out = []
            self._comp(node.generators, 0, node.elt, out)
            return _sized(out)
        raise Unknown(f"{type(node).__name__} izlenemiyor")

    def _comp(self, gens, k, elt, out):
        """Liste üreteci: [elt for ... in ... if ...] (iç içe for'lar dahil)."""
        if k == len(gens):
            out.append(self.ev(elt))
            _sized(out)
            return
        gen = gens[k]
        if gen.is_async:
            raise Unknown("async")
        for item in self.iterate(self.ev(gen.iter)):
            self.tick()
            self.assign(gen.target, item)
            if all(self.ev(cond) for cond in gen.ifs):
                self._comp(gens, k + 1, elt, out)

    # ------------------------------------------------------------ çağrılar
    def call(self, node):
        if any(isinstance(a, ast.Starred) for a in node.args) or any(k.arg is None for k in node.keywords):
            raise Unknown("* ile çağrı")
        if isinstance(node.func, ast.Name):
            name = node.func.id
            if name not in self.FUNCS or name in self.env:
                raise Unknown(f"{name}() izlenemiyor")
            self.calls.append(name)
            args = [self.ev(a) for a in node.args]
            kwargs = {k.arg: self.ev(k.value) for k in node.keywords}
            return self.builtin(name, args, kwargs)
        if isinstance(node.func, ast.Attribute):
            obj = self.ev(node.func.value)
            name = node.func.attr
            self.calls.append("." + name)
            args = [self.ev(a) for a in node.args]
            kwargs = {k.arg: self.ev(k.value) for k in node.keywords}
            return self.method(obj, name, args, kwargs)
        raise Unknown("desteklenmeyen çağrı")

    def write(self, text):
        self.size += len(text)
        if self.size > SIM_OUT:
            raise Halt
        self.out.append(text)

    def builtin(self, name, args, kwargs):
        if name == "print":
            if set(kwargs) - {"sep", "end"}:
                raise Unknown("print argümanı")
            sep, end = kwargs.get("sep", " "), kwargs.get("end", "\n")
            if not all(isinstance(x, str) or x is None for x in (sep, end)):
                raise Crash("TypeError")
            sep = " " if sep is None else sep
            end = "\n" if end is None else end
            self.write(sep.join(str(a) for a in args) + end)
            return None
        if name in ("max", "min"):
            if set(kwargs) - {"key"} or not args:
                raise Unknown("max argümanı")
            key = kwargs.get("key")
            if key is not None and not (callable(key) and getattr(key, "__name__", "") == "get"):
                raise Unknown("max key")
            items = self.iterate(args[0]) if len(args) == 1 else args
            if not items:
                raise Crash("ValueError")
            try:
                return (max if name == "max" else min)(items, key=key)
            except TypeError:
                raise Crash("TypeError") from None
        if name == "sorted":
            if set(kwargs) - {"reverse"} or len(args) != 1:
                raise Unknown("sorted argümanı")
            try:
                return sorted(self.iterate(args[0]), reverse=bool(kwargs.get("reverse", False)))
            except TypeError:
                raise Crash("TypeError") from None
        if kwargs:
            raise Unknown("anahtar sözcüklü argüman")
        try:
            if name == "range":
                if not 1 <= len(args) <= 3 or not all(isinstance(a, int) and not isinstance(a, bool) for a in args):
                    raise Crash("TypeError")
                return _sized(range(*args))
            if name in ("list", "tuple"):
                seq = self.iterate(args[0]) if args else []
                return _sized(list(seq) if name == "list" else tuple(seq))
            if name == "dict":
                if args:
                    raise Unknown("dict argümanı")
                return {}
            if name == "sum":
                return _sized(sum(self.iterate(args[0]), *args[1:]))
            if name == "len":
                if not isinstance(args[0], (str, list, tuple, dict, range)):
                    raise Crash("TypeError")
                return len(args[0])
            if name in ("int", "float") and args and isinstance(args[0], str) and len(args[0]) > 50:
                raise Unknown("metin çok uzun")
            if name == "round" and len(args) == 2 and (not isinstance(args[1], int) or abs(args[1]) > 20):
                raise Unknown("round basamağı")
            return _sized({"abs": abs, "int": int, "float": float, "str": str, "round": round,
                           "bool": bool}[name](*args))
        except _ERRORS as exc:
            raise Crash(type(exc).__name__) from None

    def method(self, obj, name, args, kwargs):
        try:
            if isinstance(obj, list):
                if name == "sort":
                    if set(kwargs) - {"reverse"} or args:
                        raise Unknown("sort argümanı")
                    obj.sort(reverse=bool(kwargs.get("reverse", False)))
                    return None
                if kwargs:
                    raise Unknown("anahtar sözcüklü argüman")
                if name in ("append", "insert", "extend"):
                    if name == "extend":
                        obj.extend(self.iterate(args[0]) if len(args) == 1 else _arity())
                    else:
                        getattr(obj, name)(*args)
                    _sized(obj)
                    return None
                if name in ("pop", "remove", "index", "count", "reverse", "copy", "clear"):
                    return getattr(obj, name)(*args)
            elif isinstance(obj, dict):
                if kwargs:
                    raise Unknown("anahtar sözcüklü argüman")
                if name == "get":
                    return obj.get(*args)
                if name in ("items", "keys", "values"):
                    if args:
                        raise Crash("TypeError")
                    return list(getattr(obj, name)())
                if name in ("pop", "copy", "clear"):
                    return getattr(obj, name)(*args)
            elif isinstance(obj, str):
                if kwargs:
                    raise Unknown("anahtar sözcüklü argüman")
                if name in ("lower", "upper", "strip", "count", "startswith", "endswith", "replace"):
                    return _sized(getattr(obj, name)(*args))
        except _ERRORS as exc:
            raise Crash(type(exc).__name__) from None
        raise Unknown(f".{name}() izlenemiyor")


def says(line, want):
    """Satır beklenen sonucu mu yazıyor? Harf/Türkçe karakter farkı ve öndeki etiket ("Sonuç: Tek") serbest."""
    got, want = fold(line), fold(want)
    return got == want or got.endswith(" " + want)


def has_node(tree, *kinds):
    """Ağaçta verilen türden bir düğüm var mı?"""
    return any(isinstance(n, kinds) for n in ast.walk(tree))


def top_assigns(tree, name):
    """Üst düzeyde `name = ...` ataması var mı?"""
    return any(isinstance(s, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in s.targets)
               for s in tree.body)


def calls_name(tree, name):
    """Kodda `name(...)` ya da `x.name(...)` çağrısı var mı?"""
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            f = n.func
            if (isinstance(f, ast.Name) and f.id == name) or (isinstance(f, ast.Attribute) and f.attr == name):
                return True
    return False


def sim_run(tree, overrides):
    """Kodu izler; (sim, not) döndürür. not: hata ya da sonsuz döngü açıklaması, sorun yoksa None.
    Unknown dışarı kaçar (check_code öğrenciye 'değerlendiremedim' notu verir)."""
    sim = Sim(overrides)
    try:
        sim.run(tree.body, top=True)
    except Crash as exc:
        return sim, f"hata verirdi (<code>{exc.name}</code>)"
    except Halt:
        return sim, "bitmezdi ya da çok uzun sürerdi (sonsuz döngü olabilir)"
    except (_Break, _Continue):
        raise Unknown("döngü dışında break") from None
    return sim, None


def given_ok(sim, var, value):
    """Öğrenci `var` değişkenine soruda verilen değeri atamış mı?"""
    got = sim.given.get(var)
    return got is not None and not isinstance(got, bool) and type(got) is type(value) and got == value


# ================================================================= denetleyiciler
@checker("kosul_tek_cift")
def check_even_odd(tree, p):
    """`var = n` ile başlayan, sayı çiftse p["even"], tekse p["odd"] yazdıran koşul (farklı sayılarla izlenir)."""
    var, n, even, odd = p["var"], p["n"], p["even"], p["odd"]
    start = f"<code>{var} = {n}</code>"
    if not top_assigns(tree, var):
        return False, f"Kod {start} satırıyla başlamalı."
    if not has_node(tree, ast.If, ast.IfExp):
        return False, "Soru koşul kullanmanı istiyor: iki durumu <code>if</code> ve <code>else</code> ile ayır."
    for value in (n, 4, 0, -3, 10, 7, 1):
        sim, note = sim_run(tree, {var: value})
        if value == n and not given_ok(sim, var, n):
            return False, f"Kod {start} satırıyla başlamalı; {var} değişkenine bu değeri ata."
        if note:
            return False, f"<code>{var} = {value}</code> olsaydı kod {note}."
        lines = sim.lines()
        want, other = (even, odd) if value % 2 == 0 else (odd, even)
        kind = "çift" if value % 2 == 0 else "tek"
        if not lines:
            return False, (f"<code>{var} = {value}</code> olsaydı ekrana hiçbir şey yazılmazdı; her sayı için bir sonuç "
                           "yazılmalı (else bloğunu unutmuş olabilir misin?).")
        if len(lines) > 1:
            return False, (f"<code>{var} = {value}</code> olsaydı ekrana iki satır yazılırdı; yalnızca bir sonuç "
                           "yazılmalı. İki durumu if / else ile ayır.")
        if not says(lines[0], want):
            if says(lines[0], other):
                return False, (f"{value} {kind} bir sayı ama kod <code>{e(lines[0])}</code> yazardı. Koşul doğruyken "
                               "hangi metnin yazılması gerektiğini ve koşulu kontrol et.")
            return False, f"Ekrana yalnızca <code>{e(even)}</code> ya da <code>{e(odd)}</code> yazılmalı."
    return True, OK


def _letter(value, limits, low):
    for limit, letter in limits:
        if value >= limit:
            return letter
    return low


@checker("kosul_not_harfi")
def check_grade_ladder(tree, p):
    """`var = n` ile başlayan, puanı eşiklere göre harfe çeviren koşul zinciri (sınır değerleri de denenir)."""
    var, n, limits, low = p["var"], p["n"], [tuple(x) for x in p["limits"]], p["low"]
    letters = [x for _, x in limits] + [low]
    start = f"<code>{var} = {n}</code>"
    if not top_assigns(tree, var):
        return False, f"Kod {start} satırıyla başlamalı."
    if not has_node(tree, ast.If, ast.IfExp):
        return False, ("Soru koşul kullanmanı istiyor: aralıkları <code>if</code> / <code>elif</code> / "
                       "<code>else</code> ile ayır.")
    edges = sorted({v for limit, _ in limits for v in (limit, limit - 1)}, reverse=True)
    for value in [n, 100, 0, (limits[0][0] + 100) // 2] + edges:
        sim, note = sim_run(tree, {var: value})
        if value == n and not given_ok(sim, var, n):
            return False, f"Kod {start} satırıyla başlamalı; {var} değişkenine bu değeri ata."
        if note:
            return False, f"<code>{var} = {value}</code> olsaydı kod {note}."
        lines = sim.lines()
        want = _letter(value, limits, low)
        if not lines:
            return False, (f"<code>{var} = {value}</code> olsaydı ekrana hiçbir şey yazılmazdı; en düşük aralık için "
                           "else bloğunu unutmuş olabilir misin?")
        if len(lines) > 1:
            return False, (f"<code>{var} = {value}</code> olsaydı ekrana birden fazla satır yazılırdı. Her puan için tek "
                           "sonuç yazılmalı; ayrı if'ler yerine elif kullanmayı düşün.")
        got = lines[0]
        if says(got, want):
            continue
        if not any(says(got, x) for x in letters):
            return False, ("Ekrana yalnızca şu sonuçlardan biri yazılmalı: "
                           + ", ".join(f"<code>{e(x)}</code>" for x in letters) + ".")
        if value in edges:
            return False, (f"<code>{var} = {value}</code> için <code>{e(want)}</code> yazılmalı ama kod "
                           f"<code>{e(got)}</code> yazardı. Sınır değerin hangi gruba dahil olduğunu kontrol et "
                           "(<code>&gt;=</code> ile <code>&gt;</code> farkı).")
        return False, (f"<code>{var} = {value}</code> için <code>{e(want)}</code> yazılmalı ama kod <code>{e(got)}</code> "
                       "yazardı. Koşulların sırasını kontrol et: Python ilk doğru koşulda durur.")
    return True, OK


# ================================================================= yeni şablonlar (ölçme raporu Ö5.1-Ö5.8)
NESTED_LABELS = [("A", "B", "C"), ("X", "Y", "Z"), ("Evet", "Hayır", "Dışarıda"), ("Kırmızı", "Mavi", "Yeşil"),
                 ("Altın", "Gümüş", "Bronz")]


def _inner_condition(x, t):
    """İç koşul: (kod, x için değeri, açıklama)."""
    kind = random.choice(["even", "odd", "gt", "lt"])
    if kind == "even":
        return "x % 2 == 0", x % 2 == 0, f"{x} % 2 = {x % 2}"
    if kind == "odd":
        return "x % 2 == 1", x % 2 == 1, f"{x} % 2 = {x % 2}"
    t2 = t + random.randint(4, 12)
    if kind == "gt":
        return f"x > {t2}", x > t2, f"{x} &gt; {t2} → {x > t2}"
    return f"x < {t2}", x < t2, f"{x} &lt; {t2} → {x < t2}"


@q("İç İçe Koşullar", verify="output")
def nested_if():
    """Kazanım: girintiden iç ve dış koşul bloklarını ve else'in hangi if'e ait olduğunu çıkarır · Bloom: An"""
    p, r_, s = random.choice(NESTED_LABELS)
    t = random.randint(8, 25)
    branch = random.choice(["in_yes", "in_no", "out"])
    while True:
        x = random.randint(t + 1, t + 20) if branch != "out" else random.randint(max(1, t - 12), t)
        cond, inner, inner_note = _inner_condition(x, t)
        if branch == "out" or inner == (branch == "in_yes"):
            break
    outer = x > t
    facts = f"x &gt; {t} → {outer}" + (f"; iç koşul: {inner_note}" if outer else "")
    if random.random() < 0.5:
        code = (f"x = {x}\nif x > {t}:\n    if {cond}:\n        print(\"{p}\")\n    else:\n        print(\"{r_}\")\n"
                f"else:\n    print(\"{s}\")")
        res = p if outer and inner else r_ if outer else s
        whys = {
            p: f"{p} yalnızca iki koşul da doğruysa yazılır; burada {facts}.",
            r_: (f"{r_} iç else bloğundadır; oraya ancak dış koşul doğru ve iç koşul yanlışsa gelinir. Burada {facts}."),
            s: f"Dış else yalnızca x &gt; {t} yanlışsa çalışır; burada {facts}.",
        }
        wrongs = [Wrong(v, whys[v]) for v in (p, r_, s) if v != res]
        wrongs.append(Wrong(f"{res}\n{s}" if res != s else f"{p}\n{s}",
                            "if / else yapısında iki bloktan yalnızca biri çalışır; iki satır yazılmaz."))
        expl = (f"Önce dış koşul denenir: {facts}. Girinti, iç if / else'in dış if bloğunun içinde olduğunu gösterir; "
                f"bu yüzden \"{res}\" yazılır.")
        hint = "Önce dıştaki koşulu kontrol et; içeri girersen içtekine bak."
    else:
        # sarkan else: iç if'in else'i yok, else girintisiyle dış if'e aittir
        code = (f"x = {x}\nif x > {t}:\n    if {cond}:\n        print(\"{p}\")\nelse:\n    print(\"{s}\")\n"
                "print(\"Bitti\")")
        res = f"{p}\nBitti" if outer and inner else "Bitti" if outer else f"{s}\nBitti"
        outcomes = {
            f"{p}\nBitti": f"{p} yalnızca iki koşul da doğruysa yazılır; burada {facts}.",
            "Bitti": (f"else girintisiyle dıştaki if'e aittir; x &gt; {t} yanlış olduğu için else bloğu çalışır."
                      if not outer else f"İç koşul da doğru ({inner_note}); Bitti'den önce {p} yazılır."),
            f"{s}\nBitti": (f"else, girintisine bakınca dıştaki <code>if x &gt; {t}</code>'e aittir; iç if'e değil. "
                            f"x &gt; {t} doğru olduğu için else çalışmaz." if outer else ""),
            f"{p}\n{s}\nBitti": "if ile ona ait else bloğundan yalnızca biri çalışır.",
            s: "<code>print(\"Bitti\")</code> girintisizdir; hiçbir koşula bağlı değildir, her durumda çalışır.",
        }
        wrongs = [Wrong(v, why) for v, why in outcomes.items() if v != res and why]
        expl = (f"<code>else</code> dış <code>if</code> ile aynı hizadadır, yani dış koşula aittir; iç if'in else'i yoktur. "
                f"{facts}. Son satırdaki print hiçbir bloğun içinde olmadığı için her durumda çalışır.")
        hint = "else hangi if ile aynı hizada? Son print hangi bloğun içinde?"
    return output_question(code, res, expl, wrongs=wrongs, hint=hint)


LADDER_LABELS = [("A", "B", "C", "F"), ("Pekiyi", "İyi", "Orta", "Geçmez"), ("5", "4", "3", "1")]
LADDER_LIMITS = [(85, 70, 50), (90, 75, 60), (80, 65, 45)]
BUG_ORDERS = [(2, 1, 0), (1, 0, 2), (0, 2, 1), (1, 2, 0), (2, 0, 1)]


@q("Koşul Sırası Hatası", verify="output")
def ladder_order_bug():
    """Kazanım: if/elif zincirinde koşul sırasının sonucu nasıl değiştirdiğini fark eder · Bloom: An"""
    labels = random.choice(LADDER_LABELS)
    limits = random.choice(LADDER_LIMITS)
    order = random.choice(BUG_ORDERS)
    pairs = list(zip(limits, labels))
    lows = [limits[0], limits[1], limits[2], 0]
    highs = [100, limits[0] - 1, limits[1] - 1, limits[2] - 1]
    want_bug = random.random() < 0.7  # çoğunlukla sıra hatasının sonucu değiştirdiği bir puan seçilir
    for _ in range(50):
        band = random.randrange(4)
        n = random.randint(lows[band], highs[band])
        hit = next((pairs[i][1] for i in order if n >= pairs[i][0]), labels[3])
        if (hit != _letter(n, pairs, labels[3])) == want_bug:
            break
    lines = "".join(f"{'if' if k == 0 else 'elif'} puan >= {pairs[i][0]}:\n    print(\"{pairs[i][1]}\")\n"
                    for k, i in enumerate(order))
    code = f"puan = {n}\n{lines}else:\n    print(\"{labels[3]}\")"
    first = next((pairs[i] for i in order if n >= pairs[i][0]), None)
    res = first[1] if first else labels[3]
    meant = _letter(n, pairs, labels[3])
    wrongs = []
    if meant != res:
        wrongs.append(Wrong(meant, f"Öğretmenin amaçladığı sonuç bu, ama kod koşulları yazıldığı sırayla dener: ilk doğru "
                                   f"koşul <code>puan &gt;= {first[0]}</code> olduğu için \"{res}\" yazılır."))
    for limit, label in pairs:
        if label in (res, meant):
            continue
        if n >= limit:
            why = (f"puan &gt;= {limit} de doğru, ama ondan önce yazılmış başka bir doğru koşul var; Python ilk doğru "
                   "koşulda durur.")
        else:
            why = f"puan &gt;= {limit} koşulu {n} için yanlış; bu blok çalışmaz."
        wrongs.append(Wrong(label, why))
    if res != labels[3]:
        wrongs.append(Wrong(labels[3], "else yalnızca yukarıdaki koşulların hiçbiri sağlanmazsa çalışır."))
    wrongs.append(Wrong(f"{res}\n{meant}" if meant != res else f"{labels[0]}\n{labels[1]}", ONLY_ONE_BLOCK))
    rule = (f"{limits[0]} ve üstüne {labels[0]}, {limits[1]} ile {limits[0] - 1} arasına {labels[1]}, {limits[2]} ile "
            f"{limits[1] - 1} arasına {labels[2]}, daha düşük puanlara {labels[3]}")
    return output_question(
        code, res,
        f"Koşullar <strong>yazıldıkları sırayla</strong> denenir ve ilk doğru koşulda durulur. puan = {n} için ilk "
        + (f"doğru koşul <code>puan &gt;= {first[0]}</code>" if first else "doğru koşul yok, else çalışır")
        + f"; bu yüzden \"{e(res)}\" yazılır. Doğru zincir en yüksek eşikten başlamalıdır.",
        wrongs=wrongs,
        text=(f"Öğretmen {e(rule)} yazdırmak istiyor ama koşulların sırasını karıştırmış. Bu kod ekrana ne yazar?"),
        hint="Python koşulları hangi sırayla dener ve ne zaman durur?",
    )


COND_RULES = [
    # (kural metni, işleç, sınır sayısı mı?)
    ("{t} ya da daha büyükse", ">="),
    ("{t} sayısından büyükse", ">"),
    ("{t} sayısından küçükse", "<"),
    ("{t} ya da daha küçükse", "<="),
    ("tam olarak {t} ise", "=="),
    ("{t} değilse", "!="),
]
COND_CONTEXTS = [("yas", "Reşit", "Reşit değil", 15, 21), ("puan", "Geçti", "Kaldı", 40, 70),
                 ("sicaklik", "Sıcak", "Serin", 20, 35), ("hiz", "Ceza", "Uygun", 50, 120),
                 ("adet", "Kargo bedava", "Kargo ücretli", 3, 10)]
OP_WHYS = {
    ">=": "&gt;= eşitliği de kapsar",
    ">": "&gt; eşitliği kapsamaz",
    "<": "&lt; eşitliği kapsamaz",
    "<=": "&lt;= eşitliği de kapsar",
    "==": "== yalnızca eşitlikte doğrudur",
    "!=": "!= eşit olmayan her değerde doğrudur",
}
OP_MISTAKES = {  # işleç: [(yanlış, açıklama, yalnızca sınırda farklı sonuç verir mi)]
    ">=": [(">", "&gt; eşitliği kapsamaz; sınırdaki değer dışarıda kalır.", True),
           ("=>", "Python'da &gt;= yazılır; =&gt; sözdizimi hatasıdır.", False)],
    ">": [(">=", "&gt;= eşitliği de kapsar; sınırdaki değer de içeri girer.", True)],
    "<": [("<=", "&lt;= eşitliği de kapsar; sınırdaki değer de içeri girer.", True)],
    "<=": [("<", "&lt; eşitliği kapsamaz; sınırdaki değer dışarıda kalır.", True),
           ("=<", "Python'da &lt;= yazılır; =&lt; sözdizimi hatasıdır.", False)],
    "==": [("=", "Tek = atamadır; karşılaştırma için == yazılır (koşulda = sözdizimi hatasıdır).", False)],
    "!=": [("=!", "Python'da 'eşit değil' != ile yazılır; =! sözdizimi hatasıdır.", False),
           ("<>", "&lt;&gt; eski Python 2 yazımıdır; Python 3'te sözdizimi hatasıdır.", False)],
}


@q("Koşulu Tamamla (Boşluk Doldurma)", verify="fill")
def cond_blank():
    """Kazanım: sözel koşulu karşılaştırma işlecine çevirir · Bloom: U"""
    var, yes, no, lo, hi = random.choice(COND_CONTEXTS)
    rule, op = random.choice(COND_RULES)
    t = random.randint(lo, hi)
    at_edge = random.random() < 0.6
    v = t if at_edge else random.choice([t - random.randint(2, 9), t + random.randint(2, 9)])
    ok = eval(f"{v} {op} {t}")  # noqa: S307 - yalnızca bizim ürettiğimiz sabit ifade
    mistakes = [Wrong(w, why) for w, why, edge_only in OP_MISTAKES[op] if at_edge or not edge_only]
    return fill_question(
        f"{var} = {v}\nif {var} ____ {t}:\n    print(\"{yes}\")\nelse:\n    print(\"{no}\")",
        [[op]], yes if ok else no,
        f"Kod, <code>{var}</code> {rule.format(t=t)} <code>{e(yes)}</code>, değilse <code>{e(no)}</code> yazmalı. "
        "Boşluğa gelmesi gereken karşılaştırma işlecini yazınız.",
        f"Kural \"{rule.format(t=t)}\" olduğu için <code>{e(op)}</code> kullanılır: {OP_WHYS[op]}. "
        f"{var} = {v} için koşul {ok} olur ve \"{e(yes if ok else no)}\" yazılır.",
        hint="Kural sınır değerin kendisini de kapsıyor mu? Her işleci sınırdaki sayıyla dene.",
        wrongs=[mistakes],
    )


TIE_LABELS = [("a", "b", "c"), ("x", "y", "z")]
TIE_NAMES = ["ali", "can", "ece", "mert", "deniz", "zeynep", "selin", "emre"]  # ASCII ve anahtar sözcük olmayan adlar


@q("Eşitlikte Hangisi?", verify="output")
def tie_max():
    """Kazanım: eşitlik durumunda koşul zincirini izler (7 > 7 yanlıştır) · Bloom: An"""
    names = random.choice(TIE_LABELS + [tuple(random.sample(TIE_NAMES, 3))])
    show = [n.capitalize() if len(n) > 1 else n for n in names]
    pattern = random.choice(["ab", "ac", "bc", "abc", "ab_low", "none"])
    hi, lo = random.randint(8, 30), random.randint(1, 5)
    mid = random.randint(lo + 1, hi - 1)
    vals = {"ab": (hi, hi, lo), "ac": (hi, lo, hi), "bc": (lo, hi, hi), "abc": (hi, hi, hi),
            "ab_low": (lo, lo, hi), "none": tuple(random.sample([hi, mid, lo], 3))}[pattern]
    strict = random.random() < 0.7
    gt = ">" if strict else ">="
    a, b, c = names
    va, vb, vc = vals
    code = (f"{a}, {b}, {c} = {va}, {vb}, {vc}\n"
            f"if {a} {gt} {b} and {a} {gt} {c}:\n    print(\"{show[0]}\")\n"
            f"elif {b} {gt} {c}:\n    print(\"{show[1]}\")\nelse:\n    print(\"{show[2]}\")")
    cmp = (lambda x, y: x > y) if strict else (lambda x, y: x >= y)
    first = cmp(va, vb) and cmp(va, vc)
    second = cmp(vb, vc)
    res = show[0] if first else show[1] if second else show[2]
    g = e(gt)
    facts = f"{a} {g} {b} → {cmp(va, vb)}, {a} {g} {c} → {cmp(va, vc)}, {b} {g} {c} → {second}"
    tie = " Eşit iki sayıdan biri ötekinden büyük değildir." if strict and len(set(vals)) < 3 else ""
    whys = {
        show[0]: (f"İlk koşul için {a}, hem {b} hem {c} değişkeninden büyük olmalı" if strict else
                  "İlk koşulun iki parçası da doğru olmalı") + f"; burada {facts}.{tie}",
        show[1]: (f"İlk koşul zaten doğru olduğu için elif'e hiç bakılmaz; {facts}." if first else
                  f"elif koşulu {b} {g} {c}; burada {facts}.{tie}"),
        show[2]: f"else yalnızca iki koşul da yanlışsa çalışır; burada {facts}.",
    }
    common = [Wrong(v, whys[v]) for v in show if v != res]
    common.append(Wrong(f"{res} {show[2]}" if res != show[2] else f"{show[0]} {show[2]}", ONLY_ONE_BLOCK))
    return output_question(
        code, res,
        f"Koşullar sırayla denenir: {facts}. "
        + ("<code>&gt;</code> eşitlikte False verir. " if strict else "<code>&gt;=</code> eşitlikte de True verir. ")
        + f"Bu yüzden ekrana \"{e(res)}\" yazılır.",
        common_wrongs=common, norm="metin_esnek",
        hint=f"Eşit iki sayı için <code>{e(gt)}</code> karşılaştırması True mu, False mu verir?",
    )


CLAIM_LABELS = [("Girebilir", "Giremez"), ("Kabul", "Ret"), ("İndirim var", "İndirim yok")]


@q("Koşullar (Doğru / Yanlış)", verify="tf_output")
def cond_claim():
    """Kazanım: and, or, not içeren koşulu değerlendirir; input() ile gelen metnin sayıyla karşılaştırılamadığını
    bilir · Bloom: U"""
    yes, no = random.choice(CLAIM_LABELS)
    limit = random.choice([12, 15, 18, 65])
    yas = random.choice([limit - random.randint(1, 5), limit, limit + random.randint(1, 9)])
    flag_name = random.choice(["izin", "kartli", "uye"])
    flag = random.random() < 0.5
    kind = random.choice(["and", "or", "not", "input_str", "input_int"])
    if kind.startswith("input"):
        conv = kind == "input_int"
        code = (f"yas = {'int(input())' if conv else 'input()'}\nif yas >= {limit}:\n    print(\"{yes}\")\n"
                f"else:\n    print(\"{no}\")")
        ok = yas >= limit
        if conv:
            output = yes if ok else no
            wrongs = [Wrong(no if ok else yes, f"{yas} &gt;= {limit} → {ok}; bu yüzden bu blok çalışmaz."),
                      Wrong(err("TypeError"), "int(input()) girdiyi sayıya çevirir; sayı ile sayı karşılaştırılabilir.")]
            expl = f"int() girdiyi sayıya çevirir; {yas} &gt;= {limit} → {ok}."
        else:
            output = err("TypeError")
            wrongs = [Wrong(yes, "input() metin (str) döndürür; metin ile sayı &gt;= ile karşılaştırılamaz, TypeError "
                                 "oluşur."),
                      Wrong(no, "input() metin döndürür; karşılaştırma False olmaz, TypeError hatası verir.")]
            expl = (f"input() her zaman metin (str) döndürür; <code>\"{yas}\" &gt;= {limit}</code> gibi metin ile sayı "
                    "karşılaştırması TypeError verir. Önce <code>int(input())</code> ile sayıya çevrilmeli.")
        q = tf_claim(code, output, wrongs, expl, stdin=str(yas),
                     hint="input() hangi tipte değer döndürür? Koşuldaki karşılaştırma bu tiple yapılabilir mi?")
        q["text"] = f"Kullanıcı <strong>{yas}</strong> yazıp Enter'a basıyor. {q['text']}"
        return q
    young = yas >= limit
    cond = {"and": f"yas >= {limit} and {flag_name}", "or": f"yas >= {limit} or {flag_name}",
            "not": f"yas >= {limit} and not {flag_name}"}[kind]
    value = {"and": young and flag, "or": young or flag, "not": young and not flag}[kind]
    code = f"yas = {yas}\n{flag_name} = {flag}\nif {cond}:\n    print(\"{yes}\")\nelse:\n    print(\"{no}\")"
    facts = f"yas &gt;= {limit} → {young}, {flag_name} → {flag}" + (f", not {flag_name} → {not flag}" if kind == "not" else "")
    rule = {"and": "and için iki tarafın da True olması gerekir",
            "or": "or için en az bir tarafın True olması yeter",
            "not": "not değeri tersine çevirir; and için iki taraf da True olmalı"}[kind]
    output = yes if value else no
    wrongs = [Wrong(no if value else yes, f"{rule}; burada {facts}, koşul {value} olur.")]
    return tf_claim(code, output, wrongs, f"{rule}. Burada {facts}; koşul {value} olur.",
                    hint="Koşulun her parçasını ayrı ayrı True/False olarak yaz, sonra and/or/not kuralını uygula.")


EVEN_WORDS = [("Çift", "Tek"), ("çift sayı", "tek sayı"), ("Sayı çift", "Sayı tek")]


@q("Tek mi Çift mi? (Kod Yazma)")
def write_even_odd():
    """Kazanım: % ile kalanı kullanarak if / else koşulu kurar · Bloom: O"""
    var = random.choice(["sayi", "n", "x"])
    n = random.randint(-30, 99)
    even, odd = random.choice(EVEN_WORDS)
    return {
        "type": "code",
        "text": f"<code>{var} = {n}</code> satırıyla başlayan; sayı çiftse <code>{e(even)}</code>, tekse "
                f"<code>{e(odd)}</code> yazdıran kodu yazınız. Kodunuz <strong>{var} değişkeninin her değeri için</strong> "
                "doğru çalışmalı (<code>if</code> / <code>else</code> kullanın).",
        "code": None,
        "check": {"kind": "kosul_tek_cift", "var": var, "n": n, "even": even, "odd": odd},
        "answer": f"{var} = {n}\nif {var} % 2 == 0:\n    print(\"{even}\")\nelse:\n    print(\"{odd}\")",
        "hint": "Bir sayının 2'ye bölümünden kalanı hangi işleç verir? Çift sayılarda bu kalan kaçtır?",
        "solution": f"<code>{var} % 2</code> sayının 2'ye bölümünden kalandır: çift sayılarda 0, tek sayılarda 1. "
                    "Koşul doğruysa if bloğu, değilse else bloğu çalışır.",
    }


@q("Not Harfi (Kod Yazma)")
def write_grade_ladder():
    """Kazanım: if / elif / else zinciriyle aralık sınıflandırır, sınır değerleri doğru ele alır · Bloom: O"""
    limits = random.choice(LADDER_LIMITS)
    labels = random.choice(LADDER_LABELS[:2])
    n = random.randint(30, 100)
    pairs = [[lim, lab] for lim, lab in zip(limits, labels)]
    rule = (f"{limits[0]} ve üstüne <code>{e(labels[0])}</code>, {limits[1]} ile {limits[0] - 1} arasına "
            f"<code>{e(labels[1])}</code>, {limits[2]} ile {limits[1] - 1} arasına <code>{e(labels[2])}</code>, "
            f"{limits[2]} sayısından küçük puanlara <code>{e(labels[3])}</code>")
    answer = (f"puan = {n}\nif puan >= {limits[0]}:\n    print(\"{labels[0]}\")\nelif puan >= {limits[1]}:\n"
              f"    print(\"{labels[1]}\")\nelif puan >= {limits[2]}:\n    print(\"{labels[2]}\")\nelse:\n"
              f"    print(\"{labels[3]}\")")
    return {
        "type": "code",
        "text": f"<code>puan = {n}</code> satırıyla başlayan; {rule} yazdıran kodu yazınız. Kodunuz <strong>her puan "
                "için</strong> (sınır değerler dahil) tek bir sonuç yazmalı.",
        "code": None,
        "check": {"kind": "kosul_not_harfi", "var": "puan", "n": n, "limits": pairs, "low": labels[3]},
        "answer": answer,
        "hint": "En yüksek eşikten başla ve elif kullan; sınır puanın hangi gruba girdiğine dikkat et.",
        "solution": "Koşullar yukarıdan aşağı denenir ve ilk doğru koşulda durulur; bu yüzden en yüksek eşik önce "
                    "yazılır. <code>&gt;=</code> sınır puanı da kapsar; else en düşük grubu yakalar.",
    }


def _range_options(v, lo, hi):
    correct = random.choice([f"if {lo} <= {v} <= {hi}:", f"if {v} >= {lo} and {v} <= {hi}:"])
    pool = [
        Wrong(f"if {v} >= {lo} or {v} <= {hi}:", "or ile bağlanınca her sayı iki koşuldan en az birini sağlar; "
                                                   "aralık dışındaki sayılar için de Evet yazılır."),
        Wrong(f"if {lo} < {v} < {hi}:", f"&lt; sınırları dışarıda bırakır; {lo} ve {hi} için hiçbir şey yazılmaz."),
        Wrong(f"if {v} >= {lo} and {v} =< {hi}:", "=&lt; geçerli bir işleç değildir (doğrusu &lt;=); kod hiç çalışmaz."),
        Wrong(f"if {v} > {lo} and {v} <= {hi}:", f"&gt; alt sınırı dışarıda bırakır; {lo} için hiçbir şey yazılmaz."),
        Wrong(f"if {v} <= {lo} and {v} >= {hi}:", "Bir sayı aynı anda alt sınırdan küçük, üst sınırdan büyük olamaz; "
                                                    "hiçbir sayı için Evet yazılmaz."),
    ]
    random.shuffle(pool)
    body = "\n    print(\"Evet\")"
    cases = [{"setup": f"{v} = {x}", "expect": "Evet" if lo <= x <= hi else ""} for x in range(lo - 3, hi + 4)]
    return (f"Hangi kod <code>{v}</code> değeri {lo} ile {hi} arasındaysa (ikisi de dahil) <code>Evet</code> yazar, "
            "değilse hiçbir şey yazmaz?", correct + body, [Wrong(w.value + body, w.why) for w in pool[:3]], cases,
            f"İki sınır da dahil olduğu için &lt;= kullanılır ve iki koşulun birlikte sağlanması gerekir (and ya da "
            f"zincirleme <code>{lo} &lt;= {v} &lt;= {hi}</code>).",
            f"Her seçeneği {lo - 1}, {lo}, {hi} ve {hi + 1} için dene.")


def _sign_options(v):
    def ladder(a, b, c):
        return f"if {a[0]}:\n    print(\"{a[1]}\")\nelif {b[0]}:\n    print(\"{b[1]}\")\nelse:\n    print(\"{c}\")"
    pos, neg = (f"{v} > 0", "Pozitif"), (f"{v} < 0", "Negatif")
    correct = ladder(pos, neg, "Sıfır") if random.random() < 0.5 else ladder(neg, pos, "Sıfır")
    pool = [
        Wrong(ladder((f"{v} >= 0", "Pozitif"), (f"{v} == 0", "Sıfır"), "Negatif"),
              "0 için ilk koşul (&gt;= 0) zaten doğrudur; Pozitif yazılır ve elif'e hiç gelinmez."),
        Wrong(f"if {v} > 0:\n    print(\"Pozitif\")\nif {v} < 0:\n    print(\"Negatif\")\nelse:\n    print(\"Sıfır\")",
              "İkinci if ayrı bir yapıdır; pozitif sayılarda hem Pozitif hem Sıfır yazılır."),
        Wrong(ladder(pos, (f"{v} < 0", "Sıfır"), "Negatif"), "Etiketler yer değiştirmiş: negatif sayılar için Sıfır yazılır."),
        Wrong(f"if {v} > 0:\n    print(\"Pozitif\")\nelse:\n    print(\"Negatif\")",
              "İki dal üç durumu ayıramaz; 0 için Negatif yazılır."),
    ]
    random.shuffle(pool)
    sign = lambda x: "Pozitif" if x > 0 else "Negatif" if x < 0 else "Sıfır"  # noqa: E731
    cases = [{"setup": f"{v} = {x}", "expect": sign(x)} for x in range(-4, 5)]
    return (f"Hangi kod <code>{v}</code> sayısı pozitifse <code>Pozitif</code>, negatifse <code>Negatif</code>, sıfırsa "
            "<code>Sıfır</code> yazar?", correct, pool[:3], cases,
            "Üç durum tek bir if / elif / else zinciriyle ayrılır; 0 ne pozitif ne negatiftir ve else'e kalır.",
            "Her seçeneği -1, 0 ve 1 için dene.")


def _ladder_options():
    limits = random.choice(LADDER_LIMITS)
    labels = random.choice(LADDER_LABELS[:2])
    pairs = list(zip(limits, labels))

    def chain(items, op=">="):
        return "".join(f"{'if' if k == 0 else 'elif'} puan {op} {lim}:\n    print(\"{lab}\")\n"
                       for k, (lim, lab) in enumerate(items)) + f"else:\n    print(\"{labels[3]}\")"
    pool = [
        Wrong(chain(pairs[::-1]), f"En düşük eşik önce denenince {limits[2]} ve üstü her puan ilk koşulda durur; "
                                  f"{labels[0]} ve {labels[1]} hiç yazılmaz."),
        Wrong(chain(pairs, ">"), "&gt; sınır puanı dışarıda bırakır; örneğin tam "
                                 f"{limits[0]} alan öğrenciye {labels[1]} yazılır."),
        Wrong("".join(f"if puan >= {lim}:\n    print(\"{lab}\")\n" for lim, lab in pairs) + f"else:\n    print(\"{labels[3]}\")",
              "Ayrı if'ler birbirini durdurmaz; yüksek puanlarda birden fazla sonuç yazılır."),
        Wrong(chain([pairs[1], pairs[0], pairs[2]]), f"{limits[1]} eşiği önce denenince {limits[0]} ve üstü puanlar da "
                                                     f"{labels[1]} alır."),
    ]
    random.shuffle(pool)
    cases = [{"setup": f"puan = {x}", "expect": _letter(x, pairs, labels[3])}
             for x in sorted({0, 100, *limits, *(lim - 1 for lim in limits), (limits[0] + 100) // 2})]
    rule = (f"{limits[0]} ve üstüne {labels[0]}, {limits[1]} ile {limits[0] - 1} arasına {labels[1]}, {limits[2]} ile "
            f"{limits[1] - 1} arasına {labels[2]}, daha düşük puanlara {labels[3]}")
    return (f"Hangi kod {e(rule)} yazar?", chain(pairs), pool[:3], cases,
            "Zincir en yüksek eşikten başlar, &gt;= ile sınır puanı kapsar ve elif ile tek bir sonuç yazar.",
            "Her seçeneği sınır puanlarla (ör. tam eşik ve bir eksiği) ve 100 ile dene.")


@q("Hangi Kod Doğru Çalışır?", verify="code_one")
def which_condition():
    """Kazanım: aynı amaca yönelik koşul yazımlarını karşılaştırıp doğru çalışanı seçer · Bloom: D"""
    purpose = random.choice(["range", "sign", "ladder"])
    v = random.choice(["x", "sayi", "n"])
    if purpose == "range":
        lo = random.randint(1, 30)
        text, correct, wrongs, cases, solution, hint = _range_options(v, lo, lo + random.randint(5, 20))
    elif purpose == "sign":
        text, correct, wrongs, cases, solution, hint = _sign_options(v)
    else:
        text, correct, wrongs, cases, solution, hint = _ladder_options()
    return code_options_question(text, correct, wrongs, cases, solution, hint=hint)
