# Story 006: Codenames: rules engine and screens

> **Epic**: Party Night
> **Status**: Ready
> **Layer**: Feature
> **Type**: Logic
> **Estimate**: [fill before starting]
> **Manifest Version**: N/A (minimal — no control manifest)
> **Last Updated**: [set by /dev-story when implementation begins]

## Context

**GDD**: `design/game-brief.md`
**Requirement**: Brief MVP feature 4
**Detailed rules**: `docs/superpowers/specs/2026-10-04-party-hub-design.md` §7 · build steps: `docs/superpowers/plans/2026-10-04-party-hub.md` Tasks 7 and 11

**ADR Governing Implementation**: N/A (minimal — no ADRs)
**ADR Decision Summary**: N/A (minimal — no ADRs)
**ADR Version**: N/A (minimal — no ADRs)

**Engine**: Web Node 20+ | **Risk**: NOT ASSESSED (no VERSION.md risk rating)
**Engine Notes**: none (no ADR engine-compatibility analysis at minimal)

**Control Manifest Rules (this layer)**: N/A (minimal — no control manifest)

---

## Acceptance Criteria

*From `design/game-brief.md` (the **Player goal & fail state** field + MVP feature 4), scoped to this story; exact values from the spec section above:*

- [ ] Key: starting team 9 agents, other 8, 7 bystanders, 1 assassin; only spymasters see it
- [ ] Spymaster says the clue aloud and taps 0–9 or ∞; guesses allowed = number+1 (0 and ∞ unlimited)
- [ ] At least one guess before End turn; bystander or opponent agent ends the turn; assassin loses instantly
- [ ] A team wins when all its agents are revealed, even by the opponent
- [ ] Illegal-clue challenge: room vote; upheld → turn ends and opposing spymaster reveals one of their agents
- [ ] Hold 1 s to reveal; avatar marks visible to own team only; operatives never see the key before reveal

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
**Required evidence**: tests: codenames.test.js; screenshots

**Status**: [ ] Not yet created

---

## Dependencies

- Depends on: Story 005
- Unlocks: Story 007
