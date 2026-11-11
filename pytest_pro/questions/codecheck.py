"""
Kod yazma sorularının denetimi (AST ile). Öğrenci kodu ASLA çalıştırılmaz.

Her denetleyici `check_<tür>(tree, params) -> (doğru_mu, not)` biçimindedir ve
CHECKS sözlüğüne kaydedilir. Sorunun "check" alanı {"kind": "<tür>", ...parametreler}
biçimindedir. "kind" olmayan eski kayıtlar "mult" kabul edilir.
"""
import ast

MAX_CODE_LEN = 2000
CHECKS = {}


def checker(kind):
    def decorator(func):
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
        return False, f"Kodda sözdizimi (syntax) hatası var{line}."
    except (ValueError, RecursionError, MemoryError):
        return False, "Kod çözümlenemedi."
    return CHECKS[kind](tree, params)


# ----------------------------------------------------------------- ortak
def _is_print(node):
    return (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name) and node.value.func.id == "print")


def _int_const(node):
    if isinstance(node, ast.Constant) and type(node.value) is int:
        return node.value
    if (isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub)
            and isinstance(node.operand, ast.Constant) and type(node.operand.value) is int):
        return -node.operand.value
    return None


def _assignments(stmt):
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


# ----------------------------------------------------------------- mult
def _is_mult_of(node, v1, v2):
    return (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult)
            and isinstance(node.left, ast.Name) and isinstance(node.right, ast.Name)
            and {node.left.id, node.right.id} == {v1, v2} and v1 != v2)


@checker("mult")
def check_mult(tree, p):
    """v1 = n1 ve v2 = n2 ataması, ardından print(v1 * v2) (ara değişkenle de olabilir)."""
    v1, v2, n1, n2 = p["v1"], p["v2"], p["n1"], p["n2"]
    values, mult_vars, printed_ok = {}, set(), False

    def values_ok():
        return values.get(v1) == n1 and values.get(v2) == n2

    for stmt in tree.body:
        pairs = list(_assignments(stmt))
        if pairs:
            ok_before = values_ok()
            for name, val in pairs:
                if isinstance(val, ast.Constant) and type(val.value) in (int, float):
                    values[name] = val.value
                else:
                    values.pop(name, None)
                if _is_mult_of(val, v1, v2) and ok_before:
                    mult_vars.add(name)
                else:
                    mult_vars.discard(name)
        elif _is_print(stmt) and stmt.value.args:
            arg = stmt.value.args[0]
            if (_is_mult_of(arg, v1, v2) and values_ok()) or (isinstance(arg, ast.Name) and arg.id in mult_vars):
                printed_ok = True

    if printed_ok:
        return True, "Kod tüm kriterleri sağlıyor."
    if values.get(v1) != n1:
        return False, f"<code>{v1}</code> değişkenine {n1} atanmamış."
    if values.get(v2) != n2:
        return False, f"<code>{v2}</code> değişkenine {n2} atanmamış."
    return False, "Çarpım <code>print()</code> ile doğru şekilde (atamalardan sonra) yazdırılmamış."


# ----------------------------------------------------------------- range_print
@checker("range_print")
def check_range_print(tree, p):
    """for döngüsü ve range() ile start..stop (dahil) arası sayıları alt alta yazdırma."""
    expected = list(range(p["start"], p["stop"] + 1))
    loops = [s for s in tree.body if isinstance(s, ast.For)]
    if not loops:
        return False, "<code>for</code> döngüsü bulunamadı."
    for loop in loops:
        it = loop.iter
        if not (isinstance(loop.target, ast.Name) and isinstance(it, ast.Call)
                and isinstance(it.func, ast.Name) and it.func.id == "range" and 1 <= len(it.args) <= 3):
            continue
        args = [_int_const(a) for a in it.args]
        if None in args or any(abs(a) > 10_000 for a in args) or (len(args) == 3 and args[2] == 0):
            continue
        seq = list(range(*args))
        var = loop.target.id
        for stmt in loop.body:
            if not (_is_print(stmt) and len(stmt.value.args) == 1):
                continue
            end_kw = [k for k in stmt.value.keywords if k.arg == "end"]
            if end_kw and not (isinstance(end_kw[0].value, ast.Constant) and end_kw[0].value.value == "\n"):
                return False, "Sayılar alt alta yazdırılmalı (<code>end</code> kullanılmamalı)."
            arg = stmt.value.args[0]
            if isinstance(arg, ast.Name) and arg.id == var:
                printed = seq
            elif (isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Add) and isinstance(arg.left, ast.Name)
                  and arg.left.id == var and _int_const(arg.right) is not None):
                printed = [x + _int_const(arg.right) for x in seq]
            else:
                continue
            if printed == expected:
                return True, "Kod tüm kriterleri sağlıyor."
            return False, (f"Döngü {p['start']}'den {p['stop']}'e kadar (dahil) yazdırmıyor. "
                           "<code>range()</code> bitiş değerinin dahil olmadığını unutma.")
        return False, "Döngü içinde döngü değişkeni <code>print()</code> ile yazdırılmamış."
    return False, "Döngü <code>range()</code> ile ve sabit sayılarla kurulmalı."


# ----------------------------------------------------------------- square_func
def _is_square_of(node, param, squares):
    if isinstance(node, ast.Name):
        return node.id in squares
    if isinstance(node, ast.BinOp):
        if (isinstance(node.op, ast.Mult) and isinstance(node.left, ast.Name) and isinstance(node.right, ast.Name)
                and node.left.id == node.right.id == param):
            return True
        if (isinstance(node.op, ast.Pow) and isinstance(node.left, ast.Name) and node.left.id == param
                and _int_const(node.right) == 2):
            return True
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "pow"
            and len(node.args) == 2 and isinstance(node.args[0], ast.Name) and node.args[0].id == param
            and _int_const(node.args[1]) == 2):
        return True
    return False


@checker("square_func")
def check_square_func(tree, p):
    """Tek parametre alıp karesini return ile döndüren fonksiyon."""
    name = p["name"]
    funcs = [s for s in tree.body if isinstance(s, ast.FunctionDef) and s.name == name]
    if not funcs:
        return False, f"<code>{name}</code> adında bir fonksiyon tanımlanmamış (<code>def {name}(...):</code>)."
    func = funcs[-1]
    params = func.args.args
    if len(params) != 1 or func.args.vararg or func.args.kwarg or func.args.kwonlyargs:
        return False, "Fonksiyon tam olarak bir parametre almalı."
    param = params[0].arg
    squares = set()
    returns = []
    for stmt in func.body:
        for name_, val in _assignments(stmt):
            if _is_square_of(val, param, squares):
                squares.add(name_)
            else:
                squares.discard(name_)
        if isinstance(stmt, ast.Return):
            returns.append(stmt)
    if not returns:
        prints = any(_is_print(s) for s in func.body)
        if prints:
            return False, "Fonksiyon sonucu <code>print</code> ile yazdırmak yerine <code>return</code> ile döndürmeli."
        return False, "Fonksiyonda <code>return</code> yok."
    if all(r.value is not None and _is_square_of(r.value, param, squares) for r in returns):
        return True, "Kod tüm kriterleri sağlıyor."
    return False, "Fonksiyon parametrenin karesini döndürmüyor."
