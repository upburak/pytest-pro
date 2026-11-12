/* PyTest Pro - pratik modu: ipucu, yanlışın nedeni, kod izi, aynı konudan yeni soru, konu tamamlama */
'use strict';
(function () {
  const P = window.PyTest;
  const { esc, fmtAnswer, levelBadge, post, request, renderAnswer, renderQuestionText } = P;
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
    ['closed', 'units-view', 'question-view'].forEach((x) => $(x).classList.toggle('hidden', x !== id));
  }

  function updateScore() {
    $('score').classList.toggle('hidden', score.total === 0);
    $('score').textContent = `${score.right} / ${score.total} doğru`;
  }

  async function loadUnits() {
    const r = await request('/api/practice/units');
    if (r.status === 403) { view('closed'); return; }
    if (!r.ok) { view('closed'); $('closed').querySelector('h2').textContent = r.data.error || 'Sunucuya ulaşılamadı.'; return; }
    units = r.data;
    const grid = $('unit-grid');
    grid.innerHTML = '';
    units.forEach((u) => {
      const li = document.createElement('li');
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'unit-card';
      const done = completedTopics(u.id);
      const progress = load()[u.id]
        ? `<span class="topic-progress">${done.length} / ${u.topics.length} konu tamamlandı</span>`
          + (done.length ? `<span class="muted small">Tamamlanan: ${done.map(esc).join(', ')}</span>` : '')
        : '';
      b.innerHTML = `<span class="unit-no">${u.order}</span>
        <span class="unit-body"><b>${esc(u.title)}</b><span class="muted">${esc(u.description)}</span>${progress}</span>
        ${levelBadge(u.level)}`;
      b.addEventListener('click', () => startUnit(u.id));
      li.appendChild(b);
      grid.appendChild(li);
    });
    view('units-view');
  }

  function startUnit(id) {
    unit = id;
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
    renderQuestionText($('q-text'), $('q-code'), current);
    renderAnswer($('answer-box'), current, '', (v) => { answer = v; }, true);
    ['hint-box', 'feedback', 'trace-box', 'after-actions'].forEach((id) => $(id).classList.add('hidden'));
    $('feedback').innerHTML = '';
    $('trace-box').innerHTML = '';
    $('ask-actions').classList.remove('hidden');
    $('btn-hint').classList.toggle('hidden', !hasHint);
    $('btn-hint').disabled = false;
    $('btn-check').disabled = false;
    view('question-view');
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

    const fb = $('feedback');
    fb.className = 'sol ' + (d.correct ? 'ok' : 'no');
    if (d.correct) {
      fb.innerHTML = `
        <div class="sol-head"><span class="pen-note green-t">Doğru${usedHint ? ' (ipucuyla)' : ''}</span></div>
        ${mastered ? `<p class="muted">Bu konuyu tamamladın: ${esc(topic)}</p>` : ''}
        <div class="sol-meta"><div class="exp"><b>Açıklama:</b> ${d.solution}</div></div>`;
    } else {
      fb.innerHTML = `
        <div class="sol-head"><span class="pen-note">Yanlış</span></div>
        ${d.why ? P.whyNote(d.why) : ''}
        <div class="sol-meta">
          <div><b>Doğru cevap:</b> <span class="ans green-t">${esc(fmtAnswer(d.type, d.answer))}</span></div>
          ${d.note && d.note !== d.why ? `<div class="muted">${d.note}</div>` : ''}
          <div class="exp"><b>Açıklama:</b> ${d.solution}</div>
        </div>`;
    }

    const actions = $('after-actions');
    actions.innerHTML = '';
    const nextBtn = button('Yeni soru', d.correct ? 'green' : '', () => nextQuestion(null));
    if (d.correct) {
      primaryAction = () => nextQuestion(null);
    } else {
      const sameGen = gen;
      actions.appendChild(button('Bu konudan yeni soru', 'green', () => nextQuestion(sameGen)));
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
    actions.querySelector('button').focus();

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

  $('btn-units').addEventListener('click', loadUnits);
  $('btn-hint').addEventListener('click', showHint);
  $('btn-check').addEventListener('click', check);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && e.ctrlKey && !$('question-view').classList.contains('hidden')) {
      if (checked) { if (primaryAction) primaryAction(); } else check();
    }
  });

  loadUnits();
})();
