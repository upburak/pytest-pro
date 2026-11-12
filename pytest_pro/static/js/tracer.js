/* PyTest Pro - adım adım kod izi bileşeni (window.PyTest.renderTrace, whyNote, traceToggle) */
'use strict';
(function () {
  const P = window.PyTest;

  function el(tag, cls, text) {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  /** Sunucudan gelen izi (trace) container içine çizer. */
  function renderTrace(container, t) {
    container.innerHTML = '';
    const steps = t.steps || [];
    if (!steps.length) {
      container.appendChild(el('p', 'muted', 'Bu kod için izlenecek adım yok.'));
      return;
    }
    const root = el('div', 'trace');
    root.tabIndex = 0;
    root.setAttribute('role', 'group');
    root.setAttribute('aria-label', 'Adım adım kod izi. Sol ve sağ ok tuşlarıyla ilerle.');

    const code = el('ol', 'trace-code');
    const items = t.lines.map((line) => {
      const li = el('li', '', line || ' ');
      code.appendChild(li);
      return li;
    });

    const panel = el('div', 'trace-panel');
    const scope = el('p', 'trace-scope');
    const table = el('table', 'trace-vars');
    table.innerHTML = '<thead><tr><th scope="col">Değişken</th><th scope="col">Değer</th></tr></thead>';
    const tbody = el('tbody');
    table.appendChild(tbody);
    const outLabel = el('p', 'trace-label', 'Ekran çıktısı');
    const out = el('pre', 'trace-out');
    const errBox = el('p', 'trace-error hidden');
    const note = el('p', 'muted small hidden');
    panel.append(scope, table, outLabel, out, errBox, note);

    const controls = el('div', 'trace-controls');
    const prev = el('button', 'btn sm', 'Önceki adım');
    const next = el('button', 'btn sm primary', 'Sonraki adım');
    prev.type = next.type = 'button';
    const range = el('input');
    range.type = 'range'; range.min = 0; range.max = steps.length - 1; range.value = 0;
    range.setAttribute('aria-label', 'Adım');
    const counter = el('span', 'muted small');
    controls.append(prev, range, next, counter);

    const live = el('p', 'visually-hidden');
    live.setAttribute('aria-live', 'polite');

    root.append(code, panel, controls, live);
    container.appendChild(root);

    let index = 0;
    function show(k) {
      index = Math.max(0, Math.min(steps.length - 1, k));
      const step = steps[index];
      const last = index === steps.length - 1;
      items.forEach((li, i) => li.classList.toggle('now', i === step.line - 1));
      const now = items[step.line - 1];
      if (now) code.scrollTop = Math.max(0, now.offsetTop - code.clientHeight / 2);

      scope.textContent = step.scope ? `Şu an ${step.scope}` : 'Ana program';
      tbody.innerHTML = '';
      const names = Object.keys(step.vars);
      if (!names.length) {
        const tr = el('tr');
        const td = el('td', 'muted', 'Henüz değişken yok');
        td.colSpan = 2;
        tr.appendChild(td);
        tbody.appendChild(tr);
      }
      names.forEach((name) => {
        const tr = el('tr', step.changed.includes(name) ? 'changed' : '');
        tr.append(el('td', 'mono', name), el('td', 'mono', step.vars[name]));
        tbody.appendChild(tr);
      });
      out.textContent = step.output || '';

      errBox.classList.toggle('hidden', !(last && t.error));
      if (last && t.error) errBox.textContent = `${t.error.type}: ${t.error.message} (satır ${t.error.line})`;
      note.classList.toggle('hidden', !last || !!t.error);
      if (last && !t.error) note.textContent = t.truncated ? 'İlk 200 adım gösteriliyor.' : 'Program bitti.';

      prev.disabled = index === 0;
      next.disabled = last;
      range.value = index;
      counter.textContent = `Adım ${index + 1} / ${steps.length}`;
      live.textContent = `Adım ${index + 1} / ${steps.length}, satır ${step.line}`;
    }

    prev.addEventListener('click', () => show(index - 1));
    next.addEventListener('click', () => show(index + 1));
    range.addEventListener('input', () => show(parseInt(range.value, 10)));
    root.addEventListener('keydown', (e) => {
      if (e.target === range) return; // kaydırıcı okları kendisi işler
      if (e.key === 'ArrowRight') { e.preventDefault(); show(index + 1); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); show(index - 1); }
    });
    show(0);
  }

  /** "Neden yanlış" notu. text sunucunun şablonlardan ürettiği güvenli HTML'dir. */
  function whyNote(text) {
    return `<div class="why-note"><b>Neden yanlış:</b> ${text}</div>`;
  }

  /** Düğmeye basılınca izi getirir ve açar; sonraki basışlarda gizler/gösterir. */
  function traceToggle(button, container, fetchTrace) {
    let loaded = false;
    button.setAttribute('aria-expanded', 'false');
    button.addEventListener('click', async () => {
      if (!loaded) {
        button.disabled = true;
        const r = await fetchTrace();
        button.disabled = false;
        container.classList.remove('hidden');
        if (!r.ok) {
          container.textContent = (r.data && r.data.error) || 'İz alınamadı.';
          return;
        }
        renderTrace(container, r.data);
        loaded = true;
        button.textContent = 'İzi gizle';
        button.setAttribute('aria-expanded', 'true');
        return;
      }
      const hidden = container.classList.toggle('hidden');
      button.textContent = hidden ? 'Kodu adım adım izle' : 'İzi gizle';
      button.setAttribute('aria-expanded', String(!hidden));
    });
  }

  Object.assign(P, { renderTrace, whyNote, traceToggle });
})();
