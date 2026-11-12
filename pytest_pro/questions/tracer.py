"""
Adım adım kod izleme.

Yalnızca sunucuda saklanan, soru şablonlarının ürettiği kodu çalıştırır; öğrenci kodu
asla buraya gelmez. Her satır çalışmadan hemen önce o anki değişkenler ve ekran çıktısı
kaydedilir; program bitince son adım nihai çıktıyla güncellenir.
"""
import builtins
import copy
import functools
import io
import sys
import types

MAX_STEPS = 200
MAX_OUTPUT = 5000
MAX_REPR = 60
FILENAME = "<soru>"
MODULE_NAME = "__soru__"
ALLOWED_MODULES = ("math",)
BLOCKED_BUILTINS = ("open", "eval", "exec", "compile", "input", "__import__", "breakpoint",
                    "exit", "quit", "help", "globals", "locals", "vars")


class _StopTrace(BaseException):
    """Adım veya çıktı sınırı aşıldı (BaseException: izlenen koddaki except Exception yakalamaz)."""


def _shorten(text):
    return text if len(text) <= MAX_REPR else text[:MAX_REPR - 1] + "…"


def _show(value):
    if isinstance(value, type):
        return "sınıf"
    if isinstance(value, (types.FunctionType, types.BuiltinFunctionType, types.MethodType)):
        return "fonksiyon"
    if getattr(type(value), "__module__", None) == MODULE_NAME and hasattr(value, "__dict__"):
        attrs = ", ".join(f"{k}={_show(v)}" for k, v in vars(value).items())
        return _shorten(f"{type(value).__name__}({attrs})")
    try:
        return _shorten(repr(value))
    except Exception:  # repr'i bozuk nesne
        return "?"


def _visible_vars(frame):
    if frame.f_code.co_name == "<module>":
        items = frame.f_globals.items()
    else:
        items = frame.f_locals.items()
    return {k: _show(v) for k, v in items
            if not k.startswith("__") and not isinstance(v, types.ModuleType)}


def _scope(frame):
    name = frame.f_code.co_name
    return None if name == "<module>" else f"{name}() içinde"


def _safe_builtins(out, stdin_lines):
    safe = {k: v for k, v in builtins.__dict__.items() if k not in BLOCKED_BUILTINS}

    def _print(*args, sep=" ", end="\n", file=None, flush=False):
        text = (" " if sep is None else sep).join(str(a) for a in args) + ("\n" if end is None else end)
        room = MAX_OUTPUT - out.tell()
        if len(text) > room:
            out.write(text[:max(room, 0)])
            raise _StopTrace
        out.write(text)

    def _input(prompt=""):
        out.write(str(prompt))
        if not stdin_lines:
            raise EOFError("EOF when reading a line")
        value = stdin_lines.pop(0)
        out.write(value + "\n")
        return value

    def _import(name, globals=None, locals=None, fromlist=(), level=0):
        if name not in ALLOWED_MODULES:
            raise ImportError(f"'{name}' modülü burada kullanılamaz")
        return __import__(name, globals, locals, fromlist, level)

    safe.update(print=_print, input=_input, __import__=_import)
    return safe


def _error_line(tb):
    line = None
    while tb is not None:
        if tb.tb_frame.f_code.co_filename == FILENAME:
            line = tb.tb_lineno
        tb = tb.tb_next
    return line


def trace(code, stdin=""):
    """Kodun adım adım izi. Önbellekteki sonucun kopyası döner; çağıran değiştirse de önbellek bozulmaz."""
    return copy.deepcopy(_trace(code, stdin))


@functools.lru_cache(maxsize=512)
def _trace(code, stdin=""):
    out = io.StringIO()
    steps = []
    last_vars = {}  # çerçeve kimliği -> önceki adımdaki değişkenler
    result = {"lines": code.split("\n"), "steps": steps, "error": None, "truncated": False}

    def snapshot(frame):
        current = _visible_vars(frame)
        before = last_vars.get(id(frame), {})
        last_vars[id(frame)] = current
        return current, [k for k, v in current.items() if before.get(k) != v]

    def local(frame, event, arg):
        if event == "line":
            if len(steps) >= MAX_STEPS or out.tell() > MAX_OUTPUT:
                raise _StopTrace
            current, changed = snapshot(frame)
            steps.append({"line": frame.f_lineno, "scope": _scope(frame), "vars": current,
                          "changed": changed, "output": out.getvalue()})
        elif event == "return" and steps and frame.f_code.co_name == "<module>":
            # Program bitti: son durumu göster. Son adım bir fonksiyonun içindeyse ana program için
            # ayrı bir bitiş adımı eklenir (hata durumunda except bloğu bunu geri alır).
            if steps[-1]["scope"] is None and steps[-1]["line"] == frame.f_lineno:
                steps[-1]["vars"] = _visible_vars(frame)
                steps[-1]["output"] = out.getvalue()
            else:
                current, changed = snapshot(frame)
                steps.append({"line": frame.f_lineno, "scope": None, "vars": current, "changed": changed,
                              "output": out.getvalue(), "_final": True})
        return local

    def global_tracer(frame, event, arg):
        return local if frame.f_code.co_filename == FILENAME else None

    try:
        compiled = compile(code, FILENAME, "exec")
    except SyntaxError as exc:
        result["error"] = {"type": "SyntaxError", "message": str(exc.msg), "line": exc.lineno or 1}
        return result

    env = {"__builtins__": _safe_builtins(out, stdin.splitlines()), "__name__": MODULE_NAME}
    previous = sys.gettrace()
    sys.settrace(global_tracer)
    try:
        exec(compiled, env)  # noqa: S102 - yalnızca şablonların ürettiği kod
    except _StopTrace:
        result["truncated"] = True
    except Exception as exc:  # izlenen kodun hatası öğretilecek bilginin parçası
        if steps and steps[-1].get("_final"):
            steps.pop()
        line = _error_line(exc.__traceback__) or (steps[-1]["line"] if steps else 1)
        result["error"] = {"type": type(exc).__name__, "message": str(exc), "line": line}
        if not steps or steps[-1]["line"] != line:
            prev = steps[-1] if steps else {"scope": None, "vars": {}}
            steps.append({"line": line, "scope": prev["scope"], "vars": prev["vars"], "changed": [],
                          "output": out.getvalue()})
        else:
            steps[-1]["output"] = out.getvalue()
    finally:
        sys.settrace(previous)
    for step in steps:
        step.pop("_final", None)
    if len(steps) > MAX_STEPS:
        del steps[MAX_STEPS:]
    return result
