const test = require('node:test');
const assert = require('node:assert/strict');
const { Game } = require('../server/game');
const { CLUE_ERROR_CLOSE } = require('../server/rules');

const stubPick = () => ({ category: 'Food', word: 'Pizza', secret: null });

// 4 players; rng 0 makes playerIds[0] (the leader, P0) the imposter.
function setup({ n = 4, passes = 1, target = 10 } = {}) {
  let t = 0;
  const g = new Game({ rng: () => 0, pickWord: stubPick, now: () => t });
  const ids = [];
  for (let i = 0; i < n; i++) ids.push(g.join(`P${i}`, `t${i}`).playerId);
  g.setSettings(ids[0], { passes, target });
  return { g, ids, leader: ids[0], imp: ids[0], crew: ids.slice(1), tick: (ms) => { t += ms; } };
}

const active = (g) => g.round.turnOrder[g.round.turnIndex];

function toClues(s) {
  assert.equal(s.g.startGame(s.leader).ok, true);
  for (const id of s.g.round.playerIds) s.g.setReady(id);
}

function toDiscussion(s) {
  toClues(s);
  let k = 0;
  while (s.g.phase === 'clues') assert.equal(s.g.submitClue(active(s.g), `clue${k++}`).ok, true);
}

function toVote(s) {
  toDiscussion(s);
  assert.equal(s.g.startVote(s.leader).ok, true);
}

function voteAll(g, map) {
  for (const [voter, target] of Object.entries(map)) assert.equal(g.castVote(voter, target).ok, true, voter);
}

const score = (g, id) => g.player(id).score;

test('start needs 3', () => {
  const g = new Game();
  const a = g.join('A', 'a').playerId;
  g.join('B', 'b');
  assert.deepEqual(g.startGame(a), { ok: false, error: 'Need at least 3 players' });
});

test('start deals a round', () => {
  const s = setup();
  assert.equal(s.g.startGame(s.ids[1]).error, 'Only the leader can do that');
  assert.equal(s.g.startGame(s.leader).ok, true);
  assert.equal(s.g.phase, 'reveal');
  assert.equal(s.g.round.word, 'Pizza');
  assert.equal(s.g.round.imposterId, s.imp);
  assert.deepEqual([...s.g.round.turnOrder].sort(), [...s.ids].sort());
});

test('reveal → clues when all ready', () => {
  const s = setup();
  s.g.startGame(s.leader);
  for (const id of s.ids.slice(0, 3)) s.g.setReady(id);
  assert.equal(s.g.phase, 'reveal');
  s.g.setReady(s.ids[3]);
  assert.equal(s.g.phase, 'clues');
});

test('continueReveal by leader', () => {
  const s = setup();
  s.g.startGame(s.leader);
  assert.equal(s.g.continueReveal(s.ids[1]).ok, false);
  assert.equal(s.g.continueReveal(s.leader).ok, true);
  assert.equal(s.g.phase, 'clues');
});

test('clue turn order and passes', () => {
  const s = setup({ passes: 2 });
  toClues(s);
  const notActive = s.ids.find((id) => id !== active(s.g));
  assert.equal(s.g.submitClue(notActive, 'cheesy').ok, false);
  const a = active(s.g);
  assert.deepEqual(s.g.submitClue(a, 'pizza'), { ok: false, error: CLUE_ERROR_CLOSE });
  assert.equal(active(s.g), a);
  for (let i = 0; i < 8; i++) {
    assert.equal(s.g.phase, 'clues');
    assert.equal(s.g.submitClue(active(s.g), `c${i}`).ok, true);
  }
  assert.equal(s.g.phase, 'discussion');
  assert.equal(s.g.round.clues.length, 8);
  assert.deepEqual(s.g.round.clues.map((c) => c.pass), [1, 1, 1, 1, 2, 2, 2, 2]);
});

test('skip after 30s', () => {
  const s = setup();
  toClues(s);
  s.tick(29999);
  assert.equal(s.g.canSkip(), false);
  assert.equal(s.g.skipTurn(s.leader).ok, false);
  s.tick(1);
  assert.equal(s.g.canSkip(), true);
  const a = active(s.g);
  assert.equal(s.g.skipTurn(s.leader).ok, true);
  assert.deepEqual(s.g.round.clues[0], { playerId: a, text: '—', pass: 1 });
  assert.equal(s.g.canSkip(), false); // timer restarted for next player
});

test('skip immediately when active player disconnected', () => {
  const s = setup();
  toClues(s);
  let a = active(s.g);
  if (a === s.leader) { s.g.submitClue(a, 'x1'); a = active(s.g); }
  s.g.disconnect(a);
  assert.equal(s.g.canSkip(), true);
});

test('imposter escaped', () => {
  const s = setup();
  toVote(s);
  const [c1, c2, c3] = s.crew;
  voteAll(s.g, { [s.imp]: c1, [c1]: c2, [c2]: c1, [c3]: c1 });
  assert.equal(s.g.phase, 'result');
  assert.equal(s.g.round.accusedId, c1);
  assert.equal(s.g.round.outcome, 'escaped');
  assert.equal(score(s.g, s.imp), 2);
  assert.equal(score(s.g, c1), 0);
});

function catchImposter(s) {
  toVote(s);
  const [c1, c2, c3] = s.crew;
  voteAll(s.g, { [s.imp]: c1, [c1]: s.imp, [c2]: s.imp, [c3]: s.imp });
  assert.equal(s.g.phase, 'guess');
}

test('imposter caught, correct guess', () => {
  const s = setup();
  catchImposter(s);
  assert.equal(s.g.submitGuess(s.crew[0], 'pizza').ok, false);
  assert.equal(s.g.submitGuess(s.imp, 'piza').ok, true);
  assert.equal(s.g.round.outcome, 'stole');
  assert.equal(s.g.round.guessCorrect, true);
  assert.equal(score(s.g, s.imp), 1);
  for (const c of s.crew) assert.equal(score(s.g, c), 0);
});

test('imposter caught, wrong guess', () => {
  const s = setup();
  catchImposter(s);
  s.g.submitGuess(s.imp, 'pasta');
  assert.equal(s.g.round.outcome, 'caught');
  assert.equal(score(s.g, s.imp), 0);
  for (const c of s.crew) assert.equal(score(s.g, c), 2);
  assert.deepEqual(s.g.scoreHistory.length, 1);
});

test('empty guess rejected', () => {
  const s = setup();
  catchImposter(s);
  assert.deepEqual(s.g.submitGuess(s.imp, '   '), { ok: false, error: 'Type a guess' });
  assert.equal(s.g.phase, 'guess');
});

test('tie then revote resolves', () => {
  const s = setup();
  toVote(s);
  const [c1, c2, c3] = s.crew;
  voteAll(s.g, { [s.imp]: c1, [c1]: s.imp, [c2]: s.imp, [c3]: c1 });
  assert.equal(s.g.phase, 'vote');
  assert.equal(s.g.round.revote, true);
  assert.deepEqual([...s.g.round.candidates].sort(), [s.imp, c1].sort());
  assert.deepEqual(s.g.castVote(c2, c3), { ok: false, error: 'Pick one of the tied players' });
  voteAll(s.g, { [s.imp]: c1, [c1]: s.imp, [c2]: s.imp, [c3]: s.imp });
  assert.equal(s.g.phase, 'guess');
  assert.equal(s.g.round.accusedId, s.imp);
});

test('double tie → escaped', () => {
  const s = setup();
  toVote(s);
  const [c1, c2, c3] = s.crew;
  voteAll(s.g, { [s.imp]: c1, [c1]: s.imp, [c2]: s.imp, [c3]: c1 });
  voteAll(s.g, { [s.imp]: c1, [c1]: s.imp, [c2]: s.imp, [c3]: c1 });
  assert.equal(s.g.phase, 'result');
  assert.equal(s.g.round.outcome, 'escaped');
  assert.equal(s.g.round.accusedId, null);
  assert.equal(score(s.g, s.imp), 2);
});

test('no self vote, no double vote', () => {
  const s = setup();
  toVote(s);
  const [c1, c2] = s.crew;
  assert.equal(s.g.castVote(c1, c1).ok, false);
  assert.equal(s.g.castVote(c1, c2).ok, true);
  assert.equal(s.g.castVote(c1, s.imp).ok, false);
});

test('vote resolves when all connected voted', () => {
  const s = setup();
  toVote(s);
  const [c1, c2, c3] = s.crew;
  voteAll(s.g, { [s.imp]: c1, [c1]: s.imp, [c2]: s.imp });
  assert.equal(s.g.phase, 'vote');
  s.g.disconnect(c3);
  assert.equal(s.g.phase, 'guess');
});

test('closeVote counts received votes', () => {
  const s = setup();
  toVote(s);
  assert.deepEqual(s.g.closeVote(s.leader), { ok: false, error: 'No votes yet' });
  const [c1, c2] = s.crew;
  voteAll(s.g, { [c1]: c2, [c2]: c1, [s.imp]: c2 });
  assert.equal(s.g.closeVote(s.ids[1]).ok, false);
  assert.equal(s.g.closeVote(s.leader).ok, true);
  assert.equal(s.g.round.outcome, 'escaped');
  assert.equal(s.g.round.accusedId, c2);
});

test('imposter gone at vote → cancelled', () => {
  const s = setup();
  // Make a crew member leader so the leader can act while the imposter is away.
  toDiscussion(s);
  s.g.disconnect(s.imp);
  const newLeader = s.g.players.find((p) => p.isLeader).id;
  assert.equal(s.g.startVote(newLeader).ok, true);
  assert.equal(s.g.phase, 'result');
  assert.equal(s.g.round.outcome, 'cancelled');
  for (const id of s.ids) assert.equal(score(s.g, id), 0);
});

test('paused under 3', () => {
  const s = setup();
  toClues(s);
  const others = s.ids.filter((id) => id !== active(s.g));
  s.g.disconnect(others[0]);
  s.g.disconnect(others[1]);
  assert.equal(s.g.paused, true);
  assert.deepEqual(s.g.submitClue(active(s.g), 'cheesy'), { ok: false, error: 'Waiting for players to reconnect' });
  s.g.join('x', `t${s.ids.indexOf(others[0])}`);
  assert.equal(s.g.paused, false);
});

test('mid-round joiner waits then is dealt in', () => {
  const s = setup();
  toClues(s);
  const late = s.g.join('Late', 'tl').playerId;
  assert.ok(s.g.waiting.includes(late));
  assert.ok(!s.g.round.playerIds.includes(late));
  while (s.g.phase === 'clues') s.g.submitClue(active(s.g), 'cheesy');
  s.g.startVote(s.leader);
  s.g.closeVote(s.leader); // no votes → error, so vote properly
  voteAll(s.g, Object.fromEntries(s.ids.map((id) => [id, id === s.crew[0] ? s.crew[1] : s.crew[0]])));
  assert.equal(s.g.phase, 'result');
  assert.equal(s.g.nextRound(s.leader).ok, true);
  assert.ok(s.g.round.playerIds.includes(late));
  assert.deepEqual(s.g.waiting, []);
});

test('game over at target and shared win', () => {
  const s = setup({ target: 3 });
  toVote(s);
  s.g.player(s.crew[0]).score = 4;
  s.g.player(s.crew[1]).score = 4;
  const [c1, c2, c3] = s.crew;
  voteAll(s.g, { [s.imp]: c1, [c1]: c2, [c2]: c1, [c3]: c1 });
  assert.equal(s.g.phase, 'result');
  assert.equal(s.g.nextRound(s.leader).ok, true);
  assert.equal(s.g.phase, 'gameover');
  assert.deepEqual([...s.g.winners].sort(), [c1, c2].sort());
  assert.equal(s.g.newGame(s.leader).ok, true);
  assert.equal(s.g.phase, 'lobby');
  assert.equal(s.g.startGame(s.leader).ok, true);
  assert.equal(score(s.g, c1), 0);
});

test('settings locked after start', () => {
  const s = setup();
  s.g.startGame(s.leader);
  assert.deepEqual(s.g.setSettings(s.leader, { passes: 3 }), { ok: false, error: 'Not now' });
});

test('imposter gone during guess → leader can cancel round', () => {
  const s = setup();
  const newLeaderGame = s.g;
  catchImposter(s);
  newLeaderGame.disconnect(s.imp);
  assert.equal(newLeaderGame.canCancel(), true);
  const leader = newLeaderGame.players.find((p) => p.isLeader).id;
  assert.equal(newLeaderGame.cancelRound(s.crew[2]).ok, s.crew[2] === leader);
  if (s.crew[2] !== leader) assert.equal(newLeaderGame.cancelRound(leader).ok, true);
  assert.equal(newLeaderGame.phase, 'result');
  assert.equal(newLeaderGame.round.outcome, 'cancelled');
  for (const id of s.ids) assert.equal(score(newLeaderGame, id), 0);
});

test('cannot cancel a healthy round', () => {
  const s = setup();
  toVote(s);
  assert.equal(s.g.canCancel(), false);
  assert.deepEqual(s.g.cancelRound(s.leader), { ok: false, error: 'Not now' });
});

test('paused round can be cancelled and newcomers dealt in', () => {
  const s = setup({ n: 3 });
  toDiscussion(s);
  s.g.disconnect(s.crew[1]);
  assert.equal(s.g.paused, true);
  const n1 = s.g.join('New1', 'n1').playerId;
  s.g.join('New2', 'n2');
  assert.equal(s.g.paused, true);
  assert.equal(s.g.cancelRound(s.leader).ok, true);
  assert.equal(s.g.phase, 'result');
  assert.equal(s.g.paused, false); // 4 connected incl. waiting players
  assert.equal(s.g.nextRound(s.leader).ok, true);
  assert.equal(s.g.phase, 'reveal');
  assert.ok(s.g.round.playerIds.includes(n1));
});
