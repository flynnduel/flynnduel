// The ONLY place game state becomes something a player can see (spec §3.4).
// Build every field explicitly; never spread game or round objects.
const { EGG_TEXT } = require('./eggs');

const REVEALED = new Set(['result', 'gameover']);
const TALLY_VISIBLE = new Set(['guess', 'result', 'gameover']);

function roundView(game, playerId) {
  const r = game.round;
  if (!r) return null;
  const revealed = REVEALED.has(game.phase);
  const inRound = r.playerIds.includes(playerId);
  const isImposter = r.imposterId === playerId;
  const nameOf = (id) => game.player(id)?.name ?? '?';

  let role = null;
  if (inRound) role = isImposter ? 'imposter' : 'crew';

  return {
    number: r.number,
    category: r.category,
    secret: r.secret,
    role,
    word: revealed || (inRound && !isImposter) ? r.word : null,
    clues: r.clues.map((c) => ({ name: nameOf(c.playerId), text: c.text, pass: c.pass })),
    pass: r.pass,
    passes: game.settings.passes,
    turnPlayerId: game.phase === 'clues' ? r.turnOrder[r.turnIndex] : null,
    revote: r.revote,
    candidates: r.candidates ? [...r.candidates] : null,
    myVote: r.votes[playerId] ?? null,
    tally: TALLY_VISIBLE.has(game.phase) && r.tally ? { ...r.tally } : null,
    votes: revealed ? { ...r.votes } : null,
    accusedId: r.accusedId,
    imposterId: revealed ? r.imposterId : null,
    guess: revealed ? r.guess : null,
    guessCorrect: revealed ? r.guessCorrect : null,
    outcome: revealed ? r.outcome : null,
    points: revealed ? { ...r.points } : {},
    eggs: revealed ? r.eggs.map((e) => EGG_TEXT[e]) : [],
  };
}

function viewFor(game, playerId) {
  const me = game.player(playerId);
  const r = game.round;
  return {
    phase: game.phase,
    paused: game.paused,
    settings: { passes: game.settings.passes, target: game.settings.target },
    me: { id: me.id, name: me.name, isLeader: me.isLeader, waiting: game.waiting.includes(me.id) },
    players: game.players.map((p) => ({
      id: p.id,
      name: p.name,
      score: p.score,
      connected: p.connected,
      isLeader: p.isLeader,
      ready: p.ready,
      hasVoted: Boolean(r && game.phase === 'vote' && r.votes[p.id]),
      inRound: Boolean(r && r.playerIds.includes(p.id)),
    })),
    canSkip: game.canSkip(),
    canCancel: game.canCancel(),
    round: roundView(game, playerId),
    winners: game.phase === 'gameover' && game.winners ? [...game.winners] : null,
    gameEggs: game.phase === 'gameover' ? game.gameEggs.map((e) => EGG_TEXT[e]) : [],
  };
}

module.exports = { viewFor };
