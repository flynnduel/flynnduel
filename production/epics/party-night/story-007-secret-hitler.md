# Story 007: Secret Hitler: rules engine, 1930s poster art and screens

> **Epic**: Party Night
> **Status**: Ready
> **Layer**: Feature
> **Type**: Logic
> **Estimate**: [fill before starting]
> **Manifest Version**: N/A (minimal — no control manifest)
> **Last Updated**: [set by /dev-story when implementation begins]

## Context

**GDD**: `design/game-brief.md`
**Requirement**: Brief MVP feature 5
**Detailed rules**: `docs/superpowers/specs/2026-10-04-party-hub-design.md` §8 · build steps: `docs/superpowers/plans/2026-10-04-party-hub.md` Tasks 8 and 12

**ADR Governing Implementation**: N/A (minimal — no ADRs)
**ADR Decision Summary**: N/A (minimal — no ADRs)
**ADR Version**: N/A (minimal — no ADRs)

**Engine**: Web Node 20+ | **Risk**: NOT ASSESSED (no VERSION.md risk rating)
**Engine Notes**: none (no ADR engine-compatibility analysis at minimal)

**Control Manifest Rules (this layer)**: N/A (minimal — no control manifest)

---

## Acceptance Criteria

*From `design/game-brief.md` (the **Player goal & fail state** field + MVP feature 5), scoped to this story; exact values from the spec section above:*

- [ ] Role table for 5–10 players; Hitler knows the Fascists only at 5–6
- [ ] Term limits (5-player exception); strict-majority Ja; tie fails; tracker at 3 enacts the top policy with power ignored and limits cleared
- [ ] Legislative session: 3 → 2 → 1 with private hands and a SILENCE screen for everyone; reshuffle below 3 cards
- [ ] Presidential powers per player-count table; investigate once per player; special-election order; execution (Hitler executed → Liberals win)
- [ ] Veto after 5 Fascist policies (accept → tracker +1; refuse → must enact)
- [ ] All four win conditions incl. Hitler elected Chancellor after 3 Fascist policies
- [ ] Intro card shows exactly: 'Secret Hitler by Goat, Wolf & Cabbage — CC BY-NC-SA 4.0'; no swastikas or real insignia
- [ ] Host Skip for an absent President/Chancellor after the phase timer (skipped nomination = failed election)

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
**Required evidence**: tests: secret-hitler.test.js; screenshots

**Status**: [ ] Not yet created

---

## Dependencies

- Depends on: Story 006
- Unlocks: None
