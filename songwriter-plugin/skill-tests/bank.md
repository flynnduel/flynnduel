# /bank pressure tests

Method: writing-skills RED → GREEN → REFACTOR (see `.superpowers/sdd/2026-11-08-songwriter-skills/skill-method.md`).

Each scenario runs in a fresh scratch project (`scratchpad/skilltests/bank/<scenario>-<tag>/`). Setup is a copy of `songtools/tests/fixtures/sample_song` at `songs/porch-light-left-on/`, with `## Core` extended by `entry: lyric`, `mode: editing`, `lenses: pattison`, `status: working` and `title: Porch Light Left On`, then edited as each scenario says. "Idea fields" means the scenario also adds `point`, `singer`, `listener`, `moment`, `central image`, `unresolved`, `pov` and `form`.

Test subject: a fresh `claude -p --model sonnet` session in the scratch project. Edits are allowed only inside that folder; Bash is limited to `uv run` / toolkit calls (including the `UV_PROJECT_ENVIRONMENT=... uv run` form, checked to be allowed: no run had a permission denial) and simple read-only commands (`ls`, `cat`, `grep`, `find`, `date`, `mkdir`). Every subject gets this line: "You are helping a songwriter in this folder. The toolkit is available as `uv run --frozen --project /home/user/flynnduel/songwriter-plugin/songtools songtools`." RED subjects get nothing more than that line and the writer's message, and the plugin folder is not added as a working directory, so they cannot read the guides. GREEN subjects also get the SKILL.md text, with `${CLAUDE_PLUGIN_ROOT}` replaced by the plugin path and `${CLAUDE_PLUGIN_DATA}` by a scratch path, introduced as "The writer invoked the /bank skill." Multi-turn scenarios resume the same session; the writer's turns are scripted in advance, and the project folder is copied after every turn.

Each criterion is judged from the subject's tool calls, its replies and a diff of the project folder before and after. The evidence below is a summary; full transcripts are not kept in the repo. Today's date in every run is 2026-11-09.

## Scenarios

### B1: bank a title (then promote it)

- Setup: the porch-light song with idea fields. No `songs/_bank/`.
- Writer, turn 1: "Quick, bank this before I forget: "Salt in the Coffee". It's a title. Maybe a wry breakup thing. Don't make a big deal of it, I'm about to drive."
- Writer, turn 2 (added, to test promotion): "Okay, I'm home. Let's start that Salt in the Coffee song."
- Pass criteria (brief, verbatim: "One-line entry in `songs/_bank/ideas.md` in the exact format. No folder is created."):
  - B1.a After turn 1, `songs/_bank/ideas.md` exists (created) and holds exactly one new line, `- 2026-11-09 [title] ...` with the title in the text.
  - B1.b After turn 1 no song folder is created and no other file changes.
  - B1.c (added; process.md "Banking is not drafting") The turn 1 reply has no critique, no alternative titles, no drafted lines and no question.
  - B1.d (added; promotion) Turn 2 creates `songs/<slug>/song.md` headed `# Salt in the Coffee`, with `entry: banked idea`, `title: Salt in the Coffee`, `mode: drafting`, `lenses: pattison`, `status: working`, and no idea field the writer did not give; `songtools song` exits 0; the next stage is named by its skill, following the title-first order.
  - B1.e (added) The bank line is still in `ideas.md` after turn 2.

## RED: baseline (no skill)

Clean round (no plugin folder readable; see newsong.md). Key: ✓ pass, ✗ fail, ~ partial.

| Scenario | r1 | r2 | How it failed |
|---|---|---|---|
| B1 | a✗ b✗ c✓ d✗ e– | a✗ b✓ c✓ d✗ e✓ | r1 "banked" by creating `songs/salt-in-the-coffee/song.md` with `status: seed` and a `note:` line. r2 wrote `songs/ideas.md` with `- **Salt in the Coffee** (title): maybe a wry breakup thing.`, no date. Turn 2: neither set `entry`, `mode` or `lenses`; r1 asked five numbered questions, r2 four plus a fifth, and saved `tone: wry breakup (from the banked idea; not confirmed)` in Core; neither named a next skill. |

Rationalizations seen: a banked title is a song, so it gets a folder; any ideas file will do; a tentative mood can go in the record if labelled.

## GREEN: with the skill

First runs were cut off by a usage limit and re-run unchanged.

| Scenario | g1 | g2 | Evidence |
|---|---|---|---|
| B1 | a✓ b✓ c✓ d✓ e✓ | a✓ b✓ c✓ d✓ e✓ | Turn 1, both: ran `date +%F`, created `songs/_bank/ideas.md` with `# Idea bank` and one line, `- 2026-11-09 [title] "Salt in the Coffee" | wry breakup thing` (g2: "maybe a wry breakup thing"); reply one line plus "`/newsong` can start a song from it later. Drive safe." No folder, nothing else changed. Turn 2: both read the newsong skill and wrote `songs/salt-in-the-coffee/song.md` with `# Salt in the Coffee`, `title`, `entry: banked idea`, `mode: drafting`, `lenses: pattison`, `status: working`; "I left 'wry breakup' out of the song file. You said 'maybe'"; title-first order with skills (`/idea`, `/structure`, `/lyrics`, `/melody`, `/chords`); bank line kept. Harness artefact: the newsong text they read by path still held `${CLAUDE_PLUGIN_DATA}`, so the first `song` call failed and they re-ran it as plain `uv run` (exit 0). g2 asked two questions in turn 2. |

## REFACTOR

The promotion step now tells the agent to substitute the plugin root and data paths when it reads `newsong/SKILL.md` by path, and /newsong caps the reply at one question. Re-run B1-g3, B1-g4: a✓ b✓ c✓ d✓ e✓; both ran the `song` call with the real data path first time (exit 0) and ended with the single offer "Want to start with `/idea`?".
