# Story 001: Rooms, avatars, join from anywhere

> **Epic**: Party Night
> **Status**: Done
> **Layer**: Foundation
> **Type**: Integration
> **Estimate**: [fill before starting]
> **Manifest Version**: N/A (minimal — no control manifest)
> **Last Updated**: [set by /dev-story when implementation begins]

## Context

**GDD**: `design/game-brief.md`
**Requirement**: Brief MVP feature 1
**Detailed rules**: `docs/superpowers/specs/2026-10-04-party-hub-design.md` §2–3, §12 · build steps: `docs/superpowers/plans/2026-10-04-party-hub.md` Tasks 1–2

**ADR Governing Implementation**: N/A (minimal — no ADRs)
**ADR Decision Summary**: N/A (minimal — no ADRs)
**ADR Version**: N/A (minimal — no ADRs)

**Engine**: Web Node 20+ | **Risk**: NOT ASSESSED (no VERSION.md risk rating)
**Engine Notes**: none (no ADR engine-compatibility analysis at minimal)

**Control Manifest Rules (this layer)**: N/A (minimal — no control manifest)

---

## Acceptance Criteria

*From `design/game-brief.md` (the **Player goal & fail state** field + MVP feature 1), scoped to this story; exact values from the spec section above:*

- [x] Creating a room returns a unique 4-letter code (no I/O); joining is case-insensitive
- [x] Names 1–16 chars, unique among connected players ('That name is taken'); max 12 players
- [x] Avatars: DiceBear lorelei/notionists or a ≤40 KB 160×160 JPEG photo; served by URL, never in views
- [x] Refresh/reconnect with the stored token restores the same seat; host passes to earliest connected player
- [x] `npm start` prints a public tunnel URL + QR, or falls back to the LAN URL with a reason and keeps running
- [x] Chat 1–140 chars, 1 msg/s, last 50 kept; per-socket 20 actions/s limit

---

## Implementation Notes

- Code in `src/party-hub/`; engines pure and deterministic (injected `rng`/`now`); only `Room` touches sockets
- Follow the plan steps named above; write tests first
- Completed via the superpowers SDD plan, commits 705bcf8..fc9f232, task reviews clean.

---

## Out of Scope

- Anything owned by other stories in this epic (see EPIC.md)

---

## QA Test Cases

*N/A — no qa-lead specs at this tier; implement against the Acceptance Criteria above*

---

## Test Evidence

*Governed by `qa.level: minimal`: tests are advisory, but every UI screen touched needs a retained screenshot in `production/qa/evidence/`.*

**Story Type**: Integration
**Required evidence**: src/party-hub/test/{rooms,room,avatar,tunnel,smoke.hub}.test.js — 38 passing

**Status**: [x] Exists — passing

---

## Dependencies

- Depends on: None
- Unlocks: Story 002
