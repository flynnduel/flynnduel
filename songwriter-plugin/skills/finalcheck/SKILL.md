---
name: finalcheck
description: Use when a songwriter thinks a song is finished, asks for a final check, final pass or last review, asks whether a song is done or ready to demo, record or pitch, or wants to mark a song done, done for now or still working.
---

# Final check

The last review before a draft counts as done: the ten checks of the final-check table, big to small, so no time goes into polishing a line in a verse that may be cut. The plugin reports; the writer decides. It never declares the song finished (or unfinished), and the only file it may change is the `status:` line, after the writer chooses.

Read `${CLAUDE_PLUGIN_ROOT}/guides/rulebook.md` first. Then read `${CLAUDE_PLUGIN_ROOT}/guides/toolkit.md` and `${CLAUDE_PLUGIN_ROOT}/guides/critique.md`; its "Final check" table is the procedure and is followed exactly, all ten steps, in its order. For step 5 also read `${CLAUDE_PLUGIN_ROOT}/guides/melody.md`.

**Violating the letter of these rules is violating the spirit.** A studio booking, "quick one" or "tell me it's done" does not shorten the check or turn it into a verdict.

## Toolkit calls

Run from the writer's project. `<song>` is the song folder, e.g. `songs/porch-light-left-on`. Run each call in the form written, one per command: no shell variables, loops or scripts. Capitalised words (SECTION, N, KEY, CAPO, ...) are placeholders: every value comes from the song files or the writer, never from these examples. If a call is refused or blocked, run it again in that plain form; never guess its result or skip the step. Add `--pron songs/pronunciations.txt` before the subcommand when that file exists.

```
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools pov <song>/lyrics.md
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools stability <song>/lyrics.md
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools cliche <song>/lyrics.md --strict
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools prosody <song> --section SECTION --line N
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools prosody <song> --section SECTION --line N --compare
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools key --melody-low MELODY_LOW --melody-high MELODY_HIGH --voice-low VOICE_LOW --voice-high VOICE_HIGH --key KEY
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools harmony --music <song>/music.md
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools chord transpose KEY CAPO
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools guitar verify SHAPE NAME
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools chart <song> --check
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools drafts diff <song>/drafts/lyrics-vN.md <song>/lyrics.md --song <song>/song.md
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools drafts diff <song>/lyrics.md <song>/lyrics.md --song <song>/song.md
```

## The ten steps

Copy this checklist and work it top to bottom. Each step ends as **pass**, **flag**, **kept by choice**, **asked**, or **not run: <reason>**, with its basis.

```
Final check:
- [ ] 1 Point clear; title in a spotlight; each verse recolors the chorus (Pattison)
- [ ] 2 Pronoun drift, time jumps, missing backstory, twin verses (Dodson)
- [ ] 3 Chorus first line contrasts; stability where intended (Pattison)
- [ ] 4 Remaining prosody flags, ranked, limit stated (Pattison; Hayes)
- [ ] 5 Leaps, breathing room, range and range changes (Perricone)   needs music.md
- [ ] 6 Listener test, stated as a simulation (Stolpe)
- [ ] 7 Voicings, chart against lyrics, capo and key (toolkit)        needs music.md
- [ ] 8 Each kept line returns once (design rule)
- [ ] 9 Irritant scan asked (Simon via Zollo)
- [ ] 10 Writer chooses: done, done for now, keep working (Zollo; Webb)
```

1. **Point, title, recoloring.** Read `song.md`'s idea fields against the lyric. Is the point clear? Is the title in a spotlight position (first or last line of a section)? Does each verse change what the chorus means? This is a reading, so say so; no tool measures it.
2. **Dodson's four checks.** Pronoun drift from `pov` (`shift`, per-section `pov`; a chordless section can raise a false shift). Time jumps and missing backstory are a reading: quote the lines. Twin verses: compare the verses' `stability` profiles and `prosody --compare`, and whether verse 2 adds new information.
3. **Contrast and stability.** From `stability`: the `contrast` result at the chorus's first line, and each section's verdict and reasons. `unstable` is a description; ask whether it is intended.
4. **Prosody.** Run `prosody` for every line that has an entry in `melody.md` and report its flags, strongest first, in the tool's terms, plus the `limit` sentence once. Report the other lines as "no melody set: N lines", not as checked. The flags are the measurement: add no stress findings of your own.
5. **Melody (Perricone).** Only if `music.md` exists; otherwise the step reads **not run: no music.md**. When it exists, ask Perricone's three questions (leaps, breath between phrases, range and range changes within a section), and if the writer gives a section's lowest and highest melody notes, run `key` with the voice range from `song.md`.
6. **Listener test (Stolpe).** Answer as a first-time listener would, and say you are simulating one and cannot hear audio: could the words be heard and followed, is the chorus start clear, could you sing a part after one listen, does the music's mood match the words.
7. **Music check.** Only if `music.md` exists; otherwise **not run: no music.md**. Do not build a chord check from the inline chords in `lyrics.md`, and do not create `music.md`. When it exists: `harmony --music` for the key, compared with `key` in `song.md`, which is the shape key under `capo` (report `dual_reading` and low confidence as ambiguity); `chord transpose KEY CAPO` gives the sounding key to state; `guitar verify SHAPE NAME` for each shape the writer has recorded or gives you, with the shape name and frets counted from the capo (none recorded: "voicings: none recorded"); `chart <song> --check` (writes nothing) for whether each section's inline chords in `lyrics.md` match its `music.md` progression (a mismatch is a flag: which file is right?) and for the chart itself: `exists` false is "no chart yet (`/chart` makes one)", `older_than_lyrics` true is "chart older than the song files". Never compare chords by eye.
8. **Kept lines.** Diff the newest snapshot in `drafts/` (highest N) against `lyrics.md` with `--song`; with no snapshot, diff `lyrics.md` against itself and say there is no snapshot to compare against. List each kept line once in its own short group: text, the issue it was kept over, the writer's reason, and what the diff reports: `kept_missing` (gone from `lyrics.md`) and `kept_changed` (altered since the snapshot). Never judge either by reading. Do not re-argue the kept issue; a new issue on it is a normal flag. Ask one question: "Are you still keeping these as they are?"
9. **Irritant scan.** Ask: "Play it back once more. Does any line, word or note still bother you?" Zollo's point: what still irks you on replay is the song showing what is wrong. The writer decides what to do about it.
10. **Status.** Offer the three choices, and say that writing done is separate from demo done. Then stop and wait.

## The reply

- A table with one row per step, in order: `# | check | result | basis`. A flagged row points to its note.
- Flag notes below the table, ranked by step number, at most three in full (location, observation, mechanism, listener effect, basis, two to four options including "leave it"). For more: "N more flags; want them?"
- The kept-lines group, the irritant question and the status choice, last:
  "Your call: **done**, **done for now**, or **keep working**."
- No verdict anywhere: not "it's done", "it's ready", "not ready yet", "I can't tell you it's done", "I wouldn't lock it". Report what each step found; the writer weighs it.
- No file is changed in this reply.

## Writing the status

Only after the writer chooses, in their own words:

1. Change only the `status:` line in `## Core` of `song.md` to exactly the value chosen: `done`, `done for now`, or `working` (for "keep working"). "Done for now" is `done for now`, never `done`. Add the line if it is missing.
2. Confirm in one line, old → new. Change nothing else: not lyrics, not kept lines, not other `## Core` keys.
3. If the writer's answer is not one of the three ("I guess?", "you decide"), ask again; never choose for them.

## Red flags: stop

Each of these was said by an agent without this skill:

| Thought | Reality |
|---|---|
| "I can't tell you it's done", "isn't ready to call final", "I wouldn't lock it" | No verdict either way. Report the steps; the writer chooses. |
| Writer said "done for now"; wrote `status: done` | Write exactly the chosen value. |
| "Mark the song `final` after those pass" | The statuses are working, done for now, done. |
| A list of stability and POV findings instead of the ten steps | All ten rows, in the table's order, each with its basis. |
| Melody and chord steps silently left out | Each step gets a row: "not run: no music.md" when it is missing. |
| "Is G the shape key or the sounding key?" built from the lyrics' inline chords | Step 7 reads `music.md`; without it, not run. |
| "The lyric chords don't match music.md; I compared them by eye" | `chart --check` measures it. |
| "That one line has stress problems ... scores 36" | Report `prosody` on the `melody.md` setting, in the tool's terms. |
| "I can start on the melody for the rest of Verse 1" | Music is coached, never written. |
| No irritant question; no kept-line question | Steps 8 and 9 are questions to the writer, asked every time. |
| "Quick one, so just the highlights" | All ten steps; the table keeps it short. |
| "The tool calls are blocked, so the check hasn't started" (after trying a script) | Run each call alone, exactly as written in Toolkit calls. |
