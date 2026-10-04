# Story 003: Wavelength: rules engine and screens

> **Epic**: Party Night
> **Status**: Ready
> **Layer**: Feature
> **Type**: Logic
> **Estimate**: [fill before starting]
> **Manifest Version**: N/A (minimal — no control manifest)
> **Last Updated**: [set by /dev-story when implementation begins]

## Context

**GDD**: `design/game-brief.md`
**Requirement**: Brief MVP feature 3
**Detailed rules**: `docs/superpowers/specs/2026-10-04-party-hub-design.md` §6 · build steps: `docs/superpowers/plans/2026-10-04-party-hub.md` Tasks 6 and 10

**ADR Governing Implementation**: N/A (minimal — no ADRs)
**ADR Decision Summary**: N/A (minimal — no ADRs)
**ADR Version**: N/A (minimal — no ADRs)

**Engine**: Web Node 20+ | **Risk**: NOT ASSESSED (no VERSION.md risk rating)
**Engine Notes**: none (no ADR engine-compatibility analysis at minimal)

**Control Manifest Rules (this layer)**: N/A (minimal — no control manifest)

---

## Acceptance Criteria

*From `design/game-brief.md` (the **Player goal & fail state** field + MVP feature 3), scoped to this story; exact values from the spec section above:*

- [ ] Bands 4.5 wide each: 2|3|4|3|2 around a random target center; only the Psychic sees the target before reveal
- [ ] Shared live dial for the active team (last write wins); Lock it in or timer locks it
- [ ] Opposing team's majority Left/Right call scores +1 when correct; tie or no call scores 0
- [ ] Second team starts with 1 point; a team scoring 4 while still behind takes another turn
- [ ] First to 10 wins; a tie at 10+ goes to sudden-death turn pairs
- [ ] 2–3 players play co-op: 7 cards, +1 card per 4-pointer, rated total, win at ≥16
- [ ] Psychic says the clue out loud and taps 'Clue given ✓' — no typing
- [ ] A rejoining Psychic still sees the target; spectators never do

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
**Required evidence**: tests: wavelength.test.js; screenshots of each phase at both widths

**Status**: [ ] Not yet created

---

## Dependencies

- Depends on: Story 002
- Unlocks: Story 004
