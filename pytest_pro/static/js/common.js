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

  /**
   * Soru tipine göre cevap alanını çizer (çoktan seçmeli, doğru/yanlış, kısa cevap, kod).
   * onChange(değer) her değişiklikte çağrılır.
   */
  function renderAnswer(box, q, saved, onChange, focus) {
    box.innerHTML = '';
    saved = saved || '';
    if (q.type === 'mc' || q.type === 'tf') {
      const opts = q.type === 'mc' ? q.options : ['True', 'False'];
      const group = document.createElement('div');
      group.setAttribute('role', 'radiogroup');
      opts.forEach((opt) => {
        const lab = document.createElement('label');
        lab.className = 'opt' + (saved === opt ? ' sel' : '');
        const inp = document.createElement('input');
        inp.type = 'radio'; inp.name = 'ans-' + q.id; inp.value = opt; inp.checked = saved === opt;
        inp.addEventListener('change', () => {
          group.querySelectorAll('.opt').forEach((l) => l.classList.toggle('sel', l.contains(inp)));
          onChange(opt);
        });
        const sp = document.createElement('span');
        sp.textContent = q.type === 'tf' ? tfLabel(opt) : opt;
        lab.append(inp, sp);
        group.appendChild(lab);
      });
      box.appendChild(group);
      return;
    }
    if (q.type === 'short') {
      const inp = document.createElement('input');
      inp.type = 'text'; inp.value = saved; inp.className = 'mono'; inp.autocomplete = 'off';
      inp.placeholder = 'Cevabını buraya yaz...'; inp.setAttribute('aria-label', 'Cevabın');
      inp.addEventListener('input', (e) => onChange(e.target.value));
      box.appendChild(inp);
      if (focus) inp.focus();
      return;
    }
    if (q.type === 'code') {
      const ta = document.createElement('textarea');
      ta.className = 'code'; ta.value = saved; ta.spellcheck = false;
      ta.placeholder = '# Python kodunu buraya yaz...'; ta.setAttribute('aria-label', 'Python kodun');
      ta.addEventListener('input', (e) => onChange(e.target.value));
      ta.addEventListener('keydown', (e) => { // Tab tuşu 4 boşluk eklesin
        if (e.key === 'Tab' && !e.shiftKey) {
          e.preventDefault();
          const s = ta.selectionStart;
          ta.value = ta.value.slice(0, s) + '    ' + ta.value.slice(ta.selectionEnd);
          ta.selectionStart = ta.selectionEnd = s + 4;
          onChange(ta.value);
        }
      });
      box.appendChild(ta);
      if (focus) ta.focus();
    }
  }

  /** Soru metnini ve kod parçasını gösterir. Metin sunucunun şablonlardan ürettiği güvenli HTML'dir. */
  function renderQuestionText(textEl, codeEl, q) {
    textEl.innerHTML = q.text;
    if (q.code) { codeEl.textContent = q.code; codeEl.classList.remove('hidden'); }
    else codeEl.classList.add('hidden');
  }

  return { esc, tfLabel, fmtAnswer, levelBadge, request, post, renderAnswer, renderQuestionText };
})();
