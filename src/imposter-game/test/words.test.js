const test = require('node:test');
const assert = require('node:assert/strict');
const { CATEGORIES, SECRET, pickWord } = require('../server/words');

// Returns the given numbers in order, then keeps repeating the last one.
function seq(...xs) {
  let i = 0;
  return () => xs[Math.min(i++, xs.length - 1)];
}

test('bank shape', () => {
  const names = Object.keys(CATEGORIES);
  assert.equal(names.length, 15);
  for (const n of ['Food', 'Animals', 'Jobs', 'Places', 'Sports', 'Movies & TV', 'Famous Characters',
    'Things at a Party', 'Superpowers', 'Things in a Bathroom', 'Vacation', 'Holidays', 'School', 'Music',
    'Fast Food Chains']) {
    assert.ok(names.includes(n), n);
  }
  let total = 0;
  for (const [n, ws] of Object.entries(CATEGORIES)) {
    assert.ok(ws.length >= 30, `${n} has ${ws.length}`);
    assert.equal(new Set(ws.map((w) => w.toLowerCase())).size, ws.length, `dupes in ${n}`);
    for (const w of ws) assert.match(w, /^\S+( \S+){0,2}$/, w);
    total += ws.length;
  }
  assert.ok(total >= 500, `total ${total}`);
});

test('secret categories', () => {
  for (const w of ['Benachin', 'Domoda', 'Kora', 'Banjul', 'Attaya', 'Wrestling', 'Ferry', 'Mango', 'Djembe', 'Baobab']) {
    assert.ok(SECRET.gambia.words.includes(w), w);
  }
  assert.ok(SECRET.gambia.words.length >= 15);
  for (const w of ['Group Chat', 'Aux Cord', 'Brunch']) assert.ok(SECRET.insideJokes.words.includes(w), w);
  assert.equal(SECRET.gambia.name, 'The Gambia');
  assert.equal(SECRET.insideJokes.name, 'Inside Jokes');
});

test('pickWord odds routing', () => {
  const g = pickWord(seq(0.01, 0.5), new Set());
  assert.equal(g.secret, 'gambia');
  assert.equal(g.category, 'The Gambia');
  assert.equal(pickWord(seq(0.05, 0.5), new Set()).secret, 'insideJokes');
  const n = pickWord(seq(0.5, 0.5, 0.5), new Set());
  assert.equal(n.secret, null);
  assert.ok(CATEGORIES[n.category].includes(n.word));
});

test('pickWord never repeats until exhausted', () => {
  const used = new Set();
  const seen = new Set();
  for (let i = 0; i < 300; i++) {
    const p = pickWord(Math.random, used);
    const k = `${p.category}|${p.word}`;
    assert.ok(!seen.has(k), k);
    seen.add(k);
  }
});

test('pickWord resets when every word is used', () => {
  const used = new Set();
  const all = Object.entries(CATEGORIES).flatMap(([c, ws]) => ws.map((w) => `${c}|${w}`));
  for (const s of Object.values(SECRET)) for (const w of s.words) all.push(`${s.name}|${w}`);
  all.forEach((k) => used.add(k));
  const p = pickWord(Math.random, used);
  assert.ok(p.word);
  assert.equal(used.size, 1);
});
