/* PyTest Pro - öğretmen paneli */
'use strict';
(function () {
  const P = window.PyTest;
  const { esc, fmtAnswer, levelBadge } = P;
  const $ = (id) => document.getElementById(id);
  const KEY = 'pytest_ogretmen_sifre';
  const POLL_MS = 3000;
  const ALL = '__tum__';

  let pw = '';
  let poll = null;
  let rows = [];
  let settings = null;
  let detailId = null;

  const mmss = (sec) => String(Math.floor(sec / 60)).padStart(2, '0') + ':' + String(sec % 60).padStart(2, '0');
  const titleLabel = (t) => (t ? t : '(başlıksız)');

  function filterQuery() {
    const sel = $('title-filter');
    if (!sel.options.length || sel.value === ALL) return '';
    return '?sinav=' + encodeURIComponent(sel.value); // '' = başlıksız sınavlar
  }

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
      $('login-stage').classList.add('hidden');
      $('panel').classList.remove('hidden');
      $('top-tools').classList.remove('hidden');
      $('url').textContent = info.url;
      $('practice-url').textContent = info.url + '/pratik';
      $('qr').src = '/api/qr.svg';
      buildSettingsForm(info);
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
    $('top-tools').classList.add('hidden');
    closeDetail();
    $('login-stage').classList.remove('hidden');
    $('login-err').textContent = typeof message === 'string' ? message : '';
  }

  function startPolling() { stopPolling(); refresh(); poll = setInterval(refresh, POLL_MS); }
  function stopPolling() { clearInterval(poll); poll = null; }

  // ---------- ayarlar ----------
  function buildSettingsForm(info) {
    $('set-count').innerHTML = info.count_choices.map((c) => `<option value="${c}">${c} soru</option>`).join('');
    $('set-units').innerHTML = info.units.map((u) => `
      <label class="unit-check" title="${esc(u.description)}">
        <input type="checkbox" value="${esc(u.id)}">
        <span><b>${u.order}. ${esc(u.title)}</b> ${levelBadge(u.level)}
        <span class="muted small">${u.templates} soru şablonu, ${u.topics.length} konu</span></span>
      </label>`).join('');
  }

  function applySettings(s) {
    settings = s;
    $('set-title').value = s.title;
    $('set-count').value = String(s.question_count);
    $('set-duration').value = s.duration_min;
    $('set-solutions').checked = s.show_solutions;
    $('set-retake').checked = s.allow_retake;
    $('set-practice').checked = s.practice_open;
    $('set-units').querySelectorAll('input').forEach((i) => { i.checked = s.units.includes(i.value); });
    $('open-state').className = 'badge ' + (s.exam_open ? 'b-ok' : 'b-no');
    $('open-state').textContent = s.exam_open ? 'Sınav açık' : 'Sınav kapalı';
    $('btn-toggle-open').textContent = s.exam_open ? 'Yeni girişleri kapat' : 'Sınavı aç';
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
    const units = [...$('set-units').querySelectorAll('input:checked')].map((i) => i.value);
    if (!units.length) { msg.textContent = '✘ En az bir ünite seç.'; return; }
    try {
      await putSettings({
        title: $('set-title').value,
        question_count: parseInt($('set-count').value, 10),
        duration_min: parseInt($('set-duration').value, 10),
        units,
        show_solutions: $('set-solutions').checked,
        allow_retake: $('set-retake').checked,
        practice_open: $('set-practice').checked,
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
  function updateTitleFilter(titles) {
    const sel = $('title-filter');
    const current = sel.value || ALL;
    const options = [`<option value="${ALL}">Tüm sınavlar</option>`]
      .concat(titles.map((t) => `<option value="${esc(t)}">${esc(titleLabel(t))}</option>`));
    const html = options.join('');
    if (sel.dataset.html !== html) {
      sel.innerHTML = html;
      sel.dataset.html = html;
      sel.value = titles.includes(current) ? current : ALL;
    }
    $('btn-clear').textContent = sel.value === ALL ? 'Tümünü sil' : 'Bu sınavı sil';
  }

  async function refresh() {
    try {
      const data = await (await api('/api/results' + filterQuery())).json();
      $('net-err').textContent = '';
      rows = data.rows;
      updateTitleFilter(data.titles);
      const s = data.summary;
      $('s-done').textContent = s.done;
      $('s-live').textContent = s.live;
      $('s-avg').textContent = s.average === null ? '—' : s.average.toFixed(1);
      $('s-pass').textContent = s.pass_rate === null ? '—' : '%' + s.pass_rate;
      $('live-note').textContent = `${s.live} öğrenci sınavda, ${s.done} bitirdi · 3 saniyede bir yenilenir`;
      renderTable();
      renderTopics(data.topics);
    } catch (e) {
      if (pw) $('net-err').textContent = 'Bağlantı sorunu: ' + e.message;
    }
  }

  function renderTable() {
    const box = $('tiles');
    const q = $('search').value.trim().toLocaleLowerCase('tr');
    const list = q ? rows.filter((r) => (r.name + ' ' + r.no).toLocaleLowerCase('tr').includes(q)) : rows;
    if (!list.length) {
      box.innerHTML = `<p class="files-empty">${rows.length ? 'Aramaya uyan öğrenci yok.' : 'Henüz sınava giren öğrenci yok. Adresi ya da QR kodu öğrencilerle paylaş.'}</p>`;
      return;
    }
    const showTitle = $('title-filter').value === ALL;
    const live = list.filter((r) => r.status === 'sinavda');
    const done = list.filter((r) => r.status !== 'sinavda');
    const sub = (r) => [`No ${esc(r.no)}`, r.attempt > 1 ? `Deneme #${r.attempt}` : '', showTitle && r.title ? esc(r.title) : '']
      .filter(Boolean).join(' · ');
    let html = '';
    if (live.length) {
      html += `<p class="group-label">Sınavda (${live.length})</p>` + live.map((r) => {
        const pct = r.total ? Math.round(r.answered * 100 / r.total) : 0;
        return `<div class="student"><span class="student-name">${esc(r.name)}</span>
          <span class="muted small">${mmss(r.remaining)}</span>
          <span class="student-meter" role="img" aria-label="${r.answered} / ${r.total} soru cevaplandı"><span data-w="${pct}"></span></span>
          <span class="student-sub">${r.answered} / ${r.total} cevaplandı · ${sub(r)}</span></div>`;
      }).join('');
    }
    if (done.length) {
      html += `<p class="group-label">Bitirdi (${done.length})</p>` + done.map((r) => `
        <button type="button" class="student${r.id === detailId ? ' current' : ''}" data-id="${esc(r.id)}">
          <span class="student-name">${esc(r.name)}</span>
          <span class="student-score${r.score < 50 ? ' low' : ''}">${r.score}</span>
          <span class="student-sub">${r.correct} D · ${r.wrong} Y${r.auto ? ' · otomatik' : ''} · ${sub(r)}</span>
        </button>`).join('');
    }
    box.innerHTML = html;
    box.querySelectorAll('[data-w]').forEach((el) => { el.style.width = el.dataset.w + '%'; });
    box.querySelectorAll('button.student').forEach((b) => b.addEventListener('click', () => detail(b.dataset.id)));
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
      name.innerHTML = `${esc(t.topic)}<span class="muted small block">${esc(t.unit)}</span>`;
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
      if (t.common_wrong) {
        const cw = document.createElement('div');
        cw.className = 'common-wrong';
        cw.innerHTML = `En sık yanlış: %${t.common_wrong.share} <span class="ans">"${esc(t.common_wrong.answer)}"</span> cevabını verdi.`
          + (t.common_wrong.why ? P.whyNote(t.common_wrong.why) : '');
        row.appendChild(cw);
      }
      box.appendChild(row);
    });
  }

  async function detail(id) {
    try {
      const d = await (await api('/api/results/' + encodeURIComponent(id))).json();
      detailId = d.id;
      $('m-title').textContent = `${d.name} (${d.no}), ${d.score} puan${d.auto ? ', otomatik gönderildi' : ''}`;
      $('tab-detail-name').textContent = `ogrenci_${d.no}.txt`;
      $('m-body').innerHTML = `<p class="muted">${d.title ? esc(d.title) + '. ' : ''}Başlama ${esc(d.started)}, bitiş ${esc(d.submitted)}. ${d.correct} doğru, ${d.wrong} yanlış ya da boş.</p>` +
        d.details.map((q, i) => `
        <div class="sol ${q.correct ? 'ok' : 'no'}">
          <div class="sol-head"><span>Soru ${i + 1}: ${esc(q.topic)} <span class="muted small">${esc(q.unit)}</span></span><span class="mark">${q.correct ? 'Doğru' : 'Yanlış'}</span></div>
          <div class="sol-text">${q.text}</div>
          ${q.code ? `<pre class="snippet"><code class="codeview">${P.highlight(q.code)}</code></pre>` : ''}
          <div class="sol-meta"><b>Öğrenci:</b> <span class="ans">${esc(q.user_answer ? fmtAnswer(q.type, q.user_answer) : 'Boş')}</span></div>
          ${!q.correct && q.why ? P.whyNote(q.why) : ''}
          ${!q.correct ? `<div class="sol-meta"><b>Doğru:</b> <span class="ans green-t">${esc(fmtAnswer(q.type, q.answer))}</span></div>` : ''}
          ${q.note ? `<div class="muted">${q.note}</div>` : ''}
          ${q.has_trace ? `<div class="row trace-row"><button type="button" class="btn sm${q.correct ? ' subtle' : ''}" data-trace="${q.id}">Kodu adım adım izle</button></div>
          <div class="trace-box hidden" data-trace-box="${q.id}"></div>` : ''}
        </div>`).join('');
      const examId = d.id;
      $('m-body').querySelectorAll('[data-trace]').forEach((btn) => {
        const box = $('m-body').querySelector(`[data-trace-box="${btn.dataset.trace}"]`);
        P.traceToggle(btn, box, async () => {
          try {
            const r = await api(`/api/results/${encodeURIComponent(examId)}/trace/${btn.dataset.trace}`);
            return { ok: true, status: r.status, data: await r.json() };
          } catch (e) {
            return { ok: false, status: 0, data: { error: e.message } };
          }
        });
      });
      $('overview').classList.add('hidden');
      $('detail').classList.remove('hidden');
      $('detail').scrollTop = 0;
      $('tab-detail').classList.remove('hidden');
      $('tab-detail').classList.add('active');
      $('tab-overview').classList.remove('active');
      renderTable();
    } catch (e) {
      $('net-err').textContent = 'Ayrıntı alınamadı: ' + e.message;
    }
  }

  function closeDetail() {
    detailId = null;
    $('detail').classList.add('hidden');
    $('overview').classList.remove('hidden');
    $('tab-detail').classList.add('hidden');
    $('tab-detail').classList.remove('active');
    $('tab-overview').classList.add('active');
    renderTable();
  }

  async function deleteOne() {
    if (!detailId || !confirm('Bu öğrencinin sınav kaydı kalıcı olarak silinecek. Emin misin?')) return;
    try {
      await api('/api/results/' + encodeURIComponent(detailId), { method: 'DELETE' });
      closeDetail();
      refresh();
    } catch (e) { alert('Silinemedi: ' + e.message); }
  }

  async function downloadCSV() {
    try {
      const r = await api('/api/results.csv' + filterQuery());
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
    const filtered = $('title-filter').value !== ALL;
    const what = filtered ? `"${titleLabel($('title-filter').value)}" sınavının TÜM kayıtları` : 'TÜM sınav kayıtları';
    if (!confirm(`${what} kalıcı olarak silinecek. Emin misin?`)) return;
    if (!confirm('Bu işlem geri alınamaz. Önce CSV indirdin mi? Silmeye devam?')) return;
    try { await api('/api/results' + filterQuery(), { method: 'DELETE' }); refresh(); }
    catch (e) { alert('Silinemedi: ' + e.message); }
  }

  // ---------- olaylar ----------
  $('login').addEventListener('submit', login);
  $('btn-logout').addEventListener('click', () => logout(''));
  $('settings-form').addEventListener('submit', saveSettings);
  $('btn-toggle-open').addEventListener('click', toggleOpen);
  $('search').addEventListener('input', renderTable);
  $('title-filter').addEventListener('change', refresh);
  $('btn-csv').addEventListener('click', downloadCSV);
  $('btn-clear').addEventListener('click', clearAll);
  $('m-close').addEventListener('click', closeDetail);
  $('tab-overview').addEventListener('click', closeDetail);
  $('m-delete').addEventListener('click', deleteOne);
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && detailId) closeDetail(); });
  document.addEventListener('visibilitychange', () => {
    if (!pw || $('panel').classList.contains('hidden')) return;
    if (document.hidden) stopPolling(); else startPolling();
  });

  try {
    const saved = sessionStorage.getItem(KEY);
    if (saved) { pw = saved; login(); }
  } catch (e) { /* yok say */ }
})();
