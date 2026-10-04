# Party Hub: Design Spec

Date: 2026-10-04
Status: Draft for review
Code location: `src/party-hub/` (new). `src/imposter-game/` is unchanged.

## 1. Purpose

A party-games app for Flynn's friend group: one hub everyone joins once, from
anywhere, that hosts several faithful digital versions of popular party games.
First build: the hub plus **Wavelength**, **Codenames**, and **Secret Hitler**.
Imposter joins the hub in a later sub-project.

The games must follow their official rules exactly (§6–8); the only deliberate
deviation is optional talk timers, which have an "Off (official rules)" setting.
Card text, word lists and spectrum pairs are written by us; Secret Hitler is used
under its CC BY-NC-SA 4.0 license with attribution, non-commercially.

The hub must create camaraderie: people talk out loud, phases have pressure, and the
look is charming (Mario Party-like), not busy.

Success: friends in different places join one room with a code, pick an avatar,
vote on a game, and play full games of all three without anyone needing to know the
rules beforehand; the night ends with a funny awards show computed from what happened.

Not goals: accounts, stats saved across nights, permanent hosting (later), the
Imposter port (later), monetization.

## 2. Hosting and joining from anywhere

- Flynn runs `npm start` on his Mac. The server listens on port 3000 (`PORT`
  overrides) and starts a **Cloudflare quick tunnel** via the `cloudflared` npm
  package, printing the public `https://…trycloudflare.com` URL and a terminal QR code.
- If the tunnel fails (download blocked, no internet), the server keeps running and
  prints the LAN URL plus a one-line reason. It never crashes because of the tunnel.
- The host's laptop must stay awake while playing. The URL changes each start.

## 3. Rooms, joining, avatars

- The first screen offers **Create room** or **Join room**. Creating makes a
  4-letter room code (letters only, no I/O, unique among open rooms). The creator is
  the room **host** (👑; passes to the earliest-joined connected player on leave).
- Join: room code + name (1–16 chars, unique case-insensitively among connected
  players in the room) → avatar step.
- **Avatars:** either (a) an illustrated cartoon avatar built from an open-license
  avatar style (CC0, bundled with credits) — choose face/hair/accessory/colors via
  "randomize" and per-feature arrows; or (b) a photo upload/selfie, center-cropped
  and resized on the phone to 160×160 JPEG ≤ 40 KB before sending. Avatars appear
  everywhere a player is shown.
- Max 12 players per room. Rooms with nobody connected for 30 min are deleted.
- Reconnect: a browser token (localStorage, try/catch) plus room code rejoins the
  same seat; a disconnected name in that room can be reclaimed by name.
- **Talking:** the lobby says "Not in the same room? Hop on a group voice call."

## 4. The lobby

- Avatars of everyone, host crown, lobby chat (140 chars, 1 msg/s, last 50 kept),
  reaction row.
- **Next-game vote:** a card per game with art and player range; disabled cards
  show why ("Needs 5–10 players"). Each player taps one card (can change). Avatars
  stack on cards. The vote resolves when everyone connected has voted or 15 s after
  the first vote; ties pick randomly with a spinning-wheel animation; then a 3-2-1
  countdown. The host can force-start any eligible game at any time.
- **Settings (host):** timer mode 😌 Chill (×1.5) / 🔥 Normal / 🌶️ Spicy (×0.6) /
  Off (official rules); content packs (§9) on/off (at least one on).
- **Before each game:** an intro splash card (art, 3-line how-to, credits where
  required) and every player taps **Ready** (host can skip).

## 5. Hub-wide systems

### 5.1 Teams (Wavelength, Codenames)
- Two teams. Players tap a team to join, or anyone taps **Shuffle**. Teams persist
  between games until changed.
- Start is blocked if a team is empty or sizes differ by 2+ ("Teams are uneven —
  move 1 player").
- Each team sets its own **name** (1–20 chars, anyone on the team can edit) and
  **color** from 8 palette colors; the two teams cannot share a color.
- Lead roles (spymaster, Psychic) rotate within a team: nobody repeats until all
  teammates have had a turn.
- A disconnected player keeps their team seat. If the current spymaster/Psychic is
  disconnected, teammates see **Take over**.
- Late joiners go to the Peanut Gallery, then join the smaller team next game.

### 5.2 Talk phases and timers
- A talk phase takes over the screen in the acting team's color with a countdown
  ring. Last 15 s: ring turns red, screen pulses, heartbeat sound. At 0: buzzer and
  the phase's timeout action (defined per game).
- Lobby/in-game chat is paused during talk phases ("🗣️ TALK IT OUT").
- One **+30 s** per turn, usable by the acting team. Timer mode Off removes all
  timers (and +30 s).
- Base durations (Normal): Codenames guessing 2:00; Wavelength dial 1:30;
  Wavelength left/right 0:30; Secret Hitler pre-vote discussion 1:30.

### 5.3 Say-it clues
- Clue-givers never type clues. Their screen says "🎙️ SAY YOUR CLUE OUT LOUD" and
  offers only the input the game needs (Codenames: number pad 0–9 and ∞; Wavelength:
  **Clue given ✓**). Everyone else sees "👂 LISTEN!" with the clue-giver's avatar.

### 5.4 Peanut Gallery (late joiners)
- Spectators see a spoiler-free live view of the current game (no secret info),
  can chat (outside talk phases) and send reactions. Dealt in at the next game.

### 5.5 Party points and leaderboard
- Each finished game awards: winners **+3**, game MVP **+1** (per game, §6–8).
- **Leaderboard:** podium for top 3 (gold/silver/bronze, crown on #1), ranked list
  below. After each game: "+N" pops from avatars, rows slide to new ranks with ▲▼,
  confetti + sound when #1 changes.
- **Streaks:** 🔥 + count for 2+ wins in a row.
- **Ranks by party points:** 🥚 Rookie (0) · 🐣 Contender (3) · 🦊 Sneaky (8) ·
  🦁 Beast (15) · 🐉 Legend (25) · 👑 Party God (40). Reaching a new rank shows
  "LEVEL UP!" on that player's screen.
- **Badges** (earned once each): 🎯 Bullseye (Wavelength 4-pointer as Psychic),
  🕵️ Mastermind (Codenames clue that yields 3+ correct guesses), 💀 Assassinated
  (revealed the assassin), 🗳️ Kingmaker (elected Chancellor who enacted a policy for
  your side), 🎭 Never Suspected (won as Hitler).
- **Profile card** on tapping any avatar: photo/avatar, rank, points, wins, badges.
- **High-five:** after a scoring moment, tap a teammate's avatar to send 🙌 (buzz +
  animation on their screen). Counted for awards. Limit 1 per teammate per turn.
- Everything resets when the server stops.

### 5.6 End-of-night awards
Host taps **End party** → awards slideshow, then the final podium. Rules (computed
from tracked stats; ties share; an award needs ≥ 1 qualifying event):

| Award | Rule |
|---|---|
| 🏆 Party Champion | most party points |
| 💀 Assassin's Best Friend | most assassins revealed |
| 🎯 Sharpshooter | most Wavelength bullseyes as Psychic's team guesser* |
| 🙃 Opposite Day | largest single Wavelength miss (dial-to-target distance) by their team while they were on it* |
| 😇 Wrongfully Accused | Secret Hitler: most times nominated as Chancellor and voted down while a Liberal |
| 🧠 Galaxy Brain | Codenames spymaster with most correct guesses from a single clue |
| 🤡 Chaos Agent | most Codenames reveals that ended their own team's turn |
| 🧊 Ice Cold | most correct Wavelength left/right calls (counted per opposing-team member who chose the majority side) |
| 🐍 Certified Snake | Fascist elected to government most times |
| 🔫 Trigger Happy | executed a player on their own team |
| 🎭 Hitler Never Suspected | won as Hitler |
| 🤝 Best Teammate | most high-fives sent |
| 💬 Yapper / 🗿 Wallflower | most / fewest chat messages (Wallflower needs ≥ 1 game played) |
| 📉 The Fumble | their team lost a game after leading by the most points (Wavelength) or agents remaining (Codenames) |
| 🫡 Showed Up | fallback for anyone with no other award |

*Team-guess stats credit every member of the guessing team.

## 6. Wavelength (official rules)

- **Modes:** 4+ players → team mode; 2–3 → co-op mode (chosen automatically).
- **Spectrum cards:** ≥ 150 two-sided cards across packs (§9), no repeats in a party.
- **Target:** center uniformly random in [0, 100]; five bands each 4.5 wide:
  2 | 3 | 4 | 3 | 2 (total 22.5). Bands may extend past the dial edges.
- **Team turn:**
  1. Huddle; the next Psychic in rotation is named.
  2. Psychic sees the dial with the target; says a clue; taps **Clue given ✓**.
  3. **Dial phase** (talk timer; timeout = lock current position): every teammate
     sees one shared live dial and can drag it; positions sync in real time; any
     teammate taps **Lock it in**.
  4. **Left/Right phase** (talk timer; timeout = count taps so far): opposing team
     members each tap Left or Right; majority is the call; a tie or no taps = no call.
  5. Reveal: shutter opens; scoring applied.
- **Scoring:** dial inside a band → that band's points to the active team (4/3/2,
  outside all bands 0). Opposing team **+1** if the call was correct (target center
  vs needle; if exactly equal, no point).
- **Second team starts with 1 point.** Teams alternate. **Catch-up:** if the active
  team scores 4 and is still behind after scoring, it takes another turn.
- **End:** when a team reaches 10+ at the end of a turn, the higher score wins. If
  tied, sudden-death turns (one per team, including left/right) until one team leads
  at the end of a pair.
- **Co-op:** 7 cards; players rotate as Psychic; everyone else moves the dial; a
  4-point hit grants +1 card. Final total rated from our own funny table
  (0–3, 4–6, 7–9, 10–12, 13–15, 16–18, 19–21, 22–24, 25+).
- **Hub results:** win +3 to every member of the winning team (co-op: +3 to all if
  total ≥ 16). MVP: Psychic with the highest average points per clue (ties → more clues).

## 7. Codenames (official rules)

- 4+ players, both teams with ≥ 2 players. One spymaster per team per game (rotation).
- **Grid:** 25 words from enabled packs. **Key:** starting team random, 9 agents;
  other team 8; 7 bystanders; 1 assassin.
- Spymasters see the key overlay; operatives see plain cards.
- **Turn:**
  1. Spymaster says a one-word clue aloud and taps a number: 0–9 or ∞.
  2. **Guessing** (talk timer; timeout = turn ends, even with no guess made — the
     timer is the one deliberate deviation and is off in "Off (official rules)" mode):
     - Tapping a card marks it with your avatar (visible to your team).
     - Holding a card 1 s reveals it.
     - Own agent → may continue; bystander or opponent agent → turn ends; assassin →
       that team loses immediately.
     - Max guesses: number + 1 for numbers 1–9; unlimited for 0 and ∞.
     - **End turn** is available after ≥ 1 guess.
  3. **Illegal clue:** the opposing spymaster may tap 🚩 before the first guess is
     revealed; all players vote Agree/Disagree (10 s; majority of votes cast, tie =
     disagree). If upheld: turn ends; the opposing spymaster reveals one of their own
     agents of their choice. A "What's illegal?" sheet lists: no word on the board,
     no part of a compound word on the board, meaning only (no letters/positions),
     one word.
- **Win:** a team wins when all its agents are revealed (by either team). Revealing
  the assassin loses immediately.
- **Hub results:** win +3 to every member of the winning team; MVP the winning
  spymaster.

## 8. Secret Hitler (official rules, official theme)

Credit on the intro card: "Secret Hitler by Goat, Wolf & Cabbage — CC BY-NC-SA 4.0".

- 5–10 players. Roles:

| Players | Liberals | Fascists | Hitler |
|---|---|---|---|
| 5 | 3 | 1 | 1 |
| 6 | 4 | 1 | 1 |
| 7 | 4 | 2 | 1 |
| 8 | 5 | 2 | 1 |
| 9 | 5 | 3 | 1 |
| 10 | 6 | 3 | 1 |

- **Night (in app):** each player privately sees secret role and party membership.
  Fascists see all Fascists and Hitler. Hitler sees the Fascist(s) only at 5–6
  players.
- **Seat order** = join order shown as a ring; first President random.
- **Election:**
  - President passes to the next living player in seat order.
  - President nominates a Chancellor. Ineligible: the last elected President and last
    elected Chancellor; with 5 or fewer living players only the last Chancellor.
    Term limits apply to the last *elected* government only.
  - Discussion (talk timer; timeout = voting opens).
  - All living players vote Ja!/Nein! secretly; revealed simultaneously. Strict
    majority Ja elects; otherwise fails.
  - Failed election → Election Tracker +1. At 3: top policy enacted (chaos), its
    power ignored, tracker reset, term limits cleared.
  - If elected and ≥ 3 Fascist policies are enacted: if the Chancellor is Hitler →
    Fascists win; else everyone sees "Not Hitler ✓".
- **Legislative session:** all screens show "🤫 SILENCE". President draws 3, discards
  1 (face down), passes 2; Chancellor discards 1, enacts 1. Any enacted policy resets
  the tracker. After the session, if fewer than 3 cards remain, discards are shuffled
  into the deck. Deck: 6 Liberal, 11 Fascist.
- **Veto** (after 5 Fascist policies): Chancellor may propose veto instead of
  enacting; President accepts (both discarded, tracker +1) or refuses (Chancellor must
  enact one).
- **Presidential powers** (on the Fascist policy just enacted, not in chaos):

| Players | F1 | F2 | F3 | F4 | F5 |
|---|---|---|---|---|---|
| 5–6 | — | — | Policy Peek | Execution | Execution |
| 7–8 | — | Investigate | Special Election | Execution | Execution |
| 9–10 | Investigate | Investigate | Special Election | Execution | Execution |

  - Investigate Loyalty: President sees a living player's party (not role); a player
    can't be investigated twice.
  - Special Election: President picks any other living player as next President; then
    order resumes from the player after the President who called it.
  - Policy Peek: President privately sees the top 3 cards (order unchanged).
  - Execution: the target is removed (no voting, no nominating, shown as dead); role
    not revealed unless Hitler → Liberals win.
- **Win:** Liberals — 5 Liberal policies or Hitler executed. Fascists — 6 Fascist
  policies or Hitler elected Chancellor after 3+ Fascist policies.
- **Look:** 1930s propaganda-poster / Art Deco style: worn paper, oxblood red, black,
  cream, Liberal blue; typewritten dossier role cards; stamped party card; boards with
  dove (Liberal) and skull/eagle-style (Fascist) emblems; Ja!/Nein! cards. **No
  swastikas or real Nazi insignia.**
- **Hub results:** win +3 to each member of the winning side; MVP the player who
  served most often in a government that enacted a policy for their own side.

## 9. Content packs

Shared across Wavelength (spectrum cards) and Codenames (words). All text is ours.
Packs: Classic, Ancient History, Philosophy, Religion & Myth, Dark & Taboo,
Pop Culture, Art & Music, Sports, Geography, Science, Economics & Politics.
Wavelength: ≥ 15 cards per pack (≥ 150 total). Codenames: ≥ 40 words per pack
(≥ 400 total), all distinct within a pack. Dark & Taboo is edgy but has no slurs and
nothing targeting protected groups. Default enabled: Classic + Pop Culture.

## 10. Look and feel

- Bright, rounded, chunky "party game" style for the hub and the first two games;
  bundled open-license rounded display font; consistent palette with light/dark.
- Graphics are SVG drawn in code (dial with glossy needle, flip-able cards, podium,
  trophies, badges); emoji only for reactions and small accents.
- Motion on moments (turn start, reveals, scoring, wins); calm while thinking.
- Sounds synthesized with Web Audio (tap pop, turn chime, heartbeat, buzzer, reveal,
  fanfare); 🔇 per device. Phones with reduced motion get fades.
- Mobile-first, works 360–1280 px wide, no horizontal scroll.

## 11. Architecture

```
src/party-hub/
  server/
    index.js      Express + Socket.IO, static files, tunnel start, QR
    tunnel.js     cloudflared quick tunnel with graceful fallback
    rooms.js      room registry, codes, expiry
    room.js       players, avatars, teams, chat, vote, ready, points, stats, game host
    awards.js     award + badge rules over stats
    timers.js     talk-phase timer helper (mode multipliers, +30 s)
    games/
      wavelength.js, codenames.js, secret-hitler.js   pure engines
    content/      packs: spectrum cards + words
  public/         hub UI, per-game screens, SVG art, sounds, avatar maker
  test/
```

- **Game engine interface** (pure, synchronous, deterministic with injected `rng`
  and `now`): `create({ players, teams, settings, rng, now })`, `act(playerId,
  action)` → `{ ok } | { ok:false, error }`, `view(playerId)` → only what that player
  may see (spectators get the public view), `nextWakeAt()`, `tick()`, `result()` →
  `null` or `{ winners: id[], mvp: id|null, stats: Event[] }`. Stats events are
  plain records (`{ type:'bullseye', playerIds:[…] }`, etc.).
- The room is the only thing that talks to sockets; it wraps engine views with hub
  data. One server timer per room wakes at `min(engine.nextWakeAt(), hub timers)`.
- Shared dial drags are rate-limited to 20 updates/s per player and broadcast to
  the team.

## 12. Safety and robustness

- Room code required; max 12 players; per-player action rate limits; chat limits.
- Photo payload ≤ 40 KB; non-image data rejected.
- All player text rendered as text (escaped), never as HTML.
- Malformed payloads never crash the server (validated types).
- Secret information (Wavelength target, Codenames key, Secret Hitler roles/party
  cards/hands/peeks) only in the views of players allowed to see it.

## 13. Testing

- Engine unit tests per official rule (Wavelength: bands, left/right, second-team
  start, catch-up, 10-point end, sudden death, co-op bonus; Codenames: 9/8/7/1 key,
  number+1, minimum guess, bystander/opponent/assassin outcomes, win by opponent
  reveal, illegal-clue penalty; Secret Hitler: role table and night knowledge per
  count, term limits incl. 5-player rule, tie vote fails, tracker/chaos (power
  ignored, limits cleared), Hitler-chancellor win and "Not Hitler", legislative
  flow, reshuffle, power table per count, investigate-once, special-election order,
  execution incl. Hitler, veto accept/refuse, all four win conditions).
- Hub tests: room codes, join/rejoin, avatars limits, vote resolution/ties, team
  rules, rotation, timers, points, ranks, streaks, every award rule.
- Secrecy tests per game for every phase.
- Smoke: 6 socket clients create/join a room, vote, and play a Codenames game and a
  Wavelength turn; 7 clients play Secret Hitler through a forced short game.
- Browser walkthrough (Playwright) at 390 px and 1280 px with screenshots of every
  screen. The tunnel itself can't be exercised from the build environment; its
  fallback path is tested.

## 14. Build order

Hub core → Wavelength → Codenames → Secret Hitler → leaderboard/awards polish.
Each game is playable as soon as it lands.

## 15. Research sources

Page fetches were blocked during research; rules come from search summaries of:
Wavelength — officialgamerules.org, gamerules.com, geekyhobbies.com,
opinionatedgamers.com, boardgamecapital.com, shutupandsitdown.com.
Codenames — officialgamerules.org, ultraboardgames.com (valid clues),
geekyhobbies.com, faq.codenamesapp.com, boardgamegeek.com (invalid clue penalty).
Secret Hitler — secrethitler.com rules PDF (listing), secrethitler.io/rules,
github.com/cozuya/secret-hitler wiki, kingpandagames.com, officialgamerules.org,
en.wikipedia.org/wiki/Secret_Hitler, bargames101.com. Tie-vote-fails and
investigate-once are taken from the published rulebook as known, not confirmed by a
fetched page.
