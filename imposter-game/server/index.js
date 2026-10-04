// HTTP + Socket.IO wiring (spec §3). Clients send intents; every client gets
// its own view (via view.js) after anything changes.
const http = require('node:http');
const os = require('node:os');
const path = require('node:path');
const express = require('express');
const { Server } = require('socket.io');
const { Game } = require('./game');
const { viewFor } = require('./view');
const { EGG_TEXT } = require('./eggs');

const SKIP_AFTER_MS = 30000;

const ACTIONS = {
  ready: (g, id) => g.setReady(id),
  continueReveal: (g, id) => g.continueReveal(id),
  clue: (g, id, a) => g.submitClue(id, a.text),
  skip: (g, id) => g.skipTurn(id),
  startVote: (g, id) => g.startVote(id),
  vote: (g, id, a) => g.castVote(id, a.targetId),
  closeVote: (g, id) => g.closeVote(id),
  guess: (g, id, a) => g.submitGuess(id, a.text),
  nextRound: (g, id) => g.nextRound(id),
  newGame: (g, id) => g.newGame(id),
  startGame: (g, id) => g.startGame(id),
  settings: (g, id, a) => g.setSettings(id, {
    passes: a.passes === undefined ? undefined : Number(a.passes),
    target: a.target === undefined ? undefined : Number(a.target),
  }),
};

function createServer({ port = 3000, game = new Game(), host = '0.0.0.0' } = {}) {
  const app = express();
  app.use(express.static(path.join(__dirname, '..', 'public')));
  const httpServer = http.createServer(app);
  const io = new Server(httpServer);
  const bound = new Map(); // playerId -> socket
  let skipTimer = null;

  function broadcast() {
    for (const [pid, sock] of bound) sock.emit('view', viewFor(game, pid));
    scheduleSkipRefresh();
  }

  // Re-send views when a clue turn crosses 30 s so the leader's Skip button appears.
  function scheduleSkipRefresh() {
    clearTimeout(skipTimer);
    skipTimer = null;
    if (game.phase !== 'clues' || game.canSkip()) return;
    const delay = game.round.turnStartedAt + SKIP_AFTER_MS - game.now();
    skipTimer = setTimeout(broadcast, Math.max(0, delay) + 50);
  }

  io.on('connection', (socket) => {
    socket.on('join', (payload, ack) => {
      const reply = typeof ack === 'function' ? ack : () => {};
      const { name, token } = payload ?? {};
      const res = game.join(name, typeof token === 'string' ? token : undefined);
      if (res.ok) {
        const previous = bound.get(res.playerId);
        if (previous && previous !== socket) {
          previous.data.playerId = null;
          previous.disconnect(true);
        }
        if (socket.data.playerId && socket.data.playerId !== res.playerId) bound.delete(socket.data.playerId);
        socket.data.playerId = res.playerId;
        bound.set(res.playerId, socket);
        broadcast();
      }
      reply(res);
    });

    socket.on('action', (payload, ack) => {
      const reply = typeof ack === 'function' ? ack : () => {};
      const pid = socket.data.playerId;
      if (!pid) return reply({ ok: false, error: 'Join first' });
      const args = payload ?? {};
      const handler = Object.hasOwn(ACTIONS, args.type) ? ACTIONS[args.type] : null;
      if (!handler) return reply({ ok: false, error: 'Unknown action' });
      const res = handler(game, pid, args);
      if (res.toast) io.emit('toast', { text: EGG_TEXT[res.toast] });
      if (res.ok) broadcast();
      const { toast, ...rest } = res;
      return reply(rest);
    });

    socket.on('disconnect', () => {
      const pid = socket.data.playerId;
      if (!pid || bound.get(pid) !== socket) return;
      bound.delete(pid);
      game.disconnect(pid);
      broadcast();
    });
  });

  return new Promise((resolve) => {
    httpServer.listen(port, host, () => {
      const actualPort = httpServer.address().port;
      resolve({
        port: actualPort,
        url: `http://${lanAddress()}:${actualPort}`,
        game,
        close: () => new Promise((done) => {
          clearTimeout(skipTimer);
          io.close(() => done());
        }),
      });
    });
  });
}

function lanAddress() {
  for (const addrs of Object.values(os.networkInterfaces())) {
    for (const a of addrs ?? []) {
      if (a.family === 'IPv4' && !a.internal) return a.address;
    }
  }
  return 'localhost';
}

async function main() {
  const qrcode = require('qrcode-terminal');
  const port = Number(process.env.PORT) || 3000;
  const { url } = await createServer({ port });
  console.log('\n  IMPOSTER is running!\n');
  console.log(`  Join at ${url}`);
  console.log('  (everyone, including you, opens this link in a browser on the same Wi-Fi)\n');
  qrcode.generate(url, { small: true });
}

if (require.main === module) main();

module.exports = { createServer };
