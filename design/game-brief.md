# Game Brief: Party Night

<!-- Detailed rules and decisions: docs/superpowers/specs/2026-10-04-party-hub-design.md
     Build plan: docs/superpowers/plans/2026-10-04-party-hub.md (code lives in party-hub/) -->

**One-sentence pitch:** One room code pulls your friends in from anywhere for a night of faithful party classics — Wavelength, Codenames, Secret Hitler — with a vote on every next game, trash talk out loud, and a leaderboard that ends in a ridiculous awards show.

## Core loop
- Lobby → everyone votes on the next game → 3-2-1 countdown
- Play it → talk-it-out phases with pressure timers, say-it clues
- Results → party points fly, leaderboard reshuffles, streaks and badges unlock
- Back to the lobby to vote again, chasing the crown

## Player goal & fail state — what "working" looks like
- Win games for your team/side, and finish the night on top of the leaderboard.
- A night is complete when the host taps End party and the awards show runs — everyone gets at least one award.
- Within a game: lose the game, get assassinated (Codenames), or elect Hitler.

## MVP — what must exist to be the game
- Join from anywhere with a room code + cartoon/photo avatar (built)
- Lobby: next-game vote, teams, talk timers, chat
- Wavelength (official rules)
- Codenames (official rules)
- Secret Hitler (official rules, 1930s poster look)
- Party points, leaderboard, ranks, end-of-night awards show
- Content packs (11 categories, all-original cards and words)

## Out of scope — not building this
- Imposter inside the hub (later); more games such as Telestrations (after a regroup)
- Accounts or stats saved across nights; permanent cloud hosting
- Side bets and shout-outs

## Build order
1. Rooms + tunnel (done)
2. Lobby, vote, teams, timers
3. Wavelength — engine then screens (first playable; proves the hub is fun)
4. Points, leaderboard, awards
5. Content packs
6. Codenames
7. Secret Hitler
8. Full playthrough and polish

---
**Who it's for / what they feel:** a friend group — in person or on a call — who want loud arguments, inside jokes and bragging rights.

**Art & audio direction:** Mario Party-style charm — bright, chunky, bouncy SVG art with synthesized pops, chimes and a heartbeat timer; Secret Hitler gets 1930s propaganda-poster art.

**Reference game:** Jackbox Party Pack — keep the room-code lobby and phones-as-controllers; drop the shared TV screen and the paid games.
