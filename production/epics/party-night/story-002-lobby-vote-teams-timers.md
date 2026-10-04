# Story 002: Lobby: next-game vote, teams, talk timers, chat + hub screens

> **Epic**: Party Night
> **Status**: Ready
> **Layer**: Core
> **Type**: Logic
> **Estimate**: [fill before starting]
> **Manifest Version**: N/A (minimal — no control manifest)
> **Last Updated**: [set by /dev-story when implementation begins]

## Context

**GDD**: `design/game-brief.md`
**Requirement**: Brief MVP feature 2
**Detailed rules**: `docs/superpowers/specs/2026-10-04-party-hub-design.md` §4, §5.1–5.4, §10 · build steps: `docs/superpowers/plans/2026-10-04-party-hub.md` Tasks 3 and 9

**ADR Governing Implementation**: N/A (minimal — no ADRs)
**ADR Decision Summary**: N/A (minimal — no ADRs)
**ADR Version**: N/A (minimal — no ADRs)

**Engine**: Web Node 20+ | **Risk**: NOT ASSESSED (no VERSION.md risk rating)
**Engine Notes**: none (no ADR engine-compatibility analysis at minimal)

**Control Manifest Rules (this layer)**: N/A (minimal — no control manifest)

---

## Acceptance Criteria

*From `design/game-brief.md` (the **Player goal & fail state** field + MVP feature 2), scoped to this story; exact values from the spec section above:*

- [ ] Each player taps one game card; vote resolves when all connected voted or 15 s after the first vote; ties random; 3 s countdown
- [ ] Ineligible games show 'Needs <min>–<max> players' and cannot be voted; host can force-start any eligible game
- [ ] Teams: tap to join or Shuffle; start blocked if a team is empty or sizes differ by 2+; teams set their own name (1–20) and one of 8 colors, never shared
- [ ] Lead roles rotate within a team (nobody repeats until all teammates led)
- [ ] Timer modes Chill ×1.5 / Normal / Spicy ×0.6 / Off; +30 s once per turn; chat paused during talk phases
- [ ] Late joiners spectate (Peanut Gallery) and join the smaller team next game
- [ ] Hub screens render with no console errors and no horizontal scroll at 390 px and 1280 px: home, avatar maker, lobby, teams, intro splash

---

## Implementation Notes

- Code in `src/party-hub/`; engines pure and deterministic (injected `rng`/`now`); only `Room` touches sockets
- Follow the plan steps named above; write tests first


---

## Out of Scope

- Anything owned by other stories in this epic (see EPIC.md)

---

## QA Test Cases

*N/A — no qa-lead specs at this tier; implement against the Acceptance Criteria above*

---

## Test Evidence

*Governed by `qa.level: minimal`: tests are advisory, but every UI screen touched needs a retained screenshot in `production/qa/evidence/`.*

**Story Type**: Logic
**Required evidence**: tests: lobby/teams/timers; screenshots of each hub screen in production/qa/evidence/

**Status**: [ ] Not yet created

---

## Dependencies

- Depends on: Story 001
- Unlocks: Story 003
