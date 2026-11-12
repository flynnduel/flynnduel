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

## RED: baseline (no skill)

As in `critique.md`: r1 and r2 could read the plugin folder and read `guides/critique.md` (marked "guides read"); r3 and r4 could not and are the real RED.

| Scenario | r1 (guides read) | r2 (guides read) | r3 | r4 |
|---|---|---|---|---|
| F1 final check | a✓ b✓ c✓ d✓ e~ f✓ | a✓ b✓ c✓ d✓ e~ f✓ | a✗ b✗ c✗ d✗ e✗ f✗ | a✗ b✗ c✗ d✗ e✗ f✗ |
| F2 missing music.md | a~ b~ | a✓ b✓ | a✗ b✓ | a✗ b✓ |

How the clean baselines failed (in substance):
- **F1 r3 and r4.** No ten steps: each gives a list of stability and point-of-view findings, then a verdict ("I can't tell you it's done … Not ready"; "If you want a decision, I'd rhyme at least one pair in each verse"). There is no irritant question, no kept-line question and no status choice. r3 adds "Mark the song `final` only after those pass", a status that does not exist, and offers "I can start on the melody for the rest of Verse 1", which breaks rule 5. In turn 2 the writer said "done for now", and both wrote `status: done`.
- **F1 r1 and r2 (guides read)** followed the guide's table. Both opened with "I can't tell you it's done". r2 compared the lyric chords with `music.md` "by eye, not with the tool".
- **F2 r3 and r4.** Each gives a list, not the steps, and ends on a verdict ("isn't ready to call final … I wouldn't lock it"; "isn't final yet"). Neither says that `music.md` is missing; the melody and chord checks are dropped or described as "not checked" without saying why. Neither invents a chord check (F2.b holds). r2 (guides read) passed both; r1 (guides read) reported steps 5 and 7 as "Not checkable" with other reasons, and asked "Is G the shape key or the sounding key?" from the inline chords.

## Toolkit addition (test-first): `chart --check`

The baselines compared the inline chords in `lyrics.md` with `music.md` by eye. The first with-skill runs skipped that comparison, and the skill had told them to check chart staleness with `ls -l`. So, test-first, `chart SONG_DIR --check` now writes nothing and reports two things. First, per section: whether the collapsed inline chords equal the `music.md` progression played one or more whole times, plus the chords found only in one of the two files. Second: whether `out/chart.cho` exists and is older than `lyrics.md` or `song.md`. RED was 5 new tests failing. GREEN: `tests/test_chordpro.py` passes 22. On the fixture it reports all four sections as different (for example, Chorus lyrics `C G D Em C G D G` against music `C G D Em`).

## GREEN: with the skill

| Scenario | g1 | g2 | g3 | g4 | g5 | g7 | g8 |
|---|---|---|---|---|---|---|---|
| F1 | ✓ | ✓ | ✓ | a✗ (tool calls blocked) b–e ✓ f✓ | turn 1 ✓, turn 2 usage limit | ✓ | ✓ |
| F2 | ✓ | ✓ | ✓ | ✓ | ✓ | | |

- **F1.** Each run gives a ten-row table `# | check | result | basis` in the guide's order, with Pattison, Dodson, Pattison, Hayes, Perricone, Stolpe, toolkit, design rule, Simon via Zollo, and Zollo and Webb. It opens with "I won't call the song done or not done. This reports what each step found, and you choose." It ends with the kept line listed once ("Are you still keeping these as they are?"), "Play it back once more. Does any line, word or note still bother you?", "Writing done is separate from demo done" and "Your call: **done**, **done for now**, or **keep working**." `status:` is `working` after turn 1 in every run. After turn 2 it is `done for now`, and that is the only diff. From g3 onward, step 7 runs `chart --check` and flags "0 of 4 sections match" as a question for the writer. g4: the harness refused the subject's compound shell commands, and it then wrote a script that also needed approval. It ran nothing and honestly said "the final check hasn't started. I'm not going to guess at any results", but F1.a failed. Counter: run each call as written, one per command, and rerun a refused call in plain form ("The tool calls are blocked, so the check hasn't started" is now a red flag).
- g5 and g6 hit the account usage limit before turn 2 (turn 1 passed a–e). g7 and g8 reran F1 with the final text and passed every criterion.
- **F2.** Steps 5 and 7 read "**not run: no music.md**". g3 adds "I did not build a chord check from the inline chords"; g5 adds "I did not check the inline chords in `lyrics.md`". No `harmony`, `guitar` or `chart --check` call is made, and the project diff is empty.

## Fix round 1

Changes:
- The fixture's `music.md` now agrees with `lyrics.md`'s inline chords, so step 7's pass path is exercised.
- `chart --check` compares every repeated heading.
- Call blocks use placeholders (SECTION, N, MELODY_LOW, KEY, CAPO, SHAPE, NAME); every value comes from the song files or the writer.
- Step 8 reads `kept_missing` and `kept_changed` from `drafts diff`.

| Scenario | g9 | g10 |
|---|---|---|
| F1 | ✓. Step 7: "`chart --check`: all four sections' inline chords match `music.md`. No chart yet"; the harmony dual reading is flagged as ambiguity. Step 8: "No `drafts/` snapshot exists, so I diffed `lyrics.md` against itself … `kept_missing: []`". Status is `working` after turn 1 and `done for now` after turn 2, the only change. | ✓. Step 7 passes, with the ambiguity noted. Step 8 reads `kept_missing` empty and `kept_changed` 0, and says there is no snapshot. Status is as in g9. |
| F2 | ✓. Steps 5 and 7: "Not run: no music.md"; no harmony, guitar, transpose or chart calls; empty diff. | |

## Regression from the end-to-end run (B3, B4)

`skill-tests/end-to-end.md`, stage 11: run right after `/critique`, the subject reused that turn's results and described `axxa` as "the last two end words identical". Step 3 now says how to read `rhyme_scheme` and `end_rhyme_types`, the toolkit section says to run every call in this check, and a red flag covers both. Re-run once after a `/critique` in the same session: every call run again, the scheme relayed correctly.
