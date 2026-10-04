// Easter-egg detection (spec §6). Pure functions; they never affect scoring.
const { normalize } = require('./rules');

const EGG_TEXT = {
  'hive-mind': '🧠 HIVE MIND',
  flawless: '🎭 FLAWLESS DECEPTION',
  'galaxy-brain': '🌌 GALAXY BRAIN',
  'from-the-bottom': '📈 FROM THE BOTTOM',
  sus: '📮 Emergency meeting energy',
};

function isSusClue(text) {
  return normalize(text) === 'sus';
}

function roundEggs(round) {
  const { outcome, imposterId, votes } = round;
  const eggs = [];
  const crewVotes = Object.entries(votes).filter(([voter]) => voter !== imposterId).map(([, target]) => target);
  const caught = outcome === 'stole' || outcome === 'caught';

  if (caught && crewVotes.length >= 2 && crewVotes.every((t) => t === imposterId)) eggs.push('hive-mind');
  if (outcome === 'escaped' && !Object.values(votes).includes(imposterId)) eggs.push('flawless');
  if (outcome === 'stole') eggs.push('galaxy-brain');
  return eggs;
}

// A winner who was ever strictly last (among 3+ players) before the final round.
function gameEggs(scoreHistory, winners, playerIds) {
  if (playerIds.length < 3) return [];
  const before = scoreHistory.slice(0, -1);
  const wasLast = (id) => before.some((scores) =>
    playerIds.every((other) => other === id || (scores[id] ?? 0) < (scores[other] ?? 0)));
  return winners.some(wasLast) ? ['from-the-bottom'] : [];
}

module.exports = { EGG_TEXT, isSusClue, roundEggs, gameEggs };
