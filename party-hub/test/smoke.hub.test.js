'use strict';
const test = require('node:test');
const assert = require('node:assert');
const { io } = require('socket.io-client');
const { createServer } = require('../server/index');

const PHOTO = 'data:image/jpeg;base64,' + Buffer.from([0xff, 0xd8, 0xff, 0xd9]).toString('base64');

async function boot() {
  const srv = await createServer({ port: 0, host: '127.0.0.1' });
  const url = 'http://127.0.0.1:' + srv.port;
  const clients = [];
  const connect = async () => {
    const s = io(url, { transports: ['websocket'], forceNew: true });
    s.views = [];
    s.fxs = [];
    s.on('view', (v) => s.views.push(v));
    s.on('fx', (f) => s.fxs.push(f));
    await new Promise((res) => s.on('connect', res));
    clients.push(s);
    return s;
  };
  const emit = (s, ev, p) => new Promise((res) => s.emit(ev, p, res));
  const until = async (fn) => { for (let i = 0; i < 100; i++) { if (fn()) return; await new Promise((r) => setTimeout(r, 20)); } throw new Error('timeout'); };
  const done = async () => { clients.forEach((c) => c.close()); await srv.close(); };
  return { srv, url, connect, emit, until, done };
}
const last = (s) => s.views[s.views.length - 1];

test('create + 2 join by code: all see 3 players with avatars', async () => {
  const h = await boot();
  try {
    const [a, b, c] = [await h.connect(), await h.connect(), await h.connect()];
    const ra = await h.emit(a, 'create', { name: 'Ann', token: 'ta' });
    assert.ok(ra.ok); assert.match(ra.code, /^[A-HJ-NP-Z]{4}$/); assert.ok(ra.playerId);
    const rb = await h.emit(b, 'join', { code: ra.code.toLowerCase(), name: 'Bob', token: 'tb' });
    const rc = await h.emit(c, 'join', { code: ra.code, name: 'Cy', token: 'tc', avatar: { kind: 'photo', data: PHOTO } });
    assert.ok(rb.ok && rc.ok);
    await h.until(() => [a, b, c].every((s) => last(s) && last(s).players.length === 3));
    for (const s of [a, b, c]) assert.ok(last(s).players.every((p) => p.avatarKind));
    assert.ok(!JSON.stringify([a, b, c].map((s) => s.views)).includes('data:image'));
    const svg = await fetch(`${h.url}/avatar/${ra.code}/${ra.playerId}.svg`);
    assert.strictEqual(svg.status, 200);
    assert.match(svg.headers.get('content-type'), /image\/svg\+xml/);
    assert.match(await svg.text(), /<svg/);
    const jpg = await fetch(`${h.url}/avatar/${ra.code}/${rc.playerId}.jpg`);
    assert.strictEqual(jpg.status, 200);
    assert.strictEqual(jpg.headers.get('content-type'), 'image/jpeg');
    assert.strictEqual(jpg.headers.get('x-content-type-options'), 'nosniff');
    assert.deepStrictEqual([...new Uint8Array(await jpg.arrayBuffer())], [0xff, 0xd8, 0xff, 0xd9]);
    assert.strictEqual((await fetch(`${h.url}/avatar/${ra.code}/${ra.playerId}.jpg`)).status, 404);
    assert.strictEqual((await fetch(`${h.url}/avatar/${ra.code}/${rc.playerId}.svg`)).status, 404);
    assert.strictEqual((await fetch(`${h.url}/avatar/ZZZZ/p1.svg`)).status, 404);
    const font = await fetch(`${h.url}/fonts/fredoka-latin-400-normal.woff2`);
    assert.strictEqual(font.status, 200);
  } finally { await h.done(); }
});

test('wrong code -> Room not found', async () => {
  const h = await boot();
  try {
    const a = await h.connect();
    assert.deepStrictEqual(await h.emit(a, 'join', { code: 'ZZZZ', name: 'A', token: 't' }), { ok: false, error: 'Room not found' });
    assert.deepStrictEqual(await h.emit(a, 'join', null), { ok: false, error: 'Room not found' });
  } finally { await h.done(); }
});

test('rejoin restores seat and secrets', async () => {
  const h = await boot();
  try {
    const a = await h.connect(); const b = await h.connect();
    const ra = await h.emit(a, 'create', { name: 'Ann', token: 'ta' });
    const rb = await h.emit(b, 'join', { code: ra.code, name: 'Bob', token: 'tb' });
    b.close();
    await h.until(() => last(a).players.find((p) => p.id === rb.playerId && !p.connected));
    const b2 = await h.connect();
    const rb2 = await h.emit(b2, 'join', { code: ra.code, name: 'Bob', token: 'tb' });
    assert.strictEqual(rb2.playerId, rb.playerId);
    await h.until(() => last(b2) && last(b2).me.id === rb.playerId);
    await h.until(() => last(a).players.find((p) => p.id === rb.playerId).connected);
  } finally { await h.done(); }
});

test('newer socket replaces old; old disconnect does not drop seat', async () => {
  const h = await boot();
  try {
    const a = await h.connect(); const b = await h.connect();
    const ra = await h.emit(a, 'create', { name: 'Ann', token: 'ta' });
    const a2 = await h.connect();
    await h.emit(a2, 'join', { code: ra.code, name: 'Ann', token: 'ta' });
    a.close();
    await new Promise((r) => setTimeout(r, 100));
    await h.emit(b, 'join', { code: ra.code, name: 'Bob', token: 'tb' });
    await h.until(() => last(a2).players.length === 2);
    assert.ok(last(a2).players.find((p) => p.id === ra.playerId).connected);
  } finally { await h.done(); }
});

test('act routes to room, chat is pushed; rate limit', async () => {
  const h = await boot();
  try {
    const a = await h.connect(); const b = await h.connect();
    const ra = await h.emit(a, 'create', { name: 'Ann', token: 'ta' });
    await h.emit(b, 'join', { code: ra.code, name: 'Bob', token: 'tb' });
    assert.ok((await h.emit(a, 'act', { type: 'chat', text: 'hi' })).ok);
    await h.until(() => last(b).chat.length === 1);
    assert.strictEqual((await h.emit(a, 'act', { type: 'nope' })).error, 'Not now');
    const rs = [];
    for (let i = 0; i < 30; i++) rs.push(h.emit(b, 'act', { type: 'nope' }));
    const res = await Promise.all(rs);
    assert.ok(res.some((r) => r.error === 'Slow down!'));
    const c = await h.connect();
    assert.strictEqual((await h.emit(c, 'act', { type: 'chat', text: 'x' })).error, 'Not now');
  } finally { await h.done(); }
});
