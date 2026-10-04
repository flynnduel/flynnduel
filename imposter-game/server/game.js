// The whole game state machine (spec §2, §3.3, §7). No networking or timers here:
// every method takes the acting player's id and returns { ok: true, ... } or { ok: false, error }.

const words = require('./words');
const { validateClue, isCorrectGuess, tallyVotes, scoreRound } = require('./rules');
const { isSusClue, roundEggs, gameEggs } = require('./eggs');

const SKIP_AFTER_MS = 30000;
const SKIPPED_CLUE = '—';

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
    // Someone leaving may be the last thing the reveal or vote was waiting on.
    if (this.paused) return;
    if (this.phase === 'reveal') this.checkAllReady();
    if (this.phase === 'vote') this.checkAllVoted();
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

  // ---- guards ----

  // Returns an error result, or null when the action may proceed.
  check(id, { phase, leader = false }) {
    if (leader && !this.isLeader(id)) return fail(ERR.leader);
    if (this.phase !== phase) return fail(ERR.notNow);
    if (this.paused) return fail(ERR.paused);
    return null;
  }

  inRound(id) {
    return Boolean(this.round && this.round.playerIds.includes(id));
  }

  connectedRoundIds() {
    return this.round.playerIds.filter((id) => this.player(id).connected);
  }

  // ---- game and round lifecycle ----

  startGame(id) {
    if (!this.isLeader(id)) return fail(ERR.leader);
    if (this.phase !== 'lobby') return fail(ERR.notNow);
    if (this.connectedPlayers().length < MIN_PLAYERS) return fail('Need at least 3 players');
    for (const p of this.players) p.score = 0;
    this.scoreHistory = [];
    this.winners = null;
    this.gameEggs = [];
    this.startRound();
    return { ok: true };
  }

  startRound() {
    this.waiting = [];
    const playerIds = this.connectedPlayers().sort((a, b) => a.joinedAt - b.joinedAt).map((p) => p.id);
    const { category, word, secret } = this.pickWord(this.rng, this.usedWords);

    const turnOrder = [...playerIds];
    for (let i = turnOrder.length - 1; i > 0; i--) {
      const j = Math.floor(this.rng() * (i + 1));
      [turnOrder[i], turnOrder[j]] = [turnOrder[j], turnOrder[i]];
    }

    this.round = {
      number: (this.round ? this.round.number : 0) + 1,
      category,
      word,
      secret,
      imposterId: playerIds[Math.floor(this.rng() * playerIds.length)],
      playerIds,
      turnOrder,
      turnIndex: 0,
      pass: 1,
      turnStartedAt: null,
      clues: [],
      votes: {},
      revote: false,
      candidates: null,
      tally: null,
      accusedId: null,
      guess: null,
      guessCorrect: null,
      outcome: null,
      points: {},
      eggs: [],
    };
    for (const p of this.players) p.ready = false;
    this.phase = 'reveal';
  }

  setReady(id) {
    const err = this.check(id, { phase: 'reveal' });
    if (err) return err;
    if (!this.inRound(id)) return fail(ERR.notNow);
    this.player(id).ready = true;
    this.checkAllReady();
    return { ok: true };
  }

  checkAllReady() {
    if (this.connectedRoundIds().every((pid) => this.player(pid).ready)) this.beginClues();
  }

  continueReveal(id) {
    const err = this.check(id, { phase: 'reveal', leader: true });
    if (err) return err;
    this.beginClues();
    return { ok: true };
  }

  beginClues() {
    this.phase = 'clues';
    this.round.turnIndex = 0;
    this.round.pass = 1;
    this.round.turnStartedAt = this.now();
  }

  activePlayerId() {
    return this.round.turnOrder[this.round.turnIndex];
  }

  submitClue(id, text) {
    const err = this.check(id, { phase: 'clues' });
    if (err) return err;
    if (id !== this.activePlayerId()) return fail("It's not your turn");
    const result = validateClue(text, this.round.word);
    if (!result.ok) return result;
    this.recordClue(id, result.text);
    return isSusClue(result.text) ? { ok: true, toast: 'sus' } : { ok: true };
  }

  canSkip() {
    if (this.phase !== 'clues' || this.paused) return false;
    const activeP = this.player(this.activePlayerId());
    return !activeP.connected || this.now() - this.round.turnStartedAt >= SKIP_AFTER_MS;
  }

  skipTurn(id) {
    const err = this.check(id, { phase: 'clues', leader: true });
    if (err) return err;
    if (!this.canSkip()) return fail(ERR.notNow);
    this.recordClue(this.activePlayerId(), SKIPPED_CLUE);
    return { ok: true };
  }

  recordClue(playerId, text) {
    const r = this.round;
    r.clues.push({ playerId, text, pass: r.pass });
    r.turnIndex += 1;
    if (r.turnIndex >= r.turnOrder.length) {
      r.turnIndex = 0;
      r.pass += 1;
    }
    if (r.pass > this.settings.passes) {
      r.pass = this.settings.passes;
      this.phase = 'discussion';
    }
    r.turnStartedAt = this.now();
  }

  // ---- voting ----

  startVote(id) {
    const err = this.check(id, { phase: 'discussion', leader: true });
    if (err) return err;
    if (!this.player(this.round.imposterId).connected) {
      this.finishRound('cancelled');
      return { ok: true };
    }
    this.round.votes = {};
    this.phase = 'vote';
    return { ok: true };
  }

  castVote(id, targetId) {
    const err = this.check(id, { phase: 'vote' });
    if (err) return err;
    const r = this.round;
    if (!this.inRound(id)) return fail(ERR.notNow);
    if (r.votes[id]) return fail('You already voted');
    if (id === targetId) return fail("You can't vote for yourself");
    if (!this.inRound(targetId)) return fail('Pick a player');
    if (r.revote && !r.candidates.includes(targetId)) return fail('Pick one of the tied players');
    r.votes[id] = targetId;
    this.checkAllVoted();
    return { ok: true };
  }

  checkAllVoted() {
    if (this.connectedRoundIds().every((pid) => this.round.votes[pid])) this.resolveVote();
  }

  closeVote(id) {
    const err = this.check(id, { phase: 'vote', leader: true });
    if (err) return err;
    if (Object.keys(this.round.votes).length === 0) return fail('No votes yet');
    this.resolveVote();
    return { ok: true };
  }

  resolveVote() {
    const r = this.round;
    r.tally = tallyVotes(r.votes).counts;
    const { top } = tallyVotes(r.votes);
    if (top.length !== 1) {
      if (!r.revote) {
        r.revote = true;
        r.candidates = top;
        r.votes = {};
        return;
      }
      this.finishRound('escaped');
      return;
    }
    r.accusedId = top[0];
    if (r.accusedId === r.imposterId) this.phase = 'guess';
    else this.finishRound('escaped');
  }

  submitGuess(id, text) {
    const err = this.check(id, { phase: 'guess' });
    if (err) return err;
    if (id !== this.round.imposterId) return fail(ERR.notNow);
    const guess = String(text ?? '').trim();
    if (!guess) return fail('Type a guess');
    this.round.guess = guess;
    this.round.guessCorrect = isCorrectGuess(guess, this.round.word);
    this.finishRound(this.round.guessCorrect ? 'stole' : 'caught');
    return { ok: true };
  }

  finishRound(outcome) {
    const r = this.round;
    r.outcome = outcome;
    const crewIds = r.playerIds.filter((pid) => pid !== r.imposterId);
    r.points = scoreRound(outcome, r.imposterId, crewIds);
    for (const [pid, pts] of Object.entries(r.points)) this.player(pid).score += pts;
    this.scoreHistory.push(Object.fromEntries(this.players.map((p) => [p.id, p.score])));
    r.eggs = roundEggs(r);
    this.phase = 'result';
  }

  nextRound(id) {
    const err = this.check(id, { phase: 'result', leader: true });
    if (err) return err;
    const top = Math.max(...this.players.map((p) => p.score));
    if (top >= this.settings.target) {
      this.winners = this.players.filter((p) => p.score === top).map((p) => p.id);
      this.gameEggs = gameEggs(this.scoreHistory, this.winners, this.round.playerIds);
      this.phase = 'gameover';
      return { ok: true };
    }
    this.startRound();
    return { ok: true };
  }

  newGame(id) {
    if (!this.isLeader(id)) return fail(ERR.leader);
    if (this.phase !== 'gameover') return fail(ERR.notNow);
    this.phase = 'lobby';
    this.round = null;
    return { ok: true };
  }
}

module.exports = { Game, ERR, MIN_PLAYERS };
