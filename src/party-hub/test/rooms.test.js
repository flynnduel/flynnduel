const test = require('node:test');
const assert = require('node:assert/strict');
const { Rooms } = require('../server/rooms');

test('create gives unique 4-letter codes without I/O', () => {
  const rooms = new Rooms({ rng: Math.random, now: Date.now });
  const seen = new Set();
  for (let i = 0; i < 1000; i++) {
    const r = rooms.create();
    assert.match(r.code, /^[ABCDEFGHJKLMNPQRSTUVWXYZ]{4}$/);
    assert.ok(!seen.has(r.code));
    seen.add(r.code);
  }
});

test('create retries on code collision', () => {
  const seq = [0, 0, 0, 0, 0, 0, 0, 0, 0.5, 0.5, 0.5, 0.5];
  let i = 0;
  const rooms = new Rooms({ rng: () => seq[i++] ?? 0.9, now: () => 0 });
  const a = rooms.create();
  const b = rooms.create();
  assert.equal(a.code, 'AAAA');
  assert.notEqual(b.code, 'AAAA');
});

test('get is case-insensitive', () => {
  const rooms = new Rooms({ rng: Math.random, now: Date.now });
  const r = rooms.create();
  assert.equal(rooms.get(r.code.toLowerCase()), r);
  assert.equal(rooms.get(' ' + r.code.toLowerCase() + ' '), r);
  assert.equal(rooms.get('ZZZZ' === r.code ? 'YYYY' : 'ZZZZ'), null);
  assert.equal(rooms.get(undefined), null);
  assert.equal(rooms.get(12), null);
});

test('sweep deletes after 30 min empty', () => {
  let t = 1000;
  const rooms = new Rooms({ rng: Math.random, now: () => t });
  const r = rooms.create();
  const { playerId } = r.join({ name: 'Ann', token: 't1' });
  rooms.sweep();
  assert.equal(rooms.get(r.code), r);
  r.disconnect(playerId);
  t += 1_799_999;
  rooms.sweep();
  assert.equal(rooms.get(r.code), r);
  t += 1;
  rooms.sweep();
  assert.equal(rooms.get(r.code), null);
});

test('sweep keeps room if someone rejoined', () => {
  let t = 0;
  const rooms = new Rooms({ rng: Math.random, now: () => t });
  const r = rooms.create();
  const { playerId } = r.join({ name: 'Ann', token: 't1' });
  r.disconnect(playerId);
  t += 1_000_000;
  r.reconnect('t1');
  t += 1_000_000;
  rooms.sweep();
  assert.equal(rooms.get(r.code), r);
});

test('sweep deletes a room nobody ever joined', () => {
  let t = 0;
  const rooms = new Rooms({ rng: Math.random, now: () => t });
  const r = rooms.create();
  t = 1_800_000;
  rooms.sweep();
  assert.equal(rooms.get(r.code), null);
});
