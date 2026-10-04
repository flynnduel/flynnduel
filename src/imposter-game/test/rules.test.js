const test = require('node:test');
const assert = require('node:assert/strict');
const {
  normalize, validateClue, isCorrectGuess, editDistance, tallyVotes, scoreRound, CLUE_ERROR_CLOSE,
} = require('../server/rules');

test('normalize', () => {
  assert.equal(normalize('  The Pizzas! '), 'pizza');
  assert.equal(normalize('Ice Cream'), 'icecream');
  assert.equal(normalize('Taco-Bell'), 'tacobell');
  assert.equal(normalize('bus'), 'bus'); // too short to strip s
  assert.equal(normalize('Glasses'), 'glass');
});

test('validateClue blocks word and variants', () => {
  for (const c of ['pizza', 'PIZZAS', 'pizzabox', 'Pizza!']) assert.equal(validateClue(c, 'Pizza').ok, false, c);
  assert.equal(validateClue('pizza', 'Pizza').error, CLUE_ERROR_CLOSE);
});

test('validateClue strips punctuation', () => {
  assert.equal(validateClue('pizza!!', 'pizza').ok, false);
});

test('plural clue blocked for -es words', () => {
  assert.equal(validateClue('horses', 'Horse').ok, false);
});

test('validateClue allows unrelated and short-substring clues', () => {
  assert.deepEqual(validateClue(' cheesy ', 'Pizza'), { ok: true, text: 'cheesy' });
  assert.equal(validateClue('nice', 'Ice').ok, true);
  assert.equal(validateClue('pear', 'Bear').ok, true);
});

test('validateClue format errors', () => {
  assert.equal(validateClue('', 'pizza').ok, false);
  assert.equal(validateClue('!!!', 'pizza').ok, false);
  assert.equal(validateClue('two words', 'pizza').ok, false);
  assert.equal(validateClue('a'.repeat(25), 'pizza').ok, false);
  assert.equal(validateClue("rock'n-roll", 'pizza').ok, true);
});

test('editDistance counts adjacent swap as 1', () => {
  assert.equal(editDistance('pizza', 'ipzza'), 1);
  assert.equal(editDistance('pizza', 'pisa'), 2);
  assert.equal(editDistance('', 'abc'), 3);
});

test('isCorrectGuess tolerance tiers', () => {
  assert.equal(isCorrectGuess('PIZZA', 'pizza'), true);
  assert.equal(isCorrectGuess('the pizzas', 'Pizza'), true);
  assert.equal(isCorrectGuess('icecream', 'Ice Cream'), true);
  assert.equal(isCorrectGuess('piza', 'pizza'), true);
  assert.equal(isCorrectGuess('ipzza', 'pizza'), true);
  assert.equal(isCorrectGuess('pisa', 'pizza'), false);
  assert.equal(isCorrectGuess('cot', 'cat'), false);
  assert.equal(isCorrectGuess('elefant', 'Elephant'), true);
  assert.equal(isCorrectGuess('spagetti', 'Spaghetti'), true);
  assert.equal(isCorrectGuess('pasta', 'pizza'), false);
});

test('isCorrectGuess punctuation', () => {
  assert.equal(isCorrectGuess('  PIZZA. ', 'pizza'), true);
});

test('tallyVotes', () => {
  assert.deepEqual(tallyVotes({ a: 'b', c: 'b', b: 'a' }), { counts: { b: 2, a: 1 }, top: ['b'] });
  assert.deepEqual(tallyVotes({ a: 'b', b: 'a' }).top.sort(), ['a', 'b']);
  assert.deepEqual(tallyVotes({}).top, []);
});

test('scoreRound', () => {
  assert.deepEqual(scoreRound('escaped', 'i', ['a', 'b']), { i: 2 });
  assert.deepEqual(scoreRound('stole', 'i', ['a', 'b']), { i: 1 });
  assert.deepEqual(scoreRound('caught', 'i', ['a', 'b']), { a: 2, b: 2 });
  assert.deepEqual(scoreRound('cancelled', 'i', ['a']), {});
});
