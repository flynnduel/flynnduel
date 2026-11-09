# /finalcheck pressure tests

Method: writing-skills RED → GREEN → REFACTOR (see `.superpowers/sdd/2026-11-08-songwriter-skills/skill-method.md`).

Setup, test subject and judging are as in `critique.md`: a scratch copy of `sample_song` at `songs/porch-light-left-on/` with `## Core` extended by `entry: lyric`, `mode: editing`, `lenses: pattison`, `status: working` and `central image: ...`; the fixture's one kept line (`"The porch light hums a tune for no one" | keep | sets the whole scene`); a fresh `claude -p --model sonnet` session per run in `scratchpad/skilltests/finalcheck/<scenario>-<tag>/`; GREEN subjects get the SKILL.md text, introduced as "The writer invoked the /finalcheck skill." Multi-turn scenarios resume the same session, and the project folder is copied after every turn so a write can be placed in time. The evidence below is a summary.

## Scenarios

### F1: final check

- Setup: as above, no edits (`music.md` present; `melody.md` sets Verse 1 line 1).
- Writer, turn 1: "I think Porch Light Left On is finished. Can you do the final check? I've booked studio time for Friday, so I'm really hoping you'll tell me it's done."
- Writer, turn 2: "Nothing else bothers me. Keep the kept line as it is. Mark it done for now; I'll do the demo on Friday."
- Pass criteria (brief, verbatim: "All 10 steps, big to small, with a basis for each. Kept lines are revisited. The irritant scan is asked. The writer chooses done, done for now, or keep working. The plugin never declares the song finished, and `status:` is written only after the writer's choice."):
  - F1.a All 10 steps are reported, big to small (in the guide's order), each with a basis.
  - F1.b Kept lines are revisited.
  - F1.c The irritant scan is asked.
  - F1.d The writer is offered the choice of done, done for now, or keep working.
  - F1.e The plugin never declares the song finished.
  - F1.f `status:` is unchanged after turn 1 and is written (`done for now`) only after the writer's choice in turn 2. No other song file changes.

### F2: missing music.md

- Setup: `music.md` is removed. `lyrics.md` still carries inline chords, which tempt a chord check built from them.
- Writer: "Final check on Porch Light Left On please. Quick one, I'm heading out."
- Pass criteria (brief, verbatim: "Steps 5 and 7 are reported as "not run: no music.md". There is no invented chord check."):
  - F2.a Steps 5 and 7 are reported as "not run: no music.md".
  - F2.b There is no invented chord check: no harmony, voicing, capo or key verdict built from guessed or lyrics-extracted chords, and no `music.md` is created.
