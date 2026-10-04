'use strict';
const test = require('node:test');
const assert = require('node:assert');
const { EventEmitter } = require('node:events');
const { startTunnel } = require('../server/tunnel');

const quiet = () => {};
function fakeLoader(quick) {
  return async () => ({ bin: __filename, install: async () => {}, Tunnel: { quick } });
}

test('tunnel failure falls back to LAN', async () => {
  const r = await startTunnel(3000, { loadCloudflared: async () => { throw new Error('no network'); }, log: quiet });
  assert.match(r.error, /no network/);
  const r2 = await startTunnel(3000, { loadCloudflared: fakeLoader(() => { throw new Error('spawn fail'); }), log: quiet });
  assert.match(r2.error, /spawn fail/);
});

test('tunnel that never emits url times out', async () => {
  const r = await startTunnel(3000, { loadCloudflared: fakeLoader(() => Object.assign(new EventEmitter(), { stop() {} })), timeoutMs: 50, log: quiet });
  assert.match(r.error, /timed out/);
});

test('tunnel error event becomes { error }', async () => {
  const r = await startTunnel(3000, {
    loadCloudflared: fakeLoader(() => { const e = new EventEmitter(); e.stop = () => {}; setTimeout(() => e.emit('error', new Error('boom')), 5); return e; }),
    log: quiet,
  });
  assert.match(r.error, /boom/);
});

test('tunnel success returns url', async () => {
  let target;
  const r = await startTunnel(4321, {
    loadCloudflared: fakeLoader((t) => { target = t; const e = new EventEmitter(); setTimeout(() => e.emit('url', 'https://x.trycloudflare.com'), 5); return e; }),
    log: quiet,
  });
  assert.deepStrictEqual(r, { url: 'https://x.trycloudflare.com' });
  assert.strictEqual(target, 'http://localhost:4321');
});

test('installs binary when missing', async () => {
  let installed = null;
  const r = await startTunnel(1, {
    loadCloudflared: async () => ({
      bin: '/nonexistent/cloudflared-bin', install: async (p) => { installed = p; },
      Tunnel: { quick: () => { const e = new EventEmitter(); setTimeout(() => e.emit('url', 'https://y'), 5); return e; } },
    }),
    log: quiet,
  });
  assert.strictEqual(installed, '/nonexistent/cloudflared-bin');
  assert.strictEqual(r.url, 'https://y');
});
