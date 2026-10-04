# Imposter Game: Design Spec

Date: 2026-10-04
Status: Draft for review
Location of code: `src/imposter-game/` in this repo

## 1. Purpose

A browser-based Imposter word game for Flynn and friends, played in the same room.
Flynn's computer runs a small server; everyone (Flynn included, in a browser tab on
that computer) joins from their own phone or laptop on the same Wi-Fi.

Not goals: public hosting, accounts, persistence across server restarts, a shared
"TV" screen, a pass-around single-device mode.

Success: a group of 3–12 people can start a game in under a minute, play repeated
rounds to a target score, and nobody can learn the secret word or the imposter's
identity except through play.

## 2. Game rules (source of truth)

Researched from published Imposter, Undercover and The Chameleon rules (see §10).
Where sources disagreed or were silent, the choice made here is final.

### 2.1 Roles and setup
- 3–12 players. Exactly **one imposter** per round, chosen uniformly at random each
  round (repeats allowed).
- Each round a random **category** and a random **secret word** from that category
  are drawn from the built-in word bank. No word repeats within one server session;
  if a category runs out, it is skipped; if all run out, the used-word list resets.
- Everyone sees the category. Every crew member sees the secret word.
  The imposter sees "You are the IMPOSTER" and **no word**.

### 2.2 Round phases
1. **Reveal.** Each player sees a private role card, hidden until they tap it, and
   hidden again on a second tap. Players tap **Ready**; when all connected players
   are ready (or the leader taps **Continue**), the clue phase starts.
2. **Clues.** Turn order is shuffled each round. The active player submits one clue.
   All clues appear on every screen in order, labelled with the player's name.
   This repeats for the configured number of **passes** (1, 2 or 3; default 2).
3. **Discussion.** Free talk out loud. The clue list stays visible. The leader taps
   **Start vote**.
4. **Vote.** Each player privately votes for one other player (no self-votes).
   Screens show who has voted, not for whom. When all connected players have voted
   (or the leader taps **Close vote**), the tally is revealed.
   - A single player with the most votes is **accused**.
   - **Tie:** one revote, in which only the tied players can be voted for (the tied
     players themselves also vote, and cannot vote for themselves). If the revote also
     ties, nobody is accused and the imposter **survives**.
5. **Imposter's guess.** Only if the accused is the imposter: the imposter types one
   guess at the secret word. If someone else was accused, the imposter survives and
   this phase is skipped.
6. **Result.** Everyone sees the secret word, who the imposter was, the votes, and
   points awarded, then the scoreboard. The leader taps **Next round**. If anyone has
   reached the target score, the game ends instead (see 2.4).

### 2.3 Clue validation
A clue is accepted only if, after trimming and lowercasing:
- it is non-empty, at most 24 characters, and contains no spaces (one word; hyphens
  and apostrophes allowed);
- it is not the secret word, and not a variant: after stripping a trailing `s` / `es`
  and any spaces from both, they are not equal, and neither contains the other when
  the shorter one is at least 4 characters (for "pizza" this blocks "pizza", "pizzas",
  "pizzabox"; for "ice" it blocks "ice"/"ices" but still allows "nice").

The imposter's clue goes through the same check against the real secret word. The
rejection message is identical for everyone ("That clue is too close to the word,
try another"), so a rejection never reveals the role. *(Accepted risk: an imposter
whose clue is rejected learns it was close to the word. This is rare and funny.)*

### 2.4 Imposter's guess matching
Typing mistakes should never cost the imposter a correct guess. Both the guess and
the secret word are normalized: trim, lowercase, remove a leading
`a ` / `an ` / `the `, remove spaces, hyphens and apostrophes, and strip a trailing
`s` / `es`. Capitals never matter ("PIZZA", "Pizza", "pizza" all match), and
"icecream" matches "Ice Cream".

Spelling errors are then tolerated by edit distance (Damerau–Levenshtein: an insert,
delete, substitution, or swap of two adjacent letters each counts as 1) between the
normalized strings, scaled to the word's length:

| Normalized secret word length | Max allowed distance | Example accepted |
|---|---|---|
| 1–3 letters | 0 (exact) | "cat" only |
| 4–7 letters | 1 | "piza", "pizzza", "ipzza" (swap); "pisa" is rejected (2) |
| 8+ letters | 2 | "elefant" for "elephant", "spagetti" for "spaghetti" |

The result screen shows what was typed and whether it was accepted, e.g.
`Guessed "piza" — close enough ✓`. Spelling tolerance applies **only to the
imposter's guess**, not to clue validation (where fuzzy matching would wrongly block
clues like "pear" for "bear").

### 2.5 Scoring
| Outcome | Imposter | Each crew member |
|---|---|---|
| Imposter not accused (other player accused, or double tie) | +2 | 0 |
| Imposter accused, guesses correctly | +1 | 0 |
| Imposter accused, guesses wrong | 0 | +2 |

- Target score: default **10**, leader can set 3–30 in the lobby.
- After a round's result, if one or more players are at or above the target, the game
  ends; everyone tied for the highest score wins.
- The leader can then start a new game (scores reset, players stay).

### 2.6 Settings (leader only, lobby only)
- Clue passes: 1 / 2 / 3 (default 2).
- Target score: 3–30 (default 10).

## 3. Architecture

- **Runtime:** Node.js (LTS), Express for static files, Socket.IO for realtime.
- **One game per server process.** No room codes. State lives in memory.
- On start, the server prints the LAN join URL (`http://<lan-ip>:3000`) and a QR code
  in the terminal. The terminal never prints the secret word or imposter.
- The **server is authoritative**. Clients send intents (`join`, `ready`, `clue`,
  `vote`, `guess`, leader actions); the server validates them, updates state, and
  pushes each player a **personal view** built by `view.js`.

### 3.1 Leader
- The first player to join is the leader (crown icon). The leader is a normal player
  with extra controls: settings, Start game, Continue (reveal), Start vote,
  Close vote, Skip (stalled turn), Next round, New game.
- If the leader disconnects, leadership passes to the next-joined connected player.
  It does not return automatically.

### 3.2 File layout
```
src/imposter-game/
  package.json         deps: express, socket.io, qrcode-terminal
                       devDeps: socket.io-client (smoke test only)
                       scripts: start, test (node --test)
  README.md            how to run, how friends join
  server/
    index.js           HTTP + Socket.IO wiring, LAN IP + QR printing
    game.js            Game class: players, phases, turns, votes, scores. No I/O.
    rules.js           pure functions: validateClue, isCorrectGuess, scoreRound,
                       tallyVotes
    words.js           word bank (categories → words) + secret categories
    view.js            viewFor(game, playerId): the ONLY place that redacts secrets
    eggs.js            easter-egg detection (pure functions over round results)
  public/
    index.html         single page
    app.js             renders the current view; no game logic
    style.css          mobile-first, also works at laptop width
  test/
    rules.test.js, game.test.js, view.test.js, eggs.test.js, smoke.test.js
```

### 3.3 Data model (in `game.js`)
```
Game {
  phase: 'lobby' | 'reveal' | 'clues' | 'discussion' | 'vote' | 'guess' | 'result' | 'gameover'
  settings: { passes, target }
  players: [{ id, name, connected, score, isLeader, ready, joinedAt }]
  round: {
    number, category, word, imposterId,
    turnOrder: [playerId], turnIndex, pass,
    clues: [{ playerId, text }],
    votes: { voterId: targetId }, revote: bool, candidates: [playerId] | null,
    accusedId | null, guess | null, outcome | null, points: { playerId: n },
    eggs: [eggId]
  } | null
  usedWords: Set
  waiting: [playerId]          // joined mid-round, dealt in next round
}
```
Player identity: a random `playerToken` stored in the browser's `localStorage`
(wrapped in try/catch) plus the name. A refreshed tab rejoins using the token.
If storage is unavailable, rejoining by the same name while that name is
disconnected also reclaims the seat.

### 3.4 View redaction (`view.js`)
`viewFor(game, playerId)` returns only:
- public state: phase, settings, players (name, score, connected, leader, has-voted,
  ready), category, clues, whose turn, vote tally **only after reveal**, results;
- private state for that player: `role: 'crew' | 'imposter'` and `word` **only if
  crew**; their own vote.
- During `result`/`gameover`: word and imposter for everyone.

No other code path emits game state to sockets.

## 4. Screens (single page, phase-driven)

Every screen has a header with the game name, the player's name, and a **?** button.

- **Join:** the first screen anyone sees when opening the link. A name field
  (autofocused, 1–16 characters, Enter submits) + Join button. Errors show inline
  under the field ("That name is taken", "Enter a name"). After joining, the player
  appears in every lobby list instantly. A returning device pre-fills its last name.
  Shows "Game in progress, you'll be dealt in next round"
  if joining mid-round.
- **Lobby:** player list (crown on leader), settings (leader edits, others read),
  Start game (enabled at 3+ connected players).
- **Reveal:** category + tap-to-reveal role card + Ready.
- **Clues:** category, clue list grouped by pass, "Your turn" input or
  "Waiting for <name>".
- **Discussion:** category, full clue list, leader's Start vote button.
- **Vote:** list of candidates as buttons, voted status of everyone.
- **Guess:** imposter sees a text box; others see "<name> is guessing…".
- **Result:** word, imposter, votes, points this round, scoreboard, any easter-egg
  banners, leader's Next round.
- **Game over:** winner(s), final scoreboard, leader's New game.

### 4.1 Rules panel (available to everyone, always)
The **?** button opens an overlay from any screen without disrupting play. It shows:
- How a round works (the six phases, one line each).
- Clue rules and the tie/revote rule.
- The scoring table.
- **Current settings** for this game (passes, target).
- A note that the imposter sees the category but not the word.
Closing it returns to the live screen, which kept updating underneath.

## 5. Word bank
- 15 everyday categories × ~35 words each (≥ 500 words total), chosen to be widely
  known and fun to clue: Food, Animals, Jobs, Places, Sports, Movies & TV,
  Famous Characters, Things at a Party, Superpowers, Things in a Bathroom,
  Vacation, Holidays, School, Music, Fast Food Chains.
- Every entry is a common noun or name of 1–3 words (e.g. "Taco Bell", "Ice Cream")
  that most players would recognize. No offensive words.
- Plus the secret categories in §6.

## 6. Easter eggs
Designed to be discovered, never to affect fairness or scoring.

1. **Secret category: "The Gambia"** — 1-in-25 chance a round draws it
   (e.g. Benachin, Domoda, Kora, Banjul, Attaya, Wrestling, Ferry, Mango, Djembe,
   Baobab). The category banner gets a flag-striped border.
2. **Secret category: "Inside Jokes"** — 1-in-40 chance. Ships with ~10 universal
   party-game words (e.g. "Group Chat", "Aux Cord", "Brunch"); the README explains
   how to replace them with your friends' own references in `words.js`.
3. **"Sus" alert** — submitting the clue `sus` shows a brief 📮 toast to everyone
   ("Emergency meeting energy"). The clue still counts normally.
4. **Hive Mind** — every crew vote lands on the imposter: result banner
   "🧠 HIVE MIND".
5. **Flawless Deception** — the imposter receives zero votes and survives:
   banner "🎭 FLAWLESS DECEPTION".
6. **Galaxy Brain** — the imposter is accused but guesses the word: banner
   "🌌 GALAXY BRAIN".
7. **Chameleon mode** — typing the Konami code (↑↑↓↓←→←→BA) or tapping the game logo
   7 times toggles a color-cycling theme on that device only.
8. **Comeback** — a player who was in last place wins the game: game-over banner
   "📈 FROM THE BOTTOM".

Detection for 3–6 and 8 lives in `eggs.js` and runs once per round/game; results
are attached to the round so every screen shows the same banners. 7 is client-only.

## 7. Error handling and edge cases
- **Disconnect:** the player keeps their seat, role, and score; they show as
  "away". Rejoin restores them to the current phase.
- **Stalled clue turn:** if the active player is disconnected or hasn't submitted
  within 30 s, the leader sees **Skip** (their clue is recorded as "—").
- **Missing votes:** the leader can **Close vote**; only received votes count.
- **Imposter leaves** (still disconnected when the leader taps Start vote): the round
  is cancelled, no points, leader taps Next round.
- **Fewer than 3 connected players** after the game starts: play pauses with a
  banner until someone rejoins or new players are dealt in at the next round.
- **Round can't continue** (play is paused, or the imposter is disconnected at any
  point mid-round, including during their guess): the leader sees **Cancel this round**,
  which ends it as cancelled with no points. On the result screen, newcomers waiting
  to be dealt in count toward the 3-player minimum, so Next round can deal them in.
- **Mid-round joins:** placed in `waiting`, dealt in at the next round.
- **Names:** 1–16 characters, trimmed, unique case-insensitively among connected
  players.
- **Invalid actions** (out-of-turn clue, double vote, self-vote, non-leader leader
  action, wrong phase): ignored server-side; the sender gets a short error toast.
- **Server restart:** everything resets. Acceptable for this use.
- **Leader settings mid-game:** settings are locked once a game starts; they apply
  again from the next New game.

## 8. Testing
- `rules.test.js`: clue validation (word, plurals, substrings, spaces, length),
  guess matching (case, articles, plurals, spaces; typos at each length tier
  including adjacent swaps; near-misses just over the limit rejected), tally with ties, scoring for all three
  outcomes.
- `game.test.js`: full rounds with 3–6 fake players: imposter not accused,
  accused + correct guess, accused + wrong guess, tie → revote resolved,
  double tie → imposter survives; skip, close vote, disconnect/rejoin, mid-round
  join, game over at target and shared win.
- `view.test.js`: for every phase, the imposter's view never contains the word,
  and no player's view contains another player's role or vote before the reveal.
- `eggs.test.js`: each egg triggers on its condition and not otherwise.
- `smoke.test.js`: start the real server on a random port, connect 3
  `socket.io-client`s that join with names (including a rejected duplicate name),
  and play one round end to end.
- Manual: run locally, screenshot each phase at phone (390 px) and laptop
  (1280 px) widths.

## 9. Out of scope (possible later)
Multiple imposters; Undercover-style "close word" mode; custom word lists; room
codes / multiple simultaneous games; online play outside the LAN; timers on
discussion; sound effects.

## 10. Research sources
Page fetches were blocked in the research environment; rules were taken from
search summaries of:
- The Chameleon (party game) — https://en.wikipedia.org/wiki/The_Chameleon_(party_game)
- How to Play Imposter Game — https://playimposter.com/guide/
- How to play Imposter — https://imposter.app/how-to-play-src/imposter-game/
- Imposter game tips — https://imposter.app/imposter-game-tips/
- Undercover for Beginners — https://yanstarstudio.com/undercover-how-to-play
- Imposter tutorial — https://gameonfamily.com/blogs/tutorials/imposter
