/* PyTest Pro - pratik modu: ipucu, yanlışın nedeni, kod izi, aynı konudan yeni soru, konu tamamlama */
'use strict';
(function () {
  const P = window.PyTest;
  const { esc, fmtAnswer, post, request, renderAnswer, renderQuestion, pickByKey } = P;
  const $ = (id) => document.getElementById(id);
  const STORE = 'pytest_pratik';
  const STREAK_TO_MASTER = 2; // ipucusuz üst üste 2 doğru = konu tamamlandı

  let units = [];        // /api/practice/units
  let unit = null;       // seçili ünite id
  let token = null;      // sunucudaki soru anahtarı
  let current = null;    // gösterilen soru
  let gen = null;        // sorunun şablonu
  let topic = '';
  let answer = '';
  let checked = false;
  let usedHint = false;
  let primaryAction = null;
  const score = { right: 0, total: 0 };

  // ---------- oturum ilerlemesi (yalnızca bu sekmede) ----------
  let memory = {};
  function load() {
    try { return JSON.parse(sessionStorage.getItem(STORE) || '{}') || {}; } catch (e) { return memory; }
  }
  function save(progress) {
    memory = progress;
    try { sessionStorage.setItem(STORE, JSON.stringify(progress)); } catch (e) { /* bellekte kalır */ }
  }
  function unitInfo(id) { return units.find((u) => u.id === id); }
  function doneGens(id) {
    const recs = load()[id] || {};
    return Object.keys(recs).filter((g) => recs[g].done);
  }
  /** Tamamlanan konular: konunun TÜM şablonları (görülmemiş olanlar dahil) tamamlandıysa konu tamamdır. */
  function completedTopics(id) {
    const recs = load()[id] || {};
    const info = unitInfo(id);
    const doneCount = {};
    Object.values(recs).forEach((r) => { if (r.done) doneCount[r.topic] = (doneCount[r.topic] || 0) + 1; });
    return Object.keys(doneCount).filter((t) => info && doneCount[t] >= (info.topic_templates[t] || Infinity));
  }
  function topicsDone(id) { return completedTopics(id).length; }
  function record(correct) {
    const progress = load();
    const recs = progress[unit] = progress[unit] || {};
    const rec = recs[gen] = recs[gen] || { streak: 0, done: false, topic };
    rec.streak = correct && !usedHint ? rec.streak + 1 : 0;
    const newlyDone = !rec.done && rec.streak >= STREAK_TO_MASTER;
    if (newlyDone) rec.done = true;
    save(progress);
    return newlyDone;
  }

  // ---------- görünümler ----------
  function view(id) {
    $('closed').classList.toggle('hidden', id !== 'closed');
    $('practice').classList.toggle('hidden', id === 'closed');
    const asking = id === 'question-view';
    $('question-view').classList.toggle('hidden', !asking);
    $('pane-idle').classList.toggle('hidden', asking);
    $('welcome').classList.toggle('hidden', asking);
    document.body.classList.toggle('in-exam', asking);
    if (!asking) {
      ['q-code', 'q-prose', 'q-slot', 'trace-box'].forEach((x) => $(x).classList.add('hidden'));
      $('q-tab').textContent = 'baslarken.txt';
      $('q-topic').textContent = '';
    }
  }

  function updateScore() {
    $('score').textContent = score.total ? `Bu oturumda ${score.right} / ${score.total} doğru` : '';
  }

  async function loadUnits() {
    const r = await request('/api/practice/units');
    if (r.status === 403) { view('closed'); return; }
    if (!r.ok) { view('closed'); $('closed').querySelector('h2').textContent = r.data.error || 'Sunucuya ulaşılamadı.'; return; }
    units = r.data;
    renderUnits();
    view('units-view');
  }

  function renderUnits() {
    const grid = $('unit-grid');
    grid.innerHTML = '';
    units.forEach((u) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'unit-item' + (u.id === unit ? ' current' : '');
      const done = completedTopics(u.id);
      const meta = done.length
        ? `<span class="unit-meta done">${done.length} / ${u.topics.length} konu tamamlandı</span>`
        : `<span class="unit-meta">${u.topics.length} konu · ${esc(u.level)}</span>`;
      b.innerHTML = `<span class="unit-no">${u.order}</span><span class="unit-name">${esc(u.title)}${meta}</span>`;
      b.title = u.description + (done.length ? '\nTamamlanan: ' + done.join(', ') : '');
      if (u.id === unit) b.setAttribute('aria-current', 'true');
      b.addEventListener('click', () => startUnit(u.id));
      grid.appendChild(b);
    });
  }

  function startUnit(id) {
    unit = id;
    renderUnits();
    $('unit-done').classList.add('hidden');
    nextQuestion(null);
  }

  /** sameGen verilirse aynı şablondan yeni soru; verilmezse tamamlanmamış konulara öncelik. */
  async function nextQuestion(sameGen) {
    $('err').textContent = '';
    const body = sameGen ? { unit, gen: sameGen } : { unit, avoid: doneGens(unit) };
    const r = await post('/api/practice/next', body);
    if (r.status === 403) { view('closed'); return; }
    if (!r.ok) { $('err').textContent = r.data.error || 'Soru alınamadı.'; return; }
    ({ token, gen, topic } = r.data);
    const hasHint = r.data.has_hint;
    current = r.data.question;
    answer = '';
    checked = false;
    usedHint = false;
    $('q-unit').textContent = r.data.unit;
    $('q-topic').textContent = topic;
    view('question-view');
    renderQuestion({ tab: $('q-tab'), code: $('q-code'), prose: $('q-prose'), slot: $('q-slot'), text: $('q-text') }, current, score.total + 1);
    renderAnswer($('answer-box'), current, '', (v) => { answer = v; }, true, $('q-slot'));
    ['hint-box', 'feedback', 'trace-box', 'after-actions'].forEach((id) => $(id).classList.add('hidden'));
    $('feedback').innerHTML = '';
    $('trace-box').innerHTML = '';
    $('ask-actions').classList.remove('hidden');
    $('btn-hint').classList.toggle('hidden', !hasHint);
    $('btn-hint').disabled = false;
    $('btn-check').disabled = false;
  }

  async function showHint() {
    $('btn-hint').disabled = true;
    const r = await post('/api/practice/hint', { token });
    if (!r.ok) { $('btn-hint').classList.add('hidden'); return; }
    usedHint = true;
    $('hint-box').innerHTML = `<b>İpucu:</b> ${r.data.hint}`;
    $('hint-box').classList.remove('hidden');
  }

  function button(label, cls, onClick) {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'btn ' + cls;
    b.textContent = label;
    if (onClick) b.addEventListener('click', onClick);
    return b;
  }

  async function check() {
    if (checked) return;
    if (!String(answer).trim()) { $('err').textContent = 'Önce bir cevap ver.'; return; }
    $('err').textContent = '';
    $('btn-check').disabled = true;
    const r = await post('/api/practice/check', { token, answer });
    if (!r.ok) {
      $('btn-check').disabled = false;
      $('err').textContent = r.data.error || 'Kontrol edilemedi.';
      if (r.status === 404) nextQuestion(null);
      return;
    }
    const d = r.data;
    checked = true;
    score.total += 1;
    if (d.correct) score.right += 1;
    updateScore();
    const before = topicsDone(unit);
    const mastered = record(d.correct) && completedTopics(unit).includes(topic);

    const group = $('answer-box').querySelector('.opts');
    if (group) {
      group.classList.add('locked');
      group.querySelectorAll('.opt').forEach((l) => {
        const inp = l.querySelector('input');
        inp.disabled = true;
        l.classList.toggle('right', inp.value === d.answer);
        l.classList.toggle('wrong', inp.checked && !d.correct);
        if (inp.checked && !d.correct) l.classList.remove('sel');
      });
    }
    const fb = $('feedback');
    fb.className = 'sol ' + (d.correct ? 'ok' : 'no');
    if (d.correct) {
      fb.innerHTML = `
        <div class="sol-head"><span class="verdict">Doğru${usedHint ? ' (ipucuyla)' : ''}</span></div>
        ${mastered ? `<p class="muted">Bu konuyu tamamladın: ${esc(topic)}</p>` : ''}
        <div class="sol-meta"><div class="exp"><b>Açıklama:</b> ${d.solution}</div></div>`;
    } else {
      fb.innerHTML = `
        <div class="sol-head"><span class="verdict">Yanlış</span></div>
        ${d.why ? P.whyNote(d.why) : ''}
        <div class="sol-meta">
          <div><b>Doğru cevap:</b> <span class="ans green-t">${esc(fmtAnswer(d.type, d.answer))}</span></div>
          ${d.note && d.note !== d.why ? `<div class="muted">${d.note}</div>` : ''}
          <div class="exp"><b>Açıklama:</b> ${d.solution}</div>
        </div>`;
    }

    const actions = $('after-actions');
    actions.innerHTML = '';
    const nextBtn = button('Yeni soru', d.correct ? 'primary' : '', () => nextQuestion(null));
    if (d.correct) {
      primaryAction = () => nextQuestion(null);
    } else {
      const sameGen = gen;
      actions.appendChild(button('Bu konudan yeni soru', 'primary', () => nextQuestion(sameGen)));
      primaryAction = () => nextQuestion(sameGen);
    }
    if (d.has_trace) {
      const traceBtn = button('Kodu adım adım izle', '');
      P.traceToggle(traceBtn, $('trace-box'), () => post('/api/practice/trace', { token }));
      actions.appendChild(traceBtn);
    }
    actions.appendChild(nextBtn);
    $('ask-actions').classList.add('hidden');
    actions.classList.remove('hidden');
    actions.querySelector('button').focus({ preventScroll: true });
    fb.scrollIntoView({ block: 'nearest' });
    renderUnits();

    const info = unitInfo(unit);
    if (info && before < info.topics.length && topicsDone(unit) === info.topics.length) {
      const next = units.find((u) => u.order > info.order);
      $('unit-done-text').textContent = next
        ? `Bu ünitedeki tüm konuları tamamladın. Sıradaki ünite: ${next.title}.`
        : 'Bu ünitedeki tüm konuları tamamladın. Bu son üniteydi.';
      $('btn-next-unit').classList.toggle('hidden', !next);
      $('btn-next-unit').onclick = next ? () => startUnit(next.id) : null;
      $('unit-done').classList.remove('hidden');
    }
  }

  $('btn-hint').addEventListener('click', showHint);
  $('btn-check').addEventListener('click', check);
  document.addEventListener('keydown', (e) => {
    if ($('question-view').classList.contains('hidden')) return;
    if (!checked && pickByKey($('answer-box'), e)) { e.preventDefault(); return; }
    if (e.key === 'Enter' && e.ctrlKey) {
      if (checked) { if (primaryAction) primaryAction(); } else check();
    }
  });

  loadUnits();
})();
