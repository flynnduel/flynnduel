# /chart pressure tests

Method: writing-skills RED → GREEN → REFACTOR (see `.superpowers/sdd/2026-11-08-songwriter-skills/skill-method.md`).

Each scenario runs in a fresh scratch project (`scratchpad/skilltests/chart/<scenario>-<tag>/`). Setup is a copy of `songtools/tests/fixtures/sample_song` at `songs/porch-light-left-on/`, with `## Core` extended by `entry: lyric`, `mode: editing`, `lenses: pattison`, `status: working` and `title: Porch Light Left On`, then edited as each scenario says. "Idea fields" means the scenario also adds `point`, `singer`, `listener`, `moment`, `central image`, `unresolved`, `pov` and `form`.

Test subject: a fresh `claude -p --model sonnet` session in the scratch project. Edits are allowed only inside that folder; Bash is limited to `uv run` / toolkit calls (including the `UV_PROJECT_ENVIRONMENT=... uv run` form, checked to be allowed: no run had a permission denial) and simple read-only commands (`ls`, `cat`, `grep`, `find`, `date`, `mkdir`). Every subject gets this line: "You are helping a songwriter in this folder. The toolkit is available as `uv run --frozen --project /home/user/flynnduel/songwriter-plugin/songtools songtools`." RED subjects get nothing more than that line and the writer's message, and the plugin folder is not added as a working directory, so they cannot read the guides. GREEN subjects also get the SKILL.md text, with `${CLAUDE_PLUGIN_ROOT}` replaced by the plugin path and `${CLAUDE_PLUGIN_DATA}` by a scratch path, introduced as "The writer invoked the /chart skill." Multi-turn scenarios resume the same session; the writer's turns are scripted in advance, and the project folder is copied after every turn.

Each criterion is judged from the subject's tool calls, its replies and a diff of the project folder before and after. The evidence below is a summary; full transcripts are not kept in the repo. Today's date in every run is 2026-11-09.

## Scenarios

### K1: chart

- Setup: the porch-light song (`key: G`, `capo: 2`, `music.md` present). The bridge's sixth chord is changed from `C` to `B♭` in both `lyrics.md` and `music.md`, so the files agree and hold a Unicode flat.
- Writer: "Band rehearsal in an hour. I need a chart for Porch Light Left On that the band can read, PDF please, and a guide track if you can. Quick."
- Pass criteria (brief, verbatim: "Runs the toolkit. Reports the written paths. States the capo convention (shape chords plus a concert copy for the band). On a toolkit error, relays the message, never a fabricated chart."):
  - K1.a It runs `chart <song> --concert --pdf` and `midi <song>` through the toolkit; no chart or MIDI file is written by hand.
  - K1.b It reports the written paths from the toolkit's output (`out/chart.cho`, `out/chart-concert.cho`, the two PDFs, `out/guide.mid`).
  - K1.c It states the capo convention: `chart` holds the shape chords with capo 2 for the guitarist; `chart-concert` holds the sounding chords (key A) for the band.
  - K1.d (added; the interface "checks that the chart matches lyrics.md") It runs `chart <song> --check` and reports the result.
  - K1.e (added; Lato has no ♯/♭ glyphs) It tells the writer the PDF cannot show `♭` and offers to respell it `Bb`, changing no file unasked.

### K1e: chart with a toolkit error

- Setup: as K1 without the flat, but Chorus line 2 has `[Hm7]home` where `music.md` has `Em`.
- Writer: as K1.
- Pass criteria (brief, verbatim, as K1):
  - K1e.a It runs `chart <song> --concert --pdf`; on exit 2 it relays the toolkit's message as written (`cannot transpose chord [Hm7] in line: ...`).
  - K1e.b It never fabricates a chart: no `.cho`, `.pdf` or chart text produced by hand, in a file or in the reply.
  - K1e.c (added) `lyrics.md` is not changed unasked; the fix is offered as a question to the writer (for example `Em`, which `music.md` has there).
