"""Soru şablonlarında ortak kullanılan yardımcılar."""
import html
import random
from typing import NamedTuple

from .fill import blank_count, same_blank
from .short import short_key

STR_VALUES = ["Python", "Kodlama", "Gelişim", "Yazılım", "Bilgisayar", "Algoritma"]
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


def output_question(code, answer, solution, wrongs=None, text=None, stdin=None, hint=None, common_wrongs=None,
                    accept=None, norm=None):
    """Kod çıktısı sorusu. wrongs verilirse çoktan seçmeli, verilmezse kısa cevap olur.
    wrongs ve common_wrongs elemanları Wrong(değer, açıklama) ya da düz metin olabilir.
    Kısa cevapta accept (kabul edilen eşdeğer cevaplar) ve norm (karşılaştırma biçimi, short.NORMS)
    verilebilir; verilmezse eski davranış geçerlidir."""
    q = {
        "type": "mc" if wrongs is not None else "short",
        "text": text or ("Aşağıdaki kodun ekran çıktısı ne olur?" if wrongs is not None
                         else "Aşağıdaki kodun ekran çıktısını yazınız:"),
        "code": code,
        "answer": answer,
        "solution": solution,
    }
    if wrongs is not None:
        if accept or norm:
            raise ValueError("accept ve norm yalnızca kısa cevap sorularında kullanılır")
        q["options"] = unique_options(answer, wrongs)
        q["whys"] = whys_for_options(answer, wrongs, q["options"])
    else:
        if norm is not None:
            q["norm"] = norm
            short_key(q, answer)  # bilinmeyen biçimde ValueError
        if accept:
            q["accept"] = list(accept)
        right = {short_key(q, a) for a in [answer, *q.get("accept", [])]}
        # doğru sayılan bir cevaba "yanlış" açıklaması verilmez (rastgele değerlerde çakışabilir)
        q["whys"] = {w.value: w.why for w in (common_wrongs or [])
                     if isinstance(w, Wrong) and short_key(q, w.value) not in right}
    if hint is not None:
        q["hint"] = hint
    if stdin is not None:
        q["stdin"] = stdin
    return q


def tf_question(statements_true, statements_false, solution, code=None, hint=None):
    """Doğru/yanlış sorusu: verilen ifadelerden rastgele biri seçilir.
    İfadeler düz metin ya da (metin, açıklama) çifti olabilir. Açıklama, öğrencinin YANLIŞ seçeneği
    işaretlemesi durumunda neden yanıldığını anlatır."""
    is_true = random.random() < 0.5
    chosen = random.choice(statements_true if is_true else statements_false)
    text, why = chosen if isinstance(chosen, tuple) else (chosen, None)
    answer = "True" if is_true else "False"
    q = {
        "type": "tf",
        "text": text,
        "code": code,
        "answer": answer,
        "solution": solution,
        "whys": {("False" if is_true else "True"): why} if why else {},
    }
    if hint is not None:
        q["hint"] = hint
    return q


def fill_question(code, answer, expect, text, solution, hint=None, wrongs=None, answer_sets=None, stdin=None):
    """Boşluk doldurma sorusu. code içindeki her ____ bir boşluktur; answer her boşluk için kabul edilen
    cevapların listesidir ([["range"], ["1"], ["6"]]); expect doldurulmuş kodun ekran çıktısıdır
    (verify="fill" ile testlerde kod çalıştırılarak doğrulanır, öğrenciye gönderilmez).

    wrongs:      her boşluk için yaygın yanlışlar: [[Wrong("str", "neden")], []]. Öğrenci bu cevabı yazarsa
                 açıklama gösterilir; testler bu yanlışların gerçekten farklı sonuç verdiğini doğrular.
    answer_sets: birbirine bağlı boşluklar için tam takımlar ([[">=", "18"], [">", "17"]]); verilirse
                 answer=None yazılır ve her takım ayrı ayrı doğrulanır.
    stdin:       kod input() kullanıyorsa klavye girdisi."""
    n = blank_count(code)
    if answer_sets is not None:
        if not answer_sets or any(len(combo) != n for combo in answer_sets):
            raise ValueError(f"Her cevap takımı {n} boşluk içermeli")
        answer = [list(dict.fromkeys(combo[i] for combo in answer_sets)) for i in range(n)]
    if n != len(answer):
        raise ValueError(f"Boşluk sayısı ({n}) cevap sayısıyla ({len(answer)}) uyuşmuyor")
    q = {"type": "fill", "text": text, "code": code, "answer": answer, "expect": expect, "solution": solution}
    if answer_sets is not None:
        q["answer_sets"] = [list(combo) for combo in answer_sets]
    if wrongs is not None:
        if len(wrongs) != n:
            raise ValueError("wrongs her boşluk için bir liste içermeli")
        blank_whys = []
        for alts, ws in zip(answer, wrongs):
            whys = {}
            for w in ws:
                # kabul edilen bir cevaba "yanlış" açıklaması verilmez (rastgele değerlerde çakışabilir)
                if not any(same_blank(w.value, a) for a in alts):
                    whys[w.value] = w.why
            blank_whys.append(whys)
        q["blank_whys"] = blank_whys
    if hint is not None:
        q["hint"] = hint
    if stdin is not None:
        q["stdin"] = stdin
    return q


# ---------------------------------------------------------------- seçenekleri kod olan ÇS
LOOP_OUTCOME = "Sonsuz döngü (adım sınırı aşıldı)"


def code_options_question(text, correct, wrongs, cases, solution, hint=None, harness="{option}", code=None):
    """Seçenekleri kod (ya da ifade) olan çoktan seçmeli soru (verify="code_one").

    correct: doğru seçenek; wrongs: Wrong(kod, neden) listesi (yanılgıyı adlandıran açıklamalarla).
    cases:   [{"setup": "x = 5", "stdin": "", "expect": "Evet"}, ...]. Testlerde her seçenek
             setup + harness kalıbıyla her durumda çalıştırılır; YALNIZCA doğru seçenek her durumda
             expect sonucunu vermelidir. expect: sondaki satır sonu atılmış çıktı, err("TypeError")
             ya da sonsuz döngü için LOOP_OUTCOME.
    harness: seçeneğin yerleştirileceği kod kalıbı; "{option}" yerine seçenek konur.
             İfade seçenekleri için "print({option})", fonksiyon seçenekleri için
             "{option}\\nprint(mutlak(-5), mutlak(0), mutlak(7))" gibi.
    code:    köke ek olarak öğrenciye gösterilecek ortak kod (isteğe bağlı).
    Öğrenciye yalnızca text, code ve options gider; cases ve harness gizlidir."""
    if not cases or any("expect" not in case for case in cases):
        raise ValueError("Her durumun (case) beklenen sonucu (expect) yazılmalı")
    if "{option}" not in harness:
        raise ValueError("harness içinde {option} geçmeli")
    options = unique_options(correct, wrongs)
    q = {
        "type": "mc",
        "text": text,
        "code": code,
        "options": options,
        "answer": correct,
        "whys": whys_for_options(correct, wrongs, options),
        "solution": solution,
        "cases": [{"setup": c.get("setup", ""), "stdin": c.get("stdin", ""), "expect": c["expect"]} for c in cases],
        "harness": harness,
    }
    if hint is not None:
        q["hint"] = hint
    return q


def option_program(question, option, case):
    """code_one sorusunda bir seçeneğin bir durumda çalıştırılacak tam kodu (testler kullanır)."""
    body = question["harness"].replace("{option}", option)
    return (case["setup"] + "\n" + body) if case["setup"] else body


# ---------------------------------------------------------------- hesaplanan doğru/yanlış
ERROR_PREFIX = "Hata verir ("


def claim_html(claim):
    """İddia edilen sonucu soru metnine uygun HTML'e çevirir (tek satır, çok satır ya da hata)."""
    if claim.startswith(ERROR_PREFIX) and claim.endswith(")"):
        return f"<code>{e(claim[len(ERROR_PREFIX):-1])}</code> hatası oluşur"
    lines = claim.split("\n")
    if len(lines) == 1:
        return f"ekrana <code>{e(claim)}</code> yazılır"
    return "ekrana alt alta " + ", ".join(f"<code>{e(line)}</code>" for line in lines) + " yazılır"


def tf_claim(code, output, wrong_claims, solution, hint=None, stdin=None, text=None, true_why=None):
    """Hesaplanan doğru/yanlış sorusu (verify="tf_output").

    output: kodun gerçek sonucu (çıktı ya da err("TypeError")); testlerde kod çalıştırılarak doğrulanır.
    wrong_claims: Wrong(değer, neden) listesi; öğrenci yanlış iddiaya "Doğru" derse neden gösterilir.
    Yarı olasılıkla gerçek sonuç, yarı olasılıkla yanlışlardan biri iddia edilir. Kök varsayılan olarak
    "Bu kod çalıştırıldığında ekrana <code>X</code> yazılır." biçimindedir; text="... {claim} ..." ile
    değiştirilebilir ({claim} yerine <code>X</code> konur). true_why: iddia doğruyken "Yanlış" diyen
    öğrenciye gösterilecek açıklama."""
    wrongs = [w for w in wrong_claims if isinstance(w, Wrong) and w.value != output]
    if not wrongs:
        raise ValueError("Gerçek sonuçtan farklı en az bir yanlış iddia gerekli")
    is_true = random.random() < 0.5
    chosen = None if is_true else random.choice(wrongs)
    claim = output if is_true else chosen.value
    if text is None:
        statement = f"Bu kod çalıştırıldığında {claim_html(claim)}."
    else:
        statement = text.format(claim=f"<code>{e(claim)}</code>")
    if is_true:
        why = true_why or f"İddia doğru: kod gerçekten {claim_html(output)}."
        whys = {"False": why}
    else:
        whys = {"True": chosen.why}
    q = {
        "type": "tf",
        "text": statement,
        "code": code,
        "answer": "True" if is_true else "False",
        "claim": claim,
        "output": output,
        "solution": f"{solution} Kod çalıştırıldığında {claim_html(output)}.",
        "whys": whys,
    }
    if hint is not None:
        q["hint"] = hint
    if stdin is not None:
        q["stdin"] = stdin
    return q
