/* PyTest Pro - pratik modu */
'use strict';
(function () {
  const { esc, fmtAnswer, levelBadge, post, request, renderAnswer, renderQuestionText } = window.PyTest;
  const $ = (id) => document.getElementById(id);

  let unit = null;       // seçili ünite id
  let token = null;      // sunucudaki soru anahtarı
  let current = null;    // gösterilen soru
  let answer = '';
  let checked = false;
  const score = { right: 0, total: 0 };

  function view(id) {
    ['closed', 'units-view', 'question-view'].forEach((x) => $(x).classList.toggle('hidden', x !== id));
  }

  function updateScore() {
    $('score').classList.toggle('hidden', score.total === 0);
    $('score').textContent = `Bu oturumda ${score.right} / ${score.total} doğru`;
  }

  async function loadUnits() {
    const r = await request('/api/practice/units');
    if (r.status === 403) { view('closed'); return; }
    if (!r.ok) { view('closed'); $('closed').querySelector('h2').textContent = r.data.error || 'Sunucuya ulaşılamadı.'; return; }
    const grid = $('unit-grid');
    grid.innerHTML = '';
    r.data.forEach((u) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'unit-card';
      b.innerHTML = `<span class="unit-no">${u.order}</span>
        <span class="unit-body"><b>${esc(u.title)}</b>
        ${levelBadge(u.level)}
        <span class="muted small">${esc(u.description)}</span></span>`;
      b.addEventListener('click', () => { unit = u.id; nextQuestion(); });
      grid.appendChild(b);
    });
    view('units-view');
  }

  async function nextQuestion() {
    $('err').textContent = '';
    const r = await post('/api/practice/next', { unit });
    if (r.status === 403) { view('closed'); return; }
    if (!r.ok) { $('err').textContent = r.data.error || 'Soru alınamadı.'; return; }
    token = r.data.token;
    current = r.data.question;
    answer = '';
    checked = false;
    $('q-unit').textContent = r.data.unit;
    $('q-topic').textContent = 'Konu: ' + current.topic;
    renderQuestionText($('q-text'), $('q-code'), current);
    renderAnswer($('answer-box'), current, '', (v) => { answer = v; }, true);
    $('feedback').className = 'hidden';
    $('feedback').innerHTML = '';
    $('btn-check').classList.remove('hidden');
    $('btn-check').disabled = false;
    $('btn-next').classList.add('hidden');
    view('question-view');
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
      if (r.status === 404) nextQuestion();
      return;
    }
    checked = true;
    score.total += 1;
    if (r.data.correct) score.right += 1;
    updateScore();
    const d = r.data;
    $('feedback').className = 'sol ' + (d.correct ? 'ok' : 'no');
    $('feedback').innerHTML = `
      <div class="sol-head"><span class="${d.correct ? 'green-t' : 'red-t'}">${d.correct ? '✔ Doğru!' : '✘ Yanlış'}</span></div>
      <div class="sol-meta">
        ${!d.correct ? `<div><b>Doğru cevap:</b> <span class="ans green-t">${esc(fmtAnswer(d.type, d.answer))}</span></div>` : ''}
        ${d.note ? `<div class="muted">${d.note}</div>` : ''}
        <div class="exp"><b>Açıklama:</b> ${d.solution}</div>
      </div>`;
    $('btn-check').classList.add('hidden');
    $('btn-next').classList.remove('hidden');
    $('btn-next').focus();
  }

  $('btn-units').addEventListener('click', loadUnits);
  $('btn-check').addEventListener('click', check);
  $('btn-next').addEventListener('click', nextQuestion);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && e.ctrlKey && !$('question-view').classList.contains('hidden')) {
      if (checked) nextQuestion(); else check();
    }
  });

  loadUnits();
})();
