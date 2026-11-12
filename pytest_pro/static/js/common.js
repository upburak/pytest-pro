/* PyTest Pro - sayfalar arasında ortak yardımcılar (window.PyTest) */
'use strict';
window.PyTest = (function () {
  const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');

  const tfLabel = (v) => (v === 'True' ? 'Doğru (True)' : v === 'False' ? 'Yanlış (False)' : v);
  const fmtAnswer = (type, v) => (type === 'tf' ? tfLabel(v) : v);
  const LEVEL_CLASS = { 'Başlangıç': 'b-ok', 'Orta': 'b-time', 'İleri': 'b-live' };
  const levelBadge = (level) => `<span class="badge ${LEVEL_CLASS[level] || ''}">${esc(level)}</span>`;

  /** JSON isteği; ağ hatasında da {ok, status, data} döner (status 0). */
  async function request(url, opts) {
    try {
      const r = await fetch(url, opts);
      let data = {};
      try { data = await r.json(); } catch (e) { /* boş gövde */ }
      return { ok: r.ok, status: r.status, data };
    } catch (e) {
      return { ok: false, status: 0, data: { error: 'Sunucuya ulaşılamadı.' } };
    }
  }

  function post(url, body) {
    return request(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  }

  // ---------- Python sözdizimi renklendirme (yalnızca görünüm; kod çalıştırılmaz) ----------
  const KEYWORDS = new Set(('and as assert break class continue def del elif else except finally for from global if import ' +
    'in is lambda nonlocal not or pass raise return try while with yield True False None').split(' '));
  const BUILTINS = new Set(('print input int float str bool len range type list dict set tuple abs round min max sum ' +
    'sorted reversed enumerate zip map filter open isinstance chr ord').split(' '));
  const TOKEN = /(#[^\n]*)|("""[\s\S]*?"""|'''[\s\S]*?'''|"(?:\\.|[^"\\\n])*"?|'(?:\\.|[^'\\\n])*'?)|(\b\d+(?:\.\d+)?\b)|([A-Za-z_À-ɏ][\wÀ-ɏ]*)/g;

  /** Kodu renklendirilmiş, satır satır HTML'e çevirir (her satır bir <span class="ln">). */
  function highlight(code) {
    code = String(code);
    let html = '';
    let last = 0;
    code.replace(TOKEN, (m, cm, st, nu, id, at) => {
      html += esc(code.slice(last, at));
      last = at + m.length;
      let cls = '';
      if (cm) cls = 'tk-cm';
      else if (st) cls = 'tk-st';
      else if (nu) cls = 'tk-nu';
      else if (KEYWORDS.has(id)) cls = 'tk-kw';
      else if (BUILTINS.has(id)) cls = 'tk-fn';
      // çok satırlı dizgiler satır sınırında kapanıp yeniden açılır
      html += cls ? esc(m).split('\n').map((part) => `<span class="${cls}">${part}</span>`).join('\n') : esc(m);
      return m;
    });
    html += esc(code.slice(last));
    return html.split('\n').map((line) => `<span class="ln">${line || ' '}</span>`).join('');
  }

  /** Salt okunur kod görünümü: satır numaralı ve renklendirilmiş. */
  function renderCode(el, code) {
    el.innerHTML = `<code class="codeview">${highlight(code)}</code>`;
  }

  /** Satır numaralı kod yazma alanı (kod sorusu). */
  function codeEditor(saved, onChange, focus) {
    const wrap = document.createElement('div');
    wrap.className = 'code-editor';
    const gutter = document.createElement('pre');
    gutter.className = 'gutter';
    gutter.setAttribute('aria-hidden', 'true');
    const ta = document.createElement('textarea');
    ta.className = 'code'; ta.value = saved; ta.spellcheck = false;
    ta.placeholder = '# Python kodunu buraya yaz...'; ta.setAttribute('aria-label', 'Python kodun');
    const lines = () => {
      const n = Math.max(ta.value.split('\n').length, 12);
      gutter.textContent = Array.from({ length: n }, (_, i) => i + 1).join('\n');
    };
    ta.addEventListener('input', () => { lines(); onChange(ta.value); });
    ta.addEventListener('scroll', () => { gutter.scrollTop = ta.scrollTop; });
    ta.addEventListener('keydown', (e) => { // Tab tuşu 4 boşluk eklesin
      if (e.key === 'Tab' && !e.shiftKey) {
        e.preventDefault();
        const s = ta.selectionStart;
        ta.value = ta.value.slice(0, s) + '    ' + ta.value.slice(ta.selectionEnd);
        ta.selectionStart = ta.selectionEnd = s + 4;
        lines();
        onChange(ta.value);
      }
    });
    lines();
    wrap.append(gutter, ta);
    if (focus) setTimeout(() => ta.focus(), 0);
    return wrap;
  }

  /**
   * Soru tipine göre cevap alanını çizer (çoktan seçmeli, doğru/yanlış, kısa cevap, kod).
   * Kod sorusunda yazma alanı codeBox'a (ortadaki editör) çizilir.
   * onChange(değer) her değişiklikte çağrılır.
   */
  function renderAnswer(box, q, saved, onChange, focus, codeBox) {
    box.innerHTML = '';
    saved = saved || '';
    if (q.type === 'mc' || q.type === 'tf') {
      const opts = q.type === 'mc' ? q.options : ['True', 'False'];
      const letters = q.type === 'mc' ? 'ABCDE' : 'DY';
      const group = document.createElement('div');
      // kısa şıklar iki sütunda: göz ve fare daha az yol alır
      const short = opts.every((o) => String(o).length <= 26 && !String(o).includes('\n'));
      group.className = 'opts' + (short ? ' cols-2' : '');
      group.setAttribute('role', 'radiogroup');
      group.setAttribute('aria-label', 'Şıklar');
      opts.forEach((opt, i) => {
        const lab = document.createElement('label');
        lab.className = 'opt' + (q.type === 'tf' ? ' opt-tf' : '') + (saved === opt ? ' sel' : '');
        lab.dataset.key = letters[i];
        const inp = document.createElement('input');
        inp.type = 'radio'; inp.name = 'ans-' + q.id; inp.value = opt; inp.checked = saved === opt;
        inp.addEventListener('change', () => {
          group.querySelectorAll('.opt').forEach((l) => l.classList.toggle('sel', l.contains(inp)));
          onChange(opt);
        });
        const dot = document.createElement('span');
        dot.className = 'radio';
        dot.setAttribute('aria-hidden', 'true');
        const sp = document.createElement('span');
        sp.className = 'opt-text';
        sp.textContent = q.type === 'tf' ? tfLabel(opt) : opt;
        const key = document.createElement('kbd');
        key.textContent = letters[i];
        key.setAttribute('aria-hidden', 'true');
        lab.append(inp, dot, sp, key);
        group.appendChild(lab);
      });
      box.appendChild(group);
      return;
    }
    if (q.type === 'short') {
      const lab = document.createElement('label');
      lab.className = 'field';
      lab.textContent = 'Cevabın';
      const inp = document.createElement('input');
      inp.type = 'text'; inp.value = saved; inp.className = 'mono short-answer'; inp.autocomplete = 'off';
      inp.placeholder = 'Buraya yaz';
      inp.addEventListener('input', (e) => onChange(e.target.value));
      lab.appendChild(inp);
      box.appendChild(lab);
      if (focus) inp.focus();
      return;
    }
    if (q.type === 'code') {
      const note = document.createElement('p');
      note.className = 'pane-note';
      note.textContent = 'Tab tuşu 4 boşluk ekler. Kodun yazdıkça kaydedilir.';
      box.appendChild(note);
      const target = codeBox || box;
      target.innerHTML = '';
      target.appendChild(codeEditor(saved, onChange, focus));
    }
  }

  /**
   * Soruyu editör düzenine yerleştirir. els: {tab, code, prose, slot, text}
   * - kodlu soru: ortada renklendirilmiş kod, sağda soru metni
   * - kodsuz soru: soru metni ortada büyük, sağda kısa yönerge
   * - kod yazma sorusu: görev metni ve altında yazma alanı ortada, cevap panelinde kısa yönerge
   * Metin sunucunun şablonlardan ürettiği güvenli HTML'dir.
   */
  function renderQuestion(els, q, n) {
    const isCode = q.type === 'code';
    const ext = q.code || isCode ? '.py' : '.txt';
    els.tab.textContent = (isCode ? 'cevap_' : 'soru_') + String(n).padStart(2, '0') + ext;
    els.code.classList.toggle('hidden', !q.code);
    els.prose.classList.toggle('hidden', !!q.code);
    els.prose.classList.toggle('task', isCode);
    els.slot.classList.toggle('hidden', !isCode);
    if (!isCode) els.slot.innerHTML = '';
    // uzun görev metinleri başlık yazısıyla değil, okunaklı gövde yazısıyla gösterilir
    const plain = String(q.text).replace(/<[^>]*>/g, '');
    els.text.classList.toggle('long', plain.length > 90 && !!q.code);
    if (q.code) {
      renderCode(els.code, q.code);
      els.text.innerHTML = q.text;
    } else if (isCode) {
      // görev editörün üstünde okunur, kod hemen altına yazılır
      els.prose.innerHTML = q.text;
      els.text.textContent = 'Kodunu yukarıdaki editöre yaz.';
    } else {
      els.prose.innerHTML = q.text;
      els.text.textContent = q.type === 'tf' ? 'Bu ifade doğru mu, yanlış mı?' : 'Doğru cevabı seç.';
    }
  }

  /** Klavye kısayolu: yazı alanında değilken harf ya da rakamla şık seçer. true dönerse olay işlendi. */
  function pickByKey(box, e) {
    if (e.ctrlKey || e.metaKey || e.altKey) return false;
    const t = e.target;
    if (t && (t.tagName === 'TEXTAREA' || t.tagName === 'SELECT' || (t.tagName === 'INPUT' && t.type !== 'radio'))) return false;
    const labels = [...box.querySelectorAll('.opt')];
    if (!labels.length) return false;
    const key = e.key.toLocaleUpperCase('tr');
    let i = labels.findIndex((l) => l.dataset.key === key);
    if (i < 0 && /^[1-5]$/.test(e.key)) i = Number(e.key) - 1;
    if (i < 0 || i >= labels.length) return false;
    const inp = labels[i].querySelector('input');
    inp.checked = true;
    inp.dispatchEvent(new Event('change'));
    inp.focus();
    return true;
  }

  return { esc, tfLabel, fmtAnswer, levelBadge, request, post, highlight, renderCode, renderAnswer, renderQuestion, pickByKey };
})();
