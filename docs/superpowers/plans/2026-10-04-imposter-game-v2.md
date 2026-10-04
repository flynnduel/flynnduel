# Imposter v2 "Fire Update" Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the accuse board, the `verdict` vote reveal, the Jester role with a 16-trick deck, anonymous chat with reactions, and motion/sound/parade effects to the existing v1 game, then merge to `main`.

**Architecture:** Game rules stay pure and synchronous in `server/`; new logic gets its own modules (`verdict.js`, `chat.js`, `tricks.js`) that `game.js` composes. Transient effects are queued by `Game` as fx records and drained by `index.js`, which emits them over Socket.IO; persistent state still reaches screens only through `view.js`. One generic server timer wakes the game at `game.nextWakeAt()` (skip availability, verdict stamp/end, effect expiry).

**Tech Stack:** Node 22 CommonJS, express 5, socket.io 4.8, `node --test`; vanilla browser JS/CSS, Web Audio, inline SVG, `<canvas>`; Playwright (global, `/opt/node22/lib/node_modules/playwright`, Chromium at `/opt/pw-browsers/chromium-1194/chrome-linux/chrome`) for the manual walkthrough only.

**Spec:** `docs/superpowers/specs/2026-10-04-imposter-game-v2-design.md` (v2), on top of `docs/superpowers/specs/2026-10-04-imposter-game-design.md` (v1). § numbers below refer to v2.

## Global Constraints

- All code under `imposter-game/`; run commands from there. No new npm dependencies; no network assets.
- Every `Game` mutator returns `{ ok: true, ... }` or `{ ok: false, error }`; never throws on user input. Non-string user text is treated as `''`.
- Verdict timeline: drumroll **1500 ms**, **1200 ms** per vote flip, last words **10000 ms**, stamp **1500 ms**, tie banner **2000 ms**.
- Accusation cooldown **2000 ms**; feed keeps last **6** events.
- Jester: setting `jester` default **false**; only with **≥ 5** round players; **+3**; knows the word; no guess.
- Deck: **16** tricks, **2** dealt per Jester round, no repeats until fewer than 2 unseen remain; each usable once in `clues`/`discussion`/`vote`.
- Chat: **1–140** chars, **1000 ms** per message, keep last **50**; reactions `😂 🔥 🤨 😈 🧐 💀 🍆`, **500 ms** per reaction; alias pool **≥ 20**.
- Parade: **1400 ms** per phone, slot order = `joinedAt`.
- Error strings (exact): `'Slow down! Try again in a sec'` (accuse cooldown), `'Slow down!'` (chat/reaction), `'Careful! That gives away the word.'`, `'Pick another player'`, plus v1's `'Not now'`, `'Only the leader can do that'`.
- Secrets reach screens only through `viewFor`; fx records never carry the word, a role, chat authorship, or the Jester's identity.

## Review Focus

1. **Phone clocks disagree with the server** — verdict animations must line up across phones. The view carries `serverNow`; the client renders from `startedAt − (serverNow − Date.now())`. Test: Task 1 `verdict view carries server clock`.
2. **Refresh during the verdict** — the phone resumes at the right moment, not from the start. Test: Task 1 `verdict view mid-way shows flipped count inputs` (view keeps `startedAt`, `order`, `votes`).
3. **Word smuggled into chat with spacing/punctuation** — "P I Z Z A", "pizza!!", "#pizzaparty" are blocked during a round. Test: Task 4 `revealsWord catches spaced and punctuated forms`.
4. **Trick aimed at a disconnected or invalid player** — returns `'Pick another player'`, does not crash or consume the trick. Test: Task 5 `invalid trick target rejected and not consumed`.
5. **Typing in chat while effects and broadcasts fire** — the chat input keeps text and focus. Check: Task 8 walkthrough step "type in chat during the verdict".

---

## File map

| File | Change |
|---|---|
| `server/verdict.js` | new: timeline math |
| `server/chat.js` | new: `Chat` class (aliases, messages, limits) |
| `server/tricks.js` | new: trick table, text pools, `dealHand` |
| `server/rules.js` | add `isClose`, `revealsWord`; `scoreRound` gains Jester |
| `server/eggs.js` | ignore Jester's vote |
| `server/game.js` | verdict phase, jester, accusations, chat, tricks, fx queue, `nextWakeAt` |
| `server/view.js` | new view fields |
| `server/index.js` | new actions, fx emit, parade slots, generic wake timer |
| `public/app.js` | new screens/panels |
| `public/fx.js`, `public/sound.js` | new: effects layer, synthesized audio |
| `public/index.html`, `public/style.css` | layers, panels, animations |
| `README.md` | v2 features |

---

### Task 1: `verdict` phase

**Files:** Create `server/verdict.js`; modify `server/game.js` (`resolveVote`, new `endVerdict`, `continueVerdict`, `nextWakeAt`), `server/view.js`; update tests `test/game.round.test.js`, `test/view.test.js`, `test/eggs.test.js` (sus test unaffected), `test/smoke.test.js`; new `test/verdict.test.js`.

**Interfaces:**
- Produces (`server/verdict.js`):
  - `DRUMROLL_MS=1500, FLIP_MS=1200, LAST_WORDS_MS=10000, STAMP_MS=1500, TIE_MS=2000`
  - `verdictTimes(startedAt: number, voteCount: number, hasAccused: boolean): { stampAt: number|null, endsAt: number }` — `flipsDone = startedAt + 1500 + 1200·voteCount`; accused → `stampAt = flipsDone + 10000`, `endsAt = stampAt + 1500`; else `stampAt = null`, `endsAt = flipsDone + 2000`.
- Produces (`Game`):
  - `round.verdict = { startedAt, order: string[], votes: Record<id,id>, tie: boolean, accusedId: string|null, stamp: 'imposter'|'jester'|'innocent'|null, stampAt, endsAt, final: boolean }` (`final` = this tie is the revote tie).
  - `resolveVote()` no longer transitions to guess/result; it sets `round.tally`, builds `round.verdict` (order = Fisher–Yates of voter ids with `rng`), sets `round.accusedId` when single, `phase = 'verdict'`.
  - `endVerdict()` (internal, also used by timer/tests): tie && !final → revote (`revote = true`, `candidates = top`, `votes = {}`, `phase='vote'`); tie && final → `finishRound('escaped')`; accused imposter → `phase='guess'`; accused jester → `finishRound('jester')` (Task 2 adds the jester branch); else `finishRound('escaped')`.
  - `continueVerdict(leaderId)` — leader, phase `verdict` → `endVerdict()`.
  - `nextWakeAt(): number|null` — earliest future time among: skip availability (`turnStartedAt+30000` in clues), `verdict.stampAt` (if future), `verdict.endsAt`; Tasks 3/5 add effect expiries. `index.js` will call `game.tick()` then broadcast at that time.
  - `tick()` — if phase `verdict` and `now() >= verdict.endsAt` → `endVerdict()`. Returns `true` if anything changed.
- View: `round.verdict` = `{ startedAt, order, votes, tie, accusedId, stampAt, endsAt, stamp }` where `stamp` is `null` until `now() >= stampAt`; top-level `serverNow: game.now()`. `round.votes` (v1 field) now exposed from `verdict` onward.

- [ ] **Step 1: Write failing tests** in `test/verdict.test.js`:
  - `verdictTimes` — `verdictTimes(0, 4, true)` → `{ stampAt: 16300, endsAt: 17800 }`; `verdictTimes(0, 4, false)` → `{ stampAt: null, endsAt: 8300 }`.
  - `vote enters verdict` (4 players, all vote imposter) → `phase === 'verdict'`, `round.verdict.order` is a permutation of the 4 ids, `accusedId === imp`.
  - `tick before endsAt does nothing; at endsAt goes to guess` (fake clock).
  - `tie → verdict → revote → tie → escaped` via `endVerdict()`.
  - `continueVerdict leader only`.
  - `verdict view carries server clock` — `viewFor(g, id).serverNow === <fake now>`; `round.verdict.stamp === null` before `stampAt`, `'imposter'` at/after.
  - `verdict view mid-way shows flipped count inputs` — view `round.verdict` has `startedAt`, `order`, `votes` for every player; `round.imposterId` still `null`.
  - `nextWakeAt` — in verdict returns `stampAt`, after that `endsAt`.
- [ ] **Step 2: Update existing tests** that cast the deciding vote to call `s.g.endVerdict()` (or `g.endVerdict()`) before asserting `guess`/`result`/`vote`(revote): in `game.round.test.js` (`catchImposter`, imposter escaped, tie then revote, double tie, vote resolves when all connected voted, closeVote, mid-round joiner, game over); in `view.test.js` (`imposter never sees word` — add a look at `verdict` and expect `seen` to be `['reveal','clues','discussion','vote','verdict','guess']`; `result reveals all`); in `smoke.test.js` use `act(ana, 'continueVerdict')` after the third vote.
- [ ] **Step 3: Run** `npm test` → new tests FAIL (`Cannot find module '../server/verdict'` / phase mismatches).
- [ ] **Step 4: Implement** per Interfaces. `stamp` value: accused is imposter → `'imposter'`, Jester → `'jester'`, else `'innocent'`.
- [ ] **Step 5: Wire timer in `server/index.js`:** replace `scheduleSkipRefresh` with `scheduleWake()`: `clearTimeout`; `t = game.nextWakeAt()`; if `t` → `setTimeout(() => { game.tick(); broadcast(); }, max(0, t - game.now()) + 30)`. Add action `continueVerdict`.
- [ ] **Step 6: Run** `npm test` → all pass.
- [ ] **Step 7: Commit** `"imposter-game v2: verdict phase"`

---

### Task 2: Jester role and scoring

**Files:** modify `server/game.js`, `server/rules.js` (`scoreRound`), `server/eggs.js`, `server/view.js`; tests in new `test/jester.test.js`, plus `test/rules.test.js`, `test/eggs.test.js`.

**Interfaces:**
- `settings.jester` (default `false`); `setSettings(id, { passes?, target?, jester? })` — `jester` must be boolean (`'Jester must be on or off'`).
- `round.jesterId: string|null` — set in `startRound` when `settings.jester && playerIds.length >= 5`: random member of `playerIds` minus imposter (via `rng`).
- `scoreRound(outcome, imposterId, crewIds, jesterId = null)` — new outcome `'jester'` → `{ [jesterId]: 3 }`. `caught` still gives +2 to every crew id (Jester included).
- `endVerdict`: accused === `jesterId` → `finishRound('jester')`.
- `roundEggs`: drop the Jester's own vote from `votes` before both checks; never award eggs on `'jester'`.
- View: `round.role` may be `'jester'`; `round.word` visible to the Jester; `round.jesterId` exposed only in `result`/`gameover`; `settings.jester` in `view.settings`.

- [ ] **Step 1: Write failing tests:**
  - `no jester under 5` — 4 players, jester on → `round.jesterId === null`.
  - `jester picked from crew at 5+` — 5 players, rng 0 → `jesterId` defined, `!== imposterId`.
  - `jester voted out wins +3, no guess` — after verdict ends → `phase === 'result'`, `outcome === 'jester'`, jester score 3, all others 0.
  - `jester scores as crew when imposter caught` — wrong guess → jester +2.
  - `jester view` — role `'jester'`, word `'Pizza'`; crew view `round.jesterId === null` before result, set in result.
  - `scoreRound jester` (rules test) — `scoreRound('jester','i',['a','j'],'j')` → `{ j: 3 }`.
  - `eggs ignore jester vote` — hive-mind still awarded when only the Jester voted elsewhere.
  - `setSettings jester` — `true` ok; `'yes'` → error; non-leader → leader error.
- [ ] **Step 2: Run** `npm test` → FAIL.
- [ ] **Step 3: Implement.** `roundEggs(round)` reads `round.jesterId`.
- [ ] **Step 4: Run** `npm test` → pass.
- [ ] **Step 5: Commit** `"imposter-game v2: jester role"`

---

### Task 3: Accusations + fx queue

**Files:** modify `server/game.js`, `server/view.js`; test `test/accuse.test.js`.

**Interfaces:**
- fx queue on `Game`: `this.fx = []`; `emit(record)` pushes; `takeFx(): object[]` returns and clears. Record shapes (all plain data, no secrets): `{ kind: 'accuse', fromName, toName|null }`, plus Task 4/5/6 kinds.
- `round.accusations: Record<accuserId, targetId>`, `round.accuseFeed: [{ fromName, toName|null }]` (last 6), `round.lastAccuseAt: Record<id, ms>`.
- `accuse(id, targetId): { ok }` — phases `clues|discussion|vote`; accuser and target in round; target ≠ accuser (`"You can't accuse yourself"`); cooldown 2000 ms since accuser's last change → `'Slow down! Try again in a sec'`; same target as current → withdraw (`toName: null`); emits `accuse` fx. Works while not paused only (v1 `check`).
- `heat(): Record<id, number>` — counts of accusations (+ active ghost accusations from Task 5).
- View: `round.accusations` (ids), `round.heat`, `round.accuseFeed`.

- [ ] **Step 1: Write failing tests:** `accuse and switch`, `tap same target withdraws`, `cooldown 2000ms` (1999 → error, 2000 → ok), `no self accuse`, `not in reveal or result`, `waiting player cannot accuse`, `accuse emits fx without secrets` (`takeFx()` returns one `{kind:'accuse', fromName:'P1', toName:'P2'}`, second call `[]`), `accusations cleared next round`, `view shows heat and feed (max 6)`.
- [ ] **Step 2: Run** → FAIL. **Step 3: Implement.** **Step 4: Run** → pass.
- [ ] **Step 5: Commit** `"imposter-game v2: accuse board"`

---

### Task 4: Anonymous chat + reactions

**Files:** create `server/chat.js`; modify `server/rules.js`, `server/game.js`, `server/view.js`; tests `test/chat.test.js`, `test/rules.test.js`.

**Interfaces:**
- `rules.js`: `isClose(text: string, word: string): boolean` — the v1 closeness rule extracted from `validateClue` (which now calls it). `revealsWord(message: string, word: string): boolean` — true if any whitespace-separated token is close, or the whole message with all non-alphanumerics removed contains `normalize(word)` (when that is ≥ 3 chars).
- `server/chat.js`: `ALIASES` (≥ 20 strings like `'🦊 Fox'`), `REACTIONS = ['😂','🔥','🤨','😈','🧐','💀','🍆']`, `class Chat { constructor({ rng, now }); aliasOf(id): string; assign(id): void; reshuffle(ids: string[]): void; post(id, text, { roundNumber, wasImposter, hotTake }): {ok, message?, error?}; react(id, emoji, ctx): {ok, message?, error?}; messages: Msg[] }` where `Msg = { id, authorId, alias, text, at, roundNumber, wasImposter, hotTake, reaction }`. Limits per Global Constraints; keeps last 50.
- `Game`: `this.chat = new Chat(...)`; `join` assigns alias for new players; `startRound` reshuffles over all players. `sendChat(id, text)` — in-round phases (`reveal`…`guess`, i.e. `inPlay && phase !== 'result'`) reject `revealsWord(text, round.word)` → `'Careful! That gives away the word.'`; passes `wasImposter: id === round?.imposterId && inRound(id)`, `roundNumber: round?.number ?? 0`, `hotTake` (Task 5). `sendReaction(id, emoji)` — emoji must be in `REACTIONS`; emits `{ kind: 'reaction', emoji }`.
- View `chat: [{ id, alias, text, at, mine, imposter, hotTake, reaction }]` where `imposter = wasImposter && (roundNumber < currentRoundNumber || (roundNumber === currentRoundNumber && phase ∈ {result, gameover}))`; `me.alias`; a `typing` alias list (Task 5).

- [ ] **Step 1: Write failing tests:**
  - `revealsWord catches spaced and punctuated forms` — for word `'Pizza'`: `'P I Z Z A'`, `'pizza!!'`, `'#pizzaparty'`, `'i love pizzas'` → true; `'nice cheese'` → false. For `'Ice Cream'`: `'icecream yum'` → true.
  - `chat limits` — `''` and 141 chars rejected; second message within 999 ms → `'Slow down!'`; 51 messages → 50 kept.
  - `word filter only during rounds` — blocked in `clues`; allowed in `lobby` and `result`.
  - `aliases unique and reshuffle per round` (rng sequence) — all distinct; at least one changes after `startRound` with a moving rng.
  - `chat view never exposes author` — `JSON.stringify(viewFor(...))` contains no other player's id or name next to chat text; `mine` true only for own.
  - `imposter red only after reveal` — imposter message `imposter:false` in `discussion`, `true` in `result`, still `true` in next round's views; lobby message never red.
  - `reactions` — `'🍆'` ok, `'👍'` rejected, 500 ms limit, emits `{kind:'reaction', emoji}`, appears in chat with `reaction: true`.
- [ ] **Step 2: Run** → FAIL. **Step 3: Implement.** **Step 4: Run** → pass.
- [ ] **Step 5: Commit** `"imposter-game v2: anonymous chat and reactions"`

---

### Task 5: Jester deck (tricks)

**Files:** create `server/tricks.js`; modify `server/game.js`, `server/view.js`; test `test/tricks.test.js`.

**Interfaces:**
- `server/tricks.js`: `TRICKS` = the 16 rows of spec §4.1 as `{ id, name, targets: 0|1|2|'random', durationMs }` (`flip` 1/5000, `alarm` 0/3000, `ghost` 1/20000, `shake` 0/4000, `jingle` 'random'/3000, `hottake` 0/0, `swap` 2/15000, `nickname` 1/0 (rest of round), `mirror` 0/6000, `typing` 0/15000, `leak` 1/5000, `spotlight` 1/5000, `bubbles` 0/8000, `loading` 0/4000, `trombone` 1/3000, `disco` 0/5000). `ALARM_LINES` (≥ 30), `NICKNAMES` (≥ 20). `dealHand(rng, seen: Set<string>, n = 2): string[]` — picks from unseen; if unseen < n, `seen.clear()` first; adds picks to `seen`.
- `Game`: `this.seenTricks = new Set()`; in `startRound`, if `jesterId`: `round.jesterHand = dealHand(...).map(id => ({ id, used: false }))`. `round.effects = { ghost: [{targetId, expiresAt}], swap: {a, b, expiresAt}|null, nicknames: {id: title}, typing: {alias, expiresAt}|null, hotTakeArmed: bool }`.
- `useTrick(id, trickId, targetIds = []): { ok }` — Jester only (`'Not now'` otherwise, same message as a phase error so non-Jesters learn nothing); phases `clues|discussion|vote`; trick in hand and unused; `targetIds.length` must equal `targets` (0/1/2), each a connected round player ≠ Jester, distinct → else `'Pick another player'` and the trick stays unused. `'random'` → server picks a connected non-Jester round player. Marks used; updates `round.effects` for `ghost`/`swap`/`nickname`/`typing`/`hottake`; emits `{ kind: 'trick', id: trickId, targetIds, text?, durationMs }` (`text` = random `ALARM_LINES` line for `alarm`, random `NICKNAMES` entry for `nickname`).
- `sendChat` from the Jester while `hotTakeArmed` → message `hotTake: true`, then disarm.
- `heat()` adds +1 per active ghost; `nextWakeAt()` includes effect `expiresAt`s; `tick()` drops expired effects.
- View: `round.jesterHand` only in the Jester's own view (`[]`/absent for others); `round.effects` public parts: `ghosts: [targetId]`, `swap: {a,b}|null`, `nicknames`, `typingAlias` — all without the Jester's id.

- [ ] **Step 1: Write failing tests:**
  - `dealHand no repeats until exhausted` — 8 deals of 2 cover all 16 ids exactly once; 9th deal resets.
  - `trick table` — 16 ids matching the spec list; `ALARM_LINES.length >= 30`; `NICKNAMES.length >= 20`.
  - `only jester can use, once` — crew `useTrick` → `'Not now'`; Jester uses `alarm` → ok + fx with `text`; second use → `'Not now'`.
  - `invalid trick target rejected and not consumed` — target = disconnected player → `'Pick another player'`; then valid target ok.
  - `ghost adds heat and expires` — heat +1; after `durationMs` + `tick()` gone.
  - `hot take marks next jester message` — `hotTake: true` once.
  - `jester hand private` — only Jester's view has `jesterHand`; no view (other than result) contains `jesterId`; trick fx JSON has no Jester id/name.
  - `tricks not allowed in reveal/verdict/result`.
- [ ] **Step 2: Run** → FAIL. **Step 3: Implement.** **Step 4: Run** → pass.
- [ ] **Step 5: Commit** `"imposter-game v2: jester trick deck"`

---

### Task 6: Server wiring — actions, fx, parade

**Files:** modify `server/game.js` (parade fx), `server/index.js`; test `test/smoke.test.js`.

**Interfaces:**
- `Game` emits `{ kind: 'parade', type: 'tease' }` when entering `discussion` in a round with `jesterId`, and `{ kind: 'parade', type: 'victory' }` in `finishRound('jester')`.
- `index.js`: new actions `accuse{targetId}`, `chat{text}`, `react{emoji}`, `trick{trickId, targetIds}`, `continueVerdict`, `settings{…, jester}` (`jester` passed through only when boolean). After every join/action/disconnect/timer: `drainFx()` then `broadcast()`. `drainFx`: for `parade` records, sort bound sockets by player `joinedAt` and emit `fx` to each with `{ kind:'parade', type, slot, total }`; every other record → `io.emit('fx', record)`. Existing `toast` event stays.

- [ ] **Step 1: Write failing smoke test** `five players, jester voted out, chat and parade`: 5 clients (rng 0, `pickWord` stub), leader sets `{passes:1, jester:true}`, starts; find Jester as the client whose `view.round.role === 'jester'`; imposter posts chat `'hi'`; collect `fx` events per client; after discussion starts each client got a `parade` with distinct `slot` 0–4 and `total` 5; everyone (except the Jester) votes the Jester, Jester votes anyone; `continueVerdict`; assert `outcome === 'jester'`, Jester score 3, a `parade` `victory` reached every client, and the imposter's chat line now has `imposter: true` in a crew view.
- [ ] **Step 2: Run** → FAIL. **Step 3: Implement.** **Step 4: Run** `npm test` → all pass.
- [ ] **Step 5: Commit** `"imposter-game v2: socket wiring for fx, chat, tricks"`

---

### Task 7: Client screens and panels

**Files:** modify `public/index.html`, `public/app.js`, `public/style.css`.

**Interfaces:** consumes the view fields from Tasks 1–5 and `fx` events from Task 6; calls `window.FX.*` and `window.Sound.*` from Task 8 if present (guard with `?.` so this task works alone).

- [ ] **Step 1: Structure.** `index.html` adds: `#fx` (fixed full-screen, `pointer-events:none` except bubbles), `#chat` slide-up panel (outside `#app`, so re-renders never touch its input) with message list, input, reaction row, unread badge on a 💬 header button; 🔇 header button; `#volume` full-screen prompt.
- [ ] **Step 2: Screens in `app.js`:**
  - Lobby: Jester toggle (leader; note "Jester mode needs 5+ players" when on and < 5 connected); 🔊 Test sound.
  - Role card: jester variant "You are the JESTER 🃏 — you know the word. Get yourself voted out to win."
  - Accuse board (clues/discussion/vote, read-only in verdict/result): each round player as a row with heat bar and 🔥 count, nickname (effects), swapped names applied, feed of last 6; tap row → `accuse`.
  - Verdict: computes `elapsed = Date.now() + (serverNow_at_receipt − receiptLocalTime) − startedAt` to decide flipped count, tie banner, last-words countdown and stamp; re-renders itself every 250 ms with `requestAnimationFrame`-driven timer while in verdict; leader Continue.
  - Troll menu (Jester only, clues/discussion/vote): 🃏 button opens the 2 cards; tricks needing targets show a player picker; sends `trick`.
  - Result: Jester outcome copy "🃏 THE JESTER WINS" + who it was; rules panel adds the Accuse, Verdict, Jester and Chat sections (spec §2–5), Jester section only when `settings.jester`.
  - Chat panel: list (alias, text, time, "(you)", red style when `imposter`, gold bold when `hotTake`, reactions as big emoji), input (Enter sends `chat`), reaction row sends `react`; unread count when closed; `typingAlias` shows "<alias> is typing…".
  - Volume prompt: shown after a successful join and when phase changes `lobby → reveal` in a new game, unless muted; Test sound plays jingle; "I can hear it 👍" hides it for that game.
- [ ] **Step 3: Verify** with a quick Playwright run (4 phones + laptop) that every new screen renders without console errors; screenshot lobby (Jester toggle), accuse board, verdict, chat, troll menu, volume prompt. Fix layout issues (no horizontal scroll at 390 px).
- [ ] **Step 4: Run** `npm test` → pass (server untouched). **Step 5: Commit** `"imposter-game v2: client screens, chat panel, accuse board"`

---

### Task 8: Effects, sound, parade + full walkthrough

**Files:** create `public/fx.js`, `public/sound.js`; modify `public/index.html` (script tags before `app.js`), `public/app.js` (hook calls), `public/style.css`, `README.md`.

**Interfaces:**
- `window.Sound = { unlock(), setMuted(bool), muted(): bool, play(name) }`; names: `turn, accuse, chat, drumroll, flip, stamp, pop, sting, jingle, siren, trombone, fanfare`. Web Audio oscillators/noise only. Muted state in `localStorage['imposter.muted']` (try/catch).
- `window.FX = { confetti(), rain(emoji), float(emoji), fireFly(), stamp(text, tone), shake(ms), mirror(ms), flip(ms), disco(ms), bubbles(ms), spotlight(name, ms), banner(text, ms, tone), loading(), parade(slot, total, type), pulse() }`. All render into `#fx`; respect `matchMedia('(prefers-reduced-motion: reduce)')` (movement → fade/banner).
- Mapping (in `app.js`): fx `accuse` → `fireFly()` + `Sound.play('accuse')`; `reaction` → `float(emoji)`; `trick` → per id (`flip`/`trombone`/`jingle` act only when `targetIds` includes `me.id`, others show the "🃏 The Jester strikes!" tag); `parade` → `parade(slot,total,type)` + jingle; phase transitions: your turn → `pulse()` + `vibrate(80)` + `turn`; verdict → drumroll/flip ticks/stamp; result → `confetti()` (caught), `rain('😈')` (escaped/stole), `rain('🃏')` + banner "THE JESTER WINS" (jester); gameover → fireworks via repeated `confetti()`.
- Parade jester: inline SVG (hat with 3 bells, face, diamond-pattern body) animated with a CSS cartwheel across the viewport in 1400 ms, starting after `slot × 1400` ms.

- [ ] **Step 1: Implement `sound.js` and `fx.js`**, hook into `app.js`, add animated gradient background and score count-up.
- [ ] **Step 2: Full Playwright walkthrough** (scratch script, not committed), 5 players (one at 1280×800), jester on, passes 1: join → volume prompt shown/dismissed → start → reveal (card flip) → clues (one accusation switch, a reaction 🍆, a chat line from the imposter, a blocked chat containing the word) → Jester fires both dealt tricks → discussion (parade tease reaches every page in slot order) → **type in chat during the verdict** and confirm the input keeps its text → everyone votes the Jester → verdict flips → stamp → result shows Jester win + red imposter chat line. Check per page: no `pageerror`, no horizontal scroll, imposter page never contains the word before result. Screenshot each step at phone and laptop size; inspect key shots by eye.
- [ ] **Step 3: Update `README.md`** (v2 features, Jester mode, sound/volume tip, 🔇).
- [ ] **Step 4: Run** `npm test` → pass. **Step 5: Commit** `"imposter-game v2: effects, sound, parade"`

---

### Task 9: Merge to main

- [ ] **Step 1:** After the final whole-branch review and its fix pass, `npm test` green on the branch.
- [ ] **Step 2:** `git fetch origin main`; confirm `origin/main` is an ancestor of the branch (fast-forward); `git checkout -B main origin/main && git merge --ff-only claude/fervent-euler-heepgf`; `npm test` on main → pass; `git push origin main`; switch back to the branch.
