// Single-page client. It only renders the view the server sends and forwards
// button presses; all game rules live on the server.
(() => {
  const $ = (id) => document.getElementById(id);
  const app = $('app');

  // ---- storage (may be unavailable: private mode, blocked site data) ----
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch { /* ignore */ } },
  };
  function newToken() {
    try { return crypto.randomUUID(); } catch { return Math.random().toString(36).slice(2) + Date.now().toString(36); }
  }
  let token = store.get('imposter.token');
  if (!token) { token = newToken(); store.set('imposter.token', token); }

  // ---- client state ----
  let view = null;
  let joinError = '';
  let roleOpen = false;
  let roleRound = 0;
  const drafts = {}; // input id -> text, so re-renders keep what people are typing

  const socket = io();

  socket.on('connect', () => {
    const name = store.get('imposter.name');
    if (view && name) join(name, true);
    else if (!view && name && store.get('imposter.joined') === '1') join(name, true);
  });
  socket.on('view', (v) => {
    // Hide the role card whenever the phase changes so the word never lingers on screen.
    if (!view || v.phase !== view.phase) roleOpen = false;
    if (v.round && v.round.number !== roleRound) { roleRound = v.round.number; roleOpen = false; }
    view = v;
    render();
  });
  socket.on('toast', ({ text }) => showToast(text));

  function join(name, silent) {
    socket.emit('join', { name, token }, (res) => {
      if (res.ok) {
        joinError = '';
        store.set('imposter.name', name.trim());
        store.set('imposter.joined', '1');
      } else if (!silent) {
        joinError = res.error;
        render();
      } else {
        store.set('imposter.joined', '0');
      }
    });
  }

  function send(type, args = {}) {
    socket.emit('action', { type, ...args }, (res) => {
      if (res && !res.ok) showToast(res.error);
    });
  }

  // ---- helpers ----
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const nameOf = (id) => (view.players.find((p) => p.id === id) || {}).name || '?';
  const isLeader = () => view && view.me.isLeader;
  const btn = (label, act, cls = '', extra = '') => `<button type="button" class="btn ${cls}" data-act="${act}" ${extra}>${label}</button>`;
  const leaderBtn = (label, act, cls = 'primary', extra = '') => (isLeader() ? btn(label, act, cls, extra) : '');

  let toastTimer = null;
  function showToast(text) {
    const t = $('toast');
    t.textContent = text;
    t.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { t.hidden = true; }, 3000);
  }

  // ---- rendering ----
  function render() {
    const focused = document.activeElement && document.activeElement.id;
    $('who').textContent = view ? `${view.me.isLeader ? '👑 ' : ''}${view.me.name}` : '';
    app.innerHTML = view ? screen() : joinScreen();
    for (const [id, text] of Object.entries(drafts)) {
      const el = $(id);
      if (el) el.value = text;
    }
    if (focused && $(focused)) $(focused).focus();
    else if (!view && $('name')) $('name').focus();
    renderRules();
  }

  function screen() {
    const paused = view.paused ? '<div class="banner paused">Waiting for players to reconnect…</div>' : '';
    if (view.me.waiting) return paused + waitingScreen();
    const screens = {
      lobby: lobbyScreen, reveal: revealScreen, clues: cluesScreen, discussion: discussionScreen,
      vote: voteScreen, guess: guessScreen, result: resultScreen, gameover: gameoverScreen,
    };
    return paused + (screens[view.phase] || lobbyScreen)();
  }

  function joinScreen() {
    return `
      <div class="card">
        <h1>Who's playing?</h1>
        <p class="muted">Everyone gets the secret word except the imposter. Find them before they figure it out.</p>
        <form id="join-form" autocomplete="off">
          <div class="field">
            <input type="text" id="name" maxlength="16" placeholder="Your name" aria-label="Your name" enterkeyhint="go">
            <button type="submit" class="btn primary">Join</button>
          </div>
          <div class="error" id="join-error">${esc(joinError)}</div>
        </form>
      </div>`;
  }

  function categoryBanner() {
    const r = view.round;
    return `<div class="banner ${r.secret === 'gambia' ? 'gambia' : ''}">
      <div class="label">${r.secret ? '✨ Secret category' : 'Category'}</div>
      <div class="value">${esc(r.category)}</div>
    </div>`;
  }

  function roleCard(mini) {
    const r = view.round;
    if (!r.role) return '';
    const imp = r.role === 'imposter';
    const inside = roleOpen
      ? (imp ? '<div class="word">You are the IMPOSTER</div><div class="hint">Blend in. You don\'t know the word.</div>'
        : `<div class="hint">The secret word is</div><div class="word">${esc(r.word)}</div>`)
      : `<div class="hint">${mini ? 'Tap to peek at your role' : 'Tap to reveal your role. Keep your screen hidden!'}</div>`;
    return `<button type="button" class="role ${mini ? 'mini' : ''} ${roleOpen && imp ? 'imposter' : ''}" data-act="toggleRole">${inside}</button>`;
  }

  function scoreboard(showPoints) {
    const pts = (view.round && view.round.points) || {};
    const rows = [...view.players].sort((a, b) => b.score - a.score).map((p) => `
      <li>
        <span class="grow">${p.isLeader ? '👑 ' : ''}${esc(p.name)}${p.connected ? '' : ' <span class="away">(away)</span>'}</span>
        ${showPoints && pts[p.id] ? `<span class="plus">+${pts[p.id]}</span>` : ''}
        <span class="score">${p.score}</span>
      </li>`).join('');
    return `<div class="card"><h2>Scores <span class="muted" style="font-size:14px;font-weight:400">· first to ${view.settings.target}</span></h2><ul class="list">${rows}</ul></div>`;
  }

  function waitingScreen() {
    return `<div class="card center"><h1>You're in! 🎉</h1>
      <p class="muted">A round is in progress. You'll be dealt in when the next one starts.</p></div>${scoreboard(false)}`;
  }

  function lobbyScreen() {
    const connected = view.players.filter((p) => p.connected).length;
    const players = view.players.map((p) => `
      <li><span class="grow">${p.isLeader ? '👑 ' : ''}${esc(p.name)}${p.id === view.me.id ? ' <span class="tag">you</span>' : ''}</span>
      ${p.connected ? '' : '<span class="away">away</span>'}</li>`).join('');
    const s = view.settings;
    const settings = isLeader()
      ? `<div class="settings-row"><label for="passes">Clue rounds</label>
           <select id="passes" data-setting="passes">${[1, 2, 3].map((n) => `<option ${n === s.passes ? 'selected' : ''}>${n}</option>`).join('')}</select></div>
         <div class="settings-row"><label for="target">Points to win</label>
           <input type="number" id="target" data-setting="target" min="3" max="30" value="${s.target}"></div>`
      : `<div class="settings-row"><span>Clue rounds</span><strong>${s.passes}</strong></div>
         <div class="settings-row"><span>Points to win</span><strong>${s.target}</strong></div>`;
    return `
      <div class="card">
        <h1>Lobby</h1>
        <p class="muted">Friends join at <strong>${esc(location.host)}</strong> on the same Wi-Fi.</p>
        <ul class="list">${players}</ul>
      </div>
      <div class="card"><h2>Settings</h2>${settings}</div>
      ${isLeader()
        ? btn(connected >= 3 ? 'Start game' : `Need ${3 - connected} more player${3 - connected === 1 ? '' : 's'}`, 'startGame', 'primary', connected >= 3 ? '' : 'disabled')
        : '<p class="center muted">Waiting for the leader to start…</p>'}`;
  }

  function revealScreen() {
    const inRound = view.players.filter((p) => p.inRound && p.connected);
    const ready = inRound.filter((p) => p.ready).length;
    const me = view.players.find((p) => p.id === view.me.id);
    return `${categoryBanner()}${roleCard(false)}
      ${me.ready ? `<p class="center muted">Waiting for others… (${ready}/${inRound.length} ready)</p>` : btn('Got it, I\'m ready', 'ready', 'primary')}
      ${leaderBtn('Everyone\'s ready, continue', 'continueReveal', '')}`;
  }

  function clueList() {
    const r = view.round;
    if (!r.clues.length) return '<p class="muted">No clues yet.</p>';
    let html = '';
    for (let pass = 1; pass <= r.passes; pass++) {
      const clues = r.clues.filter((c) => c.pass === pass);
      if (!clues.length) continue;
      if (r.passes > 1) html += `<div class="pass-label">Round ${pass}</div>`;
      html += `<ul class="list">${clues.map((c) => `<li><span class="grow">${esc(c.name)}</span><span class="clue">${esc(c.text)}</span></li>`).join('')}</ul>`;
    }
    return html;
  }

  function cluesScreen() {
    const r = view.round;
    const mine = r.turnPlayerId === view.me.id;
    const turn = mine
      ? `<div class="card"><h2>Your turn!</h2><p class="muted">One word that hints at the secret word.</p>
          <form id="clue-form" autocomplete="off"><div class="field">
            <input type="text" id="clue" maxlength="24" placeholder="Your clue" aria-label="Your clue" enterkeyhint="send">
            <button type="submit" class="btn primary">Send</button></div></form></div>`
      : `<div class="card center"><p>Waiting for <strong>${esc(nameOf(r.turnPlayerId))}</strong> to give a clue…</p></div>`;
    return `${categoryBanner()}${roleCard(true)}${turn}
      ${view.canSkip ? leaderBtn(`Skip ${esc(nameOf(r.turnPlayerId))}`, 'skip', '') : ''}
      <div class="card"><h2>Clues</h2>${clueList()}</div>`;
  }

  function discussionScreen() {
    return `${categoryBanner()}${roleCard(true)}
      <div class="card center"><h1>Talk it out 🗣️</h1><p class="muted">Who sounded like they didn't know the word?</p></div>
      <div class="card"><h2>Clues</h2>${clueList()}</div>
      ${leaderBtn('Start the vote', 'startVote')}`;
  }

  function voteScreen() {
    const r = view.round;
    const choices = view.players.filter((p) => p.inRound && p.id !== view.me.id && (!r.revote || r.candidates.includes(p.id)));
    const inRound = view.players.filter((p) => p.inRound);
    const status = inRound.map((p) => `<li><span class="grow">${esc(p.name)}</span>
      ${p.hasVoted ? '<span class="tag good">voted</span>' : `<span class="tag">${p.connected ? 'thinking…' : 'away'}</span>`}</li>`).join('');
    const canVote = view.players.find((p) => p.id === view.me.id).inRound;
    const picker = !canVote ? '' : r.myVote
      ? `<div class="card center"><p>You voted for <strong>${esc(nameOf(r.myVote))}</strong>.</p></div>`
      : `<div class="card"><h2>${r.revote ? 'Tie! Revote between:' : 'Who is the imposter?'}</h2>
          <div class="vote-grid">${choices.map((p) => `<button type="button" class="btn" data-act="vote" data-id="${p.id}">${esc(p.name)}</button>`).join('')}</div></div>`;
    return `${r.revote ? '<div class="banner"><div class="value">It\'s a tie!</div><div class="label">One more vote. Another tie and the imposter escapes.</div></div>' : ''}
      ${picker}
      <div class="card"><h2>Votes</h2><ul class="list">${status}</ul></div>
      ${leaderBtn('Close the vote now', 'closeVote', '')}
      <div class="card"><h2>Clues</h2>${clueList()}</div>`;
  }

  function guessScreen() {
    const r = view.round;
    const me = r.role === 'imposter';
    return `<div class="banner"><div class="label">Caught!</div><div class="value">${esc(nameOf(r.accusedId))} was voted out</div></div>
      ${me
        ? `<div class="card"><h2>Last chance 🎯</h2><p class="muted">Guess the secret word to steal a point. Category: <strong>${esc(r.category)}</strong></p>
            <form id="guess-form" autocomplete="off"><div class="field">
              <input type="text" id="guess" maxlength="40" placeholder="Your guess" aria-label="Your guess" enterkeyhint="send">
              <button type="submit" class="btn primary">Guess</button></div></form></div>`
        : `<div class="card center"><p><strong>${esc(nameOf(r.accusedId))}</strong> is the imposter! They're guessing the word…</p></div>`}
      <div class="card"><h2>Clues</h2>${clueList()}</div>`;
  }

  function outcomeHeadline() {
    const r = view.round;
    const imp = esc(nameOf(r.imposterId));
    if (r.outcome === 'cancelled') return ['Round cancelled', 'The imposter left the game. No points this round.'];
    if (r.outcome === 'stole') return ['Caught… but they guessed it!', `${imp} was the imposter and figured out the word.`];
    if (r.outcome === 'caught') return ['Crew wins! 🎉', `${imp} was the imposter and couldn't guess the word.`];
    if (r.accusedId) return [`${imp} got away! 😈`, `The crew voted out ${esc(nameOf(r.accusedId))}.`];
    return [`${imp} got away! 😈`, 'The vote tied twice, so nobody was voted out.'];
  }

  function guessLine() {
    const r = view.round;
    if (!r.guess) return '';
    const g = esc(r.guess);
    if (!r.guessCorrect) return `<p>Guessed "${g}" ✗</p>`;
    return r.guess.trim().toLowerCase() === String(r.word).toLowerCase() ? `<p>Guessed "${g}" ✓</p>` : `<p>Guessed "${g}" — close enough ✓</p>`;
  }

  function resultScreen() {
    const r = view.round;
    const [title, sub] = outcomeHeadline();
    const votes = r.votes && Object.keys(r.votes).length
      ? `<div class="card"><h2>Votes</h2><ul class="list">${Object.entries(r.votes).map(([v, t]) => `<li><span class="grow">${esc(nameOf(v))}</span><span>→ ${esc(nameOf(t))}${t === r.imposterId ? ' 🎯' : ''}</span></li>`).join('')}</ul></div>`
      : '';
    const atTarget = view.players.some((p) => p.score >= view.settings.target);
    return `${r.eggs.map((e) => `<div class="egg">${esc(e)}</div>`).join('')}
      <div class="card center"><h1>${title}</h1><p class="muted">${sub}</p>
        <div class="banner"><div class="label">The word was</div><div class="value">${esc(r.word)}</div></div>
        ${guessLine()}</div>
      ${scoreboard(true)}
      ${leaderBtn(atTarget ? 'See the winner 🏆' : 'Next round', 'nextRound')}
      ${isLeader() ? '' : '<p class="center muted">Waiting for the leader…</p>'}
      ${votes}
      <div class="card"><h2>Clues</h2>${clueList()}</div>`;
  }

  function gameoverScreen() {
    const names = (view.winners || []).map((id) => esc(nameOf(id)));
    return `${view.gameEggs.map((e) => `<div class="egg">${esc(e)}</div>`).join('')}
      <div class="card center"><h1>🏆 ${names.join(' & ')} win${names.length === 1 ? 's' : ''}!</h1></div>
      ${scoreboard(false)}
      ${leaderBtn('Play again', 'newGame')}
      ${isLeader() ? '' : '<p class="center muted">Waiting for the leader…</p>'}`;
  }

  // ---- rules overlay (always available) ----
  function renderRules() {
    const s = view ? view.settings : { passes: 2, target: 10 };
    $('rules-body').innerHTML = `
      <p>Everyone sees the <strong>category</strong>. Everyone except the <strong>imposter</strong> also sees the <strong>secret word</strong>. The imposter has to bluff.</p>
      <h3>A round</h3>
      <ol>
        <li><strong>Reveal:</strong> tap your card to see the word (or that you're the imposter). Keep it hidden!</li>
        <li><strong>Clues:</strong> taking turns, everyone types one word related to the secret word.</li>
        <li><strong>Discuss:</strong> talk it out. Who doesn't seem to know the word?</li>
        <li><strong>Vote:</strong> everyone secretly votes for who they think the imposter is.</li>
        <li><strong>Last chance:</strong> if the imposter is caught, they get one guess at the word.</li>
        <li><strong>Results:</strong> points are awarded and the next round begins.</li>
      </ol>
      <h3>Clues</h3>
      <p>One word only. You can't say the secret word or a version of it (like a plural).</p>
      <h3>Ties</h3>
      <p>If the vote ties, there's one revote between the tied players. If it ties again, the imposter escapes.</p>
      <h3>Scoring</h3>
      <table>
        <tr><th>What happened</th><th>Imposter</th><th>Everyone else</th></tr>
        <tr><td>Imposter not caught</td><td>+2</td><td>0</td></tr>
        <tr><td>Caught, but guessed the word</td><td>+1</td><td>0</td></tr>
        <tr><td>Caught and guessed wrong</td><td>0</td><td>+2 each</td></tr>
      </table>
      <h3>This game</h3>
      <p>${s.passes} clue round${s.passes === 1 ? '' : 's'} · first to <strong>${s.target}</strong> points wins.</p>
      <p class="muted">Small typos in the imposter's guess are forgiven. Capital letters never matter.</p>`;
  }

  function openRules() { $('rules').hidden = false; $('rules-close').focus(); }
  function closeRules() { $('rules').hidden = true; }
  $('help').addEventListener('click', openRules);
  $('rules-close').addEventListener('click', closeRules);
  $('rules').addEventListener('click', (e) => { if (e.target.id === 'rules') closeRules(); });

  // ---- events ----
  app.addEventListener('click', (e) => {
    const el = e.target.closest('[data-act]');
    if (!el || el.disabled) return;
    const act = el.dataset.act;
    if (act === 'toggleRole') { roleOpen = !roleOpen; render(); return; }
    if (act === 'vote') { send('vote', { targetId: el.dataset.id }); return; }
    send(act);
  });

  app.addEventListener('input', (e) => {
    if (e.target.id) drafts[e.target.id] = e.target.value;
    if (e.target.id === 'name' && joinError) { joinError = ''; $('join-error').textContent = ''; }
  });

  app.addEventListener('change', (e) => {
    const key = e.target.dataset.setting;
    if (key) {
      delete drafts[e.target.id];
      send('settings', { [key]: Number(e.target.value) });
    }
  });

  app.addEventListener('submit', (e) => {
    e.preventDefault();
    const form = e.target.id;
    if (form === 'join-form') { join($('name').value, false); return; }
    const fieldId = { 'clue-form': 'clue', 'guess-form': 'guess' }[form];
    if (!fieldId) return;
    const text = $(fieldId).value;
    socket.emit('action', { type: fieldId, text }, (res) => {
      if (res.ok) { delete drafts[fieldId]; } else { showToast(res.error); }
    });
  });

  // ---- easter egg 7: chameleon mode ----
  const KONAMI = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];
  let konami = 0;
  function toggleChameleon() {
    document.body.classList.toggle('chameleon');
    showToast(document.body.classList.contains('chameleon') ? '🦎 Chameleon mode!' : 'Chameleon mode off');
  }
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeRules();
    const key = e.key.length === 1 ? e.key.toLowerCase() : e.key;
    konami = key === KONAMI[konami] ? konami + 1 : (key === KONAMI[0] ? 1 : 0);
    if (konami === KONAMI.length) { konami = 0; toggleChameleon(); }
  });
  let logoTaps = [];
  $('logo').addEventListener('click', () => {
    const now = Date.now();
    logoTaps = logoTaps.filter((t) => now - t < 3000).concat(now);
    if (logoTaps.length >= 7) { logoTaps = []; toggleChameleon(); }
  });

  // Pre-fill the name a returning device used last time.
  const lastName = store.get('imposter.name');
  if (lastName) drafts.name = lastName;
  render();
})();
