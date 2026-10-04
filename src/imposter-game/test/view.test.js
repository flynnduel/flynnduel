const test = require('node:test');
const assert = require('node:assert/strict');
const { Game } = require('../server/game');
const { viewFor } = require('../server/view');

function setup() {
  const g = new Game({ rng: () => 0, pickWord: () => ({ category: 'Food', word: 'Pizza', secret: null }) });
  const ids = ['Ana', 'Ben', 'Cy', 'Dee'].map((n) => g.join(n, `secret-token-${n}`).playerId);
  g.setSettings(ids[0], { passes: 1 });
  return { g, ids, imp: ids[0], crew: ids.slice(1) };
}

const active = (g) => g.round.turnOrder[g.round.turnIndex];
const json = (v) => JSON.stringify(v).toLowerCase();

test('imposter never sees word before result', () => {
  const { g, ids, imp, crew } = setup();
  const seen = [];
  const look = () => {
    seen.push(g.phase);
    const v = viewFor(g, imp);
    assert.ok(!json(v).includes('pizza'), `word leaked in ${g.phase}`);
    assert.equal(v.round.word, null);
    assert.equal(v.round.role, 'imposter');
    assert.equal(v.round.imposterId, null);
  };
  g.startGame(imp); look();
  g.continueReveal(imp); look();
  while (g.phase === 'clues') g.submitClue(active(g), 'cheesy');
  look();
  g.startVote(imp); look();
  for (const id of crew) g.castVote(id, imp);
  g.castVote(imp, crew[0]);
  look();
  assert.deepEqual(seen, ['reveal', 'clues', 'discussion', 'vote', 'guess']);
  g.submitGuess(imp, 'pasta');
  assert.equal(viewFor(g, imp).round.word, 'Pizza');
  assert.equal(ids.length, 4);
});

test('crew sees word', () => {
  const { g, imp, crew } = setup();
  g.startGame(imp);
  const v = viewFor(g, crew[0]);
  assert.equal(v.round.word, 'Pizza');
  assert.equal(v.round.role, 'crew');
  assert.equal(v.round.category, 'Food');
  assert.equal(v.round.imposterId, null);
});

test('nobody sees others\' votes before reveal', () => {
  const { g, imp, crew } = setup();
  g.startGame(imp);
  g.continueReveal(imp);
  while (g.phase === 'clues') g.submitClue(active(g), 'cheesy');
  g.startVote(imp);
  g.castVote(crew[0], crew[1]);
  const mine = viewFor(g, crew[0]);
  assert.equal(mine.round.myVote, crew[1]);
  const other = viewFor(g, crew[2]);
  assert.equal(other.round.myVote, null);
  assert.equal(other.round.votes, null);
  assert.equal(other.round.tally, null);
  assert.equal(other.players.find((p) => p.id === crew[0]).hasVoted, true);
  assert.ok(!JSON.stringify(other).includes(`"${crew[0]}":"${crew[1]}"`));
});

test('result reveals all', () => {
  const { g, imp, crew } = setup();
  g.startGame(imp);
  g.continueReveal(imp);
  while (g.phase === 'clues') g.submitClue(active(g), 'cheesy');
  g.startVote(imp);
  for (const id of crew) g.castVote(id, imp);
  g.castVote(imp, crew[0]);
  g.submitGuess(imp, 'piza');
  for (const id of [imp, ...crew]) {
    const v = viewFor(g, id);
    assert.equal(v.phase, 'result');
    assert.equal(v.round.word, 'Pizza');
    assert.equal(v.round.imposterId, imp);
    assert.equal(v.round.votes[crew[0]], imp);
    assert.equal(v.round.tally[imp], 3);
    assert.equal(v.round.guess, 'piza');
    assert.equal(v.round.guessCorrect, true);
    assert.deepEqual(v.round.eggs, ['🧠 HIVE MIND', '🌌 GALAXY BRAIN']);
  }
});

test('waiting player', () => {
  const { g, imp } = setup();
  g.startGame(imp);
  const late = g.join('Late', 'tl').playerId;
  const v = viewFor(g, late);
  assert.equal(v.me.waiting, true);
  assert.equal(v.round.role, null);
  assert.equal(v.round.word, null);
  assert.equal(v.players.find((p) => p.id === late).inRound, false);
});

test('no token leaks', () => {
  const { g, ids, imp } = setup();
  g.startGame(imp);
  for (const id of ids) assert.ok(!JSON.stringify(viewFor(g, id)).includes('secret-token'));
});

test('lobby view', () => {
  const { g, ids } = setup();
  const v = viewFor(g, ids[1]);
  assert.equal(v.phase, 'lobby');
  assert.equal(v.round, null);
  assert.deepEqual(v.settings, { passes: 1, target: 10 });
  assert.deepEqual(v.me, { id: ids[1], name: 'Ben', isLeader: false, waiting: false });
  assert.equal(v.players.length, 4);
});

test('view exposes canCancel when imposter is gone', () => {
  const { g, imp, crew } = setup();
  g.startGame(imp);
  assert.equal(viewFor(g, crew[0]).canCancel, false);
  g.disconnect(imp);
  assert.equal(viewFor(g, crew[0]).canCancel, true);
});
