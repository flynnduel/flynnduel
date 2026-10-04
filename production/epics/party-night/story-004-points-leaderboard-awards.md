# Story 004: Party points, leaderboard, ranks and awards show

> **Epic**: Party Night
> **Status**: Ready
> **Layer**: Feature
> **Type**: Logic
> **Estimate**: [fill before starting]
> **Manifest Version**: N/A (minimal — no control manifest)
> **Last Updated**: [set by /dev-story when implementation begins]

## Context

**GDD**: `design/game-brief.md`
**Requirement**: Brief MVP feature 6
**Detailed rules**: `docs/superpowers/specs/2026-10-04-party-hub-design.md` §5.5–5.6 · build steps: `docs/superpowers/plans/2026-10-04-party-hub.md` Task 4 + Task 9 screens

**ADR Governing Implementation**: N/A (minimal — no ADRs)
**ADR Decision Summary**: N/A (minimal — no ADRs)
**ADR Version**: N/A (minimal — no ADRs)

**Engine**: Web Node 20+ | **Risk**: NOT ASSESSED (no VERSION.md risk rating)
**Engine Notes**: none (no ADR engine-compatibility analysis at minimal)

**Control Manifest Rules (this layer)**: N/A (minimal — no control manifest)

---

## Acceptance Criteria

*From `design/game-brief.md` (the **Player goal & fail state** field + MVP feature 6), scoped to this story; exact values from the spec section above:*

- [ ] Each finished game: winners +3, MVP +1; streaks count consecutive wins
- [ ] Ranks at 0/3/8/15/25/40 points (Rookie → Party God) with a LEVEL UP splash
- [ ] Leaderboard podium for top 3, ranked list, ▲▼ movement, confetti when #1 changes
- [ ] Badges and high-fives tracked per spec (1 high-five per teammate per turn)
- [ ] End party shows every award in the spec table with its exact rule; ties share; each award needs ≥1 event
- [ ] Everyone gets at least one award ('Showed Up' fallback) — the night is complete

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
**Required evidence**: tests: points/awards; screenshots of leaderboard and awards slideshow

**Status**: [ ] Not yet created

---

## Dependencies

- Depends on: Story 003
- Unlocks: Story 005
