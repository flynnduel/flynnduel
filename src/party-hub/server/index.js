'use strict';
const http = require('node:http');
const os = require('node:os');
const path = require('node:path');
const express = require('express');
const { Server } = require('socket.io');
const { Rooms } = require('./rooms');
const { renderDicebear } = require('./avatar');
const { startTunnel } = require('./tunnel');

const SWEEP_MS = 60_000;
const ACT_LIMIT = 20;
const PHOTO_RE = /^data:image\/jpeg;base64,(.*)$/s;

function createServer({ port = 3000, host = '0.0.0.0', rooms = new Rooms() } = {}) {
  const app = express();
  app.disable('x-powered-by');
  app.use(express.static(path.join(__dirname, '..', 'public')));
  app.use('/fonts', express.static(path.dirname(require.resolve('@fontsource/fredoka/package.json')) + '/files'));

  const avatarOf = (req) => {
    const room = rooms.get(req.params.code);
    return room && room.players.has(req.params.playerId) ? { room, player: room.players.get(req.params.playerId) } : null;
  };
  app.get('/avatar/:code/:playerId.svg', (req, res) => {
    const f = avatarOf(req);
    if (!f || f.player.avatar.kind !== 'dicebear') return res.sendStatus(404);
    res.set('Content-Type', 'image/svg+xml').set('Cache-Control', 'no-cache').send(renderDicebear(f.player.avatar));
  });
  app.get('/avatar/:code/:playerId.jpg', (req, res) => {
    const f = avatarOf(req);
    const m = f && PHOTO_RE.exec(f.room.getPhoto(req.params.playerId) || '');
    if (!m) return res.sendStatus(404);
    res.set('Content-Type', 'image/jpeg').set('X-Content-Type-Options', 'nosniff').set('Cache-Control', 'no-cache')
      .send(Buffer.from(m[1], 'base64'));
  });

  const httpServer = http.createServer(app);
  const io = new Server(httpServer, { maxHttpBufferSize: 256 * 1024 });

  const bySocket = new Map(); // socket.id -> { room, playerId }
  const sockets = new Map(); // room -> Map(playerId -> socket)
  const timers = new Map(); // room -> { timer, at }

  const push = (room, afterTick = false) => {
    const bound = sockets.get(room);
    if (bound) {
      for (const [id, s] of bound) {
        const v = room.viewFor(id);
        if (v) s.emit('view', v);
      }
      for (const fx of room.takeFx()) for (const s of bound.values()) s.emit('fx', fx);
    } else {
      room.takeFx();
    }
    schedule(room, afterTick);
  };

  function schedule(room, afterTick = false) {
    const at = room.nextWakeAt();
    const cur = timers.get(room);
    if (cur && cur.at === at) return;
    if (cur) clearTimeout(cur.timer);
    timers.delete(room);
    if (at == null) return;
    const timer = setTimeout(() => {
      timers.delete(room);
      room.tick();
      push(room, true);
    }, Math.max(afterTick ? 50 : 0, at - room.now()));
    timer.unref();
    timers.set(room, { timer, at });
  }

  const unbind = (socket, { disconnectPlayer }) => {
    const b = bySocket.get(socket.id);
    if (!b) return;
    bySocket.delete(socket.id);
    const m = sockets.get(b.room);
    if (m && m.get(b.playerId) === socket) {
      m.delete(b.playerId);
      if (!m.size) sockets.delete(b.room);
      if (disconnectPlayer) {
        b.room.disconnect(b.playerId);
        push(b.room);
      }
    }
  };

  const bind = (socket, room, playerId) => {
    const prev = bySocket.get(socket.id);
    const same = prev && prev.room === room && prev.playerId === playerId;
    if (!same) unbind(socket, { disconnectPlayer: true });
    let m = sockets.get(room);
    if (!m) sockets.set(room, (m = new Map()));
    const old = m.get(playerId);
    if (old && old !== socket) {
      bySocket.delete(old.id);
      m.delete(playerId);
      old.disconnect(true);
    }
    m.set(playerId, socket);
    bySocket.set(socket.id, { room, playerId });
  };

  const reply = (ack, r) => { if (typeof ack === 'function') ack(r); };
  const obj = (x) => (x && typeof x === 'object' ? x : {});

  io.on('connection', (socket) => {
    let windowStart = 0;
    let count = 0;

    socket.on('create', (p, ack) => {
      p = obj(p);
      const room = rooms.create();
      const r = room.join({ name: p.name, token: p.token, avatar: p.avatar });
      if (!r.ok) {
        rooms.rooms.delete(room.code);
        return reply(ack, r);
      }
      bind(socket, room, r.playerId);
      reply(ack, { ok: true, code: room.code, playerId: r.playerId });
      push(room);
    });

    socket.on('join', (p, ack) => {
      p = obj(p);
      const room = rooms.get(p.code);
      if (!room) return reply(ack, { ok: false, error: 'Room not found' });
      const r = room.join({ name: p.name, token: p.token, avatar: p.avatar });
      if (!r.ok) return reply(ack, r);
      bind(socket, room, r.playerId);
      reply(ack, { ok: true, code: room.code, playerId: r.playerId });
      push(room);
    });

    socket.on('act', (action, ack) => {
      const now = Date.now();
      if (now - windowStart >= 1000) { windowStart = now; count = 0; }
      if (++count > ACT_LIMIT) return reply(ack, { ok: false, error: 'Slow down!' });
      const b = bySocket.get(socket.id);
      if (!b) return reply(ack, { ok: false, error: 'Not now' });
      let r;
      try { r = b.room.act(b.playerId, action); } catch { r = { ok: false, error: 'Not now' }; }
      reply(ack, r && typeof r === 'object' ? r : { ok: false, error: 'Not now' });
      push(b.room);
    });

    socket.on('disconnect', () => unbind(socket, { disconnectPlayer: true }));
  });

  const sweepTimer = setInterval(() => rooms.sweep(), SWEEP_MS);
  sweepTimer.unref();

  return new Promise((resolve, reject) => {
    httpServer.once('error', reject);
    httpServer.listen(port, host, () => {
      resolve({
        port: httpServer.address().port,
        close() {
          clearInterval(sweepTimer);
          for (const t of timers.values()) clearTimeout(t.timer);
          timers.clear();
          return new Promise((res) => {
            io.close(() => res());
            httpServer.closeAllConnections?.();
          });
        },
      });
    });
  });
}

function lanIp() {
  for (const list of Object.values(os.networkInterfaces())) {
    for (const i of list || []) if (i.family === 'IPv4' && !i.internal) return i.address;
  }
  return 'localhost';
}

async function main() {
  const port = Number(process.env.PORT) || 3000;
  const srv = await createServer({ port });
  const local = `http://${lanIp()}:${srv.port}`;
  console.log(`Party Hub running on ${local}`);
  let t;
  try { t = await startTunnel(srv.port); } catch (e) { t = { error: (e && e.message) || String(e) }; }
  if (t.url) {
    console.log(`Public URL: ${t.url}`);
    try { require('qrcode-terminal').generate(t.url, { small: true }); } catch { /* QR is optional */ }
  } else {
    console.log(`Tunnel unavailable (${t.error}) — friends on your Wi-Fi can use ${local}`);
  }
}

module.exports = { createServer };

if (require.main === module) {
  main().catch((e) => { console.error(e); process.exit(1); });
}
