// Pure text and scoring rules (spec §2.3–2.5). No game state lives here.

const CLUE_ERROR_CLOSE = 'That clue is too close to the word, try another';
const CLUE_MAX_LENGTH = 24;

// Lowercase, drop a leading article, keep only letters/digits, strip one plural ending.
function normalize(text) {
  let s = String(text).toLowerCase().trim();
  s = s.replace(/^(a|an|the)\s+/, '');
  s = s.replace(/[^a-z0-9]/g, '');
  if (s.length > 4 && s.endsWith('es')) s = s.slice(0, -2);
  else if (s.length > 3 && s.endsWith('s')) s = s.slice(0, -1);
  return s;
}

function validateClue(clue, word) {
  const text = String(clue).trim();
  if (!text) return { ok: false, error: 'Enter a clue' };
  if (/\s/.test(text)) return { ok: false, error: 'One word only' };
  if (text.length > CLUE_MAX_LENGTH) return { ok: false, error: `Too long (${CLUE_MAX_LENGTH} characters max)` };

  const c = normalize(text);
  const w = normalize(word);
  if (!c) return { ok: false, error: 'Enter a clue' };

  const [shorter, longer] = c.length <= w.length ? [c, w] : [w, c];
  const close = c === w || (shorter.length >= 4 && longer.includes(shorter));
  if (close) return { ok: false, error: CLUE_ERROR_CLOSE };
  return { ok: true, text };
}

// Damerau–Levenshtein (optimal string alignment): insert, delete, substitute, adjacent swap.
function editDistance(a, b) {
  const d = Array.from({ length: a.length + 1 }, (_, i) => [i]);
  for (let j = 1; j <= b.length; j++) d[0][j] = j;
  for (let i = 1; i <= a.length; i++) {
    for (let j = 1; j <= b.length; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost);
      if (i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1]) {
        d[i][j] = Math.min(d[i][j], d[i - 2][j - 2] + 1);
      }
    }
  }
  return d[a.length][b.length];
}

function allowedTypos(length) {
  if (length <= 3) return 0;
  if (length <= 7) return 1;
  return 2;
}

function isCorrectGuess(guess, word) {
  const g = normalize(guess);
  const w = normalize(word);
  if (!g) return false;
  return editDistance(g, w) <= allowedTypos(w.length);
}

function tallyVotes(votes) {
  const counts = {};
  for (const target of Object.values(votes)) counts[target] = (counts[target] || 0) + 1;
  const max = Math.max(0, ...Object.values(counts));
  const top = max === 0 ? [] : Object.keys(counts).filter((id) => counts[id] === max);
  return { counts, top };
}

function scoreRound(outcome, imposterId, crewIds) {
  if (outcome === 'escaped') return { [imposterId]: 2 };
  if (outcome === 'stole') return { [imposterId]: 1 };
  if (outcome === 'caught') return Object.fromEntries(crewIds.map((id) => [id, 2]));
  return {};
}

module.exports = {
  CLUE_ERROR_CLOSE, normalize, validateClue, editDistance, isCorrectGuess, tallyVotes, scoreRound,
};
