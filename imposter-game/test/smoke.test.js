const test = require('node:test');
const assert = require('node:assert/strict');
const { io } = require('socket.io-client');
const { createServer } = require('../server/index');
const { Game } = require('../server/game');

test('three players play a full round over sockets', async () => {
  const game = new Game({ rng: () => 0, pickWord: () => ({ category: 'Food', word: 'Pizza', secret: null }) });
  const server = await createServer({ port: 0, game, host: '127.0.0.1' });
  const url = `http://127.0.0.1:${server.port}`;
  const clients = [];

  async function connect(name, token) {
    const c = io(url, { forceNew: true, transports: ['websocket'] });
    clients.push(c);
    c.view = null;
    c.on('view', (v) => { c.view = v; });
    await new Promise((resolve) => c.on('connect', resolve));
    c.joinResult = await c.emitWithAck('join', { name, token });
    return c;
  }
  const act = (c, type, args = {}) => c.emitWithAck('action', { type, ...args });
  // Views reach each socket independently, so wait for the expected state.
  async function until(c, pred) {
    const end = Date.now() + 2000;
    while (!(c.view && pred(c.view))) {
      if (Date.now() > end) throw new Error(`timed out; view phase=${c.view && c.view.phase}`);
      await new Promise((r) => setTimeout(r, 10));
    }
    return c.view;
  }

  try {
    const ana = await connect('Ana', 'ta');
    const ben = await connect('Ben', 'tb');
    const cy = await connect('Cy', 'tc');
    const dup = await connect('ana', 'tx');
    assert.deepEqual(dup.joinResult, { ok: false, error: 'That name is taken' });
    assert.equal(ana.joinResult.ok, true);

    const byId = { [ana.joinResult.playerId]: ana, [ben.joinResult.playerId]: ben, [cy.joinResult.playerId]: cy };

    assert.deepEqual(await act(ana, 'settings', { passes: 1 }), { ok: true });
    assert.deepEqual(await act(ana, 'startGame'), { ok: true });
    await until(ben, (v) => v.phase === 'reveal');
    assert.equal(ana.view.round.role, 'imposter');
    assert.equal(ana.view.round.word, null);
    assert.equal(ben.view.round.word, 'Pizza');

    for (const c of [ana, ben, cy]) await act(c, 'ready');
    await until(cy, (v) => v.phase === 'clues');

    for (let i = 0; i < 3; i++) {
      await until(ana, (v) => v.round.clues.length === i);
      const who = byId[ana.view.round.turnPlayerId];
      assert.deepEqual(await act(who, 'clue', { text: `clue${i}` }), { ok: true });
    }
    await until(ana, (v) => v.phase === 'discussion');

    await act(ana, 'startVote');
    await act(ana, 'vote', { targetId: ben.joinResult.playerId });
    await act(ben, 'vote', { targetId: ana.joinResult.playerId });
    await act(cy, 'vote', { targetId: ana.joinResult.playerId });
    await until(ana, (v) => v.phase === 'guess');
    assert.deepEqual(await act(ana, 'guess', { text: 'pizza' }), { ok: true });

    await until(ben, (v) => v.phase === 'result');
    assert.equal(ben.view.round.outcome, 'stole');
    assert.equal(ben.view.players.find((p) => p.name === 'Ana').score, 1);

    assert.deepEqual(await act(ben, 'bogus'), { ok: false, error: 'Unknown action' });

    ben.disconnect();
    await until(ana, (v) => v.players.find((p) => p.name === 'Ben').connected === false);

    const ben2 = await connect('whatever', 'tb');
    assert.equal(ben2.joinResult.playerId, ben.joinResult.playerId);
    await until(ben2, (v) => v.phase === 'result');
    assert.equal(ben2.view.me.name, 'Ben');
    assert.equal(ben2.view.players.find((p) => p.name === 'Ana').score, 1);
    await until(ana, (v) => v.players.find((p) => p.name === 'Ben').connected === true);
  } finally {
    for (const c of clients) c.disconnect();
    await server.close();
  }
});
