const test = require('node:test');
const assert = require('node:assert/strict');
const { isSusClue, roundEggs, gameEggs, EGG_TEXT } = require('../server/eggs');
const { Game } = require('../server/game');

const round = (over) => ({ imposterId: 'i', playerIds: ['i', 'a', 'b', 'c'], votes: {}, outcome: 'caught', ...over });

test('isSusClue', () => {
  assert.equal(isSusClue('SUS!'), true);
  assert.equal(isSusClue('sus'), true);
  assert.equal(isSusClue('suspect'), false);
});

test('hive mind', () => {
  assert.deepEqual(roundEggs(round({ votes: { i: 'a', a: 'i', b: 'i', c: 'i' } })), ['hive-mind']);
  assert.deepEqual(roundEggs(round({ votes: { i: 'a', a: 'i', b: 'i', c: 'a' } })), []);
});

test('flawless deception', () => {
  assert.deepEqual(roundEggs(round({ outcome: 'escaped', votes: { i: 'a', a: 'b', b: 'a', c: 'a' } })), ['flawless']);
  assert.deepEqual(roundEggs(round({ outcome: 'escaped', votes: { i: 'a', a: 'i', b: 'a', c: 'a' } })), []);
});

test('galaxy brain', () => {
  assert.ok(roundEggs(round({ outcome: 'stole', votes: { a: 'i', b: 'i', c: 'b' } })).includes('galaxy-brain'));
  assert.ok(!roundEggs(round({ outcome: 'caught', votes: { a: 'i', b: 'i', c: 'b' } })).includes('galaxy-brain'));
});

test('cancelled round has no eggs', () => {
  assert.deepEqual(roundEggs(round({ outcome: 'cancelled', votes: {} })), []);
});

test('from the bottom', () => {
  const ids = ['a', 'b', 'c'];
  const climb = [{ a: 2, b: 2, c: 0 }, { a: 2, b: 4, c: 2 }, { a: 2, b: 4, c: 6 }];
  assert.deepEqual(gameEggs(climb, ['c'], ids), ['from-the-bottom']);
  const tiedLow = [{ a: 2, b: 0, c: 0 }, { a: 2, b: 0, c: 4 }];
  assert.deepEqual(gameEggs(tiedLow, ['c'], ids), []);
  assert.deepEqual(gameEggs([{ a: 0, b: 2 }, { a: 4, b: 2 }], ['a'], ['a', 'b']), []); // needs 3+ players
});

test('egg text', () => {
  assert.equal(EGG_TEXT['hive-mind'], '🧠 HIVE MIND');
  assert.equal(EGG_TEXT.flawless, '🎭 FLAWLESS DECEPTION');
  assert.equal(EGG_TEXT['galaxy-brain'], '🌌 GALAXY BRAIN');
  assert.equal(EGG_TEXT['from-the-bottom'], '📈 FROM THE BOTTOM');
  assert.equal(EGG_TEXT.sus, '📮 Emergency meeting energy');
});

test('sus clue toasts and still counts', () => {
  const g = new Game({ rng: () => 0, pickWord: () => ({ category: 'Food', word: 'Pizza', secret: null }) });
  const ids = ['A', 'B', 'C'].map((n) => g.join(n, n).playerId);
  g.startGame(ids[0]);
  g.continueReveal(ids[0]);
  const active = g.round.turnOrder[0];
  assert.deepEqual(g.submitClue(active, 'sus'), { ok: true, toast: 'sus' });
  assert.equal(g.round.clues[0].text, 'sus');
});
