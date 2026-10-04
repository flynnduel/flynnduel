'use strict';
const { existsSync } = require('node:fs');

// Resolves { url } or { error }; never throws.
async function startTunnel(port, { loadCloudflared = () => import('cloudflared'), timeoutMs = 30000, log = console.log } = {}) {
  let tunnel = null;
  try {
    const mod = await loadCloudflared();
    const cf = mod && mod.Tunnel ? mod : (mod && mod.default) || {};
    const { bin, install, Tunnel } = cf;
    if (!Tunnel || typeof Tunnel.quick !== 'function') throw new Error('cloudflared module unavailable');
    if (bin && !existsSync(bin)) {
      log('Installing cloudflared…');
      await install(bin);
    }
    return await new Promise((resolve) => {
      let settled = false;
      let timer = null;
      const finish = (result) => {
        if (settled) return;
        settled = true;
        clearTimeout(timer);
        if (result.error && tunnel && typeof tunnel.stop === 'function') {
          try { tunnel.stop(); } catch { /* ignore */ }
        }
        resolve(result);
      };
      timer = setTimeout(() => finish({ error: 'timed out waiting for tunnel URL' }), timeoutMs);
      try {
        tunnel = Tunnel.quick('http://localhost:' + port);
      } catch (e) {
        return finish({ error: errMsg(e) });
      }
      tunnel.on('url', (url) => finish({ url }));
      tunnel.on('error', (e) => finish({ error: errMsg(e) }));
      tunnel.on('exit', (code) => finish({ error: 'cloudflared exited (' + code + ')' }));
    });
  } catch (e) {
    return { error: errMsg(e) };
  }
}

function errMsg(e) {
  return (e && e.message) || String(e);
}

module.exports = { startTunnel };
