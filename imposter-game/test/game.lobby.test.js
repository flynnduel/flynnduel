const test = require('node:test');
const assert = require('node:assert/strict');
const { Game } = require('../server/game');

const mk = () => new Game({ rng: () => 0.5 });

test('first joiner is leader', () => {
  const g = mk();
  const a = g.join('Ana', 't1');
  const b = g.join('Ben', 't2');
  assert.ok(a.ok && b.ok);
  assert.equal(g.players[0].isLeader, true);
  assert.equal(g.players[1].isLeader, false);
  assert.equal(g.isLeader(a.playerId), true);
});

test('duplicate name case-insensitive', () => {
  const g = mk();
  g.join('Flynn', 't1');
  assert.deepEqual(g.join(' flynn ', 't2'), { ok: false, error: 'That name is taken' });
});

test('name validation', () => {
  const g = mk();
  assert.deepEqual(g.join('', 't1'), { ok: false, error: 'Enter a name' });
  assert.deepEqual(g.join('   ', 't1'), { ok: false, error: 'Enter a name' });
  assert.deepEqual(g.join('x'.repeat(17), 't1'), { ok: false, error: 'Name must be 16 characters or fewer' });
  assert.equal(g.join('x'.repeat(16), 't1').ok, true);
  assert.equal(g.players[0].name, 'x'.repeat(16));
});

test('rejoin by token keeps seat', () => {
  const g = mk();
  const { playerId } = g.join('Ana', 't1');
  g.disconnect(playerId);
  assert.equal(g.players[0].connected, false);
  const again = g.join('Different', 't1');
  assert.equal(again.playerId, playerId);
  assert.equal(g.players.length, 1);
  assert.equal(g.players[0].connected, true);
  assert.equal(g.players[0].name, 'Ana');
});

test('rejoin by name when disconnected', () => {
  const g = mk();
  const { playerId } = g.join('Ana', 't1');
  g.disconnect(playerId);
  assert.equal(g.join('ANA', 't9').playerId, playerId);
  assert.equal(g.players[0].token, 't9');
});

test('leader passes on disconnect', () => {
  const g = mk();
  const a = g.join('Ana', 't1').playerId;
  const b = g.join('Ben', 't2').playerId;
  g.join('Cy', 't3');
  g.disconnect(a);
  assert.equal(g.isLeader(b), true);
  assert.equal(g.isLeader(a), false);
  g.join('Ana', 't1');
  assert.equal(g.isLeader(b), true);
  assert.equal(g.players.filter((p) => p.isLeader).length, 1);
});

test('settings', () => {
  const g = mk();
  const a = g.join('Ana', 't1').playerId;
  const b = g.join('Ben', 't2').playerId;
  assert.deepEqual(g.settings, { passes: 2, target: 10 });
  assert.deepEqual(g.setSettings(b, { passes: 1 }), { ok: false, error: 'Only the leader can do that' });
  assert.deepEqual(g.setSettings(a, { passes: 4 }), { ok: false, error: 'Passes must be 1, 2 or 3' });
  assert.deepEqual(g.setSettings(a, { target: 31 }), { ok: false, error: 'Target must be between 3 and 30' });
  assert.deepEqual(g.setSettings(a, { target: 2 }), { ok: false, error: 'Target must be between 3 and 30' });
  assert.deepEqual(g.setSettings(a, { passes: 3, target: 15 }), { ok: true });
  assert.deepEqual(g.settings, { passes: 3, target: 15 });
});

test('game full at 12', () => {
  const g = mk();
  for (let i = 0; i < 12; i++) assert.equal(g.join(`P${i}`, `t${i}`).ok, true);
  assert.deepEqual(g.join('Extra', 'tx'), { ok: false, error: 'Game is full' });
});
