"""
Kod yazma sorularının denetimi (AST ile). Öğrenci kodu ASLA çalıştırılmaz.

Öğrencinin kodu yalnızca `ast.parse` ile ağaca çevrilir; Python yorumlayıcısına (exec, eval, compile)
hiçbir zaman verilmez. `safe_eval`, sayı ve metin sabitlerinden, dört işlemden, karşılaştırmadan ve
birkaç saf yerleşik fonksiyondan (int, float, str, abs, round, min, max, pow, len, bool) oluşan
İFADELERİ bu dosyadaki kodla, sınırlı büyüklükte hesaplar (sabit katlama). Döngü, fonksiyon çağrısı,
dosya, modül gibi şeyleri hiç hesaplamaz.

Denetleyici yazmak
------------------
Her denetleyici `(tree, params) -> (doğru_mu, not)` biçiminde bir fonksiyondur ve `@checker("tür")`
ile kaydedilir. Sorunun "check" alanı {"kind": "<tür>", ...parametreler} biçimindedir; "kind" olmayan
eski kayıtlar "mult" kabul edilir. Denetleyici ünite dosyasında da tanımlanabilir:

    from ..codecheck import OK, checker, find_prints, print_values, Tracker, is_sum_of

    @checker("sum_two")
    def check_sum_two(tree, p):
        ...
        return True, OK            # ya da (False, "öğrenciyi yönlendiren Türkçe not")

Aynı tür iki kez kaydedilirse ValueError oluşur. Ayrıntılı örnek: docs/GELISTIRME.md.
"""
import ast
import copy
import math
import operator
import re

MAX_CODE_LEN = 2000
OK = "Kod tüm kriterleri sağlıyor."
UNREADABLE = ("Bu yazımı otomatik olarak değerlendiremedim. Daha sade bir yazımla tekrar dene "
              "ya da kodunu öğretmenine göster.")
CHECKS = {}


def checker(kind):
    """Denetleyici kaydı: @checker("tür"). Aynı tür ikinci kez kaydedilirse ValueError."""
    if not isinstance(kind, str) or not kind:
        raise ValueError("Denetleyici türü boş olmayan bir metin olmalı")
    if kind in CHECKS:
        raise ValueError(f"Denetleyici iki kez tanımlandı: {kind}")

    def decorator(func):
        if kind in CHECKS:
            raise ValueError(f"Denetleyici iki kez tanımlandı: {kind}")
        CHECKS[kind] = func
        return func
    return decorator


def check_code(src, params):
    kind = params.get("kind", "mult")
    if kind not in CHECKS:
        return False, "Bu soru türü değerlendirilemiyor."
    if len(src) > MAX_CODE_LEN:
        return False, "Kod çok uzun."
    try:
        tree = ast.parse(src)
    except SyntaxError as exc:
        line = f" ({exc.lineno}. satır)" if exc.lineno else ""
        return False, f"Kodda sözdizimi (syntax) hatası var{line}. Parantezleri, iki noktayı ve girintiyi kontrol et."
    except (ValueError, RecursionError, MemoryError):
        return False, "Kod çözümlenemedi."
    try:
        return CHECKS[kind](tree, params)
    except (Unknown, RecursionError):
        return False, UNREADABLE


# ================================================================= güvenli ifade hesaplayıcı
class Unknown(Exception):
    """safe_eval bir ifadeyi hesaplayamadı: bilinmeyen ad, desteklenmeyen yapı ya da sınır aşımı."""


MAX_INT = 10 ** 15
MAX_STR = 1000
MAX_DEPTH = 60
SAFE_FUNCS = {"int": int, "float": float, "str": str, "abs": abs, "round": round, "min": min, "max": max,
              "pow": pow, "len": len, "bool": bool}
_BIN = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod, ast.Pow: operator.pow}
_CMP = {ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Lt: operator.lt, ast.LtE: operator.le,
        ast.Gt: operator.gt, ast.GtE: operator.ge}
_SEQ_FUNCS = {"sum": sum, "min": min, "max": max}
_ARGC = {"int": (1, 1), "float": (1, 1), "str": (1, 1), "abs": (1, 1), "len": (1, 1), "bool": (1, 1),
         "round": (1, 2), "pow": (2, 2), "min": (2, 10), "max": (2, 10)}


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _checked(v):
    if isinstance(v, bool) or v is None:
        return v
    if isinstance(v, int):
        if abs(v) > MAX_INT:
            raise Unknown("sayı çok büyük")
        return v
    if isinstance(v, float):
        if not math.isfinite(v) or abs(v) > MAX_INT:
            raise Unknown("sayı çok büyük")
        return v
    if isinstance(v, str):
        if len(v) > MAX_STR:
            raise Unknown("metin çok uzun")
        return v
    raise Unknown("desteklenmeyen değer")


def _binop(op, left, right):
    if op not in _BIN:
        raise Unknown("desteklenmeyen işlem")
    if op is ast.Pow:
        if not (_num(left) and _num(right)) or abs(right) > 64 or (abs(left) > 10 ** 6 and abs(right) > 1):
            raise Unknown("üs çok büyük")
    if op is ast.Mult and (isinstance(left, str) or isinstance(right, str)):
        text, times = (left, right) if isinstance(left, str) else (right, left)
        if not isinstance(times, int) or isinstance(times, bool) or len(text) * max(times, 0) > MAX_STR:
            raise Unknown("metin çok uzun")
    if op is ast.Mod and isinstance(left, str):
        raise Unknown("% ile metin biçimlendirme desteklenmiyor")
    try:
        return _checked(_BIN[op](left, right))
    except (ArithmeticError, TypeError, ValueError) as exc:
        raise Unknown(str(exc)) from None


def _format(value, spec):
    if len(spec) > 20 or any(int(d) > 100 for d in re.findall(r"\d+", spec)):
        raise Unknown("biçim çok uzun")
    try:
        return _checked(format(value, spec))
    except (TypeError, ValueError) as exc:
        raise Unknown(str(exc)) from None


def _call(name, args):
    lo, hi = _ARGC[name]
    if not lo <= len(args) <= hi:
        raise Unknown("argüman sayısı")
    if name == "pow":
        return _binop(ast.Pow, *args)
    if name in ("int", "float") and isinstance(args[0], str) and len(args[0]) > 50:
        raise Unknown("metin çok uzun")
    if name == "len" and not isinstance(args[0], str):
        raise Unknown("len yalnızca metinde")
    if name == "round" and len(args) == 2 and (not isinstance(args[1], int) or abs(args[1]) > 20):
        raise Unknown("round basamağı")
    try:
        return _checked(SAFE_FUNCS[name](*args))
    except (ArithmeticError, TypeError, ValueError) as exc:
        raise Unknown(str(exc)) from None


def safe_eval(node, env=None):
    """İfadeyi (AST düğümü) hesaplar; hesaplayamazsa Unknown fırlatır. env: {ad: değer}.

    Desteklenen: sayı/metin/bool sabitleri, adlar (env'den), + - * / // % **, tekli -, not,
    karşılaştırmalar, and/or, x if k else y, f-string, SAFE_FUNCS içindeki fonksiyonlar ve yazılı bir
    liste/demet üzerinde sum/min/max (sum([a, b, c])).
    Sınırlar: sayılar 10**15, metinler 1000 karakter, üs 64, iç içe derinlik 60."""
    return _eval(node, env or {}, 0)


def _eval(node, env, depth):
    if depth > MAX_DEPTH:
        raise Unknown("ifade çok derin")
    d = depth + 1
    if isinstance(node, ast.Expression):
        node = node.body
    if isinstance(node, ast.Constant):
        if node.value is None or type(node.value) in (int, float, str, bool):
            return _checked(node.value)
        raise Unknown("desteklenmeyen sabit")
    if isinstance(node, ast.Name):
        if node.id in env:
            return env[node.id]
        raise Unknown(f"{node.id} değeri bilinmiyor")
    if isinstance(node, ast.UnaryOp):
        v = _eval(node.operand, env, d)
        if isinstance(node.op, ast.Not):
            return not v
        if not isinstance(node.op, (ast.USub, ast.UAdd)) or not (_num(v) or isinstance(v, bool)):
            raise Unknown("desteklenmeyen işlem")
        return _checked(-v if isinstance(node.op, ast.USub) else +v)
    if isinstance(node, ast.BinOp):
        return _binop(type(node.op), _eval(node.left, env, d), _eval(node.right, env, d))
    if isinstance(node, ast.BoolOp):
        value = None
        for sub in node.values:
            value = _eval(sub, env, d)
            if isinstance(node.op, ast.And) and not value:
                return value
            if isinstance(node.op, ast.Or) and value:
                return value
        return value
    if isinstance(node, ast.Compare):
        left = _eval(node.left, env, d)
        for op, comp in zip(node.ops, node.comparators):
            if type(op) not in _CMP:
                raise Unknown("desteklenmeyen karşılaştırma")
            right = _eval(comp, env, d)
            try:
                ok = _CMP[type(op)](left, right)
            except TypeError as exc:
                raise Unknown(str(exc)) from None
            if not ok:
                return False
            left = right
        return True
    if isinstance(node, ast.IfExp):
        return _eval(node.body if _eval(node.test, env, d) else node.orelse, env, d)
    if isinstance(node, ast.JoinedStr):
        out = []
        for part in node.values:
            if isinstance(part, ast.Constant):
                out.append(str(part.value))
            elif isinstance(part, ast.FormattedValue):
                v = _eval(part.value, env, d)
                if part.conversion == 114:
                    v = repr(v)
                elif part.conversion in (115, 97):
                    v = str(v)
                spec = _eval(part.format_spec, env, d) if part.format_spec is not None else ""
                out.append(_format(v, spec))
            else:
                raise Unknown("desteklenmeyen f-string")
        return _checked("".join(out))
    if isinstance(node, ast.Call):
        single_seq = len(node.args) == 1 and isinstance(node.args[0], (ast.List, ast.Tuple))
        if (isinstance(node.func, ast.Name) and node.func.id in SAFE_FUNCS and node.func.id not in env
                and not (single_seq and node.func.id in _SEQ_FUNCS)
                and not node.keywords and not any(isinstance(a, ast.Starred) for a in node.args)):
            return _call(node.func.id, [_eval(a, env, d) for a in node.args])
        # sum([a, b, c]), min((a, b)), max([a, b]): yazılı (literal) liste/demet üzerinde, sayılarla
        if (isinstance(node.func, ast.Name) and node.func.id in _SEQ_FUNCS and node.func.id not in env
                and len(node.args) == 1 and not node.keywords and isinstance(node.args[0], (ast.List, ast.Tuple))
                and 0 < len(node.args[0].elts) <= 50
                and not any(isinstance(item, ast.Starred) for item in node.args[0].elts)):
            items = [_eval(item, env, d) for item in node.args[0].elts]
            if not all(_num(v) for v in items):
                raise Unknown("liste elemanları sayı değil")
            return _checked(_SEQ_FUNCS[node.func.id](items))
        raise Unknown("bu fonksiyon hesaplanamıyor")
    raise Unknown(f"{type(node).__name__} hesaplanamıyor")


def const_value(node, env=None, default=None):
    """safe_eval; hesaplanamazsa default döndürür (Unknown fırlatmaz)."""
    try:
        return safe_eval(node, env)
    except Unknown:
        return default


def same_value(a, b):
    """İki hesap sonucu eşit mi? Sayılar küçük kayan nokta farkıyla karşılaştırılır (9.0 == 9)."""
    if _num(a) and _num(b):
        return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)
    return type(a) is type(b) and a == b


# ================================================================= print
def is_print(node):
    """node bir print çağrısı mı? (Call ya da tek başına satır olan Expr)"""
    if isinstance(node, ast.Expr):
        node = node.value
    return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "print"


def find_prints(node):
    """node içindeki (ör. tüm ağaç ya da bir döngü) bütün print çağrıları (ast.Call), kod sırasıyla."""
    return sorted((n for n in ast.walk(node) if is_print(n) and isinstance(n, ast.Call)),
                  key=lambda n: (n.lineno, n.col_offset))


def _texty(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return True
    if isinstance(node, ast.JoinedStr):
        return True
    return isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add) and (_texty(node.left) or _texty(node.right))


def _parts(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [("text", node.value)]
    if isinstance(node, ast.JoinedStr):
        out = []
        for part in node.values:
            if isinstance(part, ast.Constant):
                out.append(("text", str(part.value)))
            elif isinstance(part, ast.FormattedValue) and part.format_spec is None:
                out += _parts(part.value)
            else:
                out.append(("value", part.value if isinstance(part, ast.FormattedValue) else part))
        return out
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add) and _texty(node):
        return _parts(node.left) + _parts(node.right)
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "str"
            and len(node.args) == 1 and not node.keywords):
        return _parts(node.args[0])
    return [("value", node)]


def print_parts(call):
    """print argümanlarının parçaları: [("text", "Sonuç:"), ("value", <a * b düğümü>)].

    f-string'ler ve metin + str(...) birleştirmeleri açılır; str(x) sarmalayıcısı x olarak görülür."""
    out = []
    for arg in call.args:
        out += _parts(arg)
    return out


def print_values(call):
    """print'in yazdırdığı ifadeler (etiket metinleri hariç): print("Sonuç:", a * b) -> [a * b]."""
    return [n for kind, n in print_parts(call) if kind == "value"]


def print_texts(call):
    """print'teki sabit metin parçaları (etiketler): print("Sonuç:", a * b) -> ["Sonuç:"]."""
    return [t for kind, t in print_parts(call) if kind == "text" and t]


def print_keyword(call, name, env=None):
    """sep/end gibi bir anahtar sözcük argümanının değeri; verilmemişse print'in varsayılanı.
    Değer hesaplanamazsa Unknown."""
    for kw in call.keywords:
        if kw.arg == name:
            return safe_eval(kw.value, env)
    return {"sep": " ", "end": "\n"}.get(name)


# ================================================================= atamalar ve izleme
def assignments(stmt):
    """Atama satırındaki (ad, değer) çiftleri: a = 5, a = b = 5, a, b = 5, 3, a: int = 5."""
    if isinstance(stmt, ast.Assign):
        for target in stmt.targets:
            if isinstance(target, ast.Name):
                yield target.id, stmt.value
            elif (isinstance(target, (ast.Tuple, ast.List)) and isinstance(stmt.value, (ast.Tuple, ast.List))
                  and len(target.elts) == len(stmt.value.elts)):
                for t, v in zip(target.elts, stmt.value.elts):
                    if isinstance(t, ast.Name):
                        yield t.id, v
    elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name) and stmt.value is not None:
        yield stmt.target.id, stmt.value


def assigned_names(node):
    """node içinde değer atanan bütün adlar (=, +=, for hedefi, with ... as, := dahil)."""
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}


def uses_name(node, name):
    """İfadede (ya da satırda) `name` adı okunuyor mu?"""
    return any(isinstance(n, ast.Name) and n.id == name and isinstance(n.ctx, ast.Load) for n in ast.walk(node))


MAX_INLINE = 400


def _size(node):
    return sum(1 for _ in ast.walk(node))


class _Inliner(ast.NodeTransformer):
    def __init__(self, defs):
        self.defs = defs

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load) and node.id in self.defs:
            return copy.deepcopy(self.defs[node.id])
        return node


def inline(node, defs):
    """İfadedeki adların yerine tanımlarını koyar: defs={"c": <a * b>} ise `c + 1` -> `a * b + 1`.
    Sonuç çok büyürse Unknown."""
    names = [n.id for n in ast.walk(node) if isinstance(n, ast.Name) and n.id in defs]
    if _size(node) + sum(_size(defs[n]) for n in names) > MAX_INLINE:
        raise Unknown("ifade çok uzun")
    return _Inliner(defs).visit(copy.deepcopy(node))


class Tracker:
    """Dallanmayan (düz) koddaki atamaları sırayla izler.

    values: değeri bilinen adlar {ad: değer}; defs: adların tanımı (başka adlar yerine konmuş ifade).
    keep içindeki adlar için tanım tutulmaz; böylece `c = a` / `print(c * b)` -> `a * b` olarak görülür.
    if/for/while/def gibi bloklarda atanan adlar 'bilinmiyor' sayılır (güvenli taraf).

        tr = Tracker(keep={"a", "b"})
        for stmt in tr.run(tree.body):   # her satırdan ÖNCEKİ durum
            ... tr.values, tr.value(ifade), tr.inline(ifade) ...
    """

    def __init__(self, values=None, keep=()):
        self.values = dict(values or {})
        self.defs = {}
        self.keep = set(keep)

    def copy(self):
        other = Tracker(self.values, self.keep)
        other.defs = dict(self.defs)
        return other

    def value(self, node):
        return safe_eval(node, self.values)

    def try_value(self, node, default=None):
        return const_value(node, self.values, default)

    def inline(self, node):
        return inline(node, self.defs)

    def forget(self, name):
        self.values.pop(name, None)
        self.defs.pop(name, None)

    def _set(self, name, value_node):
        try:
            value = self.value(value_node)
            self.values[name] = value
        except Unknown:
            self.values.pop(name, None)
        if name in self.keep:
            self.defs.pop(name, None)
            return
        try:
            self.defs[name] = self.inline(value_node)
        except Unknown:
            self.defs.pop(name, None)

    def feed(self, stmt):
        """Bir satırın atamalarını kaydeder."""
        handled = set()
        pairs = list(assignments(stmt))
        if pairs:
            # sağ taraf önce bütünüyle hesaplanır (a, b = b, a)
            snapshot = self.copy()
            for name, val in pairs:
                snapshot_val = snapshot.try_value(val, _MISSING)
                if snapshot_val is _MISSING:
                    self.values.pop(name, None)
                else:
                    self.values[name] = snapshot_val
                if name in self.keep:
                    self.defs.pop(name, None)
                else:
                    try:
                        self.defs[name] = snapshot.inline(val)
                    except Unknown:
                        self.defs.pop(name, None)
                handled.add(name)
        elif isinstance(stmt, ast.AugAssign) and isinstance(stmt.target, ast.Name):
            name = stmt.target.id
            self._set(name, ast.BinOp(left=ast.Name(id=name, ctx=ast.Load()), op=stmt.op, right=stmt.value))
            handled.add(name)
        for name in assigned_names(stmt) - handled:
            self.forget(name)

    def run(self, body):
        for stmt in body:
            yield stmt
            self.feed(stmt)


_MISSING = object()

# ================================================================= ifade ne hesaplıyor?
TRIALS = ((3, 5, 7, 11), (-4, 7, 2, 9), (10, 2, -6, 5), (6, 13, 4, -2), (2.5, 4, 8, 3))


def computes(node, names, func, defs=None, trials=TRIALS):
    """İfade, `names` değişkenlerinin func(...) değerini mi hesaplıyor?

    Adlara farklı sayılar konup ifade safe_eval ile hesaplanır ve func ile karşılaştırılır. Sabit
    yazılmış cevap (print(21)) ya da yanlış işlem (a + b) yakalanır, eşdeğer yazımlar (b * a,
    a * b * 1, x ** 2.0) kabul edilir. defs verilirse ara değişkenler önce yerine konur."""
    try:
        expr = inline(node, defs) if defs else node
    except Unknown:
        return False
    for values in trials:
        values = values[:len(names)]
        try:
            got = safe_eval(expr, dict(zip(names, values)))
            want = func(*values)
        except (Unknown, ArithmeticError):
            return False
        if not same_value(got, want):
            return False
    return True


def is_product_of(node, names, defs=None):
    """İfade verilen değişkenlerin çarpımı mı? is_product_of(<b * a>, ["a", "b"]) -> True."""
    return computes(node, names, lambda *v: math.prod(v), defs)


def is_sum_of(node, names, defs=None):
    """İfade verilen değişkenlerin toplamı mı? is_sum_of(<b + a>, ["a", "b"]) -> True."""
    return computes(node, names, lambda *v: sum(v), defs)


# ================================================================= döngü ve fonksiyon
def _walk_no_defs(nodes):
    stack = list(nodes)
    while stack:
        node = stack.pop()
        yield node
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            stack.extend(ast.iter_child_nodes(node))


def loop_problems(loop):
    """Döngü gövdesinde sayıların eksik ya da yanlış yazılmasına yol açan yapı varsa öğrenciye
    gösterilecek notu döndürür (break, continue, return, döngü değişkenine atama); yoksa None."""
    for node in _walk_no_defs(loop.body):
        if isinstance(node, ast.Break):
            return ("Döngüde <code>break</code> var; döngü erken biter ve bazı değerler hiç işlenmez. "
                    "Her turda aynı şeyin yapılması gerekiyor.")
        if isinstance(node, ast.Continue):
            return "Döngüde <code>continue</code> var; bazı turlar atlanır. Her tur işlenmeli."
        if isinstance(node, ast.Return):
            return "Döngünün içinde <code>return</code> var; döngü ilk turda biter."
    loop_vars = assigned_names(loop.target)
    changed = set()
    for stmt in loop.body:
        changed |= assigned_names(stmt)
    hit = sorted(loop_vars & changed)
    if hit:
        return (f"Döngünün içinde döngü değişkenine (<code>{hit[0]}</code>) yeni değer atanmış. Döngü değişkeni "
                "her turda <code>range()</code>'den gelen değeri almalı; onu değiştirme.")
    return None


def find_loops(node, kind=ast.For):
    """node içindeki for (ya da kind=ast.While) döngüleri, kod sırasıyla."""
    return sorted((n for n in ast.walk(node) if isinstance(n, kind)), key=lambda n: (n.lineno, n.col_offset))


MAX_RANGE = 1000


def range_values(call, env=None):
    """range(...) çağrısının üreteceği sayılar (argümanlar safe_eval ile); hesaplanamazsa ya da
    1000'den fazla sayı üretecekse None. range_values(<range(1, n + 1)>, {"n": 3}) -> [1, 2, 3]."""
    if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == "range"
            and 1 <= len(call.args) <= 3 and not call.keywords):
        return None
    args = [const_value(a, env) for a in call.args]
    if any(not isinstance(a, int) or isinstance(a, bool) or abs(a) > 10 ** 6 for a in args):
        return None
    if len(args) == 3 and args[2] == 0:
        return None
    r = range(*args)
    if len(r) > MAX_RANGE:
        return None
    return list(r)


def find_function(tree, name):
    """Üst düzeyde tanımlanmış `name` adlı fonksiyon (aynı ad birden çoksa sonuncusu) ya da None."""
    found = [s for s in tree.body if isinstance(s, ast.FunctionDef) and s.name == name]
    return found[-1] if found else None


def function_params(func):
    """Fonksiyonun parametre adları (varsayılanlı olanlar dahil); *args/**kwargs gibi
    yapılar varsa None."""
    a = func.args
    if a.vararg or a.kwarg or a.kwonlyargs or a.posonlyargs:
        return None
    return [p.arg for p in a.args]


def is_called(tree, name):
    """`name(...)` biçiminde bir çağrı kodda (fonksiyonun kendi gövdesi dışında) var mı?"""
    inside = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            inside |= {id(n) for n in ast.walk(node)}
    return any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == name and id(n) not in inside
               for n in ast.walk(tree))


def function_returns(func):
    """Fonksiyonun (iç içe tanımlar hariç) return satırları."""
    return [n for n in _walk_no_defs(func.body) if isinstance(n, ast.Return)]


# ================================================================= mult
@checker("mult")
def check_mult(tree, p):
    """v1 = n1 ve v2 = n2 ataması, ardından çarpımın print ile yazdırılması (ara değişken, etiket,
    f-string, str(...) birleştirme serbest)."""
    v1, v2, n1, n2 = p["v1"], p["v2"], p["n1"], p["n2"]
    tr = Tracker(keep={v1, v2})
    notes = set()

    def values_ok():
        return all(_num(tr.values.get(v)) and same_value(tr.values.get(v), n) for v, n in ((v1, n1), (v2, n2)))

    for stmt in tr.run(tree.body):
        for call in find_prints(stmt):
            values = print_values(call)
            if not values:
                continue
            good = [v for v in values if values_ok() and same_value(tr.try_value(v), n1 * n2)]
            if not good:
                continue
            if not is_product_of(tr.inline(good[0]), [v1, v2]):
                notes.add("const")
                continue
            if len(values) > 1:
                notes.add("extra")
                continue
            return True, OK

    for v, n in ((v1, n1), (v2, n2)):
        if not (_num(tr.values.get(v)) and same_value(tr.values.get(v), n)):
            return False, f"<code>{v}</code> değişkenine {n} atanmamış."
    if "extra" in notes:
        return False, ("print içinde çarpımdan başka sayılar da var; yalnızca çarpımı yazdır (istersen yanına "
                       "açıklama metni ekleyebilirsin).")
    if "const" in notes:
        return False, (f"Sonucu elle hesaplayıp yazmak yerine değişkenleri kullan (<code>{v1} * {v2}</code>); "
                       "değerler değişince sonuç da değişmeli.")
    return False, "Çarpım <code>print()</code> ile doğru şekilde (atamalardan sonra) yazdırılmamış."


# ================================================================= range_print
class _Reject(Exception):
    pass


def _line_numbers(call, env):
    """Bir print satırındaki sayılar (etiket metinleri hariç)."""
    nums = []
    for kind, node in print_parts(call):
        value = node if kind == "text" else safe_eval(node, env)
        if kind == "text" or isinstance(value, str):
            text = str(value).strip()
            if re.fullmatch(r"-?\d+", text):
                nums.append(int(text))
        elif _num(value):
            nums.append(value)
        elif isinstance(value, bool):
            raise _Reject("Ekrana sayı yerine True/False yazdırılıyor.")
    return nums


def _check_end(call, env):
    if print_keyword(call, "end", env) != "\n":
        raise _Reject("Sayılar alt alta yazdırılmalı (<code>end</code> kullanılmamalı).")


class _RangeRun:
    """range_print için kodun ekrana yazacağı sayıları satır satır çıkarır (yalnızca düz kod, if ve
    tek bir range döngüsü; hiçbir şey çalıştırılmaz)."""

    def __init__(self, tree):
        self.tree = tree
        self.funcs = {s.name: s for s in tree.body if isinstance(s, ast.FunctionDef)}
        self.loop_nums, self.outside_nums = [], []
        self.loops_run = 0
        self.loop_without_print = False

    def body(self, stmts, tr, depth=0):
        if depth > 3:
            raise Unknown("çok iç içe")
        for stmt in tr.run(stmts):
            if isinstance(stmt, ast.Expr) and is_print(stmt):
                _check_end(stmt.value, tr.values)
                self.outside_nums += _line_numbers(stmt.value, tr.values)
            elif isinstance(stmt, ast.For):
                self.loop(stmt, tr)
            elif isinstance(stmt, ast.If):
                branch = stmt.body if tr.value(stmt.test) else stmt.orelse
                self.body(branch, tr.copy(), depth + 1)
            elif (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call)
                  and isinstance(stmt.value.func, ast.Name) and stmt.value.func.id in self.funcs):
                func = self.funcs[stmt.value.func.id]
                if func.args.args or stmt.value.args:
                    raise Unknown("parametreli fonksiyon")
                self.body(func.body, tr.copy(), depth + 1)
            elif isinstance(stmt, (ast.While, ast.AsyncFor)):
                raise _Reject("Soru <code>for</code> döngüsü istiyor; <code>while</code> yerine <code>for</code> "
                              "ve <code>range()</code> kullan.")
            elif isinstance(stmt, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Pass, ast.FunctionDef,
                                   ast.Import, ast.ImportFrom)):
                continue
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                continue  # açıklama metni
            else:
                raise Unknown("desteklenmeyen satır")

    def loop(self, loop, tr):
        if not isinstance(loop.target, ast.Name):
            raise Unknown("döngü hedefi")
        if not (isinstance(loop.iter, ast.Call) and isinstance(loop.iter.func, ast.Name)
                and loop.iter.func.id == "range"):
            raise _Reject("Döngü <code>range()</code> ile kurulmalı.")
        seq = range_values(loop.iter, tr.values)
        if seq is None:
            raise _Reject("<code>range()</code> içindeki değerler hesaplanamadı ya da çok büyük. Sabit sayılar "
                          "ya da önceden değer atanmış değişkenler kullan.")
        problem = loop_problems(loop)
        if problem:
            raise _Reject(problem)
        if loop.orelse:
            raise Unknown("for-else")
        self.loops_run += 1
        if not find_prints(loop):
            self.loop_without_print = True
        for value in seq:
            inner = tr.copy()
            inner.values[loop.target.id] = value
            self.loop_body(loop.body, inner, 0)

    def loop_body(self, stmts, tr, depth):
        if depth > 3:
            raise Unknown("çok iç içe")
        for stmt in tr.run(stmts):
            if isinstance(stmt, ast.Expr) and is_print(stmt):
                _check_end(stmt.value, tr.values)
                nums = _line_numbers(stmt.value, tr.values)
                if len(nums) > 1:
                    raise _Reject("Her satırda yalnızca bir sayı yazdırılmalı.")
                self.loop_nums += nums
            elif isinstance(stmt, ast.If):
                self.loop_body(stmt.body if tr.value(stmt.test) else stmt.orelse, tr, depth + 1)
            elif isinstance(stmt, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Pass)):
                continue
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                continue
            elif isinstance(stmt, (ast.For, ast.While)):
                raise _Reject("İç içe döngüye gerek yok; tek bir <code>for</code> döngüsü yeterli.")
            else:
                raise Unknown("desteklenmeyen satır")


@checker("range_print")
def check_range_print(tree, p):
    """for döngüsü ve range() ile start..stop (dahil) arası sayıları alt alta yazdırma."""
    start, stop = p["start"], p["stop"]
    expected = list(range(start, stop + 1))
    if not find_loops(tree):
        return False, ("<code>for</code> döngüsü bulunamadı. Soru, sayıları <code>for</code> döngüsü ve "
                       "<code>range()</code> ile yazdırmanı istiyor.")
    run = _RangeRun(tree)
    try:
        run.body(tree.body, Tracker())
    except _Reject as exc:
        return False, str(exc)
    if not run.loops_run:
        if any(isinstance(n, ast.FunctionDef) for n in tree.body):
            return False, "Döngüyü bir fonksiyonun içine yazdın ama fonksiyonu çağırmadın; döngü hiç çalışmaz."
        return False, UNREADABLE
    if not run.loop_nums:
        return False, "Döngü içinde döngü değişkeni <code>print()</code> ile yazdırılmamış."
    if run.loop_nums == expected and run.outside_nums:
        return False, "Döngünün dışında da sayı yazdırılmış; sayılar yalnızca döngüde yazdırılmalı."
    if run.loop_nums == expected:
        return True, OK
    if len(run.loop_nums) > len(expected) and sorted(set(run.loop_nums)) == expected:
        return False, "Her sayı bir kez yazılmalı; döngü içinde fazladan <code>print</code> var."
    return False, (f"Döngü {start}'den {stop}'e kadar (ikisi de dahil) her sayıyı yazdırmıyor. "
                   "<code>range()</code> bitiş değerinin dahil olmadığını unutma.")


# ================================================================= square_func
def _returns_with_defs(stmts, tr, depth=0):
    """Fonksiyon gövdesindeki return'ler ve o noktadaki izleme durumu (if dalları ayrı izlenir)."""
    if depth > 3:
        raise Unknown("çok iç içe")
    for stmt in tr.run(stmts):
        if isinstance(stmt, ast.Return):
            yield stmt, tr.copy()
            return
        if isinstance(stmt, ast.If):
            yield from _returns_with_defs(stmt.body, tr.copy(), depth + 1)
            yield from _returns_with_defs(stmt.orelse, tr.copy(), depth + 1)
        elif isinstance(stmt, (ast.For, ast.While, ast.Try, ast.With)) and function_returns(stmt):
            raise Unknown("döngü içinde return")


@checker("square_func")
def check_square_func(tree, p):
    """Tek parametre alıp karesini return ile döndüren fonksiyon."""
    name = p["name"]
    func = find_function(tree, name)
    if func is None:
        return False, f"<code>{name}</code> adında bir fonksiyon tanımlanmamış (<code>def {name}(...):</code>)."
    params = function_params(func)
    if params is None or len(params) != 1:
        return False, "Fonksiyon tam olarak bir parametre almalı."
    param = params[0]
    if not function_returns(func):
        if find_prints(func):
            return False, "Fonksiyon sonucu <code>print</code> ile yazdırmak yerine <code>return</code> ile döndürmeli."
        return False, "Fonksiyonda <code>return</code> yok."
    found = list(_returns_with_defs(func.body, Tracker()))
    if not found:
        return False, UNREADABLE
    for ret, tr in found:
        if ret.value is None:
            return False, "<code>return</code> satırına döndürülecek değeri yazmayı unutma."
        expr = tr.inline(ret.value)
        if not uses_name(expr, param):
            return False, (f"Sonuç, fonksiyona verilen <code>{param}</code> parametresinden hesaplanmalı. Parametreyi "
                           "kullanmıyorsun ya da üzerine sabit bir değer yazmışsın.")
        if not computes(expr, [param], lambda x: x * x):
            return False, "Fonksiyon parametrenin karesini döndürmüyor."
    return True, OK
