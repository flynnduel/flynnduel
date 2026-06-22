# S.A.G.E. v2 — Design Document

**Strategic Assessment of Grassroots Ecosystems**

Status: Design (pre-implementation)
Date: 2026-06-22
Supersedes: the Notion + Claude Project implementation ("Field Operator OS v1")

This document records the architectural decisions for rebuilding S.A.G.E. from a
Notion-based prototype into an owned software system. It continues the decision
log from the v1 Design Decisions document (Decisions 001–020), picking up at
Decision 021.

The **product vision, philosophy, engines, and epistemics from v1 do not change.**
Community ownership, Observed/Inferred/Unknown, approval-before-writes, the
one-question rule, the nine operating engines, the neutral synthesis voice — all
of it carries forward unchanged. v2 changes only **how the system is built**, not
what it is or what it believes.

---

## 1. Why rebuild

v1 proved the idea in days: a large system prompt inside a Claude Project, wired
to a 7-database Notion workspace via the connector, reading and writing
automatically. It works. But day-to-day use surfaced five ceilings, and all five
are true at once:

1. **It only runs inside a chat.** Proactive flagging, pattern detection, and
   synthesis happen only when the volunteer opens a session and asks. The system
   cannot work in the background.
2. **It will not scale.** Three days of data fits in context. Two years will not.
   The brain has no real retrieval — it reasons over whatever happens to be in the
   current chat.
3. **It is not an owned, showable artifact.** A Claude Project cannot be
   versioned, cannot go on a portfolio, and cannot be cleanly handed to another
   volunteer.
4. **Capture is manual.** Every observation requires opening a chat. There is no
   automated path from "voice note about my day" to "processed into the system."
5. **A giant prompt drifts.** Engine behavior is not reliably consistent run to
   run.

A system prompt cannot fix any of these. Owned software fixes all of them. That
is the rebuild.

A sixth signal confirmed the direction: **Notion was already slow at three days
of data.** Not from data volume — three days is nothing — but because the Notion
client is heavy over Gambian connectivity, and its API (~3 req/s, paginated, no
query language) is a poor foundation for an engine that must cross-reference
records constantly.

---

## 2. The key realization

The volunteers (Flynn, Maria) do exactly two things with S.A.G.E.:

1. **Add observations.**
2. **Read what S.A.G.E. surfaces back.**

They do **not** browse or hand-edit the seven databases. Those databases are the
**brain's internal memory**, not a human-facing application. v1's mistake was
forcing humans to navigate the brain's memory on their phones — that is the source
of the slowness and friction.

Once we accept that humans only need an **IN** and an **OUT**, Notion has no job
left and is removed entirely.

---

## 3. Architecture

S.A.G.E. v2 is three independently buildable and swappable layers.

```
  IN  ─ Capture ──────────────────────────────────────────────┐
       voice note or typed text, from a phone, over any signal │
       voice → transcription; volunteer identity from sender   │
                                                               ▼
  ┌──────────────────── THE BRAIN (owned Python service) ──────────────┐
  │  • SQLite system of record  (the 7 databases → 7 relational tables) │
  │  • 9 engines as real code orchestrating Claude API calls            │
  │  • Retrieval: query SQL for relevant records, feed only those       │
  │  • Approval gates enforced as logic                                 │
  │  • Runs on-demand (new observation) AND on a schedule (proactive)   │
  └────────────────────────────────────────────────────────────────────┘
                                                               │
  OUT ─ Read ──────────────────────────────────────────────────┘
       synthesis, the one clarifying question, flags, weekly focus,
       returned through the same channel; approvals happen by reply
```

The intended human experience: **talk to S.A.G.E. like a contact.** Send a voice
note about your day; get back a sharp, uncertainty-aware reflection plus one
question plus any flags; approve writes with a reply. Lighter than Notion, and
better suited to the field.

### How this addresses the five ceilings

| Ceiling | Fixed by |
|---|---|
| Only runs in a chat | Scheduled background runs in the brain |
| Won't scale | SQL retrieval — never holds everything at once |
| Not owned/showable | A versioned Python repo + SQL schema |
| Manual capture | Messaging channel + voice transcription |
| Prompt drift | Engines as code with structured, versioned prompts |

---

## 4. Design Decisions (continuing from v1's Decision 020)

### Decision 021 — Owned software replaces the system prompt
**Decision.** The nine engines become real code that calls the Claude API, not a
single system prompt interpreted per chat.
**Reasoning.** Background operation, scaling, consistency, and a showable artifact
are all impossible for a prompt and routine for a codebase.
**Implication.** The system prompt becomes structured, version-controlled prompts
plus orchestration logic. Each engine is independently testable.

### Decision 022 — SQLite is the system of record
**Decision.** The seven Notion databases become seven SQLite tables. SQLite is the
canonical store.
**Reasoning.** The data was always relational and every relation is already
documented. SQLite is fast, owned, portable (a single file), version-friendly, and
plays directly to the maintainer's relational-database strengths. It removes
Notion's API rate limits and lack of a query language.
**Implication.** A migration exports current Notion data into SQLite so nothing is
lost. Schema lives in the repo.

### Decision 023 — Notion is removed
**Decision.** Notion is dropped as both system of record and interface.
**Reasoning.** Volunteers only add observations and read what S.A.G.E. surfaces;
they never browse the databases. The interface job Notion was doing is not needed,
and Notion was already slow.
**Implication.** No Notion dependency in v2. (A read-only export could be
reconsidered later if a browsable view is ever wanted.)

### Decision 024 — Humans interact through capture-in / read-out only
**Decision.** The only two human surfaces are an IN (capture) and an OUT (read).
**Reasoning.** This matches actual usage and keeps the field experience light
enough for poor connectivity.
**Implication.** No general database-browsing UI is built. Approvals occur in the
read-out channel by reply.

### Decision 025 — Retrieval, not whole-context reasoning
**Decision.** The brain queries SQL for the records relevant to the current
observation or question and feeds only those to Claude.
**Reasoning.** This is what allows the system to grow to years of data without
hitting the context ceiling.
**Implication.** Retrieval quality becomes a first-class concern. Early on, with
thin data, retrieval may be simple (recent + related-by-key); it can grow toward
semantic retrieval as the corpus grows.

### Decision 026 — Automated, voice-first capture
**Decision.** Observations are captured as voice notes or short text from a phone
and transcribed automatically; volunteer identity is derived from the sender.
**Reasoning.** Lowest friction in the field; removes the "open a chat every time"
burden; the `Flynn:` / `Maria:` prefix becomes automatic.
**Implication.** A transcription step sits in front of the brain. The capture
channel is chosen in Phase 2 (see Open Questions).

### Decision 027 — Storage is accessed through an interface, to keep options open
**Decision.** The brain talks to its store through a thin storage interface, with a
SQLite implementation today.
**Reasoning.** If SQLite is ever outgrown (e.g. a move to Postgres, or a synced
field interface), it becomes a swap behind the same interface rather than a
rewrite.
**Implication.** Engines never issue raw store-specific calls; they go through the
interface.

### Decision 028 — Build the spine before the channel
**Decision.** Prove the full read→reason→propose→approve→write loop with one engine
via a CLI before building any messaging/voice plumbing.
**Reasoning.** The core loop is the architecture in miniature; de-risking it first
avoids building a channel onto an unproven brain.
**Implication.** Phase 1 ships without a capture channel; the channel is Phase 2.

---

## 5. What carries forward unchanged from v1

These are not up for redesign — they are the product:

- The nine engines (Field Debrief, Issue Synthesis, Stakeholder Mapping,
  Navigation, Community Action Support, Reflection, Safety, Handover, Field
  Operations Planning) and auto mode detection (primary + secondary signals).
- The seven-database schema and its relations (now SQL tables).
- Epistemics: Observed / Inferred / Unknown; Low/Medium/High confidence; high
  confidence is rare; preserve uncertainty; never refuse synthesis under thin data.
- Community ownership stance ("Community Action," over-functioning watch, neutral
  synthesis voice).
- Approval before writes.
- Reflection privacy.
- One question at a time; mobile-readable, adaptive-length output.
- The three-level safety framework.

---

## 6. Build sequence

- **Phase 0 — Scaffold.** Python repo; the 7-table SQLite schema; v1 design docs
  moved in as living documentation; Claude client; migrate current Notion data
  into SQLite.
- **Phase 1 — Core loop, one engine end to end (Field Debrief).** Observation text
  → detect mode → retrieve context from SQL → Claude runs the engine → propose
  structured Field Journal entry + "Claude Surfaced" synthesis + one question →
  approval gate → write to SQL. Driven from a CLI.
- **Phase 2 — Capture channel.** IN/OUT wiring (messaging channel + voice
  transcription). Real field use begins.
- **Phase 3 — Remaining engines + scheduled proactive flagging.**

---

## 7. Open questions

- **Capture channel (Phase 2).** WhatsApp is what the volunteers actually use in
  The Gambia but requires Meta Business approval; Telegram bots are trivial to
  stand up; a tiny web form is the simplest fallback. Leaning Telegram first,
  WhatsApp later. Decide at Phase 2.
- **Where the brain runs.** Local laptop vs. a small always-on host. A scheduled
  background brain wants something always-on; to be decided before Phase 3.
- **Transcription.** Which speech-to-text (e.g. Whisper) and whether it runs
  locally or via API; decide at Phase 2.

---

## 8. Required credentials (when running live)

- Anthropic API key (the brain).
- Capture-channel credentials (e.g. a Telegram bot token) — Phase 2 only.

Nothing above is needed to build and unit-test Phases 0–1.
