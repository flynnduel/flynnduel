# Imposter Game v2: Fire Update (Design Spec)

Date: 2026-10-04
Status: Draft for review
Builds on: `docs/superpowers/specs/2026-10-04-imposter-game-design.md` (v1). Everything in v1
still holds unless this document changes it.

## 1. Purpose

v1 works but plays quietly: people type, vote, and read a result. v2 makes the room
argue and laugh: public accusations, a dramatic vote reveal, an optional Jester who
wants to be voted out (with a deck of troll tricks), an anonymous chat, and lots of
motion and sound. Scoring stays as v1 except for the Jester outcome.

Success: in a 5–8 player game people talk over each other during discussion, react
out loud to the vote flip, and every Jester round produces at least one "WHO DID
THAT?!" moment.

## 2. Accuse board

- Phases: `clues`, `discussion`, `vote`. Board stays visible (read-only) in `verdict`
  and `result`. Cleared at the start of each round.
- Each round player has at most one accusation: `accusations[accuserId] = targetId`.
  Tapping a different player switches; tapping the current target withdraws.
  No self-accusation. Waiting (not-in-round) players cannot accuse or be accused.
- Cooldown: 2000 ms between a player's accusation changes
  (`'Slow down! Try again in a sec'`).
- Public: everyone sees who accuses whom, a heat count per player, and a feed of the
  last 6 events (`🔥 Amie → Bakary`, `↩️ Amie backed off`). Real names are used.
- No effect on scoring. Accusation events are NOT posted to chat (chat is anonymous).

## 3. Vote reveal: the `verdict` phase

New phase between `vote` and `guess`/`result`. Entered whenever a vote resolves
(all connected voted, or leader Close vote).

- On entry the server fixes `round.verdict = { startedAt, order: [voterId…],
  votes: {voterId: targetId}, tie: bool, accusedId|null, endsAt }`.
  `order` is the voters in a random order.
- Timeline (all clients animate from `startedAt`; server is the clock):
  - 1500 ms drumroll, then one vote card flips every 1200 ms.
  - If a single player is accused: 10 000 ms **last words** (accused name zooms in,
    countdown) → **stamp**: `IMPOSTER`, `JESTER`, or `INNOCENT` (1500 ms).
  - If tied: `TIE!` banner (2000 ms). First tie → revote (`vote` phase, candidates =
    tied). Tie in revote → `TIE AGAIN!` banner, imposter escapes.
  - `endsAt = startedAt + 1500 + 1200·votes + (accused ? 10000 + 1500 : 2000)`.
- At `endsAt` the server advances automatically (timer in `index.js`, logic in
  `game.endVerdict()`): accused is imposter → `guess`; accused is Jester → result
  with outcome `jester`; accused is innocent crew → result `escaped`; tie rules as above.
- Leader can tap **Continue** to end the verdict early (same transition).
- Votes become visible to everyone from the start of `verdict` (needed for the flip).
- Actions during verdict: votes ignored (`'Not now'`), accusations not allowed
  (board read-only), chat and reactions allowed.

## 4. Jester

- Lobby setting `jester: boolean`, default **off**. Leader-only, lobby-only like other
  settings. Lobby note when on with fewer than 5 connected: "Jester mode needs 5+ players".
- Each round, if `jester` is on and the round has **≥ 5 players**, one random crew
  member (never the imposter) is the Jester: `round.jesterId`. Otherwise `null`.
- The Jester **knows the word**. Their role card: "You are the JESTER 🃏 — you know
  the word. Get yourself voted out to win." Nobody else learns who the Jester is
  (including the imposter) until the result.
- Outcome `jester`: the accused (single, after any revote) is the Jester. Jester **+3**,
  everyone else 0, imposter revealed, **no guess**.
- Otherwise the Jester is crew for scoring (gets crew points on `caught`).
- Rules panel and result screen explain the Jester when the mode is on.

### 4.1 Jester deck (troll tricks)

- A pool of 16 tricks (below). Each Jester round the Jester is dealt **2 random tricks**
  from those not yet seen this server session; when fewer than 2 unseen remain, the
  seen set resets. A trick counts as seen when dealt.
- Each dealt trick can be used **once**, during `clues`, `discussion` or `vote`.
- Using a trick never reveals the user. Every trick shows a small
  "🃏 The Jester strikes!" tag on all screens.
- Only the Jester's view contains their hand. No trick changes scoring.
- Random text comes from pools in `server/tricks.js` so repeats feel different.

| id | Name | Target | Effect (all screens unless noted) | Duration |
|---|---|---|---|---|
| flip | 🙃 Flip It | 1 player | target's screen rotates 180° | 5 s |
| alarm | 🚨 Fake Alarm | — | red flash + siren + random line (≥30 lines) | 3 s |
| ghost | 👻 Ghost Accusation | 1 player | fake `🔥 ??? → target` on board, +1 heat | 20 s |
| shake | 🫨 Shake Up | — | screens shake, accuse board order scrambles | 4 s |
| jingle | 🔔 Jingle Prank | random non-Jester player | bells from that phone + giant 🔔 + vibrate | 3 s |
| hottake | 📢 Hot Take | — | Jester's next chat message shows bold gold (Jester types it) | one message |
| swap | 🔀 Name Swap | 2 players | their names swap everywhere | 15 s |
| nickname | 🏷️ Nickname | 1 player | random silly title shown next to name (≥20 titles) | rest of round |
| mirror | 🪞 Mirror World | — | screens mirror horizontally | 6 s |
| typing | ⌨️ Ghost Typing | — | chat shows "<Jester's alias> is typing…" | 15 s |
| leak | 📰 Fake Leak | 1 player | banner "LEAKED: someone is voting for <target> 👀" | 5 s |
| spotlight | 🔦 Spotlight | 1 player | screens dim except a spotlight on target's name | 5 s |
| bubbles | 🫧 Bubble Wrap | — | bubbles cover screens; tap to pop, auto-clear | ≤8 s |
| loading | ⏳ Fake Loading | — | "Skipping to the vote…" bar → "jk 🃏" | 4 s |
| trombone | 🎺 Sad Trombone | 1 player | trombone + giant 🎺 on target's phone | 3 s |
| disco | 🌈 Disco | — | disco colors + lights on all screens | 5 s |

State-bearing effects (`ghost`, `swap`, `nickname`, `typing`) live in `round.effects`
with `expiresAt` so they survive a refresh; the rest are one-shot `fx` events.

## 5. Chat

- Open in every phase. A 💬 button opens a slide-up panel; unread badge when closed.
- **Anonymous:** each player has an animal alias (e.g. "🦊 Fox"), assigned on join and
  reshuffled at the start of every round, from a pool of ≥ 20. Chat lines show alias,
  text, time. Your own lines are marked "(you)" on your screen only.
- Limits: 1–140 characters after trim; one message per 1000 ms per player
  (`'Slow down!'`); last 50 messages kept in memory.
- **Word filter:** during `reveal`…`guess` (any in-round phase before `result`), a
  message is rejected if any of its words, or the whole message with spaces removed,
  is close to the secret word by the v1 clue-closeness rule:
  `'Careful! That gives away the word.'` No filter in lobby/result/gameover.
- **Imposter in red:** the server records `wasImposter` on each message. Screens get
  `imposter: true` for a message only once that round's imposter is revealed
  (`result`/`gameover` of that round, or any later round). Lobby messages are never red.
- **Reactions:** 😂 🔥 🤨 😈 🧐 💀 🍆. One tap sends; it floats up every screen and
  appears in chat under the sender's alias. Limit one per 500 ms per player.

## 6. Effects, sound, and the Jester parade

- **Motion** (CSS keyframes + small JS; confetti on a full-screen `<canvas>`; no
  network assets):
  - role card 3D flip on reveal; imposter card slam + shake; Jester card 🃏 burst
  - your turn: screen pulse + `navigator.vibrate` where supported; new clues pop in
  - accusation: 🔥 flies across screens; heat bars with flames; top-accused glows/wobbles
  - verdict: drumroll, card flips, racing tally bars, zoom + countdown, stamp slam
  - result: confetti (crew wins), 😈 rain (imposter escapes), 🃏 rain + "THE JESTER WINS"
  - scoreboard: points count up, rows slide to new rank
  - game over: fireworks + crown
  - subtle animated gradient background
  - `prefers-reduced-motion`: replace movement with fades; no shake/flip/mirror
    (those tricks show as a banner instead)
- **Sound:** synthesized with Web Audio (no files): turn blip, accuse whoosh, chat
  blip, drumroll, card flip tick, stamp, confetti pop, evil laugh-ish sting, jingle
  bells, siren, sad trombone, fanfare. A 🔇 toggle in the header, remembered per
  device. Audio unlocks on the first tap (Join counts).
- **Volume prompt for everyone:** right after joining, every player sees a full-screen
  card: "🔊 Turn your volume up! This game makes noise." with a **Test sound** button
  (plays a jingle), the line "Can't hear it? Flip off silent mode on iPhone", and
  **I can hear it 👍** to dismiss. It shows again on every player's screen when the
  leader starts a game (`startGame`), unless that device is muted with 🔇. The lobby
  also keeps a small **🔊 Test sound** button. Dismissal is per device per game.
  Every sound still has a visual equivalent; nothing depends on hearing it.
- **Jester parade:** a code-drawn (inline SVG) jester cartwheels across phones one
  after another, in join order, with jingles. Server sends each connected socket
  `{ slot, total, kind }`; each phone starts at `slot × 1400 ms` and crosses in
  1400 ms. Triggers: `kind: 'tease'` once at the start of `discussion` in a Jester
  round ("👀 A Jester walks among you"); `kind: 'victory'` on outcome `jester`.

## 7. Changes to v1 behavior
- Votes are revealed at the start of `verdict` instead of in `result`.
- `scoreRound` gains outcome `jester` (+3 to the Jester).
- `roundEggs`: `hive-mind` and `flawless` ignore the Jester's own vote.
- New settings field `jester` (default false).
- Input-preserving rendering: transient effects render in a separate overlay layer so
  they never rebuild the page or disturb text being typed (addresses the v1 review
  note about mobile keyboards).

## 8. Edge cases
- Jester disconnects: the round continues; they can still be voted out and win.
- Accused disconnects during last words: countdown continues.
- Refresh mid-verdict: rejoining phone renders the verdict at the correct point from
  `startedAt`. Refresh mid-parade: that phone just misses it.
- Jester hand when the Jester disconnects and rejoins: kept (in round state).
- Trick targets must be connected round players other than the Jester (for Jingle,
  chosen randomly by the server); otherwise `'Pick another player'`.
- Round cancelled (v1 Cancel round): no Jester outcome; effects cleared.

## 9. Testing
- Unit (`node --test`): Jester selection (≥5 only, never imposter, knows the word),
  jester outcome scoring and no guess; verdict timeline math, auto-advance, leader
  continue, tie → revote → tie again; accusations (switch, withdraw, cooldown, no
  self, phase limits); deck dealing (2 per round, no repeats until exhausted), trick
  once-only, phase limits, targets, state-bearing effects expiry; chat limits, word
  filter on/off by phase, alias reshuffle, red flag timing.
- Secrecy (`view.test.js`): no view ever exposes another player's chat authorship,
  the imposter or Jester identity, the Jester's hand, or votes before `verdict`;
  `imposter` flag on messages only after reveal.
- Smoke: 5 socket clients with Jester on; Jester voted out → outcome `jester`, +3;
  chat message from imposter turns red at result; parade events reach every socket
  with distinct slots.
- Browser walkthrough (Playwright, phone + laptop widths): screenshots of accuse
  board, verdict flip, last words, stamp, chat panel (with red line after reveal),
  Jester troll menu, a trick firing, parade, confetti; no horizontal scroll; no
  console errors.

## 10. Out of scope
Close-word (Undercover) mode, hot seat, custom trick authoring, persistent stats.
