/* PyTest Pro - öğrenci sınav ekranı */
'use strict';
(function () {
  const P = window.PyTest;
  const { esc, fmtAnswer, post, renderAnswer, renderQuestion, pickByKey } = P;
  const $ = (id) => document.getElementById(id);
  const STORE = 'pytest_aktif_sinav';
  const SAVE_DELAY_MS = 1500;     // son tuştan sonra sunucuya kaydetme gecikmesi
  const RETRY_MS = 10000;         // bağlantı koparsa yeniden deneme aralığı
  const STATUS_POLL_MS = 10000;   // giriş ekranında sınav açık mı kontrolü

  let exam = null;                // {exam_id, name, no, questions}
  let answers = {};
  let idx = 0;
  let deadline = 0;
  let tickTimer = null, saveTimer = null, retryTimer = null, statusTimer = null;
  let dirty = false, saving = false, submitting = false, submitArmed = false;

  const hasAnswer = (id) => String(answers[id] ?? '').trim() !== '';

  // ---------- yerel yedek ----------
  function readLocal() {
    try { return JSON.parse(localStorage.getItem(STORE) || 'null'); } catch (e) { return null; }
  }
  function writeLocal() {
    if (!exam) return;
    try { localStorage.setItem(STORE, JSON.stringify({ exam_id: exam.exam_id, answers })); } catch (e) { /* özel mod */ }
  }
  function clearLocal() {
    try { localStorage.removeItem(STORE); } catch (e) { /* yok say */ }
  }

  function show(id) {
    ['login-card', 'exam-card', 'result-card'].forEach((x) => $(x).classList.toggle('hidden', x !== id));
    $('exam-tools').classList.toggle('hidden', id !== 'exam-card');
    document.body.classList.toggle('in-exam', id === 'exam-card');
    if (id !== 'exam-card') { $('answered-count').textContent = ''; $('save-state').textContent = ''; $('save-state').className = ''; }
  }

  // ---------- giriş ekranı ----------
  async function loadStatus() {
    try {
      const s = await (await fetch('/api/status')).json();
      $('exam-title').textContent = s.title || 'Sınava başla';
      $('exam-name').textContent = s.title || 'Python sınavı';
      $('exam-info').textContent = `${s.question_count} soru, ${s.duration_min} dakika`;
      $('closed-msg').classList.toggle('hidden', s.open);
      $('practice-link').classList.toggle('hidden', !s.practice_open);
    } catch (e) { /* sessizce yeniden denenecek */ }
  }
  function startStatusPolling() {
    clearInterval(statusTimer);
    loadStatus();
    statusTimer = setInterval(loadStatus, STATUS_POLL_MS);
  }

  async function startExam(ev) {
    ev.preventDefault();
    const name = $('std-name').value.trim();
    const no = $('std-no').value.trim();
    $('login-err').textContent = '';
    if (!name || !no) { $('login-err').textContent = 'Ad Soyad ve Okul No zorunludur.'; return; }
    $('btn-start').disabled = true;
    const r = await post('/api/start', { name, no });
    $('btn-start').disabled = false;
    if (!r.ok) { $('login-err').textContent = r.data.error || 'Sınav başlatılamadı.'; return; }
    const local = readLocal();
    openExam(r.data, local && local.exam_id === r.data.exam_id ? local.answers : null);
  }

  // ---------- sınav ----------
  function openExam(d, localAnswers) {
    clearInterval(statusTimer);
    exam = { exam_id: d.exam_id, name: d.name, no: d.no, questions: d.questions };
    const serverAnswers = d.answers || {};
    answers = Object.assign({}, serverAnswers, localAnswers || {});
    idx = 0;
    submitting = false;
    submitArmed = false;
    deadline = Date.now() + d.remaining * 1000;
    $('disp-name').textContent = d.name;
    $('disp-no').textContent = d.no;
    $('btn-submit').disabled = false;
    $('submit-err').textContent = '';
    $('submit-note').classList.add('hidden');
    $('btn-submit').textContent = 'Sınavı gönder';
    writeLocal();
    show('exam-card');
    renderQ(false);
    startTimer();
    clearInterval(retryTimer);
    retryTimer = setInterval(() => { if (dirty) flush(); }, RETRY_MS);
    if (JSON.stringify(answers) !== JSON.stringify(serverAnswers)) { dirty = true; flush(); }
    else setSaveState('idle');
  }

  function startTimer() {
    clearInterval(tickTimer);
    tick();
    tickTimer = setInterval(tick, 1000);
  }
  function tick() {
    const left = Math.max(0, Math.round((deadline - Date.now()) / 1000));
    $('timer').innerHTML = String(Math.floor(left / 60)).padStart(2, '0') + ':' + String(left % 60).padStart(2, '0') + '<small>kaldı</small>';
    $('timer').classList.toggle('warn', left <= 60);
    if (left <= 0) { clearInterval(tickTimer); submitExam(true); }
  }

  function emptyIndexes() {
    return exam.questions.map((q, i) => (hasAnswer(q.id) ? -1 : i)).filter((i) => i >= 0);
  }

  function renderNav() {
    const grid = $('nav-grid');
    grid.innerHTML = '';
    exam.questions.forEach((q, i) => {
      const b = document.createElement('button');
      b.type = 'button';
      const done = hasAnswer(q.id);
      b.className = 'file' + (done ? ' answered' : '') + (i === idx ? ' current' : '') + (submitArmed && !done ? ' missing' : '');
      const ext = q.code || q.type === 'code' ? '.py' : '.txt';
      b.innerHTML = `<i aria-hidden="true">${i === idx ? '●' : done ? '✓' : '○'}</i>soru_${String(i + 1).padStart(2, '0')}${ext}`;
      b.setAttribute('aria-label', `Soru ${i + 1}${done ? ', cevaplandı' : ', boş'}`);
      if (i === idx) b.setAttribute('aria-current', 'true');
      b.addEventListener('click', () => { idx = i; renderQ(true); });
      grid.appendChild(b);
    });
    const done = exam.questions.filter((q) => hasAnswer(q.id)).length;
    $('answered-count').textContent = `${done} / ${exam.questions.length} cevaplandı`;
  }

  function renderQ(focus) {
    const q = exam.questions[idx];
    $('q-badge').textContent = `Soru ${idx + 1} / ${exam.questions.length}`;
    $('q-topic').textContent = q.topic;
    renderQuestion({ tab: $('q-tab'), code: $('q-code'), prose: $('q-prose'), slot: $('q-slot'), text: $('q-text') }, q, idx + 1);
    renderAnswer($('answer-box'), q, answers[q.id], (v) => save(q.id, v), focus, $('q-slot'));
    $('btn-prev').disabled = idx === 0;
    const last = idx === exam.questions.length - 1;
    $('btn-next').textContent = last ? 'Gönder' : 'Sonraki';
    $('btn-next').className = 'btn ' + (last ? 'primary' : 'dark');
    renderNav();
  }

  function go(delta) {
    const n = idx + delta;
    if (n >= 0 && n < exam.questions.length) { idx = n; renderQ(true); }
    else if (n === exam.questions.length) trySubmit();
  }

  // ---------- otomatik kayıt ----------
  const SAVE_TEXT = {
    idle: ['', 'Cevapların otomatik kaydedilir'],
    pending: ['', 'Kaydedilmeyi bekliyor…'],
    saving: ['', 'Kaydediliyor…'],
    saved: ['ok', '✓ Kaydedildi'],
    offline: ['bad', '⚠ Bağlantı yok: cevapların bu cihazda tutuluyor, tekrar denenecek'],
  };
  function setSaveState(state) {
    const [cls, text] = SAVE_TEXT[state];
    $('save-state').className = cls;
    $('save-state').textContent = text;
  }

  function save(id, val) {
    if (String(val).trim() === '') delete answers[id]; else answers[id] = val;
    writeLocal();
    dirty = true;
    setSaveState('pending');
    clearTimeout(saveTimer);
    saveTimer = setTimeout(flush, SAVE_DELAY_MS);
    if (submitArmed) disarm();
    renderNav();
  }

  async function flush() {
    if (!exam || saving || submitting || !dirty) return;
    saving = true;
    dirty = false;
    setSaveState('saving');
    const r = await post('/api/save', { exam_id: exam.exam_id, answers });
    saving = false;
    if (submitting) return;
    if (r.ok) {
      deadline = Date.now() + r.data.remaining * 1000; // sunucu saatine eşitle
      if (dirty) { setSaveState('pending'); clearTimeout(saveTimer); saveTimer = setTimeout(flush, SAVE_DELAY_MS); }
      else setSaveState('saved');
    } else if (r.status === 404 || r.status === 409) {
      submitExam(true); // süre doldu veya sınav başka sekmede gönderildi
    } else {
      dirty = true;
      setSaveState('offline');
    }
  }

  // ---------- gönderim: boş soru varsa ilk basış uyarır, ikinci basış gönderir ----------
  function disarm() {
    submitArmed = false;
    $('submit-note').classList.add('hidden');
    $('btn-submit').textContent = 'Sınavı gönder';
    $('btn-submit').className = 'btn primary';
  }

  function trySubmit() {
    if (!exam || submitting) return;
    const empty = emptyIndexes();
    if (!empty.length || submitArmed) { submitExam(false); return; }
    submitArmed = true;
    $('submit-note').textContent = `${empty.length} soru boş, listede sarıyla işaretli. ` +
      'Doldurmak için soruya dön ya da boş haliyle göndermek için yukarıdaki düğmeye yeniden bas.';
    $('submit-note').classList.remove('hidden');
    $('btn-submit').textContent = `${empty.length} boş soruyla gönder`;
    $('btn-submit').className = 'btn warn';
    idx = empty[0];
    renderQ(true);
  }

  function stopExamTimers() {
    clearInterval(tickTimer); clearInterval(retryTimer); clearTimeout(saveTimer);
    dirty = false;
  }

  async function submitExam(auto) {
    if (submitting || !exam) return;
    submitting = true;
    clearTimeout(saveTimer);
    $('btn-submit').disabled = true;
    $('submit-err').textContent = auto ? 'Süre doldu, gönderiliyor…' : 'Gönderiliyor…';
    const r = await post('/api/submit', { exam_id: exam.exam_id, answers });
    if (r.ok) {
      stopExamTimers(); clearLocal();
      showResult(Object.assign({ exam_id: exam.exam_id }, r.data));
      return;
    }
    if (r.status === 404 || r.status === 409) {
      stopExamTimers(); clearLocal();
      backToLogin(r.data.error || 'Bu sınav zaten gönderildi.');
      return;
    }
    submitting = false;
    $('btn-submit').disabled = false;
    $('submit-err').textContent = 'Gönderilemedi: ' + (r.data.error || 'bağlantı hatası') +
      (auto ? ' — 5 sn sonra tekrar denenecek. Cevapların sunucuda kayıtlı.' : ' — Tekrar dene.');
    if (auto) setTimeout(() => submitExam(true), 5000);
  }

  function showResult(d) {
    show('result-card');
    const total = d.correct + d.wrong;
    $('res-score').textContent = d.score;
    $('res-correct').textContent = d.correct;
    $('res-wrong').textContent = d.wrong;
    $('res-percent').textContent = '%' + (total ? Math.round(d.correct * 100 / total) : 0);
    $('res-msg').textContent = d.late
      ? 'Süre aşıldığı için süre içinde kaydedilen son cevapların değerlendirildi.'
      : 'Sonucun öğretmenine iletildi.';

    $('res-score').classList.toggle('low', d.score < 50);
    const files = $('res-files');
    files.innerHTML = '';
    d.details.forEach((q, i) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'file ' + (q.correct ? 'answered' : 'wrong');
      b.innerHTML = `<i aria-hidden="true">${q.correct ? '✓' : '✗'}</i>soru_${String(i + 1).padStart(2, '0')}`;
      b.setAttribute('aria-label', `Soru ${i + 1}, ${q.correct ? 'doğru' : 'yanlış'}`);
      b.addEventListener('click', () => {
        if (q.correct && solFilter === 'wrong') applyFilter('all');
        const el = $('sol-' + i);
        if (el) el.scrollIntoView({ block: 'start' });
      });
      files.appendChild(b);
    });

    if (!d.show_solutions) {
      $('solutions-title').textContent = 'Soru soru sonuç';
      $('sol-filter').classList.add('hidden');
      $('solutions').innerHTML = '<p class="muted">Öğretmenin bu sınavda çözümleri göstermiyor.</p>' +
        d.details.map((q, i) => `<div id="sol-${i}" class="sol ${q.correct ? 'ok' : 'no'}"><div class="sol-head">
          <span>Soru ${i + 1}: ${esc(q.topic)}</span><span class="mark">${q.correct ? 'Doğru' : 'Yanlış'}</span>
        </div></div>`).join('');
      return;
    }
    $('sol-filter').classList.toggle('hidden', d.wrong === 0);
    $('solutions-title').textContent = 'Sorular ve çözümleri';
    $('solutions').innerHTML = d.details.map((q, i) => `
      <div id="sol-${i}" class="sol ${q.correct ? 'ok' : 'no'}">
        <div class="sol-head">
          <span>Soru ${i + 1}: ${esc(q.topic)}</span>
          <span class="mark">${q.correct ? 'Doğru' : 'Yanlış'}</span>
        </div>
        <div class="sol-text">${q.text}</div>
        ${q.code ? `<pre class="snippet">${'<code class="codeview">' + P.highlight(q.code) + '</code>'}</pre>` : ''}
        <div class="sol-meta">
          <div><b>Senin cevabın:</b> <span class="ans ${q.correct ? 'green-t' : 'red-t'}">${esc(q.user_answer ? fmtAnswer(q.type, q.user_answer) : 'Boş bırakıldı')}</span></div>
          ${!q.correct && q.why ? P.whyNote(q.why) : ''}
          ${!q.correct ? `<div><b>Doğru cevap:</b> <span class="ans green-t">${esc(fmtAnswer(q.type, q.answer))}</span></div>` : ''}
          ${q.note ? `<div class="muted">${q.note}</div>` : ''}
          <div class="exp"><b>Açıklama:</b> ${q.solution}</div>
          ${q.has_trace ? `<div class="row trace-row"><button type="button" class="btn sm${q.correct ? ' subtle' : ''}" data-trace="${q.id}">Kodu adım adım izle</button></div>
          <div class="trace-box hidden" data-trace-box="${q.id}"></div>` : ''}
        </div>
      </div>`).join('');
    applyFilter(d.wrong > 0 ? 'wrong' : 'all');
    const examId = d.exam_id;
    $('solutions').querySelectorAll('[data-trace]').forEach((btn) => {
      const box = $('solutions').querySelector(`[data-trace-box="${btn.dataset.trace}"]`);
      P.traceToggle(btn, box, () => post('/api/exam/trace', { exam_id: examId, question_id: Number(btn.dataset.trace) }));
    });
  }

  let solFilter = 'all';
  function applyFilter(mode) {
    solFilter = mode;
    $('sol-filter').querySelectorAll('.seg-btn').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.filter === mode)));
    $('solutions').querySelectorAll('.sol.ok').forEach((el) => el.classList.toggle('hidden', mode === 'wrong'));
  }

  function backToLogin(message) {
    exam = null; answers = {}; submitting = false; submitArmed = false;
    $('login-err').textContent = message || '';
    show('login-card');
    startStatusPolling();
  }

  // ---------- başlangıç ----------
  async function init() {
    $('login-form').addEventListener('submit', startExam);
    $('btn-prev').addEventListener('click', () => go(-1));
    $('btn-next').addEventListener('click', () => go(1));
    $('btn-submit').addEventListener('click', trySubmit);
    $('sol-filter').querySelectorAll('.seg-btn').forEach((b) => b.addEventListener('click', () => applyFilter(b.dataset.filter)));
    document.addEventListener('keydown', (e) => {
      if (!exam || submitting || $('exam-card').classList.contains('hidden')) return;
      if (pickByKey($('answer-box'), e)) { e.preventDefault(); return; }
      const t = e.target;
      const typing = t && (t.tagName === 'TEXTAREA' || (t.tagName === 'INPUT' && t.type !== 'radio'));
      if (typing || e.ctrlKey || e.metaKey || e.altKey) return;
      if (e.key === 'ArrowRight') { e.preventDefault(); if (idx < exam.questions.length - 1) go(1); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); go(-1); }
    });
    $('btn-reset').addEventListener('click', () => backToLogin(''));

    // Sayfa yenilenirse yarım kalan sınava sunucudan devam et
    const local = readLocal();
    if (local && local.exam_id) {
      const r = await post('/api/resume', { exam_id: local.exam_id });
      if (r.ok) { openExam(r.data, local.answers); return; }
      if (r.status !== 0) clearLocal();
      $('login-err').textContent = r.status === 0
        ? 'Sunucuya ulaşılamadı. Bağlantını kontrol edip sayfayı yenile.'
        : (r.data.error || '');
    }
    show('login-card');
    startStatusPolling();
  }

  init();
})();
