// The whole game state machine (spec §2, §3.3, §7). No networking or timers here:
// every method takes the acting player's id and returns { ok: true, ... } or { ok: false, error }.

const words = require('./words');

const MAX_PLAYERS = 12;
const MIN_PLAYERS = 3;
const NAME_MAX = 16;

const ERR = {
  leader: 'Only the leader can do that',
  notNow: 'Not now',
  paused: 'Waiting for players to reconnect',
};

const fail = (error) => ({ ok: false, error });

class Game {
  constructor({ rng = Math.random, now = Date.now, pickWord = words.pickWord } = {}) {
    this.rng = rng;
    this.now = now;
    this.pickWord = pickWord;
    this.phase = 'lobby';
    this.settings = { passes: 2, target: 10 };
    this.players = [];
    this.round = null;
    this.usedWords = new Set();
    this.waiting = [];
    this.scoreHistory = [];
    this.winners = null;
    this.gameEggs = [];
    this.nextId = 1;
  }

  // ---- players ----

  player(id) {
    return this.players.find((p) => p.id === id);
  }

  connectedPlayers() {
    return this.players.filter((p) => p.connected);
  }

  isLeader(id) {
    const p = this.player(id);
    return Boolean(p && p.isLeader);
  }

  get inPlay() {
    return this.phase !== 'lobby' && this.phase !== 'gameover';
  }

  get paused() {
    if (!this.inPlay || !this.round) return false;
    const connected = this.round.playerIds.filter((id) => this.player(id).connected);
    return connected.length < MIN_PLAYERS;
  }

  join(rawName, token) {
    const byToken = token && this.players.find((p) => p.token === token);
    if (byToken) {
      byToken.connected = true;
      this.ensureLeader();
      return { ok: true, playerId: byToken.id };
    }

    const name = String(rawName ?? '').trim();
    if (!name) return fail('Enter a name');
    if (name.length > NAME_MAX) return fail(`Name must be ${NAME_MAX} characters or fewer`);

    const same = this.players.find((p) => p.name.toLowerCase() === name.toLowerCase());
    if (same && same.connected) return fail('That name is taken');
    if (same) {
      same.connected = true;
      same.token = token;
      this.ensureLeader();
      return { ok: true, playerId: same.id };
    }

    if (this.players.length >= MAX_PLAYERS) return fail('Game is full');

    const p = {
      id: `p${this.nextId++}`,
      token,
      name,
      connected: true,
      score: 0,
      isLeader: false,
      ready: false,
      joinedAt: this.players.length,
    };
    this.players.push(p);
    if (this.inPlay) this.waiting.push(p.id);
    this.ensureLeader();
    return { ok: true, playerId: p.id };
  }

  disconnect(id) {
    const p = this.player(id);
    if (!p) return;
    p.connected = false;
    if (p.isLeader) {
      p.isLeader = false;
      this.ensureLeader();
    }
  }

  // Exactly one connected leader whenever anyone is connected; earliest joiner wins.
  ensureLeader() {
    const current = this.players.find((p) => p.isLeader);
    if (current && current.connected) return;
    if (current) current.isLeader = false;
    const next = this.connectedPlayers().sort((a, b) => a.joinedAt - b.joinedAt)[0];
    if (next) next.isLeader = true;
  }

  setSettings(id, { passes, target } = {}) {
    if (!this.isLeader(id)) return fail(ERR.leader);
    if (this.phase !== 'lobby') return fail(ERR.notNow);
    if (passes !== undefined && ![1, 2, 3].includes(passes)) return fail('Passes must be 1, 2 or 3');
    if (target !== undefined && !(Number.isInteger(target) && target >= 3 && target <= 30)) {
      return fail('Target must be between 3 and 30');
    }
    if (passes !== undefined) this.settings.passes = passes;
    if (target !== undefined) this.settings.target = target;
    return { ok: true };
  }
}

module.exports = { Game, ERR, MIN_PLAYERS };
