/* PyTest Pro - öğretmen paneli */
'use strict';
(function () {
  const $ = (id) => document.getElementById(id);
  const KEY = 'pytest_ogretmen_sifre';
  const POLL_MS = 3000;

  let pw = '';
  let poll = null;
  let rows = [];
  let settings = null;
  let detailId = null;

  const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  const mmss = (sec) => String(Math.floor(sec / 60)).padStart(2, '0') + ':' + String(sec % 60).padStart(2, '0');
  const tfLabel = (v) => (v === 'True' ? 'Doğru (True)' : v === 'False' ? 'Yanlış (False)' : v);

  async function api(path, opts = {}) {
    const headers = Object.assign({}, opts.headers || {}, { 'X-Ogretmen-Sifre': pw });
    const r = await fetch(path, Object.assign({}, opts, { headers }));
    if (r.status === 401) { logout('Şifre hatalı.'); throw new Error('Şifre hatalı'); }
    if (!r.ok) {
      let msg = 'Sunucu hatası (' + r.status + ')';
      try { const d = await r.json(); if (d.error) msg = d.error; } catch (e) { /* JSON değil */ }
      throw new Error(msg);
    }
    return r;
  }

  // ---------- giriş / çıkış ----------
  async function login(ev) {
    if (ev) ev.preventDefault();
    const typed = $('pw').value.trim();
    if (typed) pw = typed;
    $('login-err').textContent = '';
    if (!pw) { $('login-err').textContent = 'Şifreyi gir.'; return; }
    try {
      const info = await (await api('/api/info')).json();
      try { sessionStorage.setItem(KEY, pw); } catch (e) { /* yok say */ }
      $('pw').value = '';
      $('login').classList.add('hidden');
      $('panel').classList.remove('hidden');
      $('btn-logout').classList.remove('hidden');
      $('url').textContent = info.url;
      $('qr').src = '/api/qr.svg';
      applySettings(info.settings);
      startPolling();
    } catch (e) {
      if (e.message !== 'Şifre hatalı') $('login-err').textContent = 'Giriş başarısız: ' + e.message;
    }
  }

  function logout(message) {
    stopPolling();
    pw = '';
    try { sessionStorage.removeItem(KEY); } catch (e) { /* yok say */ }
    $('panel').classList.add('hidden');
    $('btn-logout').classList.add('hidden');
    $('modal').classList.add('hidden');
    $('login').classList.remove('hidden');
    $('login-err').textContent = typeof message === 'string' ? message : '';
  }

  function startPolling() { stopPolling(); refresh(); poll = setInterval(refresh, POLL_MS); }
  function stopPolling() { clearInterval(poll); poll = null; }

  // ---------- ayarlar ----------
  function applySettings(s) {
    settings = s;
    $('set-count').value = String(s.question_count);
    $('set-duration').value = s.duration_min;
    $('set-solutions').checked = s.show_solutions;
    $('set-retake').checked = s.allow_retake;
    $('open-state').className = 'badge ' + (s.exam_open ? 'b-ok' : 'b-no');
    $('open-state').textContent = s.exam_open ? 'Sınav AÇIK' : 'Sınav KAPALI';
    $('btn-toggle-open').textContent = s.exam_open ? 'Yeni Girişleri Kapat' : 'Sınavı Aç';
  }

  async function putSettings(body) {
    const r = await api('/api/settings', {
      method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
    });
    applySettings(await r.json());
  }

  async function saveSettings(ev) {
    ev.preventDefault();
    const msg = $('settings-msg');
    try {
      await putSettings({
        question_count: parseInt($('set-count').value, 10),
        duration_min: parseInt($('set-duration').value, 10),
        show_solutions: $('set-solutions').checked,
        allow_retake: $('set-retake').checked,
      });
      msg.textContent = '✓ Kaydedildi';
    } catch (e) {
      msg.textContent = '✘ ' + e.message;
    }
    setTimeout(() => { msg.textContent = ''; }, 3000);
  }

  async function toggleOpen() {
    try { await putSettings({ exam_open: !settings.exam_open }); } catch (e) { alert(e.message); }
  }

  // ---------- sonuçlar ----------
  async function refresh() {
    try {
      const data = await (await api('/api/results')).json();
      $('net-err').textContent = '';
      rows = data.rows;
      const s = data.summary;
      $('s-done').textContent = s.done;
      $('s-live').textContent = s.live;
      $('s-avg').textContent = s.average === null ? '—' : s.average.toFixed(1);
      $('s-pass').textContent = s.pass_rate === null ? '—' : '%' + s.pass_rate;
      renderTable();
      renderTopics(data.topics);
    } catch (e) {
      if (pw) $('net-err').textContent = 'Bağlantı sorunu: ' + e.message;
    }
  }

  function renderTable() {
    const q = $('search').value.trim().toLocaleLowerCase('tr');
    const list = q ? rows.filter((r) => (r.name + ' ' + r.no).toLocaleLowerCase('tr').includes(q)) : rows;
    if (!list.length) {
      $('tbody').innerHTML = `<tr><td colspan="6" class="muted center">${
        rows.length ? 'Aramaya uyan öğrenci yok.' : 'Henüz sınava giren öğrenci yok.'}</td></tr>`;
      return;
    }
    $('tbody').innerHTML = list.map((r) => {
      let status;
      if (r.status === 'sinavda') status = `<span class="badge b-live">Sınavda · ${mmss(r.remaining)}</span>`;
      else status = (r.score >= 50 ? '<span class="badge b-ok">Başarılı</span>' : '<span class="badge b-no">Tekrar Etmeli</span>') +
        (r.auto ? ' <span class="badge b-time" title="Süre dolunca son kaydedilen cevaplarla otomatik gönderildi">Otomatik</span>' : '');
      const attempt = r.attempt > 1 ? ` <span class="badge b-time">Deneme #${r.attempt}</span>` : '';
      const done = r.status === 'bitti';
      return `<tr class="${done ? 'click' : ''}" data-id="${esc(r.id)}"${done ? ' tabindex="0"' : ''}>
        <td class="mono">${esc(r.no)}</td><td><b>${esc(r.name)}</b>${attempt}</td>
        <td class="muted">${esc(r.started)}</td>
        <td>${done ? `<span class="green-t">${r.correct} D</span> / <span class="red-t">${r.wrong} Y</span>` : '-'}</td>
        <td class="amber-t"><b>${r.score ?? '-'}</b></td><td>${status}</td></tr>`;
    }).join('');
    document.querySelectorAll('#tbody tr.click').forEach((tr) => {
      tr.addEventListener('click', () => detail(tr.dataset.id));
      tr.addEventListener('keydown', (e) => { if (e.key === 'Enter') detail(tr.dataset.id); });
    });
  }

  function renderTopics(topics) {
    const box = $('topics');
    box.innerHTML = '';
    if (!topics.length) {
      box.innerHTML = '<p class="muted">Henüz tamamlanan sınav yok.</p>';
      return;
    }
    topics.forEach((t) => {
      const row = document.createElement('div');
      row.className = 'topic-row';
      const name = document.createElement('span');
      name.textContent = t.topic;
      const bar = document.createElement('div');
      bar.className = 'meter ' + (t.rate < 50 ? 'low' : t.rate < 75 ? 'mid' : '');
      bar.setAttribute('role', 'img');
      bar.setAttribute('aria-label', `%${t.rate} doğru`);
      const fill = document.createElement('span');
      fill.style.width = t.rate + '%';
      bar.appendChild(fill);
      const val = document.createElement('span');
      val.className = 'muted';
      val.textContent = `%${t.rate} (${t.correct}/${t.total})`;
      row.append(name, bar, val);
      box.appendChild(row);
    });
  }

  async function detail(id) {
    try {
      const d = await (await api('/api/results/' + encodeURIComponent(id))).json();
      detailId = d.id;
      $('m-title').textContent = `${d.name} (${d.no}) — ${d.score} puan${d.auto ? ' · otomatik gönderildi' : ''}`;
      const fmt = (q, v) => (q.type === 'tf' ? tfLabel(v) : v);
      $('m-body').innerHTML = `<p class="muted">Başlama: ${esc(d.started)} · Bitiş: ${esc(d.submitted)} · ${d.correct} doğru, ${d.wrong} yanlış/boş</p>` +
        d.details.map((q, i) => `
        <div class="sol ${q.correct ? 'ok' : 'no'}">
          <b class="${q.correct ? 'green-t' : 'red-t'}">${q.correct ? '✔' : '✘'} Soru ${i + 1} (${esc(q.topic)})</b>
          <div class="sol-text">${q.text}</div>
          ${q.code ? `<pre>${esc(q.code)}</pre>` : ''}
          <div class="sol-meta"><b>Öğrenci:</b> <span class="ans">${esc(q.user_answer ? fmt(q, q.user_answer) : 'Boş')}</span></div>
          ${!q.correct ? `<div class="sol-meta"><b>Doğru:</b> <span class="ans green-t">${esc(fmt(q, q.answer))}</span></div>` : ''}
          ${q.note ? `<div class="muted">${q.note}</div>` : ''}
        </div>`).join('');
      $('modal').classList.remove('hidden');
      $('m-close').focus();
    } catch (e) {
      $('net-err').textContent = 'Ayrıntı alınamadı: ' + e.message;
    }
  }

  function closeModal() { $('modal').classList.add('hidden'); detailId = null; }

  async function deleteOne() {
    if (!detailId || !confirm('Bu öğrencinin sınav kaydı kalıcı olarak silinecek. Emin misin?')) return;
    try {
      await api('/api/results/' + encodeURIComponent(detailId), { method: 'DELETE' });
      closeModal();
      refresh();
    } catch (e) { alert('Silinemedi: ' + e.message); }
  }

  async function downloadCSV() {
    try {
      const r = await api('/api/results.csv');
      const blob = await r.blob();
      const name = (r.headers.get('Content-Disposition') || '').split('filename=')[1] || 'sonuclar.csv';
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = name;
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(() => URL.revokeObjectURL(a.href), 1000);
    } catch (e) { alert('İndirilemedi: ' + e.message); }
  }

  async function clearAll() {
    if (!confirm('TÜM sınav kayıtları kalıcı olarak silinecek. Emin misin?')) return;
    if (!confirm('Bu işlem geri alınamaz. Önce CSV indirdin mi? Silmeye devam?')) return;
    try { await api('/api/results', { method: 'DELETE' }); refresh(); } catch (e) { alert('Silinemedi: ' + e.message); }
  }

  // ---------- olaylar ----------
  $('login').addEventListener('submit', login);
  $('btn-logout').addEventListener('click', () => logout(''));
  $('settings-form').addEventListener('submit', saveSettings);
  $('btn-toggle-open').addEventListener('click', toggleOpen);
  $('search').addEventListener('input', renderTable);
  $('btn-csv').addEventListener('click', downloadCSV);
  $('btn-clear').addEventListener('click', clearAll);
  $('m-close').addEventListener('click', closeModal);
  $('m-delete').addEventListener('click', deleteOne);
  $('modal').addEventListener('click', (e) => { if (e.target === $('modal')) closeModal(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeModal(); });
  document.addEventListener('visibilitychange', () => {
    if (!pw || $('panel').classList.contains('hidden')) return;
    if (document.hidden) stopPolling(); else startPolling();
  });

  try {
    const saved = sessionStorage.getItem(KEY);
    if (saved) { pw = saved; login(); }
  } catch (e) { /* yok say */ }
})();
