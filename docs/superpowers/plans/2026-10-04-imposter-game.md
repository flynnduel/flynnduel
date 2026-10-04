# Imposter Game Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A LAN party game where 3–12 friends join from their own browsers and play rounds of Imposter (one player has no word and bluffs) to a target score.

**Architecture:** One Node process: Express serves a single static page, Socket.IO carries intents in and personal views out. All game logic is pure, synchronous code in `server/game.js` + `server/rules.js`, tested without networking. `server/view.js` is the only code that turns game state into what a player may see.

**Tech Stack:** Node 22 (CommonJS), express 5, socket.io 4.8, qrcode-terminal 0.12, socket.io-client 4.8 (dev), `node --test` + `node:assert/strict`. Vanilla HTML/CSS/JS client, no build step.

**Spec:** `docs/superpowers/specs/2026-10-04-imposter-game-design.md` — read it alongside this plan; section numbers (§) below refer to it.

## Global Constraints

- All code lives under `imposter-game/`. Run every command from that folder.
- 3–12 players; exactly one imposter per round, uniformly random each round.
- Settings: passes ∈ {1,2,3} default **2**; target ∈ 3..30 default **10**; locked once a game starts.
- Scoring: escaped → imposter +2; accused + correct guess → imposter +1; accused + wrong guess → each crew member of that round +2; cancelled → nobody.
- The secret word is never sent to the imposter's socket before the result phase, and never printed to the terminal.
- Names: trimmed, 1–16 characters, unique case-insensitively among *connected* players.
- Clues: trimmed, 1–24 characters, no spaces. One identical rejection message for everyone: `That clue is too close to the word, try another`.
- Stalled clue turn: leader may Skip after **30 000 ms** or immediately if the active player is disconnected; skipped clue is recorded as `—`.
- Server listens on port **3000** by default (`PORT` env overrides) and on `0.0.0.0`.
- Client storage: `localStorage` access wrapped in try/catch; the page must work without it.

## Review Focus

1. **Refreshing or a sleeping phone mid-round** — the player should land back in the same phase with the same role and score (token rejoin; disconnected-name rejoin when storage is unavailable). Tests: Task 3 `rejoin by token keeps seat`, `rejoin by name when disconnected`; Task 7 smoke reconnect.
2. **Someone disconnects during the vote** — the vote should resolve once every *connected* player has voted, without waiting for the absent one. Test: Task 4 `vote resolves when all connected voted`.
3. **Leader drops mid-game** — crown moves to the next-joined connected player, who can then press leader buttons. Test: Task 3 `leader passes on disconnect`.
4. **Punctuation and case in clues and guesses** — "Pizza!" must be blocked as a clue for "pizza", and "  PIZZA. " must count as a correct guess; an empty/whitespace guess is rejected and does not end the round. Tests: Task 1 `validateClue strips punctuation`, `isCorrectGuess punctuation`; Task 4 `empty guess rejected`.
5. **Name collisions with spacing/case** — " flynn " while "Flynn" is connected is rejected with `That name is taken`. Test: Task 3 `duplicate name case-insensitive`.

---

## File map

| File | Responsibility |
|---|---|
| `package.json` | deps, `start` = `node server/index.js`, `test` = `node --test test/` |
| `server/rules.js` | pure text + scoring rules |
| `server/words.js` | word bank, secret categories, `pickWord` |
| `server/game.js` | `Game` class: the whole state machine, no I/O |
| `server/eggs.js` | easter-egg detection (pure) |
| `server/view.js` | `viewFor(game, playerId)` — the only redaction point |
| `server/index.js` | Express + Socket.IO wiring, LAN URL + QR, `createServer()` |
| `public/index.html`, `public/app.js`, `public/style.css` | single-page client |
| `README.md` | how to run / join / edit Inside Jokes |

All `Game` mutators return `{ ok: true, ...extra }` or `{ ok: false, error: string }` and never throw for user input.

---

### Task 1: Scaffold + `rules.js`

**Files:**
- Create: `imposter-game/package.json`, `imposter-game/.gitignore` (`node_modules/`), `imposter-game/server/rules.js`
- Test: `imposter-game/test/rules.test.js`

**Interfaces:**
- Produces (all exported from `server/rules.js`):
  - `normalize(text: string): string` — lowercase, trim, drop leading `a `/`an `/`the `, remove every char that is not `a-z0-9`, strip one trailing `es` (if length > 4) else one trailing `s` (if length > 3).
  - `validateClue(clue: string, word: string): { ok: true, text: string } | { ok: false, error: string }` — `text` is the trimmed clue.
  - `editDistance(a: string, b: string): number` — Damerau–Levenshtein (optimal string alignment).
  - `isCorrectGuess(guess: string, word: string): boolean` — tiers on `normalize(word).length`: ≤3 → 0, 4–7 → 1, ≥8 → 2.
  - `tallyVotes(votes: Record<string,string>): { counts: Record<string,number>, top: string[] }` — `top` = ids sharing the max count (empty if no votes).
  - `scoreRound(outcome: 'escaped'|'stole'|'caught'|'cancelled', imposterId: string, crewIds: string[]): Record<string, number>` — only non-zero entries.
  - `CLUE_ERROR_CLOSE = 'That clue is too close to the word, try another'`

- [ ] **Step 1: Create `package.json`** with `"type": "commonjs"`, `"engines": {"node": ">=20"}`, deps `express@^5.1.0`, `socket.io@^4.8.1`, `qrcode-terminal@^0.12.0`, devDeps `socket.io-client@^4.8.1`, scripts above. Run `npm install`; expect exit 0.

- [ ] **Step 2: Write failing tests** in `test/rules.test.js` (`const test = require('node:test'); const assert = require('node:assert/strict');`):

```js
test('normalize', () => {
  assert.equal(normalize('  The Pizzas! '), 'pizza');
  assert.equal(normalize('Ice Cream'), 'icecream');
  assert.equal(normalize('Taco-Bell'), 'tacobell');
  assert.equal(normalize('bus'), 'bus');            // too short to strip s
  assert.equal(normalize('Glasses'), 'glass');
});
test('plural clue blocked for -es words', () => assert.equal(validateClue('horses', 'Horse').ok, false));
test('validateClue blocks word and variants', () => {
  for (const c of ['pizza', 'PIZZAS', 'pizzabox', 'Pizza!']) assert.equal(validateClue(c, 'Pizza').ok, false);
  assert.equal(validateClue('pizza', 'Pizza').error, CLUE_ERROR_CLOSE);
});
test('validateClue strips punctuation', () => assert.equal(validateClue('pizza!!', 'pizza').ok, false));
test('validateClue allows unrelated and short-substring clues', () => {
  assert.deepEqual(validateClue(' cheesy ', 'Pizza'), { ok: true, text: 'cheesy' });
  assert.equal(validateClue('nice', 'Ice').ok, true);
  assert.equal(validateClue('pear', 'Bear').ok, true);
});
test('validateClue format errors', () => {
  assert.equal(validateClue('', 'pizza').ok, false);
  assert.equal(validateClue('two words', 'pizza').ok, false);
  assert.equal(validateClue('a'.repeat(25), 'pizza').ok, false);
  assert.equal(validateClue("rock'n-roll", 'pizza').ok, true);
});
test('isCorrectGuess tolerance tiers', () => {
  assert.equal(isCorrectGuess('PIZZA', 'pizza'), true);
  assert.equal(isCorrectGuess('the pizzas', 'Pizza'), true);
  assert.equal(isCorrectGuess('icecream', 'Ice Cream'), true);
  assert.equal(isCorrectGuess('piza', 'pizza'), true);
  assert.equal(isCorrectGuess('ipzza', 'pizza'), true);        // adjacent swap = 1
  assert.equal(isCorrectGuess('pisa', 'pizza'), false);        // distance 2
  assert.equal(isCorrectGuess('cot', 'cat'), false);           // ≤3 exact
  assert.equal(isCorrectGuess('elefant', 'Elephant'), true);
  assert.equal(isCorrectGuess('spagetti', 'Spaghetti'), true);
  assert.equal(isCorrectGuess('pasta', 'pizza'), false);
});
test('isCorrectGuess punctuation', () => assert.equal(isCorrectGuess('  PIZZA. ', 'pizza'), true));
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
```

- [ ] **Step 3: Run** `npm test` → FAIL (`Cannot find module '../server/rules'`).
- [ ] **Step 4: Implement `server/rules.js`** per the Interfaces block. Clue validation order: format checks (empty → `Enter a clue`, contains whitespace → `One word only`, >24 → `Too long`), then closeness: `c = normalize(clue)`, `w = normalize(word)`; close if `c === w`, or the shorter of the two has length ≥ 4 and the longer includes it. Clue `c === ''` after normalize (e.g. `!!!`) → `Enter a clue`.
- [ ] **Step 5: Run** `npm test` → all pass.
- [ ] **Step 6: Commit** `git add imposter-game && git commit -m "imposter-game: scaffold and rules"`

---

### Task 2: Word bank `words.js`

**Files:**
- Create: `imposter-game/server/words.js`
- Test: `imposter-game/test/words.test.js`

**Interfaces:**
- Produces:
  - `CATEGORIES: Record<string, string[]>` — exactly the 15 names in spec §5, ≥30 entries each, ≥500 total.
  - `SECRET: { gambia: { name: 'The Gambia', words: string[] }, insideJokes: { name: 'Inside Jokes', words: string[] } }` — gambia ≥15 words incl. the 10 in spec §6.1; insideJokes ≈10 words incl. `Group Chat`, `Aux Cord`, `Brunch`.
  - `pickWord(rng: () => number, used: Set<string>): { category: string, word: string, secret: 'gambia'|'insideJokes'|null }` — first `r = rng()`: `r < 0.04` → gambia; `r < 0.065` → insideJokes; else a uniformly random normal category (via further `rng()` calls). Within the chosen pool pick an unused word; if the pool is exhausted fall back to normal categories; if every word everywhere is used, `used.clear()` then pick. Adds the pick to `used`. Words in `used` are keyed by `category + '|' + word`.

- [ ] **Step 1: Write failing tests:**

```js
test('bank shape', () => {
  const names = Object.keys(CATEGORIES);
  assert.equal(names.length, 15);
  for (const n of ['Food','Animals','Jobs','Places','Sports','Movies & TV','Famous Characters','Things at a Party','Superpowers','Things in a Bathroom','Vacation','Holidays','School','Music','Fast Food Chains'])
    assert.ok(names.includes(n), n);
  let total = 0;
  for (const [n, ws] of Object.entries(CATEGORIES)) {
    assert.ok(ws.length >= 30, n);
    assert.equal(new Set(ws.map(w => w.toLowerCase())).size, ws.length, `dupes in ${n}`);
    for (const w of ws) assert.match(w, /^\S+( \S+){0,2}$/, w);   // 1–3 words
    total += ws.length;
  }
  assert.ok(total >= 500);
});
test('secret categories', () => {
  for (const w of ['Benachin','Domoda','Kora','Banjul','Attaya','Wrestling','Ferry','Mango','Djembe','Baobab'])
    assert.ok(SECRET.gambia.words.includes(w), w);
  for (const w of ['Group Chat','Aux Cord','Brunch']) assert.ok(SECRET.insideJokes.words.includes(w));
});
test('pickWord odds routing', () => {
  assert.equal(pickWord(seq(0.01, 0.5), new Set()).secret, 'gambia');
  assert.equal(pickWord(seq(0.05, 0.5), new Set()).secret, 'insideJokes');
  assert.equal(pickWord(seq(0.5, 0.5, 0.5), new Set()).secret, null);
});
test('pickWord never repeats until exhausted', () => {
  const used = new Set(), seen = new Set();
  for (let i = 0; i < 300; i++) { const p = pickWord(Math.random, used); const k = p.category + '|' + p.word; assert.ok(!seen.has(k)); seen.add(k); }
});
```
(`seq(...xs)` is a test helper returning the given numbers in order, then repeating the last.)

- [ ] **Step 2: Run** `npm test` → FAIL (module missing).
- [ ] **Step 3: Write `server/words.js`.** Every entry: widely known, fun to clue, no offensive words. Fast Food Chains uses brand names (e.g. `Taco Bell`, `Chick-fil-A`).
- [ ] **Step 4: Run** `npm test` → pass.
- [ ] **Step 5: Commit** `"imposter-game: word bank"`

---

### Task 3: `Game` — players, lobby, leader, settings

**Files:**
- Create: `imposter-game/server/game.js`
- Test: `imposter-game/test/game.lobby.test.js`

**Interfaces:**
- Consumes: `pickWord` (Task 2) — injected so tests control words.
- Produces: `class Game` exported from `server/game.js`:
  - `constructor({ rng = Math.random, now = Date.now, pickWord = words.pickWord } = {})`
  - fields per spec §3.3: `phase`, `settings {passes, target}`, `players[]` (`{ id, token, name, connected, score, isLeader, ready, joinedAt }`), `round`, `usedWords: Set`, `waiting: string[]`, plus `scoreHistory: Array<Record<id,number>>`.
  - `join(name: string, token: string): { ok, playerId }` — rejoin rules: existing player with this `token` → mark connected, return same id (even if name differs; keep stored name); else a disconnected player whose name matches case-insensitively → reclaim, update its token; else name taken by a connected player → `{ ok:false, error:'That name is taken' }`; else `players.length >= 12` → `'Game is full'`; else create player. Empty name → `'Enter a name'`; >16 chars → `'Name must be 16 characters or fewer'`. A new player joining while `phase` is not `lobby`/`gameover` goes into `waiting`. First player (or first when nobody is leader) becomes leader.
  - `disconnect(playerId)` — `connected = false`; if they were leader, crown goes to the earliest-`joinedAt` connected player.
  - `setSettings(playerId, { passes?, target? })` — leader + lobby only; validates ranges (`'Passes must be 1, 2 or 3'`, `'Target must be between 3 and 30'`).
  - `connectedPlayers(): Player[]`, `isLeader(playerId): boolean`, `get paused(): boolean` (true when phase ∉ {lobby, gameover} and connected round players < 3).
  - Shared error strings: `'Only the leader can do that'`, `'Not now'`.

- [ ] **Step 1: Write failing tests** (helper `mk()` returns `new Game({ rng: () => 0.5 })`):
  - `first joiner is leader` — `join('Ana','t1')` → `players[0].isLeader === true`; second joiner not leader.
  - `duplicate name case-insensitive` — after `join('Flynn','t1')`, `join(' flynn ','t2')` → `{ ok:false, error:'That name is taken' }`.
  - `name validation` — `''`, `'   '` → `'Enter a name'`; 17 chars → length error; 16 chars ok.
  - `rejoin by token keeps seat` — join, disconnect, `join('Different','t1')` returns same `playerId`, `connected === true`, players length unchanged.
  - `rejoin by name when disconnected` — join `('Ana','t1')`, disconnect, `join('ANA','t9')` → same id.
  - `leader passes on disconnect` — A, B, C join; disconnect A → B `isLeader`, A not; A rejoins → B still leader.
  - `settings` — defaults `{ passes: 2, target: 10 }`; non-leader `setSettings` → leader error; `{ passes: 4 }` and `{ target: 31 }` / `{ target: 2 }` rejected; `{ passes: 3, target: 15 }` accepted.
  - `game full at 12` — 13th join → `'Game is full'`.
- [ ] **Step 2: Run** `npm test` → FAIL.
- [ ] **Step 3: Implement** the Interfaces block in `server/game.js`. Ids: `'p' + counter`.
- [ ] **Step 4: Run** `npm test` → pass.
- [ ] **Step 5: Commit** `"imposter-game: game lobby and players"`

---

### Task 4: `Game` — round flow, voting, guess, scoring, game over

**Files:**
- Modify: `imposter-game/server/game.js`
- Test: `imposter-game/test/game.round.test.js`

**Interfaces:**
- Consumes: Task 1 `validateClue`, `isCorrectGuess`, `tallyVotes`, `scoreRound`; Task 3 `Game`.
- Produces (methods on `Game`; all leader-only ones return the leader error for others and `'Not now'` in the wrong phase):
  - `startGame(leaderId)` — lobby, ≥3 connected → scores reset to 0, `scoreHistory = []`, `startRound()`. Fewer → `'Need at least 3 players'`.
  - `startRound()` (internal) — moves `waiting` into play; `round = { number, category, word, secret, imposterId, playerIds, turnOrder, turnIndex: 0, pass: 1, turnStartedAt, clues: [], votes: {}, revote: false, candidates: null, tally: null, accusedId: null, guess: null, guessCorrect: null, outcome: null, points: {}, eggs: [] }`; `playerIds` = connected players; imposter = `playerIds[floor(rng()*n)]`; `turnOrder` = Fisher–Yates shuffle with `rng`; all `ready = false`; `phase = 'reveal'`.
  - `setReady(playerId)`; when every connected round player is ready → `phase = 'clues'`, `turnStartedAt = now()`. `continueReveal(leaderId)` forces the same.
  - `submitClue(playerId, text): { ok, toast?: 'sus' }` — only the active player (`turnOrder[turnIndex]`), only in `clues`; uses `validateClue(text, round.word)`; stores `{ playerId, text, pass }`; advances turn (skipping nobody — disconnected players are handled by Skip); after the last player of the last pass → `phase = 'discussion'`. Returns `toast: 'sus'` when `isSusClue(text)` (Task 5).
  - `canSkip(): boolean` — `clues` phase and (active player disconnected or `now() - turnStartedAt >= 30000`). `skipTurn(leaderId)` — requires `canSkip()`, records clue `'—'`, advances.
  - `startVote(leaderId)` — from `discussion`. If the imposter is disconnected → `outcome = 'cancelled'`, `phase = 'result'`. Else `phase = 'vote'`.
  - `castVote(playerId, targetId)` — voter must be a connected round player who hasn't voted; target must be a round player ≠ voter, and in `candidates` during a revote (`'Pick one of the tied players'`). When every connected round player has voted → `resolveVote()`. `closeVote(leaderId)` → `resolveVote()` (needs ≥1 vote, else `'No votes yet'`).
  - `resolveVote()` (internal) — `tally = tallyVotes(votes)`. One top → `accusedId`. Tie and not yet revote → `revote = true`, `candidates = top`, `votes = {}`, stay in `vote`. Tie in revote → outcome `'escaped'`. Accused is imposter → `phase = 'guess'`; else outcome `'escaped'`.
  - `submitGuess(playerId, text)` — imposter only, `guess` phase; blank after trim → `'Type a guess'` (round continues); sets `guess`, `guessCorrect = isCorrectGuess(text, word)`, outcome `'stole'` or `'caught'`.
  - `finishRound(outcome)` (internal) — `points = scoreRound(outcome, imposterId, playerIds without imposter)`; add to scores; push a copy of `{ id: score }` for all players to `scoreHistory`; `round.eggs = roundEggs(round)` (Task 5); `phase = 'result'`.
  - `nextRound(leaderId)` — from `result`: if any score ≥ `settings.target` → `phase = 'gameover'`, `this.winners = ids with max score`, `this.gameEggs = gameEggs(scoreHistory, winners, playerIds)`; else `startRound()`.
  - `newGame(leaderId)` — from `gameover`: `phase = 'lobby'`, `round = null`, scores kept until `startGame` resets them.
  - While `paused`, every round action except join/disconnect returns `'Waiting for players to reconnect'`.

- [ ] **Step 1: Write failing tests.** Helper `playTo(phase)` builds a 4-player game with deterministic `rng` (`() => 0` → imposter is `playerIds[0]`; tests read the active player from `round.turnOrder[round.turnIndex]` rather than assuming an order) and a stub `pickWord` returning `{ category: 'Food', word: 'Pizza', secret: null }`. Tests:
  - `start needs 3` — two players → `'Need at least 3 players'`.
  - `reveal → clues when all ready` and `continueReveal by leader`.
  - `clue turn order and passes` — with passes 2, 8 clues move phase to `discussion`; out-of-turn clue → `{ ok:false }`; clue `'pizza'` rejected with `CLUE_ERROR_CLOSE` and turn does not advance.
  - `skip after 30s` — `canSkip()` false at 29 999 ms (fake `now`), true at 30 000; `skipTurn` records `'—'`; disconnected active player → `canSkip()` true immediately.
  - `imposter escaped` — votes on a crew member → outcome `escaped`, imposter score 2.
  - `imposter caught, correct guess` — guess `'piza'` → `stole`, imposter 1, crew 0.
  - `imposter caught, wrong guess` — guess `'pasta'` → `caught`, each of 3 crew = 2.
  - `empty guess rejected` — `submitGuess(imp, '   ')` → `{ ok:false, error:'Type a guess' }`, still `guess` phase.
  - `tie then revote resolves` — 2–2 tie → `revote === true`, `candidates` = the two; vote for non-candidate rejected; revote majority → resolves.
  - `double tie → escaped` — tie in revote → outcome `escaped`, imposter +2.
  - `no self vote, no double vote`.
  - `vote resolves when all connected voted` — one crew disconnects during `vote`; remaining 3 votes resolve it.
  - `closeVote counts received votes`.
  - `imposter gone at vote → cancelled` — disconnect imposter in discussion, `startVote` → `result`, outcome `cancelled`, no points.
  - `paused under 3` — in clues, disconnect two of four → `paused`, `submitClue` returns the paused error; rejoin → not paused.
  - `mid-round joiner waits then is dealt in` — join during clues → in `waiting`, not in `round.playerIds`; after `nextRound` they are.
  - `game over at target and shared win` — target 3; force scores so two players hit 4 → `nextRound` → `gameover`, `winners` has both.
  - `settings locked after start` — `setSettings` during `reveal` → `'Not now'`.
- [ ] **Step 2: Run** `npm test` → FAIL.
- [ ] **Step 3: Implement** the Interfaces block. Import `roundEggs`, `gameEggs`, `isSusClue` from `./eggs` — create `server/eggs.js` now exporting stubs that return `[]` / `false` (Task 5 fills them).
- [ ] **Step 4: Run** `npm test` → pass.
- [ ] **Step 5: Commit** `"imposter-game: round flow, voting, scoring"`

---

### Task 5: Easter eggs `eggs.js`

**Files:**
- Modify: `imposter-game/server/eggs.js`
- Test: `imposter-game/test/eggs.test.js`

**Interfaces:**
- Produces:
  - `isSusClue(text: string): boolean` — `normalize(text) === 'sus'`.
  - `roundEggs(round): string[]` — subset of:
    - `'hive-mind'`: outcome `stole` or `caught`, and every crew member's vote (in the final `votes` map) targets the imposter, with ≥2 crew votes.
    - `'flawless'`: outcome `escaped`, and the imposter received 0 votes in the final `votes` map.
    - `'galaxy-brain'`: outcome `stole`.
  - `gameEggs(scoreHistory, winners, playerIds): string[]` — `'from-the-bottom'` if some winner was *strictly* lowest among ≥3 players in any `scoreHistory` entry before the last.
  - `EGG_TEXT = { 'hive-mind': '🧠 HIVE MIND', flawless: '🎭 FLAWLESS DECEPTION', 'galaxy-brain': '🌌 GALAXY BRAIN', 'from-the-bottom': '📈 FROM THE BOTTOM', sus: '📮 Emergency meeting energy' }`.

- [ ] **Step 1: Write failing tests** — one positive and one negative case per egg (e.g. hive-mind false when one crew voted elsewhere; flawless false when imposter got 1 vote; from-the-bottom false when the winner was only tied-lowest); `isSusClue('SUS!')` true, `isSusClue('suspect')` false. Plus in `game.round.test.js`: `submitClue` with `'sus'` returns `toast: 'sus'` and the clue is still stored.
- [ ] **Step 2: Run** `npm test` → FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `npm test` → pass.
- [ ] **Step 5: Commit** `"imposter-game: easter eggs"`

---

### Task 6: `view.js` — per-player redaction

**Files:**
- Create: `imposter-game/server/view.js`
- Test: `imposter-game/test/view.test.js`

**Interfaces:**
- Consumes: `Game` (Tasks 3–5), `EGG_TEXT`.
- Produces: `viewFor(game: Game, playerId: string): View` where

```
View = {
  phase, paused, settings: { passes, target },
  me: { id, name, isLeader, waiting: boolean },
  players: [{ id, name, score, connected, isLeader, ready, hasVoted, inRound }],
  canSkip: boolean,
  round: null | {
    number, category, secret,                      // secret: 'gambia'|'insideJokes'|null
    role: 'crew'|'imposter'|null,                  // null if me not in round
    word: string|null,                             // crew only; everyone in result
    clues: [{ name, text, pass }], pass, passes, turnPlayerId,
    revote, candidates, myVote,
    tally: Record<id,number>|null,                 // only in guess/result
    votes: Record<id,id>|null,                     // only in result
    accusedId, imposterId,                         // imposterId only in result
    guess, guessCorrect, outcome, points, eggs: string[]  // eggs as EGG_TEXT strings
  },
  winners: id[]|null, gameEggs: string[]
}
```

- [ ] **Step 1: Write failing tests:**
  - `imposter never sees word before result` — drive a game through every phase from `reveal` to `guess`; at each, `JSON.stringify(viewFor(game, imposterId))` does not contain `'Pizza'` (case-insensitive) and `round.imposterId === undefined || null`.
  - `crew sees word` — crew view `round.word === 'Pizza'`, `role === 'crew'`.
  - `nobody sees others' roles or votes before reveal` — in `vote` phase, no view contains another player's vote; `votes` null; `tally` null.
  - `result reveals all` — in `result`, every view has `word`, `imposterId`, `votes`, `tally`.
  - `waiting player` — `me.waiting === true`, `round.role === null`, `word === null`.
  - `no token leaks` — `JSON.stringify(view)` never contains any player's token.
- [ ] **Step 2: Run** `npm test` → FAIL.
- [ ] **Step 3: Implement** by building the object field by field from game state (never spreading `game` or `round`).
- [ ] **Step 4: Run** `npm test` → pass.
- [ ] **Step 5: Commit** `"imposter-game: per-player views"`

---

### Task 7: Server wiring `index.js` + smoke test

**Files:**
- Create: `imposter-game/server/index.js`
- Test: `imposter-game/test/smoke.test.js`

**Interfaces:**
- Consumes: `Game`, `viewFor`, `EGG_TEXT`.
- Produces: `createServer({ port = 3000, game = new Game() }): Promise<{ url, port, game, close(): Promise<void> }>`; running `node server/index.js` calls it with `PORT` and prints `Join at http://<lan-ip>:<port>` plus `qrcode-terminal.generate(url, { small: true })`. LAN IP = first non-internal IPv4 from `os.networkInterfaces()`, fallback `localhost`.
- Socket protocol:
  - client → `join` `{ name, token }`, ack `{ ok, playerId?, error? }`. Binds socket ↔ playerId. A previous socket bound to the same playerId is disconnected silently (its `disconnect` must not mark the player away).
  - client → `action` `{ type, ...args }`, ack `{ ok, error? }`. `type` ∈ `ready, continueReveal, clue{text}, skip, startVote, vote{targetId}, closeVote, guess{text}, nextRound, newGame, startGame, settings{passes,target}` mapped to the `Game` methods. Unknown type → `'Unknown action'`.
  - server → `view` (each bound socket gets `viewFor(game, itsPlayerId)` after every successful join/action/disconnect).
  - server → `toast` `{ text }` to all, when `submitClue` returns `toast`.
  - After each broadcast in `clues` phase, schedule one `setTimeout` (cleared on next broadcast) for `turnStartedAt + 30000 - now` so leaders see Skip become available.
- Express serves `public/` statically.

- [ ] **Step 1: Write failing smoke test:** `createServer({ port: 0, game: new Game({ rng: () => 0, pickWord: stub }) })`; connect 3 `socket.io-client` clients (`forceNew: true`); join `Ana`, `Ben`, `Cy`; a 4th client joining as `ana` gets `'That name is taken'`; Ana sets passes 1 and starts; all `ready`; each active player submits a clue; leader `startVote`; all vote for the imposter (Ana, rng 0); imposter guesses `'pizza'`; assert last `view` for Ben has `phase === 'result'`, `round.outcome === 'stole'`, and Ana's score 1. Then disconnect Ben's socket and reconnect a new client with Ben's token → its `view` has `phase === 'result'` and same scores. `await close()`.
- [ ] **Step 2: Run** `npm test` → FAIL.
- [ ] **Step 3: Implement `server/index.js`.** Listen on `0.0.0.0`. Export `createServer`; run `main()` only when `require.main === module`.
- [ ] **Step 4: Run** `npm test` → pass (whole suite).
- [ ] **Step 5: Commit** `"imposter-game: socket server"`

---

### Task 8: Client UI, rules panel, client easter egg, README

**Files:**
- Create: `imposter-game/public/index.html`, `imposter-game/public/app.js`, `imposter-game/public/style.css`, `imposter-game/README.md`

**Interfaces:**
- Consumes: the Task 7 socket protocol and the `View` shape (Task 6). Socket.IO client script from `/socket.io/socket.io.js`.

- [ ] **Step 1: Build `index.html` + `style.css`.** Title `Imposter`. Header: logo text "IMPOSTER", player name, **?** button. One `<main id="app">` re-rendered per view. CSS: color tokens on `:root`, a dark scheme under `prefers-color-scheme: dark`, explicit `body` background, mobile-first, readable from 360 px to 1280 px with no horizontal scroll, buttons ≥44 px tall. `.chameleon` class on `<body>` animates hue (egg 7). Gambia secret category: category banner gets a red/blue/green striped border.
- [ ] **Step 2: Build `app.js`.** `render(view)` switches on `view.phase` and renders the screens in spec §4 exactly (Join, Lobby, Reveal, Clues, Discussion, Vote, Guess, Result, Game over, plus a waiting screen when `me.waiting` and a paused banner when `view.paused`). Leader-only buttons only when `me.isLeader`. Join: autofocused name input, Enter submits, inline error under the field, pre-filled from `localStorage['imposter.name']`; token = `localStorage['imposter.token']` or a new `crypto.randomUUID()` (fallback `Math.random().toString(36).slice(2)`), all storage in try/catch. On socket `connect` with a stored name+token, auto-`join`. Role card hidden until tapped, toggles on tap. Result shows `Guessed "<guess>" — close enough ✓` when `guessCorrect` and the typed guess differs from the word ignoring case; `✓`/`✗` otherwise. Toasts (`toast` event and ack errors) show for 3 s. Easter-egg banners from `round.eggs` / `gameEggs`.
- [ ] **Step 3: Rules overlay (spec §4.1).** The **?** button opens a full-screen overlay available in every phase, including Join, containing: the six phases one line each; clue rules; the tie/revote rule; the scoring table; current settings (`view.settings`, or defaults before joining); "The imposter sees the category but not the word." Close button and Esc close it; the live screen keeps re-rendering underneath (overlay is a sibling of `#app`).
- [ ] **Step 4: Chameleon mode (egg 7).** Konami code (`ArrowUp ArrowUp ArrowDown ArrowDown ArrowLeft ArrowRight ArrowLeft ArrowRight b a`) or 7 logo clicks within 3 s toggles `body.chameleon`. Client-only.
- [ ] **Step 5: README.md** — prerequisites (Node 20+), `npm install`, `npm start`, open the printed link on every device (host included, in a browser tab), same Wi-Fi, how to edit `SECRET.insideJokes` in `server/words.js`, troubleshooting (firewall prompt → allow; port in use → `PORT=3001 npm start`).
- [ ] **Step 6: Manual check.** `npm start` in the background; with Playwright (Chromium at `/opt/pw-browsers`) open 4 pages at 390×844 and one at 1280×800, join 5 players, play one full round to `result`, and screenshot every phase at both sizes. Verify: no horizontal scroll, the imposter page never shows the word before result, rules overlay opens from Join and from Vote, Skip appears for the leader. Fix anything found.
- [ ] **Step 7: Run** `npm test` → all pass.
- [ ] **Step 8: Commit** `"imposter-game: client UI, rules panel, README"`
