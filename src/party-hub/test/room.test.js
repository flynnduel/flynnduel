const test = require('node:test');
const assert = require('node:assert/strict');
const { Room } = require('../server/room');

function mk() {
  const clock = { t: 1000 };
  const room = new Room({ code: 'ABCD', rng: Math.random, now: () => clock.t });
  return { room, clock };
}

test('join, duplicate name, 12 max', () => {
  const { room } = mk();
  const a = room.join({ name: 'Ann', token: 'ta' });
  assert.equal(a.ok, true);
  assert.deepEqual(room.join({ name: ' ann ', token: 'tb' }), { ok: false, error: 'That name is taken' });
  assert.equal(room.join({ name: '', token: 'x' }).ok, false);
  assert.equal(room.join({ name: 'x'.repeat(17), token: 'x' }).ok, false);
  assert.equal(room.join({ name: 5, token: 'x' }).ok, false);
  for (let i = 1; i < 12; i++) assert.equal(room.join({ name: 'P' + i, token: 't' + i }).ok, true);
  const full = room.join({ name: 'Extra', token: 'te' });
  assert.equal(full.ok, false);
  assert.equal(room.players.size, 12);
});

test('player has documented shape and default avatar', () => {
  const { room, clock } = mk();
  const { playerId } = room.join({ name: 'Ann', token: 'ta' });
  const p = room.players.get(playerId);
  assert.equal(p.token, 'ta');
  assert.equal(p.connected, true);
  assert.equal(p.joinedAt, clock.t);
  assert.equal(p.team, null);
  assert.equal(p.spectator, false);
  assert.equal(p.points, 0);
  assert.equal(p.avatar.kind, 'dicebear');
});

test('a disconnected player frees their name', () => {
  const { room } = mk();
  const a = room.join({ name: 'Ann', token: 'ta' });
  room.disconnect(a.playerId);
  assert.equal(room.join({ name: 'ANN', token: 'tb' }).ok, true);
});

test('rejoin by token keeps seat', () => {
  const { room } = mk();
  const a = room.join({ name: 'Ann', token: 'ta' });
  room.join({ name: 'Bob', token: 'tb' });
  room.disconnect(a.playerId);
  assert.equal(room.players.get(a.playerId).connected, false);
  const r = room.reconnect('ta');
  assert.deepEqual(r, { ok: true, playerId: a.playerId });
  assert.equal(room.players.get(a.playerId).connected, true);
  assert.equal(room.players.size, 2);
  assert.equal(room.reconnect('nope').ok, false);
  assert.equal(room.reconnect(7).ok, false);
});

test('join with an existing token reuses the seat', () => {
  const { room } = mk();
  const a = room.join({ name: 'Ann', token: 'ta' });
  const again = room.join({ name: 'Ann', token: 'ta' });
  assert.deepEqual(again, { ok: true, playerId: a.playerId });
  assert.equal(room.players.size, 1);
});

test('host passes on disconnect and new host can act', () => {
  const { room, clock } = mk();
  const a = room.join({ name: 'Ann', token: 'ta' });
  clock.t++;
  const b = room.join({ name: 'Bob', token: 'tb' });
  clock.t++;
  const c = room.join({ name: 'Cy', token: 'tc' });
  assert.equal(room.isHost(a.playerId), true);
  assert.equal(room.isHost(b.playerId), false);
  room.disconnect(a.playerId);
  assert.equal(room.isHost(b.playerId), true);
  assert.equal(room.isHost(a.playerId), false);
  room.disconnect(b.playerId);
  assert.equal(room.isHost(c.playerId), true);
  room.reconnect('ta');
  assert.equal(room.isHost(c.playerId), true);
  assert.equal(room.isHost('nobody'), false);
});

test('emptySince set when last player disconnects, cleared on join', () => {
  const { room, clock } = mk();
  assert.equal(room.emptySince, null);
  const a = room.join({ name: 'Ann', token: 'ta' });
  const b = room.join({ name: 'Bob', token: 'tb' });
  room.disconnect(a.playerId);
  assert.equal(room.emptySince, null);
  clock.t = 5000;
  room.disconnect(b.playerId);
  assert.equal(room.emptySince, 5000);
  room.join({ name: 'Cy', token: 'tc' });
  assert.equal(room.emptySince, null);
});

test('chat limits and rate', () => {
  const { room, clock } = mk();
  const a = room.join({ name: 'Ann', token: 'ta' });
  const b = room.join({ name: 'Bob', token: 'tb' });
  assert.equal(room.chat(a.playerId, 'hi').ok, true);
  assert.deepEqual(room.chat(a.playerId, 'again'), { ok: false, error: 'Slow down!' });
  assert.equal(room.chat(b.playerId, 'other player ok').ok, true);
  clock.t += 1000;
  assert.equal(room.chat(a.playerId, 'x'.repeat(140)).ok, true);
  clock.t += 1000;
  assert.equal(room.chat(a.playerId, 'x'.repeat(141)).ok, false);
  assert.equal(room.chat(a.playerId, '   ').ok, false);
  assert.equal(room.chat(a.playerId, 42).ok, false);
  assert.deepEqual(room.chat('ghost', 'hi'), { ok: false, error: 'Not now' });
});

test('chat keeps last 50 and can be paused', () => {
  const { room, clock } = mk();
  const a = room.join({ name: 'Ann', token: 'ta' });
  for (let i = 0; i < 60; i++) {
    clock.t += 1000;
    room.chat(a.playerId, 'm' + i);
  }
  assert.equal(room.chatLog.length, 50);
  assert.equal(room.chatLog[0].text, 'm10');
  room.chatPaused = true;
  clock.t += 1000;
  assert.deepEqual(room.chat(a.playerId, 'hey'), { ok: false, error: 'Chat is paused — talk it out!' });
});

test('setAvatar validates', () => {
  const { room } = mk();
  const a = room.join({ name: 'Ann', token: 'ta' });
  assert.equal(room.setAvatar(a.playerId, { kind: 'dicebear', style: 'notionists', seed: 'q' }).ok, true);
  assert.equal(room.players.get(a.playerId).avatar.style, 'notionists');
  assert.equal(room.setAvatar(a.playerId, { kind: 'photo', data: 'data:image/png;base64,AA' }).ok, false);
  assert.deepEqual(room.setAvatar('ghost', { kind: 'dicebear', style: 'lorelei', seed: 'q' }), { ok: false, error: 'Not now' });
});

test('viewFor has no tokens or photo data', () => {
  const { room, clock } = mk();
  const photo = 'data:image/jpeg;base64,' + Buffer.alloc(50, 1).toString('base64');
  const a = room.join({ name: 'Ann', token: 'secret-a', avatar: { kind: 'photo', data: photo } });
  const b = room.join({ name: 'Bob', token: 'secret-b' });
  room.chat(a.playerId, 'yo');
  const v = room.viewFor(b.playerId);
  assert.equal(v.code, 'ABCD');
  assert.deepEqual(v.me, { id: b.playerId, name: 'Bob', isHost: false });
  assert.equal(v.players.length, 2);
  assert.deepEqual(v.players[0], { id: a.playerId, name: 'Ann', avatarKind: 'photo', connected: true, isHost: true });
  assert.equal(v.chat[0].text, 'yo');
  assert.equal(v.chat[0].name, 'Ann');
  const s = JSON.stringify(v);
  assert.ok(!s.includes('secret-'));
  assert.ok(!s.includes('base64'));
  assert.equal(room.viewFor('ghost'), null);
  assert.equal(room.getPhoto(a.playerId), photo);
  assert.equal(room.getPhoto(b.playerId), null);
  void clock;
});

test('act dispatches chat/setAvatar and rejects unknown', () => {
  const { room } = mk();
  const a = room.join({ name: 'Ann', token: 'ta' });
  assert.equal(room.act(a.playerId, { type: 'chat', text: 'hello' }).ok, true);
  assert.deepEqual(room.act(a.playerId, { type: 'zzz' }), { ok: false, error: 'Not now' });
  assert.deepEqual(room.act('ghost', { type: 'chat', text: 'x' }), { ok: false, error: 'Not now' });
  assert.deepEqual(room.act(a.playerId, null), { ok: false, error: 'Not now' });
});

test('returning player with a now-taken name gets a suffix and keeps the seat', () => {
  const { room } = mk();
  const a = room.join({ name: 'Ann', token: 'ta' });
  room.disconnect(a.playerId);
  const b = room.join({ name: 'Bob', token: 'tb' });
  room.join({ name: 'ann', token: 'tc' });
  assert.deepEqual(room.reconnect('ta'), { ok: true, playerId: a.playerId });
  assert.equal(room.players.get(a.playerId).name, 'Ann 2');
  assert.equal(room.join({ name: 'Ann', token: 'ta' }).playerId, a.playerId);
  void b;
});

test('suffix respects the 16 char limit', () => {
  const { room } = mk();
  const long = 'x'.repeat(16);
  const a = room.join({ name: long, token: 'ta' });
  room.disconnect(a.playerId);
  room.join({ name: long, token: 'tb' });
  room.reconnect('ta');
  const n = room.players.get(a.playerId).name;
  assert.equal(n.length, 16);
  assert.ok(n.endsWith(' 2'));
});

test('disconnect on an already-disconnected player is a no-op', () => {
  const { room, clock } = mk();
  const a = room.join({ name: 'Ann', token: 'ta' });
  clock.t = 2000;
  room.disconnect(a.playerId);
  clock.t = 9000;
  assert.deepEqual(room.disconnect(a.playerId), { ok: true });
  assert.equal(room.emptySince, 2000);
});

test('avatar: null is treated like no avatar', () => {
  const { room } = mk();
  const a = room.join({ name: 'Ann', token: 'ta', avatar: null });
  assert.equal(a.ok, true);
  assert.equal(room.players.get(a.playerId).avatar.kind, 'dicebear');
});
