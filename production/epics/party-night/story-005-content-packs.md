# Story 005: Content packs: 11 categories of original cards and words

> **Epic**: Party Night
> **Status**: Ready
> **Layer**: Feature
> **Type**: Config/Data
> **Estimate**: [fill before starting]
> **Manifest Version**: N/A (minimal — no control manifest)
> **Last Updated**: [set by /dev-story when implementation begins]

## Context

**GDD**: `design/game-brief.md`
**Requirement**: Brief MVP feature 7
**Detailed rules**: `docs/superpowers/specs/2026-10-04-party-hub-design.md` §9 · build steps: `docs/superpowers/plans/2026-10-04-party-hub.md` Task 5

**ADR Governing Implementation**: N/A (minimal — no ADRs)
**ADR Decision Summary**: N/A (minimal — no ADRs)
**ADR Version**: N/A (minimal — no ADRs)

**Engine**: Web Node 20+ | **Risk**: NOT ASSESSED (no VERSION.md risk rating)
**Engine Notes**: none (no ADR engine-compatibility analysis at minimal)

**Control Manifest Rules (this layer)**: N/A (minimal — no control manifest)

---

## Acceptance Criteria

*From `design/game-brief.md` (the **Player goal & fail state** field + MVP feature 7), scoped to this story; exact values from the spec section above:*

- [ ] 11 packs with the spec's names; ≥15 spectrum cards and ≥40 words per pack (≥150 / ≥400 total)
- [ ] All text original; words distinct within a pack; no slurs or group-targeting (banned-terms check)
- [ ] Defaults: Classic + Pop Culture; host toggles packs (at least one on)
- [ ] No spectrum card repeats within a party until the pool is exhausted; 25 distinct Codenames words per board

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

**Story Type**: Config/Data
**Required evidence**: tests: content.test.js; smoke check

**Status**: [ ] Not yet created

---

## Dependencies

- Depends on: Story 004
- Unlocks: Story 006
